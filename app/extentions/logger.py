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
    def setup_logger(): 
        # Ensure the log folder exists
        log_dir = os.path.dirname(LOG_FILE_PATH)
        print(f"Log directory: {log_dir}")
        
        if not os.path.exists(log_dir):
            print("Directory does not exist, creating...")
            os.makedirs(log_dir)
        else:
            print("Directory exists.")

        print("Configuring logger...")
        logger.remove()

        # Add a new handler for file logging
        logger.add(sys.stdout, format=log_format)
        logger.add(LOG_FILE_PATH, format="{time} | {level} | {message}", rotation="1 MB", retention="10 days")
        print(f"Logging to: {LOG_FILE_PATH}")


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

# Set up the logger when the script is loaded
Logger.setup_logger()
