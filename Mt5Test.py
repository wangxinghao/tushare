from datetime import datetime

# 获取当前时间
now = datetime.now()

# 计算当前时间处于哪个5分钟区间
five_minute_interval = now.minute // 5

# 计算在当前5分钟区间内已经过了多少分钟和秒
minutes_in_interval = now.minute % 5
seconds_in_interval = now.second
weight = (minutes_in_interval*60 + seconds_in_interval)/300

print(f"当前时间: {now.strftime('%H:%M:%S')}")
print(f"处于第 {five_minute_interval + 1} 个5分钟区间")
print(f"在当前5分钟区间内已过: {minutes_in_interval}分{seconds_in_interval}秒")
print(f":{weight}")