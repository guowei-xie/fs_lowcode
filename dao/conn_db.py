from config.configration import *

def conn_db(sql, key='hive'):
    conf = my_conf
    host = conf.get(key, 'host')
    port = int(conf.get(key, 'port'))
    username = conf.get(key, 'username')
    password = conf.get(key, 'password')

    if key == 'hive':
        from pyhive import hive
        conn = hive.Connection(
            host=host,
            port=port,
            username=username,
            password=password,
            auth='LDAP'
        )

    if key == 'mysql':
        import pymysql
        database = conf.get(key, 'database')
        conn = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=str(password),
            database=database
        )
    cursor = conn.cursor()
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