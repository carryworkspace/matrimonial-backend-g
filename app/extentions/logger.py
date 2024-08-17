import os
import sys
from loguru import logger
from config import Config

# Custom log format
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

LOG_FILE_PATH = Config.LOG_FILE_PATH
# LOG_FILE_PATH = 'logs/backend.log' 

class Logger:
    
    @staticmethod
    def setup_logger(filePath = LOG_FILE_PATH): 
        # Ensure the log folder exists
        log_dir = os.path.dirname(filePath)
        print(f"Log directory: {log_dir}")
        print(f"Log file path: {filePath}")
        
        if not os.path.exists(log_dir):
            print("Directory does not exist, creating...")
            os.makedirs(log_dir)
        else:
            print("Directory exists.")

        print("Configuring logger...")
        logger.remove()

        # Add a new handler for file logging
        logger.add(sys.stdout, format=log_format)
        logger.add(filePath, format="{time} | {level} | {message}", rotation="1 MB", retention="10 days")
        print(f"Logging to: {filePath}")


    @staticmethod
    def error(text):
        logger.error(text)
        
    @staticmethod    
    def info(text):
        logger.info(text)
        
    @staticmethod    
    def debug(text):
        logger.debug(text)
        
    @staticmethod    
    def success(text):
        logger.success(text)
        
    @staticmethod    
    def warning(text):
        logger.warning(text)