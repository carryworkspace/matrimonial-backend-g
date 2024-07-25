import os
from flask import request, jsonify
from app.extentions.common_extensions import *
from app.extentions.otp_extentions import *
from app.extentions.machmaking_score import MatchmakingScore
from app.routes import createDbConnection, Router, closeDbConnection
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

@Router.route('/matchmaking', methods=['GET'])
@cross_origin(supports_credentials=True)
def perform_matchmaking():
    
    db, cursorDb = createDbConnection()
    # data = request.get_json()  # Get JSON data from request body
    # _matching = MatchmakingScore()
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
        
        cursorDb.execute(querys.AddMatchMakingQueued(profileId))
        # Call the main method of MatchmakingScore to perform matchmaking
        # sorted_scores_df = _matching.find_all_matches(profileId)
        # # print(sorted_scores_df)
        # Logger.debug(f"Sorted scores data frame: {sorted_scores_df}")
        
        # # # Process the results
        # if len(sorted_scores_df) == 0:
        #     Logger.info("Matchmaking has been already completed for this Profile")
        #     return jsonify({"status": "success", "message": "Match making has been already completed for this Profile"}), 200
        
        # for match in sorted_scores_df:
        #     model = MatchProfileModel.fill_model(match)
        #     Logger.debug(f"Model data filled for match: {len(model.__dict__.keys())}")
        #     # print(model.__dict__)
        #     model.mainProfileId = profileId
        #     db, cursorDb = createDbConnection() 
        #     Logger.debug("Database connection created for inserting match data")
            
        #     cursorDb.execute(querys.AddMatchedProfile(), model.__dict__)
        #     Logger.debug("Executed query to add matched profile")
            
        # cursorDb.execute(querys.UpdateMatchFlag(1, profileId))
        # Logger.debug("Executed query to update match flag")
        
        db.commit()
        Logger.info(f"profileId: {profileId} inserted successfully to queued match making table")
        
        return json.dumps({"status": "success", "message": "match making in process"}), 200
        # return json.dumps(sorted_scores_df)
    
    except mysql.connector.Error as e:
        Logger.error(f"JSON Decode Error: {jd}")
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
        Logger.info("Closing database connection")

@Router.route('/match-making-status', methods=['GET'])
@cross_origin(supports_credentials=True)
def match_making_status():
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
        db, cursorDb = createDbConnection()
        Logger.debug("Database connection established")
        cursorDb.execute(querys.GetMatchMakingCompleteNotification(profileId=profileId))
        Logger.debug(f"Executed database query to check matchmaking status for profileId: {profileId}")
        user_exists = cursorDb.fetchall()
        Logger.debug(f"Database query result: {len(user_exists)}")
        
        # name = user_exists[0]["Name"]
        # dob = user_exists[0]["Dob"]
        # city = user_exists[0]["City"]
        # state = user_exists[0]["State"]
        # height = user_exists[0]["HeightCM"]
        
        # dob_date = datetime.strptime(dob, '%Y-%m-%d')
        # age = calculate_age(dob_date)
        # height = str(cm_to_feet(height))
        # height_ft = height.split(".")[0]+ " Ft"
        # height_inches = height.split(".")[1][:1]+ " Inches"
        # location = city+ ", "+ state
        
        # height_str = height_ft + " "+ height_inches
        # print(height_ft, height_inches, name)
        
        
        if len(user_exists) == 0:
            return json.dumps({"status": "success", "message": "pending", 'profileId': profileId}), 200
        return json.dumps({'status': 'success', 'message': 'complete', 'profileId': profileId}), 200
    
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
    