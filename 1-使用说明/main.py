import pandas as pd

from library import fs_api
import yaml

# 配置信息
with open('conf.yml', 'r', encoding='utf-8') as f:
    conf = yaml.full_load(f)

# 机器人配置信息
bot_webhook_url = conf['BOT_INFO']['WEBHOOK_URL']
bot_secret = conf['BOT_INFO']['SECRET']
# 自建应用凭证信息
licence_app_id = conf['LICENCE_INFO']['APPID']
licence_app_secret = conf['LICENCE_INFO']['SECRET']



"""使用机器人发送消息"""
bot = fs_api.FeishuBot(secret=bot_secret, webhook_url=bot_webhook_url)
mycloud = fs_api.MyCloud(app_id=licence_app_id, app_secret=licence_app_secret)

text = '机器人文本消息测试'
img_path = 'img/测试图片.jpg'

# 发送纯文本消息
bot.send_text(text)

# 发送图片消息
img_key = mycloud.upload_image(img_path)
bot.send_img(image_key=img_key)


"""多维表格操作"""
bitable = fs_api.BiTable(app_id=licence_app_id,
                         app_secret=licence_app_secret,
                         app_token='bascnWgJYXqhBSwgIRtcZxUlsve') # app_token 指多维表格的Id

table_id = 'tblAawLennTHnbzz' # table_id 指多维表格下的数据表id

# 假设已在飞书多维表格建表，表字段同如下DataFrame
df = pd.DataFrame({'城市等级': ['一线', '二线', '三线', '四线', '五线'],
                       '活动A': [150, 1200, 1300, 2800, 2000],
                       '活动B': [400, 1100, 2300, 2900, 2700],
                       '活动C': [390, 1700, 3300, 3500, 4200],
                       '活动D': [300, 900, 1900, 2800, 3300],
                       '活动E': [130, 790, 1800, 3000, 4200]})

# 获取指定table_id的数据
records = bitable.show_records(table_id=table_id)

# 将指定table_id的数据清空并将DataFrame数据批量插入
bitable.refresh_records(table_id=table_id, df=df)

# 在指定table_id末尾插入DataFrame
bitable.insert_records_from_df(table_id=table_id, df=df)

