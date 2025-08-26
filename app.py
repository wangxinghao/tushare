# Updated app.py with lifespan event handlers

from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import logConfig
import Mt5Lib



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
    

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )