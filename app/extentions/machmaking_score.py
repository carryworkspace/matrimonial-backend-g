import pandas as pd
from app.routes import createDbConnection, closeDbConnection
from app.extentions.common_extensions import feet_to_cm, is_null_or_empty, split_list
import json
from app.extentions.chatgpt import Chatgpt
from app.services.astrology_data_service import AstroService
from app.models.astrological_model import AstrologicalDataModel
from app.extentions.logger import Logger
from config import Config
from app.extentions.multiprocess import MultiProcess
import traceback
import time
from app.querys.user import user_query as querys

class MatchmakingScore:
    def __init__(self):
        pass
        # self.conn, self.cursor = createDbConnection()

    def get_user_preferences(self, profile_id):
        conn, cursor = createDbConnection()
        Logger.info("Starting get_user_preferences method")
        query = f"SELECT * FROM Profiles_M WHERE Id = {profile_id}"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        #columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        Logger.debug(f"Columns retrieved")
        closeDbConnection(conn, cursor)
        return result
    
    def get_main_matrimonial_data(self, profile_id):
        conn, cursor = createDbConnection()
        Logger.info("Starting get_user_preferences method")
        query = f"SELECT * FROM MatrimonialProfile_M WHERE ProfileId = {profile_id} and matching_flag = 0"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        closeDbConnection(conn, cursor)
        return result
    
    def check_matchmaking_done_already(self, profile_id):
        conn, cursor = createDbConnection()
        Logger.info("Starting match making completed data")
        query = f"SELECT * FROM MatrimonialProfile_M WHERE ProfileId = {profile_id} and matching_flag = 1"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        closeDbConnection(conn, cursor)
        return result
    
    def get_other_matrimonial_data_opposite_gender(self, user_gender: str, profile_id):
        conn, cursor = createDbConnection()
        Logger.info("Starting get_other_matrimonial_data_opposite_gender method")
        user_gender = user_gender[0]
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId != {profile_id};"
        else:
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId != {profile_id};"
        Logger.debug(f"Generated SQL query: {query}")
        
        cursor.execute(query)
        Logger.debug("Executed SQL query")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        closeDbConnection(conn, cursor)
        return result
    
    def get_other_matrimonial_data_for_ids(self, user_gender: str, profileIds):
        conn, cursor = createDbConnection()
        Logger.info("Starting get_other_matrimonial_data_opposite_gender method")
        user_gender = user_gender[0]
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId in ({profileIds});"
        else:
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId in ({profileIds});"
        Logger.debug(f"Generated SQL query: {query}")
        
        cursor.execute(query)
        Logger.debug("Executed SQL query")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        closeDbConnection(conn, cursor)
        return result

    def get_potential_matches(self, user_gender, profile_id):
        conn, cursor = createDbConnection()
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId != {profile_id};"
        else:
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId != {profile_id};"
        
        cursor.execute(query)
        result = cursor.fetchall()
        closeDbConnection(conn, cursor)
        # columns = [desc[0] for desc in self.cursor.description]
        return result

    def calculate_scores(self, main_preferences, other_preferences, user_preferences):
        Logger.info("Starting calculate_scores method")

        print("WOrking For ", len(other_preferences))
        
        main_profile = main_preferences
        matrimonial_attributes = list(main_profile.keys())
        user_dict = user_preferences
        scores = {}
        user_gotra = main_profile.get('Gotra', '')
        user_subCaste = main_profile.get('SubCaste', '')
        Logger.debug(f"Main profile: {main_profile}")
        Logger.debug(f"User preferences: {user_dict}")
        
        for profile in other_preferences:
            Logger.debug(f"Processing profile: {profile['ProfileId']}")
            profile_dict = profile
            profile_gotra = profile_dict.get('Gotra', '')
            profile_subCaste = profile_dict.get('SubCaste', '')
            Logger.debug(f"Profile Gotra: {profile_gotra}, Profile SubCaste: {profile_subCaste}")
            if user_gotra == profile_gotra:
                scores[profile['ProfileId']] = 0
                Logger.debug(f"Profile {profile['ProfileId']} skipped due to matching Gotra")
                continue
            
            # check if users subCaste are same it other profile is not selected
            if is_null_or_empty(user_subCaste) == False or is_null_or_empty(profile_subCaste) == False:
                if user_subCaste == profile_subCaste:
                    scores[profile['ProfileId']] = 0
                    Logger.debug(f"Profile {profile['ProfileId']} skipped due to matching SubCaste")
                    continue
                
            
            score = 0
            properties_mached = []
            
            
            #get score for matrimonial profile
            for attr in matrimonial_attributes:
                if attr not in ['AboutMe', 'astro_flag', 'LanguagesKnown', 'Interests', 'OccupationCompany', 'matching_flag', 'OccupationLocation', 'AdditionalQualification', 'YearOfPassing', 'Institution', 'MotherName', 'FatherName', 'ZipCode', 'Email', 'PhoneNumber', 'Address', 'Religion', 'Caste', 'BloodGroup', 'Gender', 'ProfileId', 'Name', 'Id', 'AnnualIncomeINR', 'Time']:
                    if main_profile.get(attr) == profile_dict.get(attr):
                        properties_mached.append(attr)
                        score += 1
                        Logger.debug(f"Attribute {attr} matched for profile {profile['ProfileId']}, score incremented")
                    
                    try:    
                        # score for marital status
                        if attr == "MaritalStatus":
                            
                            # print(attr)
                            main_marital_status = main_profile.get(attr)
                            if main_profile.get(attr) == 'Single' and (user_dict["Unmarried"]) == 1:
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"MaritalStatus matched (Single) for profile {profile['ProfileId']}, score incremented")
                            elif main_profile.get(attr) == 'Married' and (user_dict["Unmarried"]) == 0:
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"MaritalStatus matched (Married) for profile {profile['ProfileId']}, score incremented")
                            elif main_profile.get(attr) == 'Divorced' and (user_dict["Divorced"]) == 1:
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"MaritalStatus matched (Divorced) for profile {profile['ProfileId']}, score incremented")
                    except Exception as e:
                        Logger.error(f"Marital Error{e}")
                        
                    try:   
                        # location score 
                        if attr == "State":
                            
                            if user_dict["PreferredLocation"] == "Anytown":
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"PreferredLocation matched (Anytown) for profile, score incremented")
                            elif user_dict["PreferredLocation"] == 'Within my State':
                                if main_profile.get("State") == profile_dict.get("State"):
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"State matched for profile, score incremented")
                                    
                    except Exception as e:
                        Logger.error(f"Location Error {e}")
                      
                    try:                
                        # Degree score
                        if attr == "HighestDegree":
                            
                            education = user_dict.get("Education")
                            other_education = profile.get("HighestDegree")
                            
                            if education == None or other_education == None:
                                Logger.warning(f"User eduction : {education} or Other eduction : {other_education} may be null or empty skiping education matching.")
                                continue
                            
                            education = education.lower()[0]
                            other_education = other_education.lower()[0]
                            
                            if education == other_education:
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"HighestDegree matched for profile {profile['ProfileId']}, score incremented")
                    except Exception as e:
                        Logger.error(f"Education Error {e}")   
                        
                    try:
                        # Occupation score
                        if attr == "Occupation":
                            
                            preferredProfession: str = user_dict["PreferredProfession"]
                            occupation: str = profile.get("Occupation")
                            
                            if occupation == None or preferredProfession == None:
                                Logger.warning(f"User occupation : {user_hobbies} or Other occupation : {occupation} may be null or empty skiping occupation matching.")
                                continue
                            
                            properties_mached.append(attr)
                            count = Chatgpt().matching_job_title(preferredProfession, occupation)
                            if count == 0:
                                if preferredProfession.__contains__(occupation):
                                    count = 1
                                elif occupation.__contains__(preferredProfession):
                                    count = 1
                                
                            Logger.debug(f"Matching job titles count: {count}")
                            print("count", count)
                            score += count
                                
                    except Exception as e:
                        Logger.error(f"Occupation Error{e}")  
                        
                    try:
                        
                        if attr == "Hobbies":
                            
                            user_hobbies: str = user_dict["Hobbies"]
                            other_hobbies: str = profile.get("Hobbies")
                            
                            if user_hobbies == None or other_hobbies == None:
                                Logger.info(f"User Hobbies : {user_hobbies} or Other Hobbies may be null or empty : {other_hobbies} skiping hobbies matching.")
                                continue
                            
                            if other_hobbies.__contains__(user_hobbies):
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"Hobbies matched for profile {profile['ProfileId']}, score incremented")
                                
                            elif other_hobbies == user_hobbies:
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"Complexion matched for profile {profile['ProfileId']}, score incremented")
                                
                    except Exception as e:
                        Logger.error(f"Hobbies error: {e}")
                        
                    try:
                        # Color complexion Score
                        if attr == "Complexion":
                            
                            desiredColor = user_dict["DesiredColorComplexion"]
                            complexion = profile.get("Complexion")
                            if desiredColor == complexion:
                                properties_mached.append(attr)
                                score += 1
                                Logger.debug(f"Complexion matched for profile {profile['ProfileId']}, score incremented")
                                
                    except Exception as e:
                        Logger.error(f"Hobbies error:{e}")
                        
                    # height score
                    try:
                        if attr == "HeightCM":
                            
                            
                            if is_null_or_empty(profile.get("HeightCM")):
                                Logger.warning(f"Height for profile {profile['ProfileId']} is null or empty")
                                continue
                            
                            other_height: int = int(profile.get("HeightCM"))
                            user_height = user_dict.get('Height')
                            
                            if other_height < 50:
                                continue
                            
                            if user_height == "Below 5ft":
                                if other_height < feet_to_cm(5):
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Height matched (Below 5ft) for profile {profile['ProfileId']}, score incremented")
    
                            elif user_height == "5.1ft to 5.7ft":
                                if other_height < feet_to_cm(5.7) and other_height > feet_to_cm(5.1):
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Height matched (5.1ft to 5.7ft) for profile {profile['ProfileId']}, score incremented")
                            elif user_height == "5.8ft to 5.11ft":
                                Logger.debug(f"Height matched (5.8ft to 5.11ft) for profile {profile['ProfileId']}, score incremented")
                                if other_height < feet_to_cm(5.11) and other_height > feet_to_cm(5.8):
                                    properties_mached.append(attr)
                                    score += 1
                                    
                            elif user_height == "Above 6ft":
                                if other_height > feet_to_cm(6):
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Height matched (Above 6ft) for profile {profile['ProfileId']}, score incremented")
                        
                    except Exception as e:
                        Logger.error(f"Height error: {e}")

                        
                    # weight score  
                    try:
                        if attr == "WeightKG" :
                            
                            other_weight = int(profile.get("WeightKG"))
                            user_weight = user_dict["Weight"]
                            
                            Logger.info("Fetching user weight and opposite gender weight")
                            if is_null_or_empty(profile.get("WeightKG")):
                                Logger.warning(f"Weight for profile {profile['ProfileId']} is null or empty")
                                continue
                                
                            if other_weight < 20:
                                continue
                            
                            if user_weight == "Less than 50kg":
                                if other_weight <= 50:
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Weight matched (Less than 50kg) for profile {profile['ProfileId']}, score incremented")
    
                            elif user_weight == "51kg to 60kg":
                                if other_weight <= 60 and other_weight >= 51:
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Weight matched (51kg to 60kg) for profile {profile['ProfileId']}, score incremented")
                                
                            elif user_weight == "61kg to 65kg":
                                if other_weight <= 65 and other_weight >= 61:
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Weight matched (61kg to 65kg) for profile {profile['ProfileId']}, score incremented")
                                    
                            elif user_weight == "Above 65kg":
                                if other_weight >= 65:
                                    properties_mached.append(attr)
                                    score += 1
                                    Logger.debug(f"Weight matched (Above 65kg) for profile {profile['ProfileId']}, score incremented")
                                
                    except Exception as e:
                        Logger.error("Weight error: {e}")
                        
                    # try:
                    #     # Astro score
                        
                    #     if attr == "Dob":
                    #         astro_api = AstroService()
                    #         astro_response = astro_api.get_gunn_score(main_dict=main_profile, user_dict=profile)
                    #         print(astro_response.guna_milan.total_points)
                    #         score += int(astro_response.guna_milan.total_points)
                    #         print(score)
                    #         Logger.debug(f"Astrology score added for profile {profile['ProfileId']}, total score: {score}") 
                    # except Exception as e:
                        
                    #     tb = traceback.extract_tb(e.__traceback__)
                    #     filename, line_number, func_name, text = tb[-1]
                    #     # print(f"Exception occurred in file: {filename}, line: {line_number}")
                    #     # print(f"Exception type: {type(e).__name__}, Exception message: {e}")

                    #     # Optional: Print the full traceback
                    #     traceback.print_exc()
                        
                    #     print(f"Error: {e}")
                    #     Logger.error(f"Astro error {e}")
                        
            scores[profile['ProfileId']] = score
            # if other_preferences[1] == profile:
            #     break
        # score for astrology things
            Logger.info("Score for astrology")
        return scores
    
    

    def find_all_matches(self, profile_id, other_profiles = None):
        Logger.info(f"Starting find_all_matches for profile_id: {profile_id}")
        db, cursorDb = createDbConnection()
        user_preferences = self.get_user_preferences(profile_id)
        if len(user_preferences) == 0:
            Logger.warning(f"User Preferance data or Profile data not found for the user id: {profile_id}")
            return pd.DataFrame()
        
        user_preferences = user_preferences[0]
        
        main_preferences = self.get_main_matrimonial_data(profile_id)
        if len(main_preferences)==0:
            print("NO User Found")
            Logger.warning(f"No matrimonial found for user ID: {profile_id} or may be that already done matchmaking")
            
            matchedMaking = self.check_matchmaking_done_already(profile_id)
            if len(matchedMaking) != 0:
                Logger.warning(f"Match making already competed for this profile id: {profile_id} updating status in queued.")
                cursorDb.execute(querys.UpdateMatchQueuedFlag(matched_flag=1, profileId=profile_id, processing_flag=0))
                db.commit()  
            return pd.DataFrame()
        
        
        main_preferences = main_preferences[0]
        
        user_gender = main_preferences['Gender'] if len(main_preferences) > 0 else ''
        
        if other_profiles == None:
            other_preferences = self.get_other_matrimonial_data_opposite_gender(user_gender, profile_id)
        else:
            other_profile_id_list  = ', '.join(str(num) for num in other_profiles)
            other_preferences = self.get_other_matrimonial_data_for_ids(user_gender, other_profile_id_list)
        
        print("TOtal itesm:", len(other_preferences))
        if len(other_preferences) == 0:
            Logger.warning(f"NO Other User Found for Matchmaking With Opposite Gender: {user_gender}")
            cursorDb.execute(querys.UpdateMatchQueuedFlag(matched_flag=0, profileId=profile_id, processing_flag=0))
            return pd.DataFrame()
        # return
        res = MultiProcess()
        
        # scores = res.process(self.calculate_scores,main_preferences, other_preferences, user_preferences)
        scores = self.calculate_scores(main_preferences, other_preferences, user_preferences)
        print(scores)
        Logger.info(f"Scores calculated for profile_id: {profile_id}")
        Logger.debug(f"Calculated scores: {scores}")
    
        scores_df = pd.DataFrame(scores.items(), columns=['ProfileId', 'Score'])
        sorted_scores_df = scores_df.sort_values(by='Score', ascending=False)
        
        Logger.info(f"Sorted scores for profile_id {profile_id} obtained")
        Logger.debug(f"Sorted scores DataFrame: {sorted_scores_df}")
        return sorted_scores_df.to_dict(orient='records')
    