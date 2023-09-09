import sys
import requests
import pandas as pd
import json
import yaml
import os
import datetime


class SpreadSheet:
    """飞书电子表格操作"""
    def __init__(self, spreadsheetToken):
        conf_path = os.getenv('myconf')
        conf = yaml.full_load(open(conf_path + '/fs_conf.yml', encoding='utf-8').read())
        current_time = datetime.datetime.now()
        """初始化生成应用凭证"""
        self.app_id = conf['feishu_app']['app_id']
        self.app_secret = conf['feishu_app']['app_secret']
        self.spreadsheetToken = spreadsheetToken  # 电子表格id
        print(self.spreadsheetToken)
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

    def show_range(self, sheet_id, cell_range, valueRenderOption='ToString', dateTimeRenderOption='FormattedString'):
        """读取电子表格range内的单元格数据"""
        url = 'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/' + \
              self.spreadsheetToken + '/values/' + sheet_id + '!' + cell_range +\
              '?valueRenderOption='+valueRenderOption+\
              '&dateTimeRenderOption='+dateTimeRenderOption

        response = requests.get(url=url, headers=self.headers).json()
        return response['data']['valueRange']['values']