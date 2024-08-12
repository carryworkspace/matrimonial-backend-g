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
import traceback

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
        
        cursorDb.execute(querys.GetQueuedMatchMakingById(profileId))
        queuedData = cursorDb.fetchall()
        
        if len(queuedData) != 0:
            Logger.info(f"Profile Id: {profileId} added in queued successfully")
            return json.dumps({"status": "success", "message": "already started"}), 200
        
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
        
        return json.dumps({"status": "success", "message": "started"}), 200
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
    db, cursorDb = createDbConnection()
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
        Logger.info("Closing database connection")


@Router.route('/match-making-result', methods=['GET'])
@cross_origin(supports_credentials=True)
def match_making_result():
    
    db, cursorDb = createDbConnection()
    user_match_making_results = []
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
            upload_folder = Config.PROFILE_PIC_PATH
            try:
                otherProfileId = match_profile["OtherProfileId"]
                cursorDb.execute(querys.GetMatrimonialData(profileId=otherProfileId))
                profile = cursorDb.fetchone()
                
                if profile == None:
                    Logger.info(f"Profile not found for profileId: {otherProfileId}")
                    continue
                
                # print("PROFILEDIEDFDFDJ:LJSDLKFJKSDLJFLKSF:", profile, otherProfileId)
                Logger.debug(f"Database query result Matrimonial: {len(profile)}")
                
                name = profile["Name"]
                gender = profile["Gender"]
                dob = profile["Dob"]
                city = profile["City"]
                subscribeToken = profile["Subscribe_Token"]
                state = profile["State"]
                height = profile["HeightCM"]
                
                if int(height) < 50:
                    height = 165
                
                dob_datetime = datetime.strptime(dob, '%Y-%m-%d')
                age = calculate_age(dob_datetime)
                
                height = str(cm_to_feet(height))
                height_ft = height.split(".")[0]+ " Ft"
                height_inches = height.split(".")[1][:1]+ " Inches" 
                final_height = height_ft + " "+ height_inches
                
                location = city+ ", "+ state
                
                # filling dictionary for result
                match_making_result["profileId"] = otherProfileId
                match_making_result["name"] = name
                match_making_result["gender"] = gender
                match_making_result["age"] = age
                match_making_result["height"] = final_height
                match_making_result["location"] = location
                match_making_result["SubscribeToken"] = subscribeToken
                
                # fetch profile picure
                cursorDb.execute(querys.GetProfilePictureById(otherProfileId))
                profile_picture_data = cursorDb.fetchone()
                if profile_picture_data == None:
                    Logger.debug(f"Profile Picture data: {profile_picture_data}")
                    match_making_result["picture"] = None
                    
                else:
                    requestFileName = profile_picture_data["ProfilePicture"]
                    Logger.debug(f"Fetched profile picture filename: {requestFileName}")
                    profile_path = os.path.join(upload_folder, requestFileName)
                    
                    if not os.path.exists(profile_path):
                        Logger.warning(f"Profile Picture not found for user ID: {otherProfileId}")
                        match_making_result["picture"] = None
                                
                    db.commit()
                    
                    try:
                        with open(profile_path, 'rb') as file:
                            # Read the file content and convert it into a byte array
                            file_content = file.read()
                            byte_array = bytearray(file_content)
                            byte_array_list = list(byte_array)
                            match_making_result["picture"] = byte_array_list
                            match_making_result["filename"] = requestFileName
                            
                    except FileNotFoundError:
                        Logger.error("Image not found error")
                        match_making_result["picture"] = None
                
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                filename, line_number, func_name, text = tb[-1]
                    
                traceback.print_exc()
                print(tb)
                db.rollback()
                Logger.error(f"Error occurred while filling object for match making: {e}")
                match_making_result["Error"] = f"Some error occurs for key: {e}"
            print("***************", match_making_result)
            user_match_making_results.append(match_making_result)
            print("F*********FFF*FF", user_match_making_results)
            
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
        Logger.info("Closing database connection")
        

@Router.route('/download-bio-data', methods=['GET'])
@cross_origin(supports_credentials=True)
def download_pdf():
    # doing someting else will continue after some time
    db, cursorDb = createDbConnection()
    user_match_making_results = []
    bio_data_pdf_result = {}
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
            return json.dumps({'status': 'success', 'message': 'pdf not found for the profile_id', 'pdf_file': None}), 200
            
            
        
    
        return json.dumps({'status': 'success', 'message': 'pdf not found for the profile_id', 'pdf_file': None}), 200
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
    