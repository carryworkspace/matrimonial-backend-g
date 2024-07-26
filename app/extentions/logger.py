import os
from datetime import datetime
from config import Config
import sys
from loguru import logger

# Custom log format
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

LOG_FILE_PATH = Config.LOG_FILE_PATH

class Logger:
    
    
    @staticmethod
    def setup_logger():
        # Ensure the log folder exists
        if not os.path.exists(LOG_FILE_PATH):
            os.makedirs(LOG_FILE_PATH)
        
        # Remove all existing handlers
        logger.remove()
        
        # Add a new handler for file logging
        logger.add(sys.stdout, format=log_format)
        logger.add(LOG_FILE_PATH, format="{time} | {level} | {message}")
    
    # @staticmethod
    # def ensure_log_file(file_name = LOG_FILE_PATH):
    #     file_name = file_name
    #     # if not os.path.exists(file_name):
    #     logger.add(sys.stdout, format=log_format)
    #     logger.add(file_name, format=log_format, rotation="1 MB", retention="10 days")

    @staticmethod
    def error(text):
        logger.error(text)
        
    @staticmethod    
    def info(text):
        logger.info(text +"\n")
        
    @staticmethod    
    def debug(text):
        logger.debug(text+"\n")
        
    @staticmethod    
    def success(text):
        logger.success(text+"\n")
        
    @staticmethod    
    def warning(text):
        logger.warning(text+"\n")

Logger.setup_logger()