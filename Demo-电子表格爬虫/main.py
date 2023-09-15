# demo演示地址：https://wrpnn3mat2.feishu.cn/sheets/T4FnsQJlXhDwXLtpxQ3cJaMgnRb?sheet=3bf7d9
import sys
import os
sys.path.append(os.getenv('library'))

from fs_sprsheet import *

app = SpreadSheet(spreadsheetToken="T4FnsQJlXhDwXLtpxQ3cJaMgnRb")

# 爬取指定电子表格的range内容，返回嵌套列表
dat = app.read_range(sheet_id="3bf7d9", range="C3:E11")

# 将嵌套列表写入指定电子表格内的range
app.write_range(sheet_id="3bf7d9", range="G2:J12", ls=dat[:5])

# 伪清空range,实现原理是向整个range写入空值（之所这么干，是因为官方没有提供清空单元格的接口...）
app.clean_range(sheet_id="3bf7d9", range="G2:I15")
#
# 清空range后再写入，实际上是clean_range和write_range的连续调用
app.cover_range(sheet_id="3bf7d9", range="G2:J12", ls=dat)
