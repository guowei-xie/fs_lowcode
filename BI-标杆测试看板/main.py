import os
import sys

sys.path.append(os.getenv('library'))
from conn_db import fetch_raw
from fs_sprsheet import *
from range_view import *


if __name__ == '__main__':
    # 电子表格id
    # 看板url：https://wrpnn3mat2.feishu.cn/sheets/TkLMsqMgXh3TxytXZQacKB6mnU9?sheet=f50ec9&table=tblh5HdLnUuS98FU&view=vewTIVWgsL
    app = SpreadSheet(spreadsheetToken="TkLMsqMgXh3TxytXZQacKB6mnU9")

    # 读取range配置
    cnf = yaml.full_load(open('range_cnf.yml', encoding='utf-8').read())

    raw = fetch_raw(sql='sql file name')

    # 9.9常规班
    # 过程漏斗
    app.cover_range(sheet_id=cnf['9.9常规班']['sheetID'],
                    range=cnf['9.9常规班']['range']['过程漏斗'],
                    ls=yourmethod(raw))
