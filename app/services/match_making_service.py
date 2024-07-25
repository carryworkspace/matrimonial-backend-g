from app.extentions.machmaking_score import MatchmakingScore
from app.routes import createDbConnection, closeDbConnection
from app.extentions.logger import Logger
import json
from app.models.match_profile_model import MatchProfileModel
from app.querys.user import user_query as querys
import mysql.connector

class MatchMakingService:
    def __init__(self) -> None:
        pass
    
    
    def start_match_making(self):
        
        try:
            _matching = MatchmakingScore()
            db, cursorDb = createDbConnection()
            
            cursorDb.execute(querys.GetAllQueuedMatchMaking())
            profileIds = cursorDb.fetchall()
            
            for data in profileIds:
                profileId = data["ProfileId"]
                print(profileId)
                
                cursorDb.execute(querys.UpdateMatchQueuedFlag(matched_flag=0, profileId=profileId, processing_flag=1))
                db.commit()
                sorted_scores_df = _matching.find_all_matches(profileId)
                Logger.debug(f"Sorted scores data frame: {sorted_scores_df}")
                
                # # Process the results
                if len(sorted_scores_df) == 0:
                    Logger.info("Matchmaking has been already completed for this Profile")
                    return json.dumps({"status": "success", "message": "Match making has been already completed for this Profile",}), 200
                
                for match in sorted_scores_df:
                    model = MatchProfileModel.fill_model(match)
                    Logger.debug(f"Model data filled for match: {len(model.__dict__.keys())}")
                    model.mainProfileId = profileId
                    db, cursorDb = createDbConnection() 
                    Logger.debug("Database connection created for inserting match data")
                    
                    cursorDb.execute(querys.AddMatchedProfile(), model.__dict__)
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
            db.rollback()
            return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
        
        finally:
            closeDbConnection(db, cursorDb)
            Logger.info("Closing database connection")
            
            
