import sys
import requests
import pandas as pd
import json
import yaml
import os
import datetime
import re


class SpreadSheet:
    """飞书电子表格操作"""
    def __init__(self, spreadsheetToken):
        conf_path = os.getenv('fs_conf')
        conf = yaml.full_load(open(conf_path, encoding='utf-8').read())
        current_time = datetime.datetime.now()
        """初始化生成应用凭证"""
        self.app_id = conf['feishu_app']['app_id']
        self.app_secret = conf['feishu_app']['app_secret']
        self.spreadsheetToken = spreadsheetToken  # 电子表格id
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        params = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        response = requests.request("POST", url, json=params).json()

        if response['msg'] == 'ok':
            self.token = response['tenant_access_token']
            self.headers = {'Authorization': 'Bearer ' + self.token}
            print("current time:{} tenant:{}".format(current_time, self.token))
        else:
            print('current time:{} Error:failed in initialize method, return code:{}'.format(current_time,
                                                                                             response['code']))

    def read_range(self, sheet_id, range, valueRenderOption='ToString', dateTimeRenderOption='FormattedString'):
        """读取指定range内容"""
        url = 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/' + \
              self.spreadsheetToken + '/values/' + sheet_id + '!' + range +\
              '?valueRenderOption='+valueRenderOption+\
              '&dateTimeRenderOption='+dateTimeRenderOption

        response = requests.get(url=url, headers=self.headers).json()

        if response.get("code") and response.get("code") != 0:
            print("failed in show_range method!\n res:{}".format(response))

        return response['data']['valueRange']['values']

    def write_range(self, sheet_id, range, ls):
        """向指定range写入数据"""
        url = 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/'+self.spreadsheetToken+'/values'

        params = {
            "valueRange":{
                "range": sheet_id + '!' + range,
                "values": ls
            }
        }

        response = requests.request(method="PUT", url=url, headers=self.headers, json=params).json()

        if response.get("code") and response.get("code") != 0:
            print("failed in write_range method!\n res:{}".format(response))


    def col_index(self, col_str):
        """将电子表格英文索引转换为数字索引"""
        column_str = col_str.upper()
        num = 0
        for char in column_str:
            num = num * 26 + (ord(char) - ord('A')) + 1
        return num

    def range_shape(self, range):
        """计算电子表格range的行列数"""
        splt = re.findall(r'[A-Z]+|\d+', range)
        col_start = self.col_index(splt[0])
        col_end = self.col_index(splt[2])
        row_start = int(splt[1])
        row_end = int(splt[3])
        col_n = col_end - col_start + 1
        row_n = row_end - row_start + 1
        return row_n, col_n

    def generate_na(self, row_n, col_n):
        """生成空值矩阵"""
        NA_matrix = [[''] * col_n for _ in range(row_n)]
        return NA_matrix

    def clean_range(self, sheet_id, range):
        """伪清空指定range内容"""
        row_n, col_n = self.range_shape(range)
        NA_matrix = self.generate_na(row_n=row_n, col_n=col_n)
        self.write_range(sheet_id=sheet_id, range=range, ls=NA_matrix)

    def cover_range(self, sheet_id, range, ls):
        """覆盖写入range：清空整个range后再写入"""
        self.clean_range(sheet_id=sheet_id, range=range)
        self.write_range(sheet_id=sheet_id, range=range, ls=ls)

