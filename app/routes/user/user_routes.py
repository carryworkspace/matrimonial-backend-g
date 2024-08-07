import time
import os
from datetime import datetime
import json
import mysql.connector
from flask import jsonify, request
from flask_cors import cross_origin
from werkzeug.utils import secure_filename

# Assuming these are in a package one level up
from app.routes import createDbConnection, Router, closeDbConnection
from app.querys.user import user_query
from app.extentions.common_extensions import *
from app.extentions.otp_extentions import *
from app.extentions.chatgpt import Chatgpt
from app.extentions.pdf_extractor import PdfExtracter
from app.extentions.common_extensions import users_otp
from app.services.bio_data_extraction import GoogleDrive
from app.extentions.base import info
# from app.extentions.logger import Logger 
import traceback
from app.models.update_matrimonial_profile_model import UpdateMatrimonialProfileModel
from app.models.matrimonial_profile_model import MatrimonialProfileModel

# check  token before login
@Router.before_request
def authorize_request():
    """Verifying each request to be authrized
    """
    if 'request_otp' not in request.endpoint and 'verify_otp' not in request.endpoint:  # Exclude the 'login' endpoint from authorization check
        Logger.info("Checking request for authorization")
        # error_response = check_request_authorized(request)
        # if error_response:
            # return error_response

