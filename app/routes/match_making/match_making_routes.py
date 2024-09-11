import os
from flask import request, jsonify
from app.extentions.common_extensions import *
from app.extentions.otp_extentions import *
from app.extentions.machmaking_score import MatchmakingScore
from app.routes import Router, closeDbConnection, closePoolConnection, _database
from flask_cors import cross_origin
import mysql.connector
from app.models.match_profile_model import MatchProfileModel
from app.querys.user import user_query as querys
from app.services.astrology_data_service import AstroService
from app.extentions.logger import Logger
from app.extentions.multiprocess import MultiProcess
from app.services.match_making_service import MatchMakingService
from app.services.mapping_match_making_service import MappingMatchMakingService
from datetime import datetime
import traceback
import shutil
import math

@Router.route('/matchmaking', methods=['GET'])
@cross_origin(supports_credentials=True)
def perform_matchmaking():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    Logger.debug("Database connection obtained from _matching")
    try:
        Logger.info("Starting perform_matchmaking function")
        profileId :int = 0
        try:
            profileId = int(request.args["profileId"])
        except:
            Logger.error("Error occured while parsing profile ID")
            profileId = 0
        
        if profileId == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "Profile ID not provided"}), 400
        Logger.info(f"Received profileId: {profileId}")
        
        cursorDb.execute(querys.CheckMatrimonialProfileExist(profileId))
        Logger.debug(f"Executed query to check profile existence for profileId: {profileId}")
        user_exists = cursorDb.fetchall()

        if not user_exists:
            Logger.warning(f"Profile ID {profileId} does not exist")
            return jsonify({"status": "failed", "message": "User Invalid"}), 400
        
        cursorDb.execute(querys.GetQueuedMatchMakingById(profileId))
        queuedData = cursorDb.fetchall()
        
        if len(queuedData) != 0:
            Logger.info(f"Profile Id: {profileId} added in queued successfully")
            return json.dumps({"status": "success", "message": "already started"}), 200
        
        cursorDb.execute(querys.AddMatchMakingQueued(profileId))
        
        db.commit()
        Logger.info(f"profileId: {profileId} inserted successfully to queued match making table")
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({"status": "success", "message": "started"}), 200
    
    except mysql.connector.Error as e:
        Logger.error(f"JSON Decode Error: {e}")
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
        # closePoolConnection(db)
        Logger.info("Closing database connection")

@Router.route('/match-making-status', methods=['GET'])
@cross_origin(supports_credentials=True)
def match_making_status():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    try:
        Logger.info("Starting match_making_status function")
        profileId :int = 0
        try:
            profileId = int(request.args["profileId"])
        except Exception as e:
            Logger.error(f"Error occurred while parsing profileId: {e}")
            profileId = 0
        
        if profileId == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "Profile ID not provided"}), 400
        Logger.debug("Database connection established")
        cursorDb.execute(querys.GetMatchMakingCompleteNotification(profileId=profileId))
        Logger.debug(f"Executed database query to check matchmaking status for profileId: {profileId}")
        user_exists = cursorDb.fetchall()
        Logger.debug(f"Database query result: {len(user_exists)}")
        
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        if len(user_exists) == 0:
            return json.dumps({"status": "success", "message": "pending", 'profileId': str(profileId)}), 200
        return json.dumps({'status': 'success', 'message': 'complete', 'profileId': str(profileId)}), 200
    
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        Logger.info("Closing database connection")


