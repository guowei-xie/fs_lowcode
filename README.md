## 配置文件
library/`my_conf.yml`
```yaml
# 飞书企业应用凭证（飞书开放者后台进入应用获取）
feishu_app:
  app_id: 
  app_secret:

# hive数仓配置
hive:
  host: 
  port: 
  username: 
  password: 

# mysql_superset数据库配置
mysql_superset:
  host: 
  port: 
  database: s
  username: 
  password: 
```

## 环境变量
本地运行时添加环境变量`library`,`xxx`替换为本地实际路径
```shell
export library='xxx/fs_lowcode/library'
```
