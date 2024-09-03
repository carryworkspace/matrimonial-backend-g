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
from app.querys.data import data_querys 

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

