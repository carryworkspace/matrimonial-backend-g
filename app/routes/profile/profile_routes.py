
import os
import time
import json
import asyncio
import mysql.connector
from flask_cors import cross_origin
from datetime import datetime, timedelta
from ...extentions.chatgpt import Chatgpt
from ...extentions.otp_extentions import *
from werkzeug.utils import secure_filename
from ...extentions.common_extensions import *
from ...querys.user import user_query as querys
from ...models.profile_model import ProfileModel
from concurrent.futures import ThreadPoolExecutor
from ...extentions.pdf_extractor import PdfExtracter
from ...extentions.common_extensions import users_otp
from ...models.bio_data_pdf_model import BioDataPdfModel
from ...models.match_profile_model import MatchProfileModel
from .. import createDbConnection, Router,closeDbConnection
from ...models.gallery_images_model import GalleryImagesModel
from ...models.profile_interest_model import ProfileInterestModel
from flask import jsonify, request, abort, send_file, make_response
from ...models.matrimonial_profile_model import MatrimonialProfileModel
from ...models.response.extraction_payload_model import ExtractionPayloadModel
import traceback
# from app.extentions.base import info
# from app.extentions.logger import Logger

# authentication is in user_routes
@Router.route('/profile', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def add_profile():
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    data = request.get_json()
    
    try:
        
        # Check if all expected keys are present
        # print(data)
        attributes = ProfileModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            return missing_keys
        
        model = ProfileModel.fill_model(data)
        Logger.debug(f"Profile model created: {len(model.__dict__.keys())}")
        cursorDb.execute(querys.CheckProfileExists(userId=model.userId))
        profiles = cursorDb.fetchall()
        if len(profiles) == 0:
            Logger.info("User Id Invalid. This user id does not exist ")
            return json.dumps({"status": "failed", "message": "User Id Invalid. This user id not exist"})
        
        cursorDb.execute(querys.UpdateProfile(), model.__dict__)
        db.commit()
        Logger.info(f"Profile updated successfully for user id: {model.userId}")
        return json.dumps({"status": "success", "message": "Profile Updated Successfully"}), 200
        
    except mysql.connector.Error as e:
        Logger.error(f"Database error: {e}")
        # print(f"Error: {e} This is Erorr")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"Invalid data format: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        # print(f"Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")

# upload profile
@Router.route('/upload-profile-picture', methods=['PATCH'])
@cross_origin(supports_credentials=True)
def upload_profile_picture():

    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    upload_folder = Config.PROFILE_PIC_PATH
    Logger.debug(f"Upload folder path: {upload_folder}")
    try:
        # Check if all expected keys are present

        userId :int = 0
        requestFileName: str
        try:
            userId = int(request.form["userId"])
        except Exception as e:
            Logger.error(f"Error parsing userId: {e}")
            userId = 0

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            Logger.info(f"Created upload folder: {upload_folder}")
            
        if 'file' not in request.files:
            Logger.info("No file part or profile picture found.")
            return json.dumps({"status": "failed", "message":'No file part or profile picture'}), 404

        if userId == 0:
            Logger.warning("User ID not specified or user ID not provided")
            return json.dumps({"status": "failed", "message":'User not specified or user id not provided'}), 400
        
        if 'file' in request.files:
            file = request.files['file']
            Logger.debug(f"File retrieved from request files: {file.filename}")

        elif 'file' in request.form:
            file = request.form['file']

        try:
            requestFileName = str(userId)+ "_" + str(generate_random_number()) + "_" +file.filename
            file.save(os.path.join(upload_folder, requestFileName))
            Logger.info(f"Saved profile picture as: {requestFileName}")

        except Exception as e:
            Logger.error(f"Error saving profile picture: {e}")
            # print(f"error: {e}")
            db.rollback()
            try:
                return json.dumps({"status": "failed", 'message': str(e)}), 400
            except:
                Logger.error("Error saving profile picture")
                return json.dumps({"status": "failed", 'message': "Failed to save picture. Please contact to developer"}), 400

        profile_path = os.path.join(upload_folder, requestFileName)
        Logger.debug(f"Profile picture path: {profile_path}")
        # print(profile_path)
        if not os.path.exists(profile_path):
            Logger.warning("Profile picture not uploaded or saved.")
            return json.dumps({"status": "failed", "message": "Profile Picture not uploaded. Please try again"}), 400
        
        if os.path.exists(profile_path):
            cursorDb.execute(querys.CheckProfileExists(userId=userId))
            profiles = cursorDb.fetchall()
            Logger.debug(f"Fetched profiles: {len(profiles)}")
            if len(profiles) == 0:
                Logger.info(f"User ID does not exist in database: {userId}")
                return json.dumps({"status": "failed", "message": "User Id Invalid. This user id not exist"}), 400
            
            cursorDb.execute(querys.UpdateProfilePicture(userId=userId, picture=requestFileName), {"profilePicture": requestFileName, "userId": userId})
            db.commit()
            Logger.info(f"Profile picture updated successfully for userId: {userId}")
        return json.dumps({"status": "success", "message": "Profile picture uploaded successfully"}), 200
        
    except mysql.connector.Error as e: 
        Logger.error(f"Database error: {e}")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"Invalid data format: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")

# profile picture fetch
@Router.route('/profile-picture', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_profile_picture():

    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    upload_folder = Config.PROFILE_PIC_PATH
    Logger.debug(f"Upload folder path: {upload_folder}")
    try:
        # Check if all expected keys are present
        userId :int = 0
        requestFileName: str
        try:
            userId = int(request.args["userId"])
        except Exception as ex:
            userId = 0
            Logger.error(f"Error parsing userId from request arguments: {ex}")
        if userId == 0:
            Logger.info("User ID not specified or invalid.")
            return json.dumps({"status": "failed", "message":'User not specified or user id not provided'}), 400
        
        cursorDb.execute(querys.GetProfilePicture(userId))
        requestFileName = cursorDb.fetchall()[0]["ProfilePicture"]
        Logger.debug(f"Fetched profile picture filename: {requestFileName}")
        profile_path = os.path.join(upload_folder, requestFileName)
        if not os.path.exists(profile_path):
            Logger.warning(f"Profile Picture not found for user ID: {userId}")
            return json.dumps({"status": "failed", "message": "Profile Picture not found. Please upload first"}), 400
        
        db.commit()
        responseData = {}
        try:
            with open(profile_path, 'rb') as file:
                # Read the file content and convert it into a byte array
                file_content = file.read()
                byte_array = bytearray(file_content)
                byte_array_list = list(byte_array)
                responseData["status"] = "success"
                responseData["image"] = byte_array_list
                responseData["filename"] = requestFileName
        except FileNotFoundError:
            Logger.error("Image not found error")
            return json.dumps({'status': 'failed','message': 'Image not found'})
        
        # return send_file(profile_path, mimetype='image/png, image/jpeg')
        Logger.info(f"Profile picture retrieved successfully for userId: {userId}")
        return json.dumps(responseData), 200
        
    except mysql.connector.Error as e:
        Logger.error(f"Database error: {e}") 
        # print(f"Error: {e} This is Erorr")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"Invalid data format: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        # print(f"Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")

@Router.route('/profile-interest', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_profile_interest():
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    data = request.get_json()
    Logger.debug(f"Received JSON data: {data}")
    try:
        # Check if all expected keys are present
        attributes = ProfileInterestModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            Logger.warning(f"Missing keys in request data: {missing_keys}")
            return missing_keys
        
        model = ProfileInterestModel.fill_model(data)
        Logger.debug(f"ProfileInterestModel created: {len(model.__dict__.keys())}")
        cursorDb.execute(querys.AddProfileInterest(), model.__dict__)
        db.commit()
        return "Profile Interest Created Successfully", 200
        
    except mysql.connector.Error as e: 
        Logger.error(f"MySQL Database Error: {e}")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"Value Error: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")

@Router.route('/matrimonial', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_matrimonial_profile():
    Logger.info("Creating database connection.")
    db, cursorDb = createDbConnection()
    data = request.get_json()
    Logger.info("Received data")
    
    try:
        Logger.info("Checking for missing keys in the input data.")
        # Check if all expected keys are present
        attributes = MatrimonialProfileModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            Logger.warning("Missing keys found in the input data")
            return missing_keys
        Logger.info("Filling the model with input data.")
        
        model = MatrimonialProfileModel.fill_model(data)
        Logger.info(f"Checking if profile with ID {model.profileId} exists.")
        cursorDb.execute(querys.GetProfileDetailsById(model.profileId))
        profiles = cursorDb.fetchall()
        if len(profiles) == 0:
            Logger.warning(f"Profile ID {model.profileId} is invalid.")
            return json.dumps({"status": "failed", "message": "Profile Id Invalid. This profile id not exist"})
        
        Logger.info(f"Checking if matrimonial profile with profile ID {model.profileId} exists.")
        
        cursorDb.execute(querys.GetMatrimonialProfileByProfileId(model.profileId))
        matrimonial_profile = cursorDb.fetchall()
        if len(matrimonial_profile) != 0:
            Logger.info("Matrimonial profile exists, updating the profile.")
            cursorDb.execute(querys.UpdateMatrimonial(), model.__dict__)
            db.commit()
            
            return json.dumps({"status": "success", "message": "Matrimonial Profile already exists for this profile we just updated all vaulues"})
        dataDict  = model.__dict__
        dataDict["subscribeToken"] = f"{dataDict['name'].replace(' ', '_')}_{dataDict['phoneNumber'].replace(' ', '_')}"
        cursorDb.execute(querys.AddMatrimonialProfile(), dataDict)
        Logger.info("Matrimonial profile created successfully.")
        db.commit()
        return json.dumps({"status":"success", "message": "Matrimonial Profile Created Successfully"}), 200
        
    except mysql.connector.Error as e: 
            Logger.error(f"MySQL Error: {e}")
            return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"ValueError: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        Logger.info("Closing database connection.")
        closeDbConnection(db, cursorDb)

@Router.route('/match', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_match_profile():
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    data = request.get_json()
    Logger.debug(f"Received JSON data: {data}")
    
    try:
        # Check if all expected keys are present
        attributes = MatchProfileModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            Logger.info(f"Missing keys in request data: {missing_keys}")
            return missing_keys
        
        model = MatchProfileModel.fill_model(data)
        Logger.debug(f"Profile interest model filled: {len(model.__dict__.keys())}")
        cursorDb.execute(querys.AddMatchedProfile(), model.__dict__)
        db.commit()
        Logger.info("Profile Interest created successfully.")
        return "Match Profile Added Successfully", 200
        
    except mysql.connector.Error as e:
        Logger.error(f"MySQL Database error: {e}") 
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"Invalid data format: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")

@Router.route('/gallery-images', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_gallery_images():
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    data = request.get_json()
    Logger.debug(f"Received JSON data: {data}")
    
    try:
        # Check if all expected keys are present
        attributes = GalleryImagesModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            Logger.info(f"Missing keys in request data: {missing_keys}")
            return missing_keys
        
        model = GalleryImagesModel.fill_model(data)
        Logger.debug(f"Gallery images model filled: {len(model.__dict__.keys())}")
        cursorDb.execute(querys.AddGalleryImages(), model.__dict__)
        db.commit()
        Logger.info("Gallery Images added successfully.")
        return "Gallery Images Added Successfully", 200
        
    except mysql.connector.Error as e:
        Logger.error(f"MySQL Database error: {e}") 
        return json.dumps({"status": "failed",'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"Invalid data format: {ve}")
        db.rollback()
        return json.dumps({"status": "failed",'message': "Invalid data format"}), 400
    
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        db.rollback()
        return json.dumps({"status": "failed","message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")

# extract bio data
@Router.route('/bio-data-pdf-extract', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_bio_data_pdf():
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    data = request.get_json()
    upload_folder = Config.BIO_DATA_PDF_PATH
    Logger.info(f"Requesting json : {request.get_json()}")
    
    try:
        Logger.info("Starting add_bio_data_pdf function")
        # Check if all expected keys are present
        attributes = BioDataPdfModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            Logger.warning(f"request json have these: {missing_keys} empty fields")
            return missing_keys

        model = BioDataPdfModel.fill_model(data)
        pdf_file_path = os.path.join(upload_folder, model.pdfName)
        if not os.path.exists(pdf_file_path):
            Logger.error(f"pdf file not found on server for profileId: {model.profileId}")
            return json.dumps({"status": "failed", "message": "Pdf not Found"}), 404
            
        
        if os.path.exists(pdf_file_path):
            cursorDb.execute(querys.CheckPdfExistWithProfileId(), model.__dict__)
            pdfDetail = cursorDb.fetchall()
            if len(pdfDetail) == 0:
                cursorDb.execute(querys.CheckPdfExistWithProfileIdOnly(model.profileId))
                Logger.info(f"getting info of pdf name for profileId: {model.profileId}")
                pdfDetail = cursorDb.fetchall()
                if len(pdfDetail) == 0:
                    cursorDb.execute(querys.AddBioDataPdfFile(), model.__dict__)
                    Logger.info(f"Bio Data Pdf Name: {model.pdfName} Inserted Successfully")
                else:
                    cursorDb.execute(querys.UpdateBioDataPdfFile(), model.__dict__)
                    Logger.info(f"Bio Data Pdf Name: {model.pdfName} Updated Successfully")
                    
                db.commit()
                Logger.debug(f"Last inserted row ID: {cursorDb.lastrowid}")

        _chatgpt = Chatgpt()
        exeptionOccurs = True
        tries: int = 0
        while exeptionOccurs and tries < 3:
            try:
                exeptionOccurs = False
                tries += 1
                Logger.debug(f"Attempt {tries} to process PDF data")
                bio_data_json = chatgpt_pdf_to_json(pdf_file_path)
                response_payload_json = _chatgpt.chat(text=bio_data_json, payload=query_payload)
                jsonObject = json.loads(response_payload_json)
                
                model = ExtractionPayloadModel.fill_model(jsonObject)
            except json.JSONDecodeError as jd:
                # tb = traceback.extract_tb(e.__traceback__)
                # filename, line_number, func_name, text = tb[-1]
                    
                # traceback.print_exc()
                Logger.error(f"JSON Decode Error: {jd}")
                exeptionOccurs = True
        return json.dumps({"status": "success", "message": model.__dict__}), 200
        
    except mysql.connector.Error as e: 
        tb = traceback.extract_tb(e.__traceback__)
        filename, line_number, func_name, text = tb[-1]
                    
        traceback.print_exc()
        Logger.error(f"MySQL Database Error: {e}")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    except json.JSONDecodeError as jd:
        Logger.error(f"JSON Decode Error: {jd}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format of json"}), 400
    
    except ValueError as ve:
        Logger.error(f"Value Error: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400

    
    except Exception as e:
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed")
        Logger.info("add_bio_data_pdf function execution completed")