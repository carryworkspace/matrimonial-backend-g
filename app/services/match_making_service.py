from app.extentions.machmaking_score import MatchmakingScore
from app.routes import createDbConnection, closeDbConnection
from app.extentions.logger import Logger
import json
from app.models.match_profile_model import MatchProfileModel
from app.querys.user import user_query as querys
import mysql.connector
import traceback
import time

class MatchMakingService:
    def __init__(self) -> None:
        pass
    
    
    def start_match_making(self):
        
        try:
            _matching = MatchmakingScore()
            db, cursorDb = createDbConnection()
            Logger.info(f"*************** Starting Matchmaking Service ****************")
            
            cursorDb.execute(querys.GetAllQueuedMatchMaking())
            profileIds = cursorDb.fetchall()
            Logger.info(f"Total Queued For Matchmaking: {len(profileIds)}")
            
            for data in profileIds:
                profileId = data["ProfileId"]
                print(profileId)
                
                cursorDb.execute(querys.UpdateMatchQueuedFlag(matched_flag=0, profileId=profileId, processing_flag=1))
                db.commit()
                sorted_scores_df = _matching.find_all_matches(profileId)
                Logger.debug(f"Sorted scores data frame: {sorted_scores_df}")
                
                # # Process the results
                if len(sorted_scores_df) == 0:
                    Logger.info("Matchmaking has been already completed for this Profile  or does not have opposite gender data.")
                    # return json.dumps({"status": "success", "message": "Match making has been already completed for this Profile or does not have opposite gender data.",}), 200
                    continue
                
                db, cursorDb = createDbConnection() 
                Logger.debug("Database connection created for inserting match data")
                for match in sorted_scores_df:
                    model = MatchProfileModel.fill_model(match)
                    model.mainProfileId = profileId
                    Logger.debug(f"Model data filled for match count: {len(model.__dict__.keys())} with score of : {model.matchScore} and MainProfile: {model.mainProfileId} and Other Profile: {model.profileId}")
                    
                    if model.matchScore == 0:
                        Logger.warning(f"Match score is 0, skipping this match for ProfileId: {model.profileId}")
                        continue
                    cursorDb.execute(querys.AddMatchedProfile(), model.__dict__)
                    db.commit()
                    Logger.debug("Executed query to add matched profile")
                    
                cursorDb.execute(querys.UpdateMatchFlag(1, profileId))
                cursorDb.execute(querys.UpdateMatchQueuedFlag(1, profileId))
                Logger.debug("Executed query to update match flag")
                
                db.commit()
                Logger.info("Match data inserted successfully")
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
            tb = traceback.extract_tb(e.__traceback__)
            traceback.print_exc()
            Logger.error(f"Unexpected Error trackback: {tb}")
            print(tb)
            db.rollback()
            return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
        
        finally:
            closeDbConnection(db, cursorDb)
            Logger.info("Closing database connection")
            Logger.info(f"*************** Finished Matchmaking ****************")
            
    def sleep_timer(self, total_time=30, interval=2):
        start_time = time.time()
        end_time = start_time + total_time

        while time.time() < end_time:
            current_time = time.time()
            remaining_time = end_time - current_time
            if remaining_time <= 0:
                break
            Logger.warning(f"Match Making Service will starts again in: {int(remaining_time)} seconds")
            # Logger.warning(f"Time left: {int(remaining_time)} seconds")
            time.sleep(interval)
    
    def start_service(self):
        while True:
            self.start_match_making()
            sleepTime = 60 * 10
            self.sleep_timer(total_time=sleepTime)
            