@Router.route('/match-making-result', methods=['GET'])
@cross_origin(supports_credentials=True)
def match_making_result():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    user_match_making_results = []
    male_max_age_diff = -3
    male_min_age_diff = 1
    female_min_age_diff = 3
    female_max_age_diff = -1
    try:
        Logger.info("Starting match_making_status function")
        mainProfileId :int = 0
        try:
            mainProfileId = int(request.args["profileId"])
        except Exception as e:
            Logger.error(f"Error occurred while parsing profileId: {e}")
            mainProfileId = 0
        
        if mainProfileId == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "Profile ID not provided"}), 400
        Logger.debug("Database connection established")
        cursorDb.execute(querys.GetMatchMakingCompleteNotification(profileId=mainProfileId))
        Logger.debug(f"Executed database query to check matchmaking status for profileId: {mainProfileId}")
        user_exists = cursorDb.fetchall()
        Logger.debug(f"Database query result: {len(user_exists)}")
        if len(user_exists) == 0:
            return json.dumps({"status": "success", "message": "Matchmaking is Inprogress.", 'user_details': user_match_making_results}), 200
        
        main_profile_dob = user_exists[0]["Dob"]
        main_profile_gender = user_exists[0]["Gender"]
        main_profile_age = calculate_age(main_profile_dob)
        
        cursorDb.execute(querys.GetMatchedProfiles(mainProfileId))
        matched_profiles = cursorDb.fetchall()
        print(matched_profiles)
        Logger.debug(f"Database query result for matched profiles: {len(matched_profiles)}")
        for match_profile in matched_profiles:
            match_making_result = {}
            upload_folder = Config.PROFILE_PIC_PATH
            try:
                otherProfileId = match_profile["OtherProfileId"]
                gunn_score = match_profile["GunnMatchScore"]
                notificationMsg = match_profile["NotificationMsg"]
                total_score = match_profile["MatchScore"]
                percentage = get_score_percentage(total_score)
                score_percentage = str(math.floor(percentage))+ "%"
                
                
                if not is_null_or_empty(notificationMsg):
                    notificationMsg.replace('"', "")
                    
                hobbies = match_profile["Hobbies"]
                astroMsg = match_profile["AstroMsg"]
                cursorDb.execute(querys.GetMatrimonialData(profileId=otherProfileId))
                profile = cursorDb.fetchone()
                
                if profile == None:
                    Logger.info(f"Matrimonial Profile not found for profileId: {otherProfileId}")
                    continue
                
                # print("PROFILEDIEDFDFDJ:LJSDLKFJKSDLJFLKSF:", profile, otherProfileId)
                Logger.debug(f"Database query result Matrimonial: {len(profile)}")
                
                name = profile["Name"]
                gender = profile["Gender"]
                dob = profile["Dob"]
                city = profile["City"]
                subscribeToken = profile["Subscribe_Token"]
                state = profile["State"]
                height = profile["HeightCM"].split(".")
                height = height[0].split(",")
                height = height[0]
                
                if height == None or height == "" or height == "0" or height == "0.0":
                    height = 165
                
                if int(height) < 50:
                    height = 165
                
                age = calculate_age(dob)
                
                age_diff = main_profile_age - age
                age_diff_ok = False
                
                # check for max male age under constant value
                if main_profile_gender.lower() == "male":
                    Logger.info(f"Checking age difference for male profile")
                    age_diff_ok = age_diff <= female_min_age_diff and age_diff >= female_max_age_diff
                    Logger.info(f"Age difference check result: {age_diff_ok}")
                    Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                    
                # check female max age under or equal to the constant value
                elif main_profile_gender.lower() == "female":
                    Logger.info(f"Checking age difference for female profile")
                    age_diff_ok = age_diff <= male_min_age_diff and age_diff >= male_max_age_diff
                    Logger.info(f"Age difference check result: {age_diff_ok}")
                    Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                    
                else:
                    Logger.info(f"Checking age difference for other gender profile")
                    age_diff_ok = age_diff <= 1 or age_diff >= 1
                    Logger.info(f"Age difference check result: {age_diff_ok}")
                    Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                    
                if age_diff_ok == False:
                    Logger.warning(f"Age difference : {age_diff} is not satisfied for profileId: {otherProfileId}")
                    Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                    Logger.warning(f"Skiping the profile")
                    continue
                    
                
                
                height = str(cm_to_feet(height))
                height_ft = height.split(".")[0]+ " Ft"
                height_inches = height.split(".")[1][:1]+ " Inches" 
                final_height = height_ft + " "+ height_inches
                
                if is_null_or_empty(city):
                    location = state
                elif is_null_or_empty(state):
                    location = city
                elif is_null_or_empty(city) and is_null_or_empty(state):
                    location = None
                else:
                    location = city+ ", "+ state
                
                # filling dictionary for result
                match_making_result["profileId"] = otherProfileId
                match_making_result["name"] = name
                match_making_result["gender"] = gender
                match_making_result["age"] = age
                match_making_result["height"] = final_height
                match_making_result["location"] = location
                match_making_result["SubscribeToken"] = subscribeToken
                match_making_result["gunnScore"] = str(gunn_score)
                match_making_result["notificationMsg"] = notificationMsg
                match_making_result["hobbies"] = hobbies
                match_making_result["astroMsg"] = astroMsg
                match_making_result["percentage"] = score_percentage
                
                # fetch profile picure
                cursorDb.execute(querys.GetProfilePictureById(otherProfileId))
                profile_picture_data = cursorDb.fetchone()
                if profile_picture_data == None:
                    Logger.debug(f"Profile Picture data: {profile_picture_data}")
                    match_making_result["picture"] = None
                    
                else:
                    requestFileName = profile_picture_data["ProfilePicture"]
                    if is_null_or_empty(requestFileName):
                        if gender.lower() == "male":
                            requestFileName = Config.DEFAULT_PROFILE_PIC_MALE
                        elif gender.lower() == "female":
                            requestFileName = Config.DEFAULT_PROFILE_PIC_FEMALE
                        else:
                            requestFileName = Config.DEFAULT_PROFILE_PIC
                        
                    Logger.debug(f"Fetched profile picture filename: {requestFileName}")
                    profile_path = os.path.join(upload_folder, requestFileName)
                    
                    if not os.path.exists(profile_path):
                        Logger.warning(f"Profile Picture not found on server for user ID: {otherProfileId}")
                        
                        if gender.lower() == "male":
                            requestFileName = Config.DEFAULT_PROFILE_PIC_MALE
                        elif gender.lower() == "female":
                            requestFileName = Config.DEFAULT_PROFILE_PIC_FEMALE
                        else:
                            requestFileName = Config.DEFAULT_PROFILE_PIC
                    
                    profile_path = os.path.join(upload_folder, requestFileName)
                                
                    db.commit()
                    
                    try:
                        with open(profile_path, 'rb') as file:
                            # Read the file content and convert it into a byte array
                            file_content = file.read()
                            byte_array = bytearray(file_content)
                            byte_array_list = list(byte_array)
                            match_making_result["filename"] = requestFileName
                            match_making_result["picture"] = byte_array_list
                            
                    except FileNotFoundError:
                        Logger.error("Image not found error")
                        match_making_result["picture"] = None
                
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                filename, line_number, func_name, text = tb[-1]
                    
                traceback.print_exc()
                print(tb)
                db.rollback()
                Logger.error(f"Error occurred while filling object for match making: {tb}")
                Logger.error(f"Skiping data for profile Id: {otherProfileId}")
                continue
                # match_making_result["Error"] = f"Some error occurs for key: {e}"
            user_match_making_results.append(match_making_result)
            
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({'status': 'success', 'message': 'Matchmaking is Completed.', 'user_details': user_match_making_results}), 200
    
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        # Logger.info("Closing database connection")
        pass
        

@Router.route('/matched_profile_viewed', methods=['GET'])
@cross_origin(supports_credentials=True)
def update_match_making_profile_viewed():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    # doing someting else will continue after some time
    db, cursorDb = _database.get_connection()
    try:
        Logger.info("Starting match_making_status function")
        id :int = 0
        try:
            id = int(request.args["id"])
        except Exception as e:
            Logger.error(f"Error occurred while parsing profileId: {e}")
            id = 0
        
        if id == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "id not provided"}), 400
        
        cursorDb.execute(querys.GetMatchedProfileById(id))
        matched_data = cursorDb.fetchall()
        
        if len(matched_data) == 0:
            Logger.info(f"Did not get any results for the id: {id} in database.")
            return json.dumps({'status': 'failed', 'message': 'provided id not exists in datababse'}), 200
                    
        else:
            Logger.info(f"Got results for the id: {id} in database.")
            Logger.info(f"Got results for the id: {matched_data} in database.")
            Logger.warning(f"Updating Viewed Status for id: {id}")
            cursorDb.execute(querys.UpdateViewedStatusMatchedProfile(id))
            db.commit()
            return json.dumps({'status': 'success', 'message': 'updated status of viewed'}), 200
        
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        # Logger.info("Closing database connection")

@Router.route('/download-bio-data', methods=['GET'])
@cross_origin(supports_credentials=True)
def download_pdf():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    # doing someting else will continue after some time
    db, cursorDb = _database.get_connection()
    bio_data_pdf_result = {}
    upload_folder = Config.BIO_DATA_PDF_PATH
    try:
        Logger.info("Starting match_making_status function")
        profileId :int = 0
        try:
            profileId = int(request.args["profileId"])
        except Exception as e:
            Logger.error(f"Error occurred while parsing profileId: {e}")
            profileId = 0
        
        if profileId == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "Profile ID not provided"}), 400
        
        cursorDb.execute(querys.GetBioDataPdfByProfileId(profileId))
        bio_data_pdf = cursorDb.fetchall()
        
        if len(bio_data_pdf) == 0:
            Logger.info(f"Did not get any pdf bio file for the profile id: {profileId} in database.")
            return json.dumps({'status': 'failed', 'message': 'pdf not found for the profile_id', 'pdf_file': None}), 200
                    
        else:
            requestFileName = bio_data_pdf[0]["PdfName"]
            Logger.debug(f"Fetched profile picture filename: {requestFileName}")
            pdf_path = os.path.join(upload_folder, requestFileName)
            
            if not os.path.exists(pdf_path):
                Logger.warning(f"Pdf not found on server for the profile id: {profileId}")
                bio_data_pdf_result["picture"] = None
                        
            db.commit()
            
            try:
                with open(pdf_path, 'rb') as file:
                    # Read the file content and convert it into a byte array
                    file_content = file.read()
                    byte_array = bytearray(file_content)
                    byte_array_list = list(byte_array)
                    bio_data_pdf_result["status"] = "success"
                    bio_data_pdf_result["message"] = f"pdf found for the profile_id: {profileId}"
                    bio_data_pdf_result["filename"] = requestFileName
                    bio_data_pdf_result["pdf_file"] = byte_array_list
                Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
                return json.dumps(bio_data_pdf_result), 200
                    
            except FileNotFoundError:
                Logger.error("Pdf not found error")
                bio_data_pdf_result["pdf_file"] = None    
        
    
        return json.dumps({'status': 'failed', 'message': 'pdf not found for the profile_id in Db', 'pdf_file': None}), 200
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        # Logger.info("Closing database connection")
        pass


