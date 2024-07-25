import os
from mysql import connector

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

    DB_HOST = "68.178.159.203"
    DB_USER = "adminuser"
    DB_PASSWORD = "Miisco@123"
    DB_NAME = "clientdb"

    NEW_DB_PASSWORD="Miiscollp@123"

    # Token Keys
    CHAT_GPT_API_KEY = "sk-proj-ZKe056YhGNDp7JfuJBLtT3BlbkFJL5Vss2v7B3CWw4fzt94V"
    JWT_SECRET_KEY = "miiscollpOrg"
    JWT_AUTH_EXPIRE_DAY = 1
    JWT_AUTH_EXPIRE_MINUTE = 0
    JWT_AUTH_EXPIRE_SECOND = 60
    
    PHOTO_GALLERY_PATH = os.path.join(UPLOAD_FOLDER, 'gallery')
    PROFILE_PIC_PATH = os.path.join(UPLOAD_FOLDER, 'profiles')
    BIO_DATA_PDF_PATH = os.path.join(UPLOAD_FOLDER, 'bio_data_pdfs')
    
    
    
    
    
    #astro api
    
    CLIENT_ID = "6bb8a6ed-cd27-493f-935c-2f7a0733ab96"
    CLIENT_SECRET = "xkBFZsTYqiLvJvILEuSEq9AYRTw1GCmrZAA6OrjK"
    GRANT_TYPE = "client_credentials"
    BASE_URL = "https://api.prokerala.com"
    END_POINT = "/v2/astrology/kundli"
    START_TIME = ''
    END_TIME = ''
    REQUEST = 0
