import sys
import requests
import pandas as pd
import json
import yaml
import os
import datetime

class BiTable:
    """飞书多维表格操作"""
    def __init__(self, app_token):
        conf_path = os.getenv('library')
        conf = yaml.full_load(open(conf_path + 'my_conf.yml', encoding='utf-8').read())
        current_time = datetime.datetime.now()

        """初始化生成应用凭证"""
        self.app_id = conf['feishu_app']['app_id']
        self.app_secret = conf['feishu_app']['app_secret']
        self.app_token = app_token  # 多维表格id

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
            print('current time:{} Error:failed in initialize method, return code:{}'.format(current_time, response['code']))


    def show_all_records(self, table_id):
        """列出数据表记录:fields及record_id"""
        has_more = True
        page_token = ''

        fields = []
        record_ids = []

        while has_more:
            url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/' + \
                  self.app_token + '/tables/' + table_id + '/records/?page_token=' + \
                  page_token + '&page_size=500'

            response = requests.get(url=url, headers=self.headers).json()

            if response['msg'] == 'success':
                if response['data']['total'] == 0:
                    print('Warning:in show_all_records, because the table has no record.')
                    return pd.DataFrame(fields), record_ids

                items = response['data']['items']
                has_more = response['data']['has_more']
                page_token = response['data']['page_token']

                for item in items:
                    fields.append(item['fields'])
                    record_ids.append(item['record_id'])

            else:
                print('Error:failed in show_records method. \n response:{}'.format(response))

        return pd.DataFrame(fields), record_ids


    def delete_records(self, table_id, record_ids_ls):
        """按给定记录id列表进行删除"""
        if len(record_ids_ls) > 500:
            print('Error:delete_records method, 500 ids limit.')
            sys.exit()

        if len(record_ids_ls) == 0:
            print('Warning:delete_records method, record_ids_ls is Null')
            return ''

        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/' +\
              self.app_token + '/tables/' + table_id + '/records/batch_delete'
        params = json.dumps({"records": record_ids_ls})

        response = requests.request("POST", url, headers=self.headers, data=params).json()
        if response['msg'] != 'success':
            print('Error:delete_some_records method. \nresponse:{}'.format(response))
            sys.exit()


    def delete_all_records(self, table_id):
        """删除整表记录"""
        fields, record_ids = self.show_all_records(table_id=table_id)

        if len(record_ids) > 0:
            ids_split = [record_ids[i:i+500] for i in range(0, len(record_ids), 500)]
            for ids in ids_split:
                self.delete_records(table_id=table_id, record_ids_ls=ids)
        else:
            print('Warning:delete_all_records method, table was empty before.')
            pass


    def insert_records(self, table_id, records_ls):
        """插入多行记录"""
        if len(records_ls) > 500:
            print('Error:insert_records method, 500 rows limit.')
            sys.exit()
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/' + \
              self.app_token + '/tables/' + table_id + '/records/batch_create'
        params = json.dumps({"records": records_ls})

        response = requests.request("POST", url, headers=self.headers, data=params).json()

        if response['msg'] != 'success':
            print('Error:failed in insert_records method. \nresponse:{}'.format(response))
            sys.exit(1)


    def insert_df(self, table_id, df):
        """将dataframe转换格式后分页插入"""
        df_to_dict = df.to_dict(orient='records')
        fields_ls = [{'fields': d} for d in df_to_dict]
        fields_split = [fields_ls[i:i + 500] for i in range(0, len(fields_ls), 500)]
        for records_ls in fields_split:
            self.insert_records(table_id=table_id, records_ls=records_ls)
        print('{} records were inserted into table:{}'.format(len(fields_ls), table_id))


    def refresh(self, table_id, df):
        """清空数据表后插入完整dataframe"""
        self.delete_all_records(table_id=table_id)
        self.insert_df(table_id=table_id, df=df)


class SpreadSheet:
    """飞书电子表格操作"""
    def __init__(self, spreadsheetToken):
        conf_path = os.getenv('myconf')
        conf = yaml.full_load(open(conf_path + '/my_conf.yml', encoding='utf-8').read())
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