# verify the otp
@Router.route('/verify-otp', methods=['POST'])
@cross_origin(supports_credentials=True)
def verify_otp():
    """verify user phone number

    Returns:
        _type_: _json_string_
    """
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    data = request.get_json()
    Logger.debug(f"Received JSON data: {data}")
    try:
        phone = validate_data(data, 'phone')
        if phone != None:
            return phone
        Logger.debug(f"Received JSON data: {data}")
        # otp = validate_data(data, 'otp')
        # if otp != None:
        #     return otp
        
        phone = int(data['phone'])
        Logger.info(f"Phone number received: {phone}")
        # otp = int(data['otp'])

    except Exception as ve:
        Logger.error(f"ValueError: {ve}")
        return json.dumps({"status": "failed", 'message': "Error while parsing phone and otp"}), 400

    if is_null_or_empty(phone):
        Logger.info(f"Phone number not received: {phone}")
        return json.dumps({"status": "failed", 'message': "phone number cannot be null or empty"}), 400
    
    # if is_null_or_empty(otp):
    #     return json.dumps({"status": "failed", 'message': "otp cannot be null or empty"}), 400

    # try:
    #     print(users_otp)
    #     if phone not in users_otp or users_otp.get(phone) != otp:
    #         return jsonify({"status": "failed", 'message': 'Invalid OTP'}), 403

    # except Exception as e:
    #     print(f"Error: {e}")
    #     return json.dumps({"status": "failed", 'message': "some error while getting otp, Please contact to developerr"}), 400
    
    try:
        cursorDb.execute(user_query.CheckUserPhoneExist(phone))
        userDetails = cursorDb.fetchall()
        if(len(userDetails)==0):
            username = get_random_name(phone)
            insert_user_query = user_query.AddUser(username, phone, 'null', 'null', 'null')
            cursorDb.execute(insert_user_query)
            new_user_id = cursorDb.lastrowid
            cursorDb.execute(user_query.AddProfileForUser(new_user_id))
            new_profile_id = cursorDb.lastrowid
            token = encode_auth_token(phone)
            # del users_otp[phone]
            db.commit()
            Logger.info(f"Sending response data")
            return json.dumps({'status': "success", "token": token, "username": username, "userId": new_user_id, "profileId": new_profile_id, "message": "User created successfully", "created": True}), 200
        
        else:

            username = userDetails[0]["Username"]
            old_user_id = userDetails[0]["Id"]
            cursorDb.execute(user_query.GetProfileDetails(old_user_id))
            oldProfileId = cursorDb.fetchall()[0]['Id']
            token = encode_auth_token(phone)
            # del users_otp[phone]
            db.commit()
            Logger.info("User already exists.")
            return json.dumps({'status': "success", "token": token, "username": username, "userId": old_user_id, "profileId": oldProfileId, "message": "User already exist",  "created": False}), 200
        
    except mysql.connector.Error as e: 
            Logger.error(f"Database DataError: {e}")
            db.rollback()
            return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"ValueError: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    except KeyError as key:
        Logger.error(f"KeyError: {key}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "no otp found for this user. Please send otp first"}), 400
    except Exception as e:
        Logger.error(f"Unexpected error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    
    finally:
        closeDbConnection(db, cursorDb)
        Logger.debug("Database connection closed.")
        Logger.info("verify_otp function execution completed.")


# request for otp
@Router.route('/request-otp', methods=['POST'])
@cross_origin(supports_credentials=True)
def request_otp():
    data = request.get_json()
    Logger.debug(f"Received JSON data: {data}")
    try:
        validation = validate_data(data, 'phone')
        Logger.debug(f"Validation result for phone number: {validation}")
        Logger.info("Phone number validation successful")
        if validation != None:
            Logger.info("Validation failed for phone number")
            return validation
        
        phone = int(data['phone'])
        Logger.info(f"Phone number validated: {phone}")
        validation = validate_phone_number(phone)
        Logger.info("Validation Successful")
        if validation != None:
            Logger.info("Phone number validation failed")
            return validation
        
        otp = generate_otp()
        users_otp[phone] = otp
        Logger.info(f"Generated OTP ({otp}) for phone: {phone}")
        # send_otp(phone, otp)
        # print("OTP:", users_otp)
        Logger.info(f"OTP sent successfully to phone: {phone}")
        return json.dumps({'status': "success", "message": "Otp send successfully"}), 200
        
    except Exception as e:
        Logger.error(f"Error occurred: {e}")
        return json.dumps({"status": "failed", "message": "some error occurs. Please contact to the developer"}), 400
    
# google auth
@Router.route('/google-auth', methods=['POST'])
@cross_origin(supports_credentials=True)
def google_auth():
    db, cursorDb = createDbConnection()
    data = request.get_json()
    Logger.debug(f"Received JSON data: {data}")
    try:
        emailError = validate_string_data(data, 'email')
        if emailError != None:
            Logger.error(f"Validation failed for email: {emailError}")
            return emailError
        
        # otp = validate_data(data, 'otp')
        # if otp != None:
        #     return otp
        
        email: str = data['email']
        Logger.info(f"Email validated: {email}")
        # authToken = data['googleAuthToken']

    except Exception as e:
        Logger.error(f"Error occurred during initial validation: {e}")
        try:
            return json.dumps({"status": "failed", 'message': str(e)}), 400
        except Exception as e:
            Logger.error(f"Error occured: {e}")
            return json.dumps({"status": "failed", 'message': "some error ocurs. Please contact to developer"}), 400

    if is_null_or_empty(email):
        Logger.error("Email is null or empty")
        return json.dumps({"status": "failed", 'message': "Email cannot be null or empty"}), 400
    
    try:
        cursorDb.execute(user_query.CheckUserEmailExist(email))
        userDetails = cursorDb.fetchall()
        if(len(userDetails)==0):
            username = get_random_name(email.split("@")[0])
            insert_user_query = user_query.AddUser(username, 'null', 'null', 'null', email)
            Logger.info(f"Inserting new user with query: {insert_user_query}")
            cursorDb.execute(insert_user_query)
            new_user_id = cursorDb.lastrowid
            cursorDb.execute(user_query.AddProfileForUser(new_user_id))
            new_profile_id = cursorDb.lastrowid
            token = encode_auth_token(email)
            # del users_otp[phone]
            db.commit()
            Logger.info(f"New user created successfully. User ID: {new_user_id}")
            return json.dumps({'status': "success", "token": token, "username": username, "userId": new_user_id, "profileId": new_profile_id, "message": "User created successfully", "created": True}), 200
        
        else:

            username = userDetails[0]["Username"]
            oldUserId = userDetails[0]["Id"]
            cursorDb.execute(user_query.GetProfileDetails(oldUserId))
            oldProfileId = cursorDb.fetchall()[0]['Id']
            token = encode_auth_token(email)
            # del users_otp[phone]
            db.commit()
            # tb = traceback.extract_tb(e.__traceback__)
            # filename, line_number, func_name, text = tb[-1]
            # traceback.print_exc()
            # Logger.info(f"User already exists. User ID: {oldUserId}, Profile ID: {oldProfileId}")
            return json.dumps({'status': "success", "token": token, "username": username, "userId": oldUserId, "profileId": oldProfileId, "message": "User already exist",  "created": False}), 200
            
        
    except mysql.connector.Error as e: 
            Logger.error(f"MySQL Error: {e}")
            db.rollback()
            return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"ValueError: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    except KeyError as key:
        Logger.error(f"KeyError: {key}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "no otp found for this user. Please send otp first"})
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        filename, line_number, func_name, text = tb[-1]
        traceback.print_exc()
        
        print(f"Error: {e}")
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    
    finally:
        closeDbConnection(db, cursorDb)
        Logger.info("Database connection closed")

# uplaod bio data
@Router.route('/upload-biodata', methods=['POST'])
@cross_origin(supports_credentials=True)
def bio_data():
    root = get_project_root()
    upload_folder = Config.BIO_DATA_PDF_PATH
    Logger.debug(f"Project root: {root}")
    Logger.debug(f"Upload folder: {upload_folder}")
    db, cursorDb = createDbConnection()
    Logger.debug("Database connection established.")
    profileId :int = 0
    try:
        profileId = int(request.form["profileId"])
        Logger.info(f"Profile ID parsed successfully: {profileId}")
    except Exception as pe:
        Logger.error(f"Error parsing profileId: {pe}")
        profileId = 0

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        Logger.info(f"Created upload folder: {upload_folder}")
        
    if 'file' not in request.files:
        Logger.error("No file part in request")
        return json.dumps({"status": "failed", "message":'No file part'}), 400

    if profileId == 0:
        Logger.error("User not specified or user id not provided")
        return json.dumps({"status": "failed", "message":'User not specified or user id not provided'}), 400
    
    if 'file' in request.files:
        file = request.files['file']

    elif 'file' in request.form:
        file = request.form['file']

        # decoded_data = base64.b64decode(file_data)
        # new_file = File(name=file_name, data=decoded_data)

    try:
        requestFileName = str(profileId)+ "_" + str(generate_random_number()) + "_" +file.filename

        file.save(os.path.join(upload_folder, requestFileName))
        Logger.info(f"File uploaded successfully: {requestFileName}")
        return json.dumps({"status": "success", "message": "File uploaded successfully", "filename": requestFileName}), 200

    except Exception as e:
        Logger.error(f"Error occurred: {e}")
        db.rollback()
        try:
            return json.dumps({"status": "failed", 'message': str(e)}), 400
        except Exception as je:
            Logger.error(f"JSON encoding error: {je}")
            return json.dumps({"status": "failed", 'message': "some error ocuurs. Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.info("Database connection closed")

@Router.route('/photo-gallery', methods=['POST'])
@cross_origin(supports_credentials=True)
def photo_gallery():
    Upload_Folder = Config.PHOTO_GALLERY_PATH
    if not os.path.exists(Upload_Folder):
        os.makedirs(Upload_Folder)
        Logger.info(f"Created upload folder: {Upload_Folder}")

    userId = 0
    db, cursorDb = createDbConnection()

    # if userId == 0:
    #     return 'User not specified', 400
    
    try:
        uploaded_files = request.files.getlist('files')
        for file in uploaded_files:
            if file.filename == '':
                continue
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(Upload_Folder, filename)
                file.save(file_path)
                Logger.info(f"File uploaded successfully: {filename}")
                return json.dumps({"status": "failed", "message": "File uploaded successfully"}), 200
    except Exception as e:
        Logger.error(f"Error uploading file: {e}")
        return json.dumps({"status": "failed", "message": "some errror occurs"}), 400

@Router.route('/user-details', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_user_details():

    db, cursorDb = createDbConnection()
    Logger.debug("Database connection")
    upload_folder = Config.PROFILE_PIC_PATH
    try:
        # Check if all expected keys are present
        userId :int = 0
        try:
            userId = int(request.args["userId"])
            Logger.info(f"User ID parsed successfully: {userId}")
        except Exception as ex:
            Logger.error("UserId Not given")
            userId = 0

        if userId == 0:
            Logger.warning("User ID not provided or invalid")
            return json.dumps({"status": "failed", "message":'User not specified or user id not provided'}), 400
        
        cursorDb.execute(user_query.GetUserDetails(userId))

        userDetails = cursorDb.fetchall()
        Logger.info("User Details Fetched")

        if len(userDetails) == 0:
            Logger.warning(f"User with ID {userId} not found")
            return json.dumps({"status": "failed", "message": "User not found"}), 404
        
        username = userDetails[0]["Username"]
        email = userDetails[0]["Email"]
        
        cursorDb.execute(user_query.GetProfileDetails(userId))
        userDetails = cursorDb.fetchall()
        
        profileId = userDetails[0]["Id"]
        
        cursorDb.execute(user_query.GetMatrimonialData(profileId))
        matrimonial_details = cursorDb.fetchone()
        subscribe_Token = matrimonial_details['Subscribe_Token']
        name = matrimonial_details['Name']
        sub_caste = matrimonial_details['SubCaste']
        weight = matrimonial_details['WeightKG']
        height = matrimonial_details['HeightCM']
        address = matrimonial_details['Address']
        about_me = matrimonial_details['AboutMe']
        gender = matrimonial_details['Gender']
        dob = matrimonial_details['Dob']
        marital_status = matrimonial_details['MaritalStatus']
        email = matrimonial_details['Email']
        education = matrimonial_details['HighestDegree']
        
        dob_datetime = datetime.datetime.strptime(dob, '%Y-%m-%d')
        age = calculate_age(dob_datetime)
        
        # h 
        
        
        try:
            phoneNumber: int = int(userDetails[0]["PhoneNumber"])
            Logger.warning(f"Phone Number: {phoneNumber}")
        except Exception as e:
            Logger.error("Value Error Phone Number not Available in user details")
            Logger.warning(f"Phone Number IN Matrimonial: {matrimonial_details['PhoneNumber']}")
            
            phoneNumber: int = int(matrimonial_details['PhoneNumber'])
            Logger.warning(f"Phone Number: {phoneNumber}")
            
        db.commit()
        Logger.info(f"User details retrieved successfully for UserID: {userId}")
        Logger.debug(f"username: {username} | matri_name: {name} | phoneNumber: {phoneNumber} | email: {email} | sub_caste: {sub_caste} | weight: {weight} | height: {height} | address: {address} | about_me: {about_me} | subscribe_token: {subscribe_Token}")
        return json.dumps({"status": "success", "username": username, "matri_name": name, "age": age, "phoneNumber" : phoneNumber, "email": email,"gender": gender, "dob": dob , "marital_status": marital_status,"sub_caste": sub_caste, "weight": weight, "height": height,"education": education ,"address": address, "about_me": about_me, "subscribe_token": subscribe_Token}), 200
        
    except mysql.connector.Error as e: 
            Logger.error(f"MySQL Error: {e}")
            return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"ValueError: {ve}")
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        traceback.print_exc()
        Logger.error(f"Unexpected Error: {tb}")
        print(tb)
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        Logger.info("Database connection closed")

@Router.route('/edit-user-details', methods=['POST'])
@cross_origin(supports_credentials=True)
def update_matrimonial_profile():
    Logger.info("Creating database connection.")
    db, cursorDb = createDbConnection()
    data = request.get_json()
    Logger.info("Received data")
    try:
        # Logger.info("Checking for missing keys in the input data.")
        # Check if all expected keys are present
        # exclude = ['aboutMe']
        # attributes = UpdateMatrimonialProfileModel().get_attribute_names()
        # missing_keys = check_missing_keys(data, attributes)
        # if missing_keys != None:
        #     Logger.warning("Missing keys found in the input data")
        #     return missing_keys
        Logger.info("Filling the model with input data.")
        
        model = UpdateMatrimonialProfileModel.fill_model(data)
        print("DATA", model.__dict__)
        Logger.info(f"Checking if profile with ID {model.profileId} exists.")
        cursorDb.execute(user_query.GetProfileDetailsById(model.profileId))
        profiles = cursorDb.fetchall()
        if len(profiles) == 0:
            Logger.warning(f"Profile ID {model.profileId} is invalid.")
            return json.dumps({"status": "failed", "message": "Profile Id Invalid. This profile id not exist"})
        
        Logger.info(f"Checking if matrimonial profile with profile ID {model.profileId} exists.")
        
        cursorDb.execute(user_query.GetMatrimonialProfileByProfileId(model.profileId))
        matrimonial_profile = cursorDb.fetchall()
        if len(matrimonial_profile) != 0:
            print("PROFILES", matrimonial_profile)
            Logger.info("Matrimonial profile exists, updating the profile.")
            cursorDb.execute(user_query.UpdateMatrimonialUserDetails(), model.__dict__)
            print("ROW AFFECT")
            db.commit()
            
            return json.dumps({"status": "success", "message": "User Details Data Updated Successfully"})
        Logger.info("User Details Profile Not Exsist Successfully")
        db.commit()
        return json.dumps({"status":"failed", "message": "This profile id does not exists"}), 400
        
    except mysql.connector.Error as e: 
            Logger.error(f"MySQL Error: {e}")
            print("ERROR SQL")
            return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    
    except ValueError as ve:
        Logger.error(f"ValueError: {ve}")
        print("ERROR Value")
        
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        traceback.print_exc()
        Logger.error(f"Unexpected Error: {tb}")
        print(tb)
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        Logger.info("Closing database connection.")
        closeDbConnection(db, cursorDb)



# this section take pdf and extract text from the pdf
@Router.route('/chatgpt', methods=['GET'])
@cross_origin(supports_credentials=True)
def chatgpt_api():
    response = chatgpt_pdf_to_json("D:\\Ayushi Biodata.pdf")
    # response = chatgpt_pdf_to_json("D:\\Ayushi Biodata.pdf")
    return response


@Router.route('/authorization', methods=['GET'])
@cross_origin(supports_credentials=True)
def authorization_check():
#    authrization =  check_request_authorized(request)
#    if authrization == "":
    drive = GoogleDrive().extract_and_add_to_DB_MAIN()
    time.sleep(1)
    return drive
#    else:
        # return authrization