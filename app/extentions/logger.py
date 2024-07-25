import os
from datetime import datetime
from config import Config
import sys
from loguru import logger

# Custom log format
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)



LOG_FILE_PATH = Config.LOG_FILE_PATH

class Logger:
    @staticmethod
    def ensure_log_file(file_name = LOG_FILE_PATH):
        file_name = file_name
        # if not os.path.exists(file_name):
        logger.add(sys.stdout, format=log_format)
        logger.add(file_name, format=log_format, rotation="1 MB", retention="10 days")

    @staticmethod
    def error(text):
        Logger.ensure_log_file()
        logger.error(text)
        # with open(LOG_FILE_PATH, 'a') as file:
        #     log_entry = "[{}] [{}] {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "ERROR", text)
        #     file.write(log_entry)
        
    @staticmethod    
    def info(text):
        Logger.ensure_log_file()
        logger.info(text)
        # with open(LOG_FILE_PATH, 'a') as file:
        #     log_entry = "[{}] [{}] {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "INFO", text)
        #     file.write(log_entry)
        
    @staticmethod    
    def debug(text):
        Logger.ensure_log_file()
        logger.debug(text)
        
    @staticmethod    
    def success(text):
        Logger.ensure_log_file()
        logger.success(text)
        
    @staticmethod    
    def warning(text):
        Logger.ensure_log_file()
        logger.warning(text)
