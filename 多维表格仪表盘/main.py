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

# # 方式1：整表覆盖
# for d in range(days):
#     date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=d+1)).strftime("%Y-%m-%d")
#     df = pd.concat([df, generate_city_gmv(date)], axis=0)
#     app.refresh(table_id=table_id, df=df)
#     time.sleep(5)


# 方式2：末尾插入
app.delete_all_records(table_id=table_id)

for d in range(days):
    date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=d)).strftime("%Y-%m-%d")
    df = generate_city_gmv(date)
    app.insert_df(table_id=table_id, df=df)
    time.sleep(5)









