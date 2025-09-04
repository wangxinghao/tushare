# Updated app.py with lifespan event handlers

from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import logConfig
import Mt5Lib
import importlib
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger():
    # 创建logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)  # 设置日志级别
    
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
    
    # 移除了手动设置 suffix 的代码行
    # handler.suffix = "%Y-%m-%d.log"  # 这行会导致问题，应该删除
    
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



# Global variables
strategy_thread = None
strategy_running = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to manage startup and shutdown events
    """
    # Startup event
    logger = logConfig.setup_logger()
    logger.info("Starting FastAPI service and initializing MT5 connection")
    
    if Mt5Lib.initialize_mt5():
        logger.info("MT5 connection initialized successfully")
    else:
        logger.error("Failed to initialize MT5 connection")
    
    yield  # App will be running during this time
    
    # Shutdown event
    global strategy_running
    logger.info("Shutting down FastAPI service")
    
    # Stop strategy if running
    strategy_running = False
    if strategy_thread and strategy_thread.is_alive():
        strategy_thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
    
    # Shutdown MT5 connection
    Mt5Lib.shutdown()
    logger.info("MT5 connection has been shut down")

# Create FastAPI app instance with lifespan
app = FastAPI(
    title="MT5 Trading API", 
    description="Web service for MT5 trading operations",
    lifespan=lifespan
)


@app.get("/context-fields")
async def get_context_fields():
    """
    Get all fields from context.py file
    Returns the current values of all global variables defined in context.py
    """
    try:
        # Import the context module
        import context
        
        # Reload the module to get current values
        importlib.reload(context)
        
        # Get all attributes from the context module
        context_data = {}
        for attr_name in dir(context):
            # Skip private attributes and modules
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(context, attr_name)
                    # Only include basic data types (avoid functions, classes, modules)
                    if isinstance(attr_value, (str, int, float, bool, list, dict, tuple)) or attr_value is None:
                        context_data[attr_name] = attr_value
                except Exception:
                    # Skip attributes that cause errors when accessed
                    pass
        
        return {
            "success": True,
            "data": context_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )