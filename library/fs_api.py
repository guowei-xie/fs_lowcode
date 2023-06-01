import base64
import hashlib
import hmac
from datetime import datetime
import requests

import pandas as pd
from requests_toolbelt import MultipartEncoder
import json
import math


class FeishuBot:
    """自定义机器人"""
    def __init__(self, webhook_url: str, secret: str) -> None:
        # webhook_url,secret参数获取说明：https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN
        if not secret:
            raise ValueError("invalid secret key")
        self.secret = secret
        self.webhook_url = webhook_url

    # 拼接时间戳以及签名校验
    def gen_sign(self, timestamp: int) -> str:
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)

        # 使用 HMAC-SHA256 进行加密
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()

        # 对结果进行 base64 编码
        sign = base64.b64encode(hmac_code).decode('utf-8')

        return sign


    # 可发送消息类型及参数参考：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/im-v1/message/create_json
    def send_text(self, content: str) -> None:
        """发送纯文本内容"""
        timestamp = int(datetime.now().timestamp())
        sign = self.gen_sign(timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "text",
            # "content": {"text": content},
            "content": {"text": content}
        }
        resp = requests.post(url=self.webhook_url, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result["code"] != 0:
            print(result["msg"])
            return
        print("消息发送成功")

    def send_rich_text(self, content_json_format: str) -> None:
        """发送富文本内容"""
        timestamp = int(datetime.now().timestamp())
        sign = self.gen_sign(timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "post",
            "content": content_json_format
        }
        resp = requests.post(url=self.webhook_url, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result["code"] != 0:
            print(result["msg"])
            return
        print("消息发送成功")

    def send_card(self, card_json: str) -> None:
        """发送消息卡片"""
        timestamp = int(datetime.now().timestamp())
        sign = self.gen_sign(timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "interactive",
            "card": card_json
        }
        resp = requests.post(url=self.webhook_url, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result["code"] != 0:
            print(result["msg"])
            return
        print("消息发送成功")

    def send_img(self, image_key) -> None:
        """发送图片消息"""
        timestamp = int(datetime.now().timestamp())
        sign = self.gen_sign(timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "content": {"image_key": image_key},
            "msg_type": "image"
        }
        resp = requests.post(url=self.webhook_url, json=params)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") and result["code"] != 0:
            print(result["msg"])
            return
        print("消息发送成功")

class MyCloud:
    """------云空间------"""
    def __init__(self, app_id: str, app_secret: str) -> None:
        # 初始化参数获取：在自建应用内--凭证与基础信息
        self.app_id = app_id
        self.app_secret = app_secret

        # 获取自建应用tenant_access_token
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        params = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.request("POST", url, json=params)
        response = response.json()
        if response['msg'] == 'ok':
            self.token = response['tenant_access_token']
        else:
            print('token获取失败，code:{}'.format(response['code']))

    # 图片上传,返回image_key
    def upload_image(self, image_path):
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        form = {'image_type': 'message',
                'image': (open(image_path, 'rb'))}  # 需要替换具体的path
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': 'Bearer '+ self.token  # 获取tenant_access_token, 需要替换为实际的token
        }
        headers['Content-Type'] = multi_form.content_type
        response = requests.request("POST", url, headers=headers, data=multi_form)
        response = response.json()
        if response['msg'] == 'ok':
            return response['data']['image_key']
        else:
            print('图片上传失败，code:{}, msg:{}'.format(response['code'], response['msg']))

    # 上传文件，返回file_key
    def upload_file(self, file_path, file_rename, file_type):
        url = "https://open.feishu.cn/open-apis/im/v1/files"
        form = {'file_type': 'stream',
                'file_name': file_rename,
                'file': (file_rename, open(file_path, 'rb'),
                         file_type)}  # 需要替换具体的path  具体的格式参考  https://www.w3school.com.cn/media/media_mimeref.asp
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': 'Bearer '+self.token  # 获取tenant_access_token, 需要替换为实际的token
        }
        headers['Content-Type'] = multi_form.content_type
        response = requests.request("POST", url, headers=headers, data=multi_form)
        response = response.json()
        if response['msg'] == 'ok':
            return response['data']['file_key']
        else:
            print('文件上传失败，code:{}, msg:{}'.format(response['code'], response['msg']))

class BiTable:
    """------多维表格------"""
    def __init__(self, app_id: str, app_secret: str, app_token: str) -> None:
        # 初始化参数：自建应用--凭证与基础信息
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token  # 此处的app_token并非自建应用的，而是多维表格的token_id
        # 获取自建应用tenant_access_token
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        params = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.request("POST", url, json=params)
        response = response.json()
        if response['msg'] == 'ok':
            self.token = response['tenant_access_token']
            self.headers = {'Authorization': 'Bearer ' + self.token}
        else:
            print('token获取失败，code:{}'.format(response['code']))

    # 获取多维表格元数据
    def get_meta_data(self):
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/'+self.app_token
        response = requests.get(url=url, headers=self.headers)
        response = response.json()

        if response['msg'] == 'success':
            return response['data']
        else:
            print('获取多为表格元数据失败！ response:{}'.format(response))

    # 列出数据表名及table_id
    def show_table_list(self):  # -> df
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/'+self.app_token+'/tables'
        response = requests.get(url=url, headers=self.headers)
        response = response.json()

        df = pd.DataFrame(response['data']['items'])
        if response['msg'] == 'success':
            return df
        else:
            print('列出数据表失败! response:{}'.format(response))

    #列出数据表记录
    def show_records(self, table_id): # -> df
        df_list = []
        page_token = ''
        has_more = True
        while has_more:
            url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/' + self.app_token + '/tables/' + table_id + '/records/?page_token=' + page_token + '&page_size=500'
            response = requests.get(url=url, headers=self.headers)
            response = response.json()
            if response['msg'] == 'success':
                items = response['data']['items']
                records_info = []
                if items: #表记录非空时
                    for item in items:
                        record_info = item['fields']
                        record_info['record_id'] = item['record_id']
                        records_info.append(record_info)
                    df_list.append(pd.DataFrame(records_info))
                    has_more = response['data']['has_more']
                    page_token = response['data']['page_token']
                else:
                    print('目标数据表空！')
            else:
                print('失败！ response:{}'.format(response))
        return pd.concat(df_list)

    # 添加数据记录（单条，末尾添加）
    def insert_record(self, table_id, record_dict): # <- dict，例如：{'字段1': '测试', '字段2': 123, '字段3': 35, '字段4': '100%'}
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/'+self.app_token+'/tables/'+table_id+'/records'
        params = json.dumps({
            "fields": record_dict
        })
        response = requests.request("POST", url, headers=self.headers, data=params)
        response = response.json()
        if response['msg'] != 'success':
            print('新增记录失败！response:{}'.format(response))

    # dataframe转换成字典列表格式
    def df_format(self, df):
        df_dicts = df.to_dict("records")
        dict_list = []
        for df_dict in df_dicts:
            dict = {}
            dict['fields'] = df_dict
            dict_list.append(dict)
        return dict_list

    # 批量添加数据记录
    def insert_records(self, table_id, record_dict_list): # <- dict_list, 例如：[{"fields":{'字段1': '测试', '字段2': 123, '字段3': 35, '字段4': '100%'}},...]
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/'+self.app_token+'/tables/'+table_id+'/records/batch_create'
        params = json.dumps({
            "records": record_dict_list
        })
        response = requests.request("POST", url, headers=self.headers, data=params)
        response = response.json()
        if response['msg'] != 'success':
            print(record_dict_list)
            print('新增记录失败！response:{}'.format(response))
            return 0
        else:
            return len(record_dict_list)

    # 将DataFrame,list分页
    def split_df_list(self, data, limit=500): # -> list， [df1,df2...]
        data_list = []
        if len(data) <= limit:
            return data
        else:
            page_num = math.ceil(len(data) / limit)
            if str(type(data)) == '<class \'pandas.core.frame.DataFrame\'>':
                for p_num in range(page_num):
                    data_limit = data.iloc[p_num*limit:(p_num+1)*limit]
                    data_list.append(data_limit)
            elif str(type(data)) == '<class \'list\'>':
                for p_num in range(page_num):
                    data_limit = data[p_num*limit:(p_num+1)*limit]
                    data_list.append(data_limit)
            else:
                print('未识别分页数据类型')

        return data_list


    # 将DataFrame格式数据直接添加进多维表格
    def insert_records_from_df(self, table_id, df):
        print('累计待插入行数：{}'.format(len(df)))
        total = 0
        if df.empty == False:
            df_list = self.split_df_list(df, limit=500)
            for df in df_list:
                record_dict_list = self.df_format(df)
                total += self.insert_records(table_id, record_dict_list)
            print('成功插入行数:{}'.format(total))
        else:
            print('数据源为空！')

    # 删除多条记录（指定行记录id批量删除）
    def delete_records(self, table_id, record_list): # <- list 例如：["recIcJBbvC", "recvmiCORa"]
        url = 'https://open.feishu.cn/open-apis/bitable/v1/apps/'+self.app_token+'/tables/'+table_id+'/records/batch_delete'

        record_ids_list = self.split_df_list(record_list)
        if record_ids_list:
            for record_ids in record_ids_list:
                params = json.dumps({
                    "records": record_ids
                })
                response = requests.request("POST", url, headers=self.headers, data=params)
                response = response.json()
                if response['msg'] != 'success':
                    print('删除记录失败！response:{}'.format(response))
                    return False
        else:
            print('传入record_id为空！')

    # 清空整表记录（指定单个表id）
    def clean_records(self, table_id):
        records = self.show_records(table_id)
        if records.empty == False:
            self.delete_records(table_id, records['record_id'].tolist())
            return True
        else:
            return False


    # 刷新整表记录（指定单个表id,待写入数据源格式->DataFrame）
    def refresh_records(self, table_id, df):
        if self.clean_records(table_id):
            print('table内记录已清空...')
            self.insert_records_from_df(table_id, df)
