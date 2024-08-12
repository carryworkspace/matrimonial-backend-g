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

class Logger:
    
    @staticmethod
    def setup_logger():
        # Ensure the log folder exists
        if not os.path.exists(LOG_FILE_PATH):
            os.makedirs(LOG_FILE_PATH)
        
        # Check if logger is already configured
        if logger._core.handlers:
            return

        # Remove all existing handlers
        logger.remove()

        # Add a new handler for file logging
        logger.add(sys.stdout, format=log_format)
        logger.add(LOG_FILE_PATH, format="{time} | {level} | {message}", rotation="1 MB", retention="10 days")

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

Logger.setup_logger()
