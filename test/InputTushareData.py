# 导入tushare
import tushare as ts
import pandas as pd
from sqlalchemy import create_engine
import pymysql

from sqlalchemy.dialects.mysql import Insert

def insert_ignore(table, conn, keys, data_iter):
    """
    自定义插入方法，使用INSERT IGNORE
    """
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = Insert(table.table).values(data)
    stmt = stmt.on_duplicate_key_update(**{col: stmt.inserted[col] for col in keys})
    result = conn.execute(stmt)
    return result.rowcount

# 初始化pro接口
pro = ts.pro_api('93abe9c0f07a4be297d483362262b58230c175d0afd9edbdb48b7e19')

# 拉取数据pip
df = pro.daily(**{
    "ts_code": "",
    "trade_date": "",
    "start_date": "20250808",
    "end_date": "20250808",
    "limit": "",
    "offset": ""
}, fields=[
    "ts_code",
    "trade_date",
    "open",
    "high",
    "low",
    "close",
    "pre_close",
    "change",
    "pct_chg",
    "vol",
    "amount"
])

print("获取数据:" + str(len(df)) + " 条数据")
print(df.head())

# 数据库连接配置
db_config = {
    'host': '121.41.91.74',
    'user': 'root',  # 替换为你的MySQL用户名
    'password': 'db.9922.',  # 替换为你的MySQL密码
    'database': 'stream_lit',
    'port': 14407
}

# 创建数据库连接引擎
engine = create_engine(
    f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?charset=utf8mb4",
    pool_pre_ping=True,  # 添加连接池预检查
    echo=False  # 设置为True可以查看SQL语句
)

#将数据写入MySQL数据库
try:
    with engine.connect() as conn:
        df.to_sql('stock_trading', con=conn, if_exists='append', index=False,
                  method=insert_ignore)
        print(f"成功使用 INSERT IGNORE 插入 {len(df)} 条记录到数据库")
except Exception as e3:
    print(f"数据插入失败: {e3}")

