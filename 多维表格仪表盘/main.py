from library.fs_bitable import *
from library.helper import *
from datetime import datetime, timedelta
import time

app_token = "W5sbbe0h2a8YNts7e2echw8UnWg"
app = BiTable(app_token=app_token)

# 初始化
start_date = '2023-08-01'
df = generate_city_gmv(start_date)
days = 30
table_id = "tblBIToLPiVS2SpK"

app.delete_all_records(table_id=table_id)

方式1：末尾插入
for d in range(days):
    date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=d)).strftime("%Y-%m-%d")
    df = generate_city_gmv(date)
    app.insert_df(table_id=table_id, df=df)
    time.sleep(5)

# # 方式2：整表覆盖
# for d in range(days):
#     date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=d+1)).strftime("%Y-%m-%d")
#     df = pd.concat([df, generate_city_gmv(date)], axis=0)
#     app.refresh(table_id=table_id, df=df)
#     time.sleep(5)

# from library.fs_sprsheet import *
# app2 = SpreadSheet(spreadsheetToken="T4FnsQJlXhDwXLtpxQ3cJaMgnRb")
#
#
# dat = app2.show_range(sheet_id="3bf7d9", cell_range="C3:E11")
# print(dat)






