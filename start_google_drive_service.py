from app.services.bio_data_extraction import GoogleDrive
from app.extentions.logger import Logger
import time

if __name__ == "__main__":
    _drive = GoogleDrive()
    while True:
        _drive.start_service()
        sleepTime = 60 * 10
        Logger.warning(f"Waiting for {sleepTime} seconds before checking again")
        time.sleep(sleepTime)  # Wait for 10 minute before checking again