@Router.route('/generate-bio-data-link', methods=['GET'])
@cross_origin(supports_credentials=True)
def generate_bio_data_link():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    # doing someting else will continue after some time
    db, cursorDb = _database.get_connection()
    upload_folder = Config.BIO_DATA_PDF_PATH
    public_folder = Config.BIO_DATA_PUBLIC_FOLDER_SERVER if detect_environment() == "server" else Config.BIO_DATA_PUBLIC_FOLDER
    pdf_host = Config.SERVER_PDF_HOST
    link = None
    public_pdf_name = None
    
    if os.path.exists(public_folder) == False:
        os.makedirs(public_folder)
        
    random_name = str(generate_random_number(12)) + '.pdf'
    try:
        Logger.info("Starting generate_bio_data_link function")
        profileId :int = 0
        try:
            profileId = int(request.args["profileId"])
        except Exception as e:
            Logger.error(f"Error occurred while parsing profileId: {e}")
            profileId = 0
        
        if profileId == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "Profile ID not provided"}), 400
        
        cursorDb.execute(querys.GetBioDataPdfByProfileId(profileId))
        bio_data_pdf = cursorDb.fetchall()
        
        if len(bio_data_pdf) == 0:
            Logger.info(f"Did not get any pdf bio file for the profile id: {profileId} in database.")
            return json.dumps({'status': 'failed', 'message': 'pdf not found in db for the profile_id', 'pdf_link': None}), 404
                    
        else:
            public_pdf_name = bio_data_pdf[0]["PublicPdfName"]
            Logger.debug(f"Fetched public pdf name: {public_pdf_name}")
            if is_null_or_empty(public_pdf_name):
                Logger.warning(f"Public pdf name : {public_pdf_name}")
                Logger.warning(f"Processing link to generate")
            
                requestFileName = bio_data_pdf[0]["PdfName"]
                Logger.debug(f"Fetched profile picture filename: {requestFileName}")
                pdf_path = os.path.join(upload_folder, requestFileName)
                
                if not os.path.exists(pdf_path):
                    Logger.warning(f"Pdf not found on server for the profile id: {profileId}")
                    return json.dumps({'status': 'failed', 'message': 'pdf not found on server for the profile_id', 'pdf_link': None}), 404
                    
                dest_file = os.path.join(public_folder, random_name)
                try:
                    shutil.copy(pdf_path, dest_file)
                    Logger.info(f'Copied and renamed {random_name} to {dest_file}')
                except Exception as e:
                    Logger.info(f'Failed to copy and rename {random_name}: {e}')
                
                cursorDb.execute(querys.UpdateBioDataPdfPublicFileName(profileId, random_name))
                db.commit()
                link = pdf_host + random_name
            else:
                link = pdf_host + public_pdf_name                
                
        return json.dumps({'status': 'success', 'message': 'pdf found', 'pdf_link': link}), 200
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        # Logger.info("Closing database connection")
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        

@Router.route('/whatsapp-notification-status', methods=['GET'])
@cross_origin(supports_credentials=True)
def whatsapp_notification_result():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    results = []
    try:
        cursorDb.execute(querys.GetAllMatchedProfiles())
        matched_users = cursorDb.fetchall()
        Logger.info(f"Total matched_users : {len(matched_users)}")
        if len(matched_users) == 0:
            Logger.info(f"Did not get any results for the matched making users in database.")
            return json.dumps({'status': 'failed', 'message': 'No users found for match making', 'user_details': []}), 200
        
        for user in matched_users:
            match_making_result = {}
            profileId = user["MainProfileId"]
            
        
            cursorDb.execute(querys.GetUserDetails(profileId))
            users = cursorDb.fetchall()
            
            if len(users) == 0:
                Logger.info(f"Did not get any results for the profile id: {profileId} in database.")
                return json.dumps({'status': 'failed', 'message': 'provided id not exists in datababse'}), 400
            Logger.info(f"Total users : {len(users)}")
            users = users[0]
            phoneNumber = users["PhoneNumber"]
            email = users["Email"]
            
            
            # cursorDb.execute(querys.GetProfileDetailsById(profileId))
            # profiles = cursorDb.fetchall()
            # Logger.info(f"Total profiles : {len(profiles)}")
            # marital_status = profiles["MaritalStatus"]
        
            cursorDb.execute(querys.CheckMatrimonialProfileExist(profileId))
            matrimonial_profiles = cursorDb.fetchall()
            if len(matrimonial_profiles) == 0:
                Logger.info(f"Did not get any results for the profile id: {profileId} in database.")
                return json.dumps({'status': 'failed', 'message': 'provided id not exists in datababse'}), 400
            
            Logger.info(f"Total matrimonial profiles : {len(matrimonial_profiles)}")
            matrimonial_profiles = matrimonial_profiles[0]
            name = matrimonial_profiles["Name"]
            gender = matrimonial_profiles["Gender"]
            
            if is_null_or_empty(phoneNumber):
                phoneNumber = matrimonial_profiles["PhoneNumber"]
                
            if is_number_zero(phoneNumber):
                phoneNumber = matrimonial_profiles["PhoneNumber"]
                
            
            whatsapp_notification = int(matrimonial_profiles["WhatsappNotification"])
            if whatsapp_notification == 1:
                continue
            else:
                match_making_result['profileId'] = profileId
                match_making_result['name'] = name
                match_making_result['gender'] = gender
                match_making_result['email'] = email
                match_making_result['phoneNumber'] = str(phoneNumber)
                match_making_result['age'] = calculate_age(matrimonial_profiles["Dob"])
                results.append(match_making_result)
        
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({'status': 'success', 'message': f'found {len(results)} users that has done match making', 'user_details': results}), 200
    
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        # Logger.info("Closing database connection")
        pass

