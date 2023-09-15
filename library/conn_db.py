import os
import yaml
import pandas as pd

def conn_db(sql, key='hive', not_vectorized=False):
    conf_path = os.getenv('library')
    conf = yaml.full_load(open(conf_path + 'my_conf.yml', encoding='utf-8').read())

    if key == 'mysql':
        key = 'mysql_superset'

    host = conf[key].get('host')
    port = conf[key].get('port')
    username = conf[key].get('username')
    password = conf[key].get('password')

    if key == 'hive':
        from pyhive import hive
        conn = hive.Connection(
            host=host,
            port=port,
            username=username,
            password=password,
            auth='LDAP'
        )

    if 'mysql_superset' in key:
        import pymysql
        conn = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=str(password)
        )

    cursor = conn.cursor()
    if not_vectorized:
        cursor.execute("set hive.vectorized.execution.enabled=false")
    cursor.execute(sql)
    values = cursor.fetchall()

    # 获取字段名
    columns = []
    description = cursor.description
    if description is not None:
        for i in range(len(description)):
            des = description[i][0]
            if '.' in des:
                des = des.split('.')[-1]
            columns.append(des)

    conn.commit()
    cursor.close()
    conn.close()

    return values, columns


def fetch_raw(sql, db_from="hive", type="sql_file"):
    if type == 'sql_file':
        sql = open(sql, 'r', encoding='UTF-8').read()
        values, columns = conn_db(key=db_from, sql=sql)
    if type == 'sql_code':
        values, columns = conn_db(key=db_from, sql=sql)
    return pd.DataFrame(values, columns=columns)