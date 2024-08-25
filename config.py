import os

def get_project_root():
    current_dir = os.path.abspath(os.getcwd())
    while not os.path.exists(os.path.join(current_dir, 'app')):
        current_dir = os.path.dirname(current_dir)
        if current_dir == os.path.dirname(current_dir):
            # Reached the root directory without finding the marker file
            raise Exception("Marker file not found in project hierarchy")
    return current_dir


class Config:
    root = get_project_root()
    UPLOAD_FOLDER = os.path.join(root, 'uploads')
    LOG_FILE_PATH = 'logs/backend.log' 
    GOOGLE_DRIVE_LOG_FILE = 'logs/google_drive.log'
    MATCH_MAKING_LOG_FILE = 'logs/match_making.log'

    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    
    # DB_HOST = "68.178.159.203"
    # DB_USER = "adminuser"
    # DB_PASSWORD = "Miisco@123"
    # DB_NAME = "clientdb"


    # Token Keys
    CHAT_GPT_API_KEY = os.getenv('CHAT_GPT_API')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_AUTH_EXPIRE_DAY = 1 
    JWT_AUTH_EXPIRE_MINUTE = 0
    JWT_AUTH_EXPIRE_SECOND = 60
    
    PHOTO_GALLERY_PATH = os.path.join(UPLOAD_FOLDER, 'gallery')
    PROFILE_PIC_PATH = os.path.join(UPLOAD_FOLDER, 'profiles')
    BIO_DATA_PDF_PATH = os.path.join(UPLOAD_FOLDER, 'bio_data_pdfs')
    DEFAULT_PROFILE_PIC = 'default.png'
    DEFAULT_PROFILE_PIC_FEMALE = 'female.jpg'
    DEFAULT_PROFILE_PIC_MALE = 'male.jpg'
    MM_SCORE_5 = 5
    MM_SCORE_10 = 10
    
    
    
    
    
    #astro api
    
    CLIENT_ID = os.getenv('ASTRO_CLIENT_ID')
    CLIENT_SECRET = os.getenv('ASTRO_CLIENT_SECRET')
    GRANT_TYPE = "client_credentials"
    BASE_URL = "https://api.prokerala.com"
    END_POINT = "/v2/astrology/kundli"
    START_TIME = ''
    END_TIME = ''
    REQUEST = 0

    # Driver Folder ids
    
    SOURCE_FOLDER = '14uVaxzCcghLs3fgtMfrnFEIWfyjw_keE'
    DESTINATION_FOLDER = '1aBQEr8pGoJ8uWzzrUi83meAuWpj9tva3'
    ERROR_FOLDER = '1Z9H02HF5mYl8Z7TtZSnQ2bn8W6_dnxd-'