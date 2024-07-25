import os.path
import io
import json

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from app.routes import createDbConnection, closeDbConnection
from app.models.matrimonial_profile_model import MatrimonialProfileModel
from app.models.bio_data_pdf_model import BioDataPdfModel
from app.querys.user import user_query as querys
from app.extentions.common_extensions import chatgpt_pdf_to_json, query_payload, get_project_root, generate_random_number
from app.extentions.chatgpt import Chatgpt
from config import Config
from app.extentions.logger import Logger

# If modifying these scopes, delete the file token.json.
root = get_project_root()
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
SERVICE_ACCOUNT_FILE = os.path.join(root, fr'app\services\credentials_bio.json')

class GoogleDrive:

  def __init__(self) -> None:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    self.drive_service = build("drive", "v3", credentials=creds)
    Logger.info("Google Drive service initialized.")
  
  
  def list_files_in_folder(self, folder_id: str):
    """List all PDF files in a specific folder."""
    Logger.debug(f"Listing PDF files in folder with ID: {folder_id}")
    query = f"'{folder_id}' in parents and mimeType='application/pdf'"
    results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    Logger.info(f"Found {len(items)} PDF files.")
    return items
  
  def download_file(self, file_id: str, file_name: str, save_path: str):
    """Download a file from Google Drive."""
    # Logger.debug(f"Downloading file ID: {file_id} with name: {file_name} to path: {save_path}")
    request = self.drive_service.files().get_media(fileId=file_id)
    absolue_path = os.path.join(save_path, file_name)
    if os.path.exists(absolue_path):
      Logger.warning(f"File {file_name} already exists.")
      return False
    fh = io.FileIO(absolue_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        Logger.debug(f"Downloading {file_name}: {int(status.progress() * 100)}%")
    fh.close()
    Logger.info(f"File {file_name} downloaded successfully.")
    return True
    
  def move_file_to_folder(self, file_id: str, folder_id: str, fileName: str):
    """Move a file to a new folder."""
    try:
      Logger.debug(f"Moving file '{fileName}' (ID: {file_id}) to folder with ID: {folder_id}")
      # Retrieve the existing parents to remove
      file = self.drive_service.files().get(fileId=file_id, fields='parents').execute()
      previous_parents = ",".join(file.get('parents'))
      # Move the file to the new folder
      file = self.drive_service.files().update(
          fileId=file_id,
          addParents=folder_id,
          removeParents=previous_parents,
          fields='id, parents'
      ).execute()
      Logger.info(f"File '{fileName}' moved successfully to folder.")
    except Exception as e:
      Logger.error(f"Error moving file '{fileName}' ID: {file_id}) to folder {folder_id}: {e}")
  
  
  # def profile_exists(self, cursor, name, phoneNumber):
  #       query = f"SELECT * FROM MatrimonialProfile_M WHERE Name = {name} AND PhoneNumber = {phoneNumber}"
  #       cursor.execute(query, (name, phoneNumber))
  #       result = cursor.fetchall()
  #       return len(result) > 0
      
      
      
  def insert_into_matrimonial(self, data, fileName: str):
    Logger.debug("Starting insert_into_matrimonial method.")
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    
    try:
      dataDict = json.loads(data)
      Logger.debug("JSON data loaded successfully.")
      
      # check for N/A values and replace them with empty string
      for key in dataDict.keys():
        Logger.debug("JSON data loaded successfully.")
        if "N/A" in dataDict[key]:
          dataDict[key] = ""
          Logger.debug(f"Replaced 'N/A' with empty string in key: {key}")
          
          #user already exist
      # if self.profile_exists(cursorDb, dataDict['Name'], dataDict['PhoneNumber']):
      #   return "User already exists."
          
      dataDict["profileId"] = generate_random_number()
      Logger.debug(f"Generated profile ID: {dataDict['profileId']}")
          
      model = MatrimonialProfileModel.fill_model(dataDict)
      pdf_model = BioDataPdfModel.fill_model({"profileId": model.profileId, "pdfName": fileName})
      Logger.debug("Filled MatrimonialProfileModel and BioDataPdfModel.")
      cursorDb.execute(querys.AddMatrimonialProfile(), model.__dict__)
      Logger.debug("Executed query to insert MatrimonialProfileModel.")
      cursorDb.execute(querys.AddBioDataPdfFile(), pdf_model.__dict__)
      Logger.debug("Executed query to insert BioDataPdfModel.")
      
      #cursorDb.execute(querys.Subscribe_Token_Generate(), pdf_model.__dict__)
      
      db.commit()
      Logger.info("Data inserted successfully.")
    except Exception as e:
      Logger.error(f"An error occurred: {e}")
  
  def extract_and_add_to_DB_MAIN(self):
    Logger.debug("Starting extract_and_add_to_DB_MAIN method.")
    # IDs of the source and destination folders
    source_folder_id = '14uVaxzCcghLs3fgtMfrnFEIWfyjw_keE'
    destination_folder_id = '1aBQEr8pGoJ8uWzzrUi83meAuWpj9tva3'
    save_path = Config.BIO_DATA_PDF_PATH
    
    
    try:
      Logger.debug(f"Ensuring save path exists: {save_path}")
      # Ensure the save path exists
      os.makedirs(save_path, exist_ok=True)
      Logger.debug("Save path created or already exists.")

      # List all PDF files in the source folder
      pdf_files = self.list_files_in_folder(source_folder_id)
      Logger.debug(f"Listed PDF files in source folder. Count: {len(pdf_files)}")
      
      if len(pdf_files) == 0:
        Logger.warning("No PDF files found in the source folder.")
        return json.dumps({"message":"No PDF files found in the source folder.", "status": "success"})
        
      for file in pdf_files:
          file_id = file['id']
          file_name = file['name']
          Logger.debug(f"Processing file: {file_name}")
          
          # Download the PDF file
          self.download_file(file_id, file_name, save_path)
          Logger.debug(f"Downloaded file: {file_name}")
          _chatgpt = Chatgpt()
          pdf_file_path = os.path.join(save_path, file_name)
          
          chatgpt_response_json = chatgpt_pdf_to_json(pdf_file_path)
          Logger.debug(f"Converted PDF to JSON for file: {file_name}")
          response_payload_json = _chatgpt.chat(text=chatgpt_response_json, payload=query_payload)
          Logger.debug(f"Performed chat interaction for file: {file_name}")
          filter_data_json = _chatgpt.filter_data(response_payload_json)
          Logger.debug(f"Filtered data for file: {file_name}")
          fill_empty_fields = _chatgpt.fill_other_empty_fields(filter_data_json, pdf_file_path)
          Logger.debug(f"Filled empty fields for file: {file_name}")
          self.insert_into_matrimonial(fill_empty_fields, file_name)
          Logger.debug(f"Inserted data into matrimonial database for file: {file_name}")
          
          # Move the file to the destination folder
          self.move_file_to_folder(file_id, destination_folder_id, file_name)
          Logger.debug(f"Moved file {file_name} to destination folder.")
      Logger.info("Bio datas extracted and added to database successfully.")
      return json.dumps({"message": "Bio datas extracted and added to database successfully."})
    except Exception as e:
      Logger.error(f"An error occurred: {e}")
      return json.dumps({"status": "failed", "message": str(e)})

  
  
