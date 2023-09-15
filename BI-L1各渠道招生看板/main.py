import os
import sys

sys.path.append(os.getenv('library'))
from conn_db import fetch_raw
from fs_bitable import *
from data_process import *

if __name__ == '__main__':
    # 多维表格ID
    app_token = 'ZcaqbuRJzaV2ajsIPApcAO04nTg'
    app = BiTable(app_token=app_token)

    raw = fetch_raw(sql="各渠道招生续报.sql" )

    tables = [
        (enroll_renewal_data, 'tblggHXDWRDABvGJ')
    ]

    for table_func, table_id in tables:
        try:
            if not raw.empty:
                table_data = table_func(raw)
                app.refresh(table_id=table_id, df=table_data)
        except Exception as e:
            print(f"An error occurred in the {table_id} section:", str(e))