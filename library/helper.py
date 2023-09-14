import random
import pandas as pd
import re
from datetime import datetime, timedelta

def generate_city_gmv(date):
    """生成模拟数据集：城市GMV"""
    city_levels = ["一线城市", "二线城市", "三线城市", "四线城市", "五线城市"]
    gmv = [round(random.uniform(10000, 50000), 2) for _ in range(len(city_levels))]
    return pd.DataFrame({'日期': date, '城市线级': city_levels, 'GMV': gmv})

def column_index(column_str):
    """将电子表格列索引转换为数字"""
    column_str = column_str.upper()
    num = 0
    for char in column_str:
        num = num * 26 + (ord(char) - ord('A')) + 1
    return num

def range_shape(range_str):
    """计算电子表格range的行列数"""
    splt = re.findall(r'[A-Z]+|\d+', range_str)
    col_start = column_index(splt[0])
    col_end = column_index(splt[2])
    row_start = int(splt[1])
    row_end = int(splt[3])

    col_n = col_end - col_start + 1
    row_n = row_end - row_start + 1

    return row_n, col_n


def create_empty_matrix(row_n, col_n):
    # 使用列表生成式创建一个包含row_n个嵌套列表的列表，每个嵌套列表包含col_n个空值元素
    matrix = [[''] * col_n for _ in range(row_n)]
    return matrix

# 示例用法
row_n = 3
col_n = 4
result = create_empty_matrix(row_n, col_n)
print(result)