import json
import requests
import os
import yaml
import base64
import hashlib
import hmac
from requests_toolbelt import MultipartEncoder
from datetime import datetime


class MsgBot:
    def __init__(self, webhook_url, secret):
        """应用凭证"""
        conf_path = os.getenv('myconf')
        conf = yaml.full_load(open(conf_path + '/fs_conf.yml', encoding='utf-8').read())
        self.app_id = conf['feishu_app']['app_id']
        self.app_secret = conf['feishu_app']['app_secret']
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        params = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.request("POST", url, json=params).json()
        if response['msg'] == 'ok':
            self.token = response['tenant_access_token']
            self.headers = {'Authorization': 'Bearer ' + self.token}
            print("current time:{} tenant:{}".format(datetime.now(), self.token))
        else:
            print('current time:{} \nfailed in initialize method, return code:{}'.format(datetime.now(), response['code']))

        """安全秘钥"""
        if not secret:
            raise ValueError("invalid secret key")
        self.timestamp = int(datetime.now().timestamp())
        string_to_sign = '{}\n{}'.format(self.timestamp, secret)
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()

        self.sign = base64.b64encode(hmac_code).decode('utf-8')
        self.webhook_url = webhook_url

    def send_msg(self, msg_type, msg_content_js):
        """可以发送任意消息类型，但有时不便捷"""
        params = {
            "timestamp": self.timestamp,
            "sign": self.sign,
            "msg_type": msg_type,
            "content": json.dumps(msg_content_js, ensure_ascii=False)
        }
        response = requests.request("POST", url=self.webhook_url, json=params).json()
        if response.get("code") and response.get("code") != 0:
            print("failed in send_msg method!\n res:{}".format(response))
            exit(1)

    def send_text(self, content):
        """纯文本消息发送"""
        params = {
            "timestamp": self.timestamp,
            "sign": self.sign,
            "msg_type": "text",
            "content": {"text": content},
        }
        response = requests.post(url=self.webhook_url, json=params).json()

        if response.get("code") and response.get("code") != 0:
            print("failed in send_text method!\n res: {}".format(response))
            exit(1)

    def upload_img(self, img_path):
        """上传图片到应用的云空间，获取image_key"""
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        form = {
            'image_type': 'message',
            'image': (open(img_path, 'rb'))}
        multi_form = MultipartEncoder(form)
        headers = self.headers
        headers['Content-Type'] = multi_form.content_type
        response = requests.request("POST", url=url, headers=headers, data=multi_form).json()

        if response.get("code") and response.get("code") != 0:
            print("failed in upload_img method!\n res:{}".format(response))

        return response['data']['image_key']

    def upload_file(self, file_path, file_rename, mime_type):
        """上传文件到应用的云空间，获取file_key"""
        url = "https://open.feishu.cn/open-apis/im/v1/files"
        form = {'file_type': 'stream',
                'file_name': file_rename,
                # MIME格式参考  https://www.w3school.com.cn/media/media_mimeref.asp
                'file': (file_rename, open(file_path, 'rb'), mime_type)
                }
        multi_form = MultipartEncoder(form)
        headers = self.headers
        headers['Content-Type'] = multi_form.content_type

        response = requests.request("POST", url=url, headers=headers, data=multi_form).json()
        if response.get("code") and response.get("code") !=0:
            print("failed in upload_file method!\n res:{}".format(response))
            exit(1)
        return response['data']['file_key']


    def send_img(self, img_path):
        """发送本地图片"""
        img_key = self.upload_img(img_path=img_path)
        self.send_msg(msg_type="image", msg_content_js={"image_key": img_key})


    def send_file(self, file_path, file_name, mime_type):
        """发送本地文件"""
        file_key = self.upload_file(file_path=file_path, file_rename=file_name,mime_type=mime_type)
        self.send_msg(msg_type="file", msg_content_js={"file_key": file_key})