from app.services.bio_data_extraction import GoogleDrive

if __name__ == "__main__":
    _drive = GoogleDrive()
    _drive.start_service()