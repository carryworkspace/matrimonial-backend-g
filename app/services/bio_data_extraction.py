import os.path
import io
import json
import time
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
from app.extentions.common_extensions import chatgpt_pdf_to_json, query_payload, get_project_root, generate_random_number, get_random_name, get_phone_number, is_null_or_empty, is_number_zero, extract_text_from_pdf
from app.extentions.chatgpt import Chatgpt
from config import Config
from app.extentions.logger import Logger
import traceback
from app.extentions.regex_extraction import *

# If modifying these scopes, delete the file token.json.
root = get_project_root()
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
SERVICE_ACCOUNT_FILE = os.path.join(root, fr'app/services/credentials_bio.json')

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
  
  
  def profile_exists(self, name:str, phoneNumber:str):
    db, cursor = createDbConnection()
    query = f"SELECT * FROM MatrimonialProfile_M WHERE Name = '{name}' AND PhoneNumber = '{phoneNumber}'"
    cursor.execute(query)
    result = cursor.fetchall()
    closeDbConnection(db, cursor)
    return len(result) > 0
      
      
      
  def insert_into_matrimonial(self, dataDict, fileName: str):
    Logger.debug("Starting insert_into_matrimonial method.")
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    
    phoneNumberStr: str = str(dataDict['phoneNumber'])
    phoneNumber = get_phone_number(phoneNumberStr)
    dataDict["phoneNumber"] = str(phoneNumber)
    
    # check for N/A values and replace them with empty string
    for key in dataDict.keys():
      Logger.debug(f"JSON data loaded successfully for {key}.")
      if "N/A" in str(dataDict[key]):
        dataDict[key] = ""
        Logger.debug(f"Replaced 'N/A' with empty string in key: {key}")
    #user already exist
    if self.profile_exists(dataDict['name'], dataDict['phoneNumber']):
      Logger.warning("User already exists skipping this pdf.")
      return "User already exists."

    username = get_random_name(phoneNumber)
    password = generate_random_number(length=8)
    insert_user_query = querys.AddUser(username, phoneNumber, 'null', 'null', dataDict['email'])
    Logger.info(f"Inserting new user with query: {insert_user_query}")
    cursorDb.execute(insert_user_query)
    new_user_id = cursorDb.lastrowid
    cursorDb.execute(querys.UpdatePassword(new_user_id, password))
    Logger.debug(f"Update Password")
    cursorDb.execute(querys.AddProfileForUser(new_user_id))
    Logger.debug(f"Add Profile For User")
    new_profile_id = cursorDb.lastrowid
    
        
    dataDict["profileId"] = new_profile_id
    Logger.debug(f"Generated profile ID: {dataDict['profileId']}")
        
    model = MatrimonialProfileModel.fill_model(dataDict)
    pdf_model = BioDataPdfModel.fill_model({"profileId": model.profileId, "pdfName": fileName})
    Logger.debug("Filled MatrimonialProfileModel and BioDataPdfModel.")
    matrimonialData = model.__dict__
    matrimonialData["subscribeToken"] = f"{str(matrimonialData['name']).replace(' ', '_')}_{str(matrimonialData['phoneNumber']).replace(' ', '_')}"
    cursorDb.execute(querys.AddMatrimonialProfile(), matrimonialData)
    Logger.debug("Executed query to insert MatrimonialProfileModel.")
    cursorDb.execute(querys.AddBioDataPdfFile(), pdf_model.__dict__)
    Logger.debug("Executed query to insert BioDataPdfModel.")
    
    #cursorDb.execute(querys.Subscribe_Token_Generate(), pdf_model.__dict__)
    
    db.commit()
    Logger.info("Data inserted successfully.")
    closeDbConnection(db, cursorDb)
  
  def extract_and_add_to_DB_MAIN(self):
    Logger.debug("Starting extract_and_add_to_DB_MAIN method.")
    # IDs of the source and destination folders
    source_folder_id = Config.SOURCE_FOLDER
    destination_folder_id = Config.DESTINATION_FOLDER
    save_path = Config.BIO_DATA_PDF_PATH
    
    
    try:
      Logger.debug(f"Ensuring save path exists: {save_path}")
      # Ensure the save path exists
      os.makedirs(save_path, exist_ok=True)
      Logger.debug("Save path created or already exists.")

      # List all PDF files in the source folder
      pdf_files = self.list_files_in_folder(source_folder_id)
      Logger.debug(f"Listed PDF files in source folder. Count: {len(pdf_files)}")
      total_pdfs = len(pdf_files)
      pdf_completed_count = 0
      
      if total_pdfs == 0:
        Logger.warning("No PDF files found in the source folder.")
        return json.dumps({"message":"No PDF files found in the source folder.", "status": "success"})
        
      for file in pdf_files:
          pending_pdf = total_pdfs - pdf_completed_count
          
          file_id = file['id']
          file_name = file['name']
          Logger.debug(f"********************Processing file: {file_name}**** Pending: {pending_pdf} **** Completed: {pdf_completed_count} ***********")
          
          # Download the PDF file
          self.download_file(file_id, file_name, save_path)
          Logger.debug(f"Downloaded file: {file_name}")
          # _chatgpt = Chatgpt()
          pdf_file_path = os.path.join(save_path, file_name)
          
          try:
            chatgpt_response_json = chatgpt_pdf_to_json(pdf_file_path)
            Logger.debug(f"Converted PDF to JSON for file: {file_name}")
            
            if is_null_or_empty(chatgpt_response_json) or chatgpt_response_json.__contains__('sorry') or chatgpt_response_json.__contains__('apologize'):
              Logger.warning(f"No data extracted from pdf file: {file_name}")
              self.move_file_to_folder(file_id, Config.ERROR_FOLDER, file_name)
              Logger.warning(f"Moved file {file_name} to Error_pdfs folder.")
              continue
            
            dataDict = json.loads(chatgpt_response_json)
            Logger.debug(f"JSON data loaded successfully for file: {file_name}")
            
            phoneNumberStr: str = str(dataDict['phoneNumber'])
            
            # getting pdf text
            pdf_text = extract_text_from_pdf(pdf_file_path)
            
            if is_null_or_empty(pdf_text):
              Logger.warning(f"No data extracted from pdf file: {file_name}")
            
            # checking for phone number fnd in pdf text
            if is_null_or_empty(phoneNumberStr):
              Logger.warning(f"No phone number: {phoneNumberStr} found in the extracted data for file: {file_name}")
              phoneNumber = extract_phone_numbers(pdf_text)
              if is_null_or_empty(phoneNumber) == False:
                Logger.debug(f"Extracted phone number: {phoneNumber} from pdf file: {file_name}")
                phoneNumberStr = str(phoneNumber)
                dataDict['phoneNumber'] = phoneNumberStr
              else:
                self.move_file_to_folder(file_id, Config.ERROR_FOLDER, file_name)
                Logger.warning(f"Moved file {file_name} to Error_pdfs folder.")
                continue
            
            phoneNumber: int = get_phone_number(phoneNumberStr)
            if is_number_zero(phoneNumber):
              Logger.warning(f"No phone number: {str(phoneNumber)} found in the extracted data for file: {file_name}")
              self.move_file_to_folder(file_id, Config.ERROR_FOLDER, file_name)
              Logger.warning(f"Moved file {file_name} to Error_pdfs folder.")
              continue
            
            try:
              if is_null_or_empty(dataDict['zipCode']):
                dataDict['zipCode'] = extract_zip_code(pdf_text)
            except:
              pass
            
            try:
              if is_null_or_empty(dataDict['dob']):
                dataDict['dob'] = extract_dob(pdf_text)
            except:
              pass
            
            try:
              if is_null_or_empty(dataDict['time']):
                dataDict['time'] = extract_time(pdf_text)
            except:
              pass
            
            try:
              if is_null_or_empty(dataDict['email']):
                dataDict['email'] = extract_email(pdf_text)
            except:
              pass
            
          
            self.insert_into_matrimonial(dataDict, file_name)
            Logger.debug(f"Inserted data into matrimonial database for file: {file_name}")
            self.move_file_to_folder(file_id, destination_folder_id, file_name)
            Logger.success(f"Moved file {file_name} to destination folder.")
            Logger.success(f"********************Completed file: {file_name}***********")
            
          except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            traceback.print_exc()
            print(tb)
            Logger.error(f"An error occurred for Pdf : {file_name}: {tb}")
            self.move_file_to_folder(file_id, Config.ERROR_FOLDER, file_name)
            Logger.debug(f"Moved file {file_name} to error folder.")
            # return json.dumps({"status": "failed", "message": str(e)})
          
          # Move the file to the destination folder
          pdf_completed_count = pdf_completed_count + 1

      Logger.info("Bio datas extracted and added to database successfully.")
      # return json.dumps({"message": "Bio datas extracted and added to database successfully."})
    except Exception as e:
      tb = traceback.extract_tb(e.__traceback__)
      traceback.print_exc()
      print(tb)
      Logger.error(f"An error occurred: {tb}")
      return json.dumps({"status": "failed", "message": str(e)})
    
  def sleep_timer(self, total_time=30, interval=2):
        start_time = time.time()
        end_time = start_time + total_time

        while time.time() < end_time:
            current_time = time.time()
            remaining_time = end_time - current_time
            if remaining_time <= 0:
                break
            Logger.warning(f"Google Drive Service will starts again in: {int(remaining_time)} seconds")
            # Logger.warning(f"Time left: {int(remaining_time)} seconds")
            time.sleep(interval)
  
  def start_service(self):
    while True:
      try: 
        self.extract_and_add_to_DB_MAIN()
      except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        traceback.print_exc()
        Logger.error(f"Unexpected Error trackback: {tb}")
        print(tb)
        Logger.error(f"An error occurred while starting the service. {e}")
        
      sleepTime = 60 * 10
      self.sleep_timer(total_time=sleepTime)