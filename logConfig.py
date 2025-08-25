import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger():
    # 创建logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)  # 设置日志级别
    
    # 创建文件处理器
     # 创建按时间轮转的文件处理器
    # when='D' 表示按天轮转
    # interval=1 表示每1个单位时间轮转一次
    # backupCount=30 表示保留30天的历史日志
    handler = TimedRotatingFileHandler(
        "app.log",
        when='D',          # 轮转单位：'S'秒, 'M'分, 'H'时, 'D'天, 'W0'-'W6'周(0是周一)
        interval=1,        # 轮转间隔
        backupCount=30,    # 保留的备份日志数量
        encoding='utf-8'   # 日志编码
    )
    
    # 设置轮转后的文件后缀（默认是YYYY-MM-DD）
    handler.suffix = "%Y-%m-%d.log"
    
    # 创建格式化器并添加到处理器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()  # 默认输出到sys.stdout（控制台）
    console_handler.setFormatter(formatter)
    # 控制台可单独设置日志级别（如记录DEBUG及以上，方便调试）
    console_handler.setLevel(logging.DEBUG)

    
    # 确保只添加一个文件处理器，避免重复输出
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console_handler)
    
    return logger