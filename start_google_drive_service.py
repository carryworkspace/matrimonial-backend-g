from app.services.bio_data_extraction import GoogleDrive
from app.extentions.logger import Logger
from config import Config
if __name__ == "__main__":
    Logger.setup_logger(Config.GOOGLE_DRIVE_LOG_FILE)
    _drive = GoogleDrive()
    _drive.start_service()