@Router.route('/matched-making-result-with-tag', methods=['GET'])
@cross_origin(supports_credentials=True)
def matched_making_result_with_tag():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    user_match_making_results = []
    male_max_age_diff = -3
    male_min_age_diff = 1
    female_min_age_diff = 3
    female_max_age_diff = -1
    google_drive_data = False
    try:
        Logger.info("Starting match_making_status function")
        mainProfileId :int = 0
        try:
            mainProfileId = int(request.args["profileId"])
        except Exception as e:
            Logger.error(f"Error occurred while parsing profileId: {e}")
            mainProfileId = 0
        
        if mainProfileId == 0:
            Logger.warning("Profile ID not provided or invalid")
            return jsonify({"status": "failed", "message": "Profile ID not provided"}), 400
        Logger.debug("Database connection established")
        
        cursorDb.execute(querys.GetMatchMakingCompleteNotification(profileId=mainProfileId))
        Logger.debug(f"Executed database query to check matchmaking status for profileId: {mainProfileId}")
        user_exists = cursorDb.fetchall()
        Logger.debug(f"Database query result: {len(user_exists)}")
        if len(user_exists) == 0:
            return json.dumps({"status": "success", "message": "Matchmaking is Inprogress.", 'user_details': user_match_making_results}), 200
        
        cursorDb.execute(querys.GetMatchedProfiles(mainProfileId))
        matched_profiles = cursorDb.fetchall()
        print(matched_profiles)
        Logger.debug(f"Database query result for matched profiles: {len(matched_profiles)}")
        for match_profile in matched_profiles:
            match_making_result = {}
            # upload_folder = Config.PROFILE_PIC_PATH
            try:
                otherProfileId = match_profile["OtherProfileId"]
                # gunn_score = match_profile["GunnMatchScore"]
                # notificationMsg = match_profile["NotificationMsg"].replace('"', "")
                cursorDb.execute(querys.GetMatrimonialData(profileId=otherProfileId))
                matrimonial = cursorDb.fetchone()
                
                cursorDb.execute(querys.GetProfileDetailsById(otherProfileId))
                profile = cursorDb.fetchone()
                
                if matrimonial == None:
                    Logger.info(f"Matrimonial Profile not found for profileId: {otherProfileId}")
                    continue
                
                if profile == None:
                    Logger.info(f"Profile not found for profileId: {otherProfileId}")
                    continue
                
                marital_status = profile["MaritalStatus"]
                
                if is_null_or_empty(marital_status):
                    google_drive_data = True
                else:
                    google_drive_data = False
                
                whatsapp_notification = int(matrimonial["WhatsappNotification"])
                if whatsapp_notification == 1:
                    continue
                else:
                
                    # print("PROFILEDIEDFDFDJ:LJSDLKFJKSDLJFLKSF:", profile, otherProfileId)
                    Logger.debug(f"Database query result Matrimonial: {len(matrimonial)}")
                    
                    name = matrimonial["Name"]
                    gender = matrimonial["Gender"]
                    dob = matrimonial["Dob"]
                    email = matrimonial["Email"]
                    phone = matrimonial["PhoneNumber"]
                    age = calculate_age(dob)
                    match_making_result["profileId"] = otherProfileId
                    match_making_result["name"] = name
                    match_making_result["gender"] = gender
                    match_making_result["age"] = age
                    match_making_result["email"]= email
                    match_making_result["phoneNumber"] = phone
                    match_making_result["tag"] = "google drive" if google_drive_data else ""
                    # city = profile["City"]
                    # subscribeToken = profile["Subscribe_Token"]
                    # state = profile["State"]
                    # height = profile["HeightCM"].split(".")
                    # height = height[0].split(",")
                    # height = height[0]
                    
                    # if height == None or height == "" or height == "0" or height == "0.0":
                        # height = 165
                    
                    # if int(height) < 50:
                        # height = 165
                    
                    
                    # age_diff = main_profile_age - age
                    # age_diff_ok = False
                    
                    # check for max male age under constant value
                    # if main_profile_gender.lower() == "male":
                    #     Logger.info(f"Checking age difference for male profile")
                    #     age_diff_ok = age_diff <= female_min_age_diff and age_diff >= female_max_age_diff
                    #     Logger.info(f"Age difference check result: {age_diff_ok}")
                    #     Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                        
                    # # check female max age under or equal to the constant value
                    # elif main_profile_gender.lower() == "female":
                    #     Logger.info(f"Checking age difference for female profile")
                    #     age_diff_ok = age_diff <= male_min_age_diff and age_diff >= male_max_age_diff
                    #     Logger.info(f"Age difference check result: {age_diff_ok}")
                    #     Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                        
                    # else:
                    #     Logger.info(f"Checking age difference for other gender profile")
                    #     age_diff_ok = age_diff <= 1 or age_diff >= 1
                    #     Logger.info(f"Age difference check result: {age_diff_ok}")
                    #     Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                        
                    # if age_diff_ok == False:
                    #     Logger.warning(f"Age difference : {age_diff} is not satisfied for profileId: {otherProfileId}")
                    #     Logger.info(f"main_profile_age: {main_profile_age} and other Age: {age}")
                    #     Logger.warning(f"Skiping the profile")
                    #     continue
                        
                    
                    
                    # height = str(cm_to_feet(height))
                    # height_ft = height.split(".")[0]+ " Ft"
                    # height_inches = height.split(".")[1][:1]+ " Inches" 
                    # final_height = height_ft + " "+ height_inches
                    
                    # if is_null_or_empty(city):
                    #     location = state
                    # elif is_null_or_empty(state):
                    #     location = city
                    # elif is_null_or_empty(city) and is_null_or_empty(state):
                    #     location = None
                    # else:
                    #     location = city+ ", "+ state
                    
                    # filling dictionary for result
                    # match_making_result["height"] = final_height
                    # match_making_result["location"] = location
                    # match_making_result["SubscribeToken"] = subscribeToken
                    # match_making_result["gunnScore"] = str(gunn_score)
                    # match_making_result["notificationMsg"] = notificationMsg
                    
                    # fetch profile picure
                #     cursorDb.execute(querys.GetProfilePictureById(otherProfileId))
                #     profile_picture_data = cursorDb.fetchone()
                #     if profile_picture_data == None:
                #         Logger.debug(f"Profile Picture data: {profile_picture_data}")
                #         match_making_result["picture"] = None
                        
                #     else:
                #         requestFileName = profile_picture_data["ProfilePicture"]
                #         if is_null_or_empty(requestFileName):
                #             if gender.lower() == "male":
                #                 requestFileName = Config.DEFAULT_PROFILE_PIC_MALE
                #             elif gender.lower() == "female":
                #                 requestFileName = Config.DEFAULT_PROFILE_PIC_FEMALE
                #             else:
                #                 requestFileName = Config.DEFAULT_PROFILE_PIC
                            
                #         Logger.debug(f"Fetched profile picture filename: {requestFileName}")
                #         profile_path = os.path.join(upload_folder, requestFileName)
                        
                #         if not os.path.exists(profile_path):
                #             Logger.warning(f"Profile Picture not found for user ID: {otherProfileId}")
                #             match_making_result["picture"] = None
                                    
                #         db.commit()
                        
                #         try:
                #             with open(profile_path, 'rb') as file:
                #                 # Read the file content and convert it into a byte array
                #                 file_content = file.read()
                #                 byte_array = bytearray(file_content)
                #                 byte_array_list = list(byte_array)
                #                 match_making_result["filename"] = requestFileName
                #                 match_making_result["picture"] = byte_array_list
                                
                #         except FileNotFoundError:
                #             Logger.error("Image not found error")
                #             match_making_result["picture"] = None
                    
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                filename, line_number, func_name, text = tb[-1]
                    
                traceback.print_exc()
                print(tb)
                db.rollback()
                Logger.error(f"Error occurred while filling object for match making: {tb}")
                Logger.error(f"Skiping data for profile Id: {otherProfileId}")
                continue
                # match_making_result["Error"] = f"Some error occurs for key: {e}"
            user_match_making_results.append(match_making_result)
            
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({'status': 'success', 'message': 'Matchmaking is Completed.', 'user_details': user_match_making_results}), 200
    
    except mysql.connector.Error as e:
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
        # closePoolConnection(db)
        Logger.info("Closing database connection")

# @Router.route('/astro', methods=['GET'])
# @cross_origin(supports_credentials=True)
# def astro():
# #    authrization =  check_request_authorized(request)
# #    if authrization == "":
#     res = AstroService()
#     matrimonial = res.get_and_insert_astrological_data(26)
#     print(matrimonial)
#     return matrimonial


@Router.route('/', methods=['GET'])
@cross_origin(supports_credentials=True)
def multipro():
    
    # tasks = MatchmakingScore().find_all_matches(26)
    # return tasks
    
    # MatchMakingService().start_match_making()
    # MappingMatchMakingService().start_mapping()
    return " SUCCESS"
    