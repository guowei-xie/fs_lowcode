import sys
import requests
import yaml
import os
import datetime
from requests_toolbelt import MultipartEncoder

class Doc:
    """云文档自动化demo"""
    def __init__(self, document_id):
        conf_path = os.getenv('library')
        conf = yaml.full_load(open(conf_path + 'my_conf.yml', encoding='utf-8').read())
        current_time = datetime.datetime.now()

        """初始化生成应用凭证"""
        self.app_id = conf['feishu_app']['app_id']
        self.app_secret = conf['feishu_app']['app_secret']
        self.document_id = document_id  # 云文档id

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

        """其他初始化变量"""
        self.create_block_url = 'https://open.feishu.cn/open-apis/docx/v1/documents/' + self.document_id + '/blocks/' + self.document_id + '/children'
        self.text_elements = []
        self.img_elements = []


    def show_blocks(self):
        """获取文档所有block"""
        url = 'https://open.feishu.cn/open-apis/docx/v1/documents/' + self.document_id + '/blocks'

        response = requests.get(url=url, headers=self.headers).json()

        if response['msg'] != 'success':
            print('failed in show_blocks method, response:{}'.format(response))
            sys.exit(1)

        return response


    def clean(self):
        """删除所有block"""
        url = 'https://open.feishu.cn/open-apis/docx/v1/documents/' + self.document_id + '/blocks/' + self.document_id + '/children/batch_delete'

        doc_info = self.show_blocks()

        # 如果文档为空，不做任何事
        if len(doc_info['data']['items']) == 1:
            return

        doc_childrens = doc_info['data']['items'][0]['children']

        params = {
            "start_index": 0,
            "end_index": len(doc_childrens)
        }

        response = requests.request("DELETE", url=url, headers=self.headers, json=params).json()
        if response['code'] != 0:
            print('failed in clean method, response:{}'.format(response))
            sys.exit(1)


    def generate(self, block_name, block_type, content):
        """用于生成不带样式的文本block"""
        params = {
                "index": -1,
                "children": [
                  {
                    "block_type": block_type,
                    block_name: {
                      "elements": [
                        {
                          "text_run": {
                            "content": content
                          }
                        }
                      ],
                      "style": {}
                    }
                  }
                ]
        }
        return params


    def text(self, content):
        """插入无样式纯文本"""
        url = self.create_block_url
        params = self.generate(block_name="text", block_type=2, content=content)
        response = requests.post(url, headers=self.headers, json=params).json
        return response


    def h1(self, content):
        """插入H1标题"""
        url = self.create_block_url
        params = self.generate(block_name="heading1", block_type=3, content=content)
        response = requests.post(url, headers=self.headers, json=params).json()
        return response


    def h2(self, content):
        """插入H2标题"""
        url = self.create_block_url
        params = self.generate(block_name="heading2", block_type=4, content=content)
        response = requests.post(url, headers=self.headers, json=params).json()
        return response


    def h3(self, content):
        """插入H3标题"""
        url = self.create_block_url
        params = self.generate(block_name="heading3", block_type=5, content=content)
        response = requests.post(url, headers=self.headers, json=params).json()
        return response


    def h4(self, content):
        """插入H4标题"""
        url = self.create_block_url
        params = self.generate(block_name="heading4", block_type=6, content=content)
        response = requests.post(url, headers=self.headers, json=params).json()
        return response


    def h5(self, content):
        """插入H5标题"""
        url = self.create_block_url
        params = self.generate(block_name="heading5", block_type=7, content=content)
        response = requests.post(url, headers=self.headers, json=params).json()
        return response


    def text_add(self, content, text_element_style={}):
        """有样式文本，多次调用可为同一行文本创建多个样式"""
        element = {
            "text_run": {
                "content": content,
                "text_element_style": text_element_style
            }
        }
        self.text_elements.append(element)

    def text_commit(self):
        """将容器内的有样式文本插入到飞书，并清空容器"""
        url = self.create_block_url
        params = {
            "index": -1,
            "children": [
                {
                    "block_type": 2,
                    "text": {
                        "elements": self.text_elements,
                        "style": {}
                    }
                }
            ]
        }
        response = requests.post(url=url, headers=self.headers, json=params).json()
        if response['msg'] != 'success':
            print('failed in text_commit method, response:{}'.format(response))
            sys.exit(1)

        self.text_elements = []


    def create_img_block(self, parent_block_id = ''):
        """创建空image block"""
        # 未指定block_id时默认在文档末尾创建块
        if parent_block_id == '':
            parent_block_id = self.document_id
        else:
            parent_block_id = parent_block_id

        url = 'https://open.feishu.cn/open-apis/docx/v1/documents/'+ self.document_id +'/blocks/'+ parent_block_id +'/children'
        params = {
            "index": -1,
            "children": [
                {
                    "block_type": 27,
                    "image": {
                        "token": ""
                    }
                }
            ]
        }
        response = requests.request("POST", url=url, headers=self.headers, json=params).json()

        if response['code'] != 0:
            print('failed in create_img_block method, response:{}'.format(response))
            sys.exit(1)

        return response['data']['children'][0]['block_id']


    def upload_media(self, block_id, file_path, parent_type):
        """上传素材到指定父节点（即block_id）,并返回file_token"""
        size = os.path.getsize(file_path)
        url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        form = {'file_name': file_path.split("/")[-1],
                'parent_type': parent_type,  # 图片：docx_image；文件：docx_file
                'parent_node': block_id,
                'size': str(size),
                'file': (open(file_path, 'rb'))
                }
        multi_form = MultipartEncoder(form)
        headers = self.headers
        headers['Content-Type'] = multi_form.content_type
        response = requests.request("POST", url, headers=headers, data=multi_form).json()

        if response['code'] != 0:
            print('failed in upload_media method, response:{}'.format(response))
            sys.exit(1)

        return response['data']['file_token']


    def update_img_block(self, block_id, img_token):
        """更新图片到指定block"""
        url = 'https://open.feishu.cn/open-apis/docx/v1/documents/' + self.document_id + '/blocks/' + block_id
        params = {
            "replace_image": {
                "token": img_token
            }
        }

        response = requests.request('PATCH', url=url, headers=self.headers, json=params).json()

        if response['code'] != 0:
            print('failed in upload_media method, response:{}'.format(response))
            sys.exit(1)


    def img(self, img_path):
        """插入单张图片的方法"""
        block_id = self.create_img_block()
        img_token = self.upload_media(block_id=block_id, file_path=img_path, parent_type='docx_image')
        self.update_img_block(block_id=block_id, img_token=img_token)


    def create_grid_block(self, ncol):
        """创建n列分栏block,返回children block id"""
        url = self.create_block_url

        params = {
            "index": -1,
            "children": [
                {
                    "block_type": 24,
                    "grid": {
                        "column_size": ncol
                    }
                }
            ]
        }

        response = requests.post(url=url, headers=self.headers, json=params).json()

        if response['code'] != 0:
            print('failed in create_grid_block method, response:{}'.format(response))
            sys.exit(1)

        return response['data']['children'][0]['children']


    def img_add(self, img_path):
        """添加多张图到容器"""
        self.img_elements.append(img_path)


    def img_commit(self):
        """遍历容器内的图片并依次推送到分栏"""
        """插图步骤：先创建空block，再上传素材，最后再更新替换"""
        ncol = len(self.img_elements)
        block_id_ls = self.create_grid_block(ncol=ncol)
        for i in range(ncol):
            img_block_id = self.create_img_block(parent_block_id=block_id_ls[i])
            img_token = self.upload_media(block_id=img_block_id,
                              file_path=self.img_elements[i],
                              parent_type='docx_image')

            self.update_img_block(block_id=img_block_id,
                                  img_token=img_token)
        self.img_elements = []
