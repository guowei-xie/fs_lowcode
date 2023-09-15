import os
import sys

sys.path.append(os.getenv('library'))
from conn_db import fetch_raw
from fs_bitable import *
from fs_tbl_view import *

if __name__ == '__main__':
    # 多维表格ID
    app_token = 'BV5qbDtvCa3qlLsJ33WcG6lhnjc'
    app = BiTable(app_token=app_token)

    # 成本录入
    cost_input, row_id = app.show_all_records(table_id="tblwT77pGtmIBT1z")

    # 硬编数据底表
    raw_hard = fetch_raw("hardware.sql")

    # 软编&千川渠道数据底表
    raw_soft = fetch_raw("control_group.sql")

    # 预处理：成本均摊
    dat = dat_pre(cost_input, raw_hard)



    # # 飞书表格视图
    # ## raw-招生数据-汇总
    app.refresh(table_id="tblrXuYeGNffX1HP", df=enroll_total(dat))

    # ## raw-招生数据-学期
    app.refresh(table_id="tbly8tfNsOZVQ7Rp", df=enroll_term(dat))

    # ## raw-招生数据-学期&渠道
    app.refresh(table_id="tblbEtkS4douM4V2", df=enroll_term_channel(dat))

    # ## raw-过程数据-学期
    app.refresh(table_id="tblqLYYtMmmwVzSa", df=funnel_term(dat, raw_soft))

    # ## raw-过程数据-学期&性别
    app.refresh(table_id="tblxno22EIpBY3Za", df=funnel_term_gender(dat))

    # ## raw-过程数据-学期&千川
    app.refresh(table_id="tblvlDZJVk1OiTEY", df=hard_soft_contrast(dat, raw_soft))

    # ## raw-过程数据-年龄
    app.refresh(table_id="tblJFXdYmmbDwqAj", df=funnel_term_age(dat))

    # ## raw-过程数据-登录设备
    app.refresh(table_id="tblTUzMYkAYAUw6B", df=funnel_term_os(dat))

