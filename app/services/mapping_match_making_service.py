from app.extentions.machmaking_score import MatchmakingScore
from app.routes import _database, closeDbConnection
from app.extentions.logger import Logger
import json
from app.models.match_profile_model import MatchProfileModel
from app.querys.user import user_query as querys
import mysql.connector

class MappingMatchMakingService:
    def __init__(self) -> None:
        pass
    
    
    def start_mapping(self):
        
        try:
            _matching = MatchmakingScore()
            db, cursorDb = _database.get_connection()
            
            cursorDb.execute(querys.GetAllMatrimonialData())
            profileIds = cursorDb.fetchall()
            
            profileIdList = [data["ProfileId"] for data in profileIds]
            
            for profileId in profileIdList:
                cursorDb.execute(querys.GetMatchedProfiles(profileId))
                mapping_data = cursorDb.fetchall()
                temp_profileIdList = [data["ProfileId"] for data in profileIds]
                if len(mapping_data) != 0:
                    temp_profileIdList.remove(profileId)
                
                mappingProfileIdList = [data["OtherProfileId"] for data in mapping_data]
                for mappingId in mappingProfileIdList:
                    if(profileIdList.__contains__(mappingId)):
                        profileIdList.remove(mappingId)
            # for data in profileIds:
                
                print(profileId)
                
                sorted_scores_df = _matching.find_all_matches(profileId, temp_profileIdList)
                Logger.debug(f"Sorted scores data frame: {sorted_scores_df}")
                
                # # Process the results
                if len(sorted_scores_df) == 0:
                    Logger.info("Matchmaking has been already completed for this Profile")
                    return json.dumps({"status": "success", "message": "Match making has been already completed for this Profile",}), 200
                
                for match in sorted_scores_df:
                    model = MatchProfileModel.fill_model(match)
                    Logger.debug(f"Model data filled for match: {len(model.__dict__.keys())}")
                    model.mainProfileId = profileId
                    db, cursorDb = _database.get_connection() 
                    Logger.debug("Database connection created for inserting match data")
                    
                    cursorDb.execute(querys.AddMatchedProfile(), model.__dict__)
                    Logger.debug("Executed query to add matched profile")
                    
                cursorDb.execute(querys.UpdateMatchFlag(1, profileId))
                Logger.debug("Executed query to update match flag")
                
                db.commit()
                Logger.info("Match data inserted successfully")
        except mysql.connector.Error as e:
            print(e)
            Logger.error(f"JSON Decode Error: {e}")
            return json.dumps({"status": "failed", 'message': "some error occurs, in query execution"}), 400
        
        except json.JSONDecodeError as jd:
            print(jd)
            Logger.error(f"JSON Decode Error: {jd}")
            db.rollback()
            return json.dumps({"status": "failed", 'message': "Invalid data format of json"}), 400
        
        except ValueError as ve:
            print(ve)
            Logger.error(f"Value Error: {ve}")
            db.rollback()
            return json.dumps({"status": "failed", 'message': "Invalid data format"}), 400
        
        except Exception as e:
            print(e)
            Logger.error(f"Unexpected Error: {e}")
            db.rollback()
            return json.dumps({"status": "failed", "message": "some error occurs, Please contact to developer"}), 400
        
        finally:
            closeDbConnection(db, cursorDb)
            Logger.info("Closing database connection")
            
            
