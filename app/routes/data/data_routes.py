import os
from flask import request
from app.extentions.common_extensions import *
from app.extentions.otp_extentions import *
from app.routes import Router, closeDbConnection, closePoolConnection, _database
from flask_cors import cross_origin
import mysql.connector
from app.extentions.logger import Logger
import traceback
from app.querys.data import data_querys 
from app.models.user_stage_model import UserStageModel

@Router.route('/gotras', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_gotras():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    # data = request.get_json()  # Get JSON data from request body
    # _matching = MatchmakingScore()
    Logger.debug("Database connection obtained from _matching")
    try:
        Logger.info("Starting get_gotras function")
        query = data_querys.GetGotras()
        cursorDb.execute(query)
        gotras_data = cursorDb.fetchall()
        gotras_data_list = [gotra['Gotra'] for gotra in gotras_data]
        Logger.info(f"Gotras: {gotras_data_list}")
        
        db.commit()
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({"status": "success", "message": "retrived data successfully", "gotra": gotras_data_list}), 200
        # return json.dumps(sorted_scores_df)
    
    except mysql.connector.Error as e:
        Logger.error(f"JSON Decode Error: {e}")
            # print(f"Error: {e} This is Erorr")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    except json.JSONDecodeError as jd:
        Logger.error(f"JSON Decode Error: {jd}")
        #print("JSONERROR:",jd)
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format of json"}), 400
    
    except ValueError as ve:
        Logger.error(f"Value Error: {ve}")
        #print(ve)
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        #print(f"Error: {e}")
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        # closeDbConnection(db, cursorDb)
        # closePoolConnection(db)
        Logger.info("Closing database connection")
        

@Router.route('/sub-caste', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_subcaste():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    # data = request.get_json()  # Get JSON data from request body
    # _matching = MatchmakingScore()
    Logger.debug("Database connection obtained from _matching")
    try:
        Logger.info("Starting get_sub_castes function")
        query = data_querys.GetSubCastes()
        cursorDb.execute(query)
        subcaste_data = cursorDb.fetchall()
        subcaste_data_list = [subcaste['SubCaste'] for subcaste in subcaste_data]
        Logger.info(f"Subcastes: {subcaste_data_list}")
        
        db.commit()
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({"status": "success", "message": "gotras_data", "subCaste":subcaste_data_list}), 200
        # return json.dumps(sorted_scores_df)
    
    except mysql.connector.Error as e:
        Logger.error(f"JSON Decode Error: {e}")
            # print(f"Error: {e} This is Erorr")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    except json.JSONDecodeError as jd:
        Logger.error(f"JSON Decode Error: {jd}")
        #print("JSONERROR:",jd)
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format of json"}), 400
    
    except ValueError as ve:
        Logger.error(f"Value Error: {ve}")
        #print(ve)
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        #print(f"Error: {e}")
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        # closePoolConnection(db)
        Logger.info("Closing database connection")
        
        
@Router.route('/general-data', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_general_data():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    result_data_dict = {}
    # data = request.get_json()  # Get JSON data from request body
    # _matching = MatchmakingScore()
    Logger.debug("Database connection obtained from _matching")
    try:
        Logger.info("Starting get_sub_castes function")
        query = data_querys.GetSubCastes()
        cursorDb.execute(query)
        subcaste_data = cursorDb.fetchall()
        subcaste_data_list = [subcaste['SubCaste'] for subcaste in subcaste_data]
        Logger.info(f"Subcastes: {subcaste_data_list}")
        result_data_dict["subCaste"] = subcaste_data_list
        
        Logger.info("Starting get_gotras function")
        query = data_querys.GetGotras()
        cursorDb.execute(query)
        gotras_data = cursorDb.fetchall()
        gotras_data_list = [gotra['Gotra'] for gotra in gotras_data]
        Logger.info(f"Gotras: {gotras_data_list}")
        result_data_dict["gotra"] = gotras_data_list
        
        Logger.info("Starting get_occupation function")
        query = data_querys.GetOccupation()
        cursorDb.execute(query)
        occupation_data = cursorDb.fetchall()
        occupation_data_list = [occupation['Occupation'] for occupation in occupation_data]
        Logger.info(f"Occupation: {occupation_data_list}")
        result_data_dict["occupation"] = occupation_data_list
        
        Logger.info("Starting get_hobbies function")
        query = data_querys.GetHobbies()
        cursorDb.execute(query)
        hobbies_data = cursorDb.fetchall()
        hobbies_data_list = [hobby['Hobbie'] for hobby in hobbies_data]
        Logger.info(f"Hobbies: {hobbies_data_list}")
        result_data_dict["hobbies"] = hobbies_data_list
        
        db.commit()
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({"status": "success", "message": "data fetch successfully", "generalData":result_data_dict}), 200
        # return json.dumps(sorted_scores_df)
    
    except mysql.connector.Error as e:
        Logger.error(f"JSON Decode Error: {e}")
            # print(f"Error: {e} This is Erorr")
        return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
    except json.JSONDecodeError as jd:
        Logger.error(f"JSON Decode Error: {jd}")
        #print("JSONERROR:",jd)
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format of json"}), 400
    
    except ValueError as ve:
        Logger.error(f"Value Error: {ve}")
        #print(ve)
        db.rollback()
        return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
    
    except Exception as e:
        #print(f"Error: {e}")
        Logger.error(f"Unexpected Error: {e}")
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        closeDbConnection(db, cursorDb)
        # closePoolConnection(db)
        Logger.info("Closing database connection")
    

@Router.route('/user-stages', methods=['POST'])
@cross_origin(supports_credentials=True)
def insert_or_update_stage():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    data = request.get_json()
    Logger.info("Received data")
    
    try:
        Logger.info("Checking for missing keys in the input data.")
        # Check if all expected keys are present
        attributes = UserStageModel().get_attribute_names()
        missing_keys = check_missing_keys(data, attributes)
        if missing_keys != None:
            Logger.info(f"Missing keys in request data: {missing_keys}")
            return missing_keys
        
        model = UserStageModel.fill_model(data)
        Logger.info(f"Checking if profile with ID {model.profileId} exists.")
        
        cursorDb.execute(data_querys.GetStage(model.profileId))
        profile = cursorDb.fetchall()
        if len(profile) != 0:
            Logger.info("Stage profile exists, updating the profile.")
            cursorDb.execute(data_querys.UpdateStage(model.profileId, model.registrationStage))
            db.commit()
            return json.dumps({"status": "success", "message": "Updating Stage"}), 200
        
        Logger.info("Stage profile Created")
        cursorDb.execute(data_querys.InsertDataStage(), model.__dict__)
        Logger.info("profile created successfully.")
        db.commit()
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({"status":"success", "message": "Profile Created Successfully"}), 200
        
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
        db.rollback()
        return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
    finally:
        Logger.info("Closing database connection.")
        # closePoolConnection(db)
        closeDbConnection(db, cursorDb)
        
        

# profile picture fetch
@Router.route('/get-stage', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_stage():
    Logger.warning(f"*********************** Start Processing For Endpoint: {request.endpoint} *********************** ")
    db, cursorDb = _database.get_connection()
    Logger.debug("Database connection established.")
    try:
        # Check if all expected keys are present
        profileId :int = 0
        try:
            profileId = int(request.args["profileId"])
        except Exception as ex:
            profileId = 0
            Logger.error(f"Error parsing profileId from request arguments: {ex}")
            
        if profileId == 0:
            Logger.info("User ID not specified or invalid.")
            return json.dumps({"status": "failed", "message":'User not specified or profileId not provided'}), 400
        
        cursorDb.execute(data_querys.GetStage(profileId))
        profile_data = cursorDb.fetchall()
        
        if len(profile_data) == 0:
            Logger.info(f"Profile ID does not exist in database: {profileId} for stages data")
            return json.dumps({"status": "failed", "message": "ProfileId ID does not exist in database stages table"})
        
        stage = profile_data[0]["Stage"]
        Logger.info(f"Profile picture retrieved successfully for userId: {profileId}")
        Logger.success(f"************************** Processed Request : {request.endpoint} Success! **************************")
        return json.dumps({'status': 'success', 'message': 'found user stage', 'registrationStage': stage}), 200
        
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
        # closePoolConnection(db)
        Logger.debug("Database connection closed.")