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
import math
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
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId != {profile_id};"
        elif user_gender.lower() == 'female':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId != {profile_id};"
        else:
            Logger.warning("Invalid gender provided")
            return []
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
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId in ({profileIds});"
        elif user_gender.lower() == 'female':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId in ({profileIds});"
        else:
            Logger.warning("Invalid gender provided")
            return []
        Logger.debug(f"Generated SQL query: {query}")
        
        cursor.execute(query)
        Logger.debug("Executed SQL query")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        closeDbConnection(conn, cursor)
        return result
    
    def get_already_matched_profileIds(self, profileId: int):
        conn, cursor = createDbConnection()
        Logger.info("Retriving Already Matched Profile Ids to remove from the other profile ids")
        query = f"select OtherProfileId from MatchedProfiles_M where MainProfileId = {profileId} and IsExpired = 0"
        Logger.debug(f"Generated SQL query: {query}")
        
        cursor.execute(query)
        Logger.debug("Executed SQL query")
        result = cursor.fetchall()
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
        
        astro_api: AstroService = None
        is_astro_method_called = False
        last_called = time.time()
        interval = 3000
        
        for profile in other_preferences:
            profileId = profile["ProfileId"]
            Logger.debug(f"Processing profile: {profileId}")
            profile_dict = profile
            profile_gotra = profile_dict.get('Gotra', '')
            profile_subCaste = profile_dict.get('SubCaste', '')
            Logger.debug(f"Profile Gotra: {profile_gotra}, Profile SubCaste: {profile_subCaste}")
            if user_gotra == profile_gotra:
                scores[profileId] = 0
                Logger.debug(f"Profile {profileId} skipped due to matching Gotra")
                continue
            
            # check if users subCaste are same it other profile is not selected
            # if is_null_or_empty(user_subCaste) or is_null_or_empty(profile_subCaste):
                # continue
                # if user_subCaste == profile_subCaste:
                #     scores[profileId] = 0
                #     Logger.warning(f"Profile {profileId} skipped due to null or empty SubCaste")
                
            
            score = 0
            properties_mached = []
            
            matchMaritalFound = False
            #get score for matrimonial profile
            # for attr in matrimonial_attributes:
                
                    # print(attr)
                    # main_marital_status = main_profile.get(attr)
                # if matchMaritalFound == False:
            attr = "MaritalStatus"
            try:  
                other_marital_status: str = str(profile_dict.get(attr))
                user_marital_preference: str = str(user_dict[attr])
                
                if is_null_or_empty(user_marital_preference):
                    Logger.warning(f"This User is an google drive pdf extracted user don't have preference so skiping match making for this user. with ProfileId: {profileId}")
                    break
                
                if is_null_or_empty(other_marital_status) or is_null_or_empty(user_marital_preference):
                    scores[profileId] = 0
                    Logger.warning(f"Profile {profileId} skipped due to null or empty Marital Status")
                    continue
                
                if other_marital_status == user_marital_preference:
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus are equal for profile {profileId}, score incremented")
                    
                elif other_marital_status.__contains__(user_marital_preference):
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus other matrimonial contains user marital status for profile {profileId}, score incremented")
                    
                elif user_marital_preference.__contains__(other_marital_status):
                    properties_mached.append("MaritalStatus")
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus other matrimonial contains user marital status for profile {profileId}, score incremented")
                    
                if matchMaritalFound == False:
                    scores[profileId] = 0
                    Logger.warning(f"MaritalStatus not matched for profile: {profileId}")
                    Logger.warning(f"Skiping this profile")
                    continue
                
            except Exception as e:
                Logger.error(f"Marital Error{e}")
                        
                # if attr not in ['UpdatedAt', 'AboutMe', 'astro_flag', 'LanguagesKnown', 'Interests', 'OccupationCompany', 'matching_flag', 'OccupationLocation', 'AdditionalQualification', 'YearOfPassing', 'Institution', 'MotherName', 'FatherName', 'ZipCode', 'Email', 'PhoneNumber', 'Address', 'Religion', 'Caste', 'BloodGroup', 'Gender', 'ProfileId', 'Name', 'Id', 'AnnualIncomeINR', 'Time', 'Subscribe_Token', 'CreatedAt', 'IsActive']:
                    # if main_profile.get(attr) == profile_dict.get(attr):
                    #     properties_mached.append(attr)
                    #     score += 1
                    #     Logger.debug(f"Attribute {attr} matched for profile {profileId}, score incremented")
                    
                    # try:    
                    #     # score for marital status
                    #     if attr == "MaritalStatus":
                            
                    #         matchMaritalFound = False
                    #         # print(attr)
                    #         # main_marital_status = main_profile.get(attr)
                    #         if main_profile.get(attr) == 'Single' and (user_dict["Unmarried"]) == 1:
                    #             properties_mached.append(attr)
                    #             score += Config.MM_SCORE_5
                    #             matchMaritalFound = True
                                
                    #             Logger.debug(f"MaritalStatus matched (Single) for profile {profileId}, score incremented")
                    #         elif main_profile.get(attr) == 'Married' and (user_dict["Unmarried"]) == 0:
                    #             properties_mached.append(attr)
                    #             score += Config.MM_SCORE_5
                    #             matchMaritalFound = True
                                
                    #             Logger.debug(f"MaritalStatus matched (Married) for profile {profileId}, score incremented")
                    #         elif main_profile.get(attr) == 'Divorced' and (user_dict["Divorced"]) == 1:
                    #             properties_mached.append(attr)
                    #             score += Config.MM_SCORE_5
                    #             matchMaritalFound = True
                    #             Logger.debug(f"MaritalStatus matched (Divorced) for profile {profileId}, score incremented")
                            
                    #     if matchMaritalFound == False:
                    #         break
                    # except Exception as e:
                    #     Logger.error(f"Marital Error{e}")
                        
            try:   
                # location score 
                # if attr == "State":
                attr = "State"
                    
                if user_dict["PreferredLocation"] == "Anytown":
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"PreferredLocation matched (Anytown) for profile, score incremented")
                    
                elif user_dict["PreferredLocation"] == 'Within my State':
                    if main_profile.get(attr) == profile_dict.get(attr):
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"State matched for profile, score incremented")
                elif user_dict["PreferredLocation"] == 'Any State':
                    # if main_profile.get(attr) == profile_dict.get(attr):
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"State matched for profile, score incremented")
                        
            except Exception as e:
                Logger.error(f"Location Error {e}")
                
            try:                
                # Degree score
                # if attr == "HighestDegree":
                    
                education = user_dict.get("Education")
                other_education = profile.get("HighestDegree")
                
                if is_null_or_empty(education) or is_null_or_empty(other_education):
                    Logger.warning(f"User eduction : {education} or Other eduction : {other_education} may be null or empty skiping education matching.")
                    continue
                
                education_char = education.lower()[0]
                other_education_char = other_education.lower()[0]
                
                if education_char == other_education_char:
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"HighestDegree matched for profile {profileId}, score incremented")
                elif education == 'No Preference':
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"No Preference {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Education : {education} or Other eduction : {other_education}, Error {e}")   
                
            try:
                # Occupation score
                # if attr == "Occupation":
                    
                preferredProfession: str = user_dict["PreferredProfession"]
                occupation: str = profile.get("Occupation")
                
                if is_null_or_empty(occupation) or is_null_or_empty(preferredProfession):
                    Logger.warning(f"User occupation : {user_hobbies} or Other occupation : {occupation} may be null or empty skiping occupation matching.")
                    continue
                
                properties_mached.append(attr)
                count = Chatgpt().matching_job_title(preferredProfession, occupation)
                if count == 0:
                    if preferredProfession.__contains__(occupation):
                        count = Config.MM_SCORE_10
                    elif occupation.__contains__(preferredProfession):
                        count = Config.MM_SCORE_10
                    elif preferredProfession == 'No Preference':
                        count = Config.MM_SCORE_10
                    
                Logger.debug(f"Matching job titles count: {count}")
                print("count", count)
                score += count
                        
            except Exception as e:
                Logger.error(f"Occupation Error{e}")  
                
            try:
                
                # if attr == "Hobbies":
                    
                user_hobbies: str = user_dict["Hobbies"]
                other_hobbies: str = profile.get("Hobbies")
                
                if is_null_or_empty(user_hobbies) or is_null_or_empty(other_hobbies):
                    Logger.info(f"User Hobbies : {user_hobbies} or Other Hobbies may be null or empty : {other_hobbies} skiping hobbies matching.")
                    continue
                
                if other_hobbies.__contains__(user_hobbies):
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_10
                    Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                
                elif user_hobbies.__contains__(other_hobbies):
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_10
                    Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                    
                elif other_hobbies == user_hobbies:
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_10
                    Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                elif user_hobbies == 'No Preference':
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_10
                    Logger.debug(f"No Preference hobbies for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Hobbies error: {e}")
                
            try:
                # Color complexion Score
                # if attr == "Complexion":
                attr = "Complexion"
                    
                desiredColor = user_dict["DesiredColorComplexion"]
                complexion = profile.get(attr)
                
                if is_null_or_empty(desiredColor) or is_null_or_empty(complexion):
                    Logger.warning(f"User complexion : {desiredColor} or Other complexion : {complexion} may be null or empty skiping complexion matching.")
                    continue
                
                if desiredColor == complexion:
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"Complexion matched for profile {profileId}, score incremented")
                    
                elif desiredColor == 'No Preference':
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"No Preference {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Hobbies error:{e}")
                
            # height score
            try:
                # if attr == "HeightCM":
                attr = "HeightCM"
                    
                if is_null_or_empty(profile.get(attr)):
                    Logger.warning(f"Height for profile {profileId} is null or empty")
                    continue
                
                other_height: int = int(profile.get(attr).split(".")[0])
                user_height = user_dict.get('Height')
                
                if other_height < 50:
                    continue
                
                if user_height == "Below 5ft":
                    if other_height < feet_to_cm(5):
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Height matched (Below 5ft) for profile {profileId}, score incremented")

                elif user_height == "5.1ft to 5.7ft":
                    if other_height < feet_to_cm(5.7) and other_height > feet_to_cm(5.1):
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Height matched (5.1ft to 5.7ft) for profile {profileId}, score incremented")
                        
                elif user_height == "5.8ft to 5.11ft":
                    Logger.debug(f"Height matched (5.8ft to 5.11ft) for profile {profileId}, score incremented")
                    if other_height < feet_to_cm(5.11) and other_height > feet_to_cm(5.8):
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        
                elif user_height == "Above 6ft":
                    if other_height > feet_to_cm(6):
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Height matched (Above 6ft) for profile {profileId}, score incremented")
                        
                elif user_height == 'No Preference':
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"Height matched No Preference {attr} for profile {profileId}, score incremented")
                
            except Exception as e:
                Logger.error(f"Height error: {e}")

                
            # weight score  
            try:
                # if attr == "WeightKG" :
                attr = "WeightKG"
                    
                if is_null_or_empty(profile.get(attr)):
                    Logger.warning(f"Weight for profile {profileId} is null or empty")
                    continue
                
                other_weight = int(profile.get(attr))
                user_weight = user_dict["Weight"]
                
                Logger.info("Fetching user weight and opposite gender weight")
                    
                if other_weight < 20:
                    continue
                
                if user_weight == "Less than 50kg":
                    if other_weight <= 50:
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Weight matched (Less than 50kg) for profile {profileId}, score incremented")

                elif user_weight == "51kg to 60kg":
                    if other_weight <= 60 and other_weight >= 51:
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Weight matched (51kg to 60kg) for profile {profileId}, score incremented")
                    
                elif user_weight == "61kg to 65kg":
                    if other_weight <= 65 and other_weight >= 61:
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Weight matched (61kg to 65kg) for profile {profileId}, score incremented")
                        
                elif user_weight == "Above 65kg":
                    if other_weight >= 65:
                        properties_mached.append(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Weight matched (Above 65kg) for profile {profileId}, score incremented")
                        
                elif user_weight == 'No Preference':
                    properties_mached.append(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"Weight matched (No Preference) {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Weight error: {e}")
                
            try:
                # Astro score
                
                # if attr == "Dob":
                current_time = time.time()
                if current_time - last_called >= interval or is_astro_method_called == False:
                    astro_api = AstroService()
                    last_called = current_time
                    is_astro_method_called = True
                    
                astro_response = astro_api.get_gunn_score(main_dict=main_profile, user_dict=profile)
                print(astro_response.guna_milan.total_points)
                score += int(astro_response.guna_milan.total_points)
                print(score)
                Logger.debug(f"Astrology score added for profile {profileId}, total score: {score}") 
            except Exception as e:
                
                tb = traceback.extract_tb(e.__traceback__)
                traceback.print_exc()
                
                print(f"Error: {tb}")
                Logger.error(f"Astro error {tb}")
                        
            scores[profileId] = score
            # if other_preferences[1] == profile:
            #     break
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
        
        # remove ids that has already match making done
        alreadyMatched = self.get_already_matched_profileIds(profile_id)
        print("Already Matched: ", alreadyMatched)
        for alreadyMatchedId in alreadyMatched:
            for item in other_preferences:
                if item['ProfileId'] == alreadyMatchedId["OtherProfileId"]:
                    Logger.warning(f"Removing already matched profile id: {alreadyMatchedId['OtherProfileId']}")
                    other_preferences.remove(item)
        # return
        print("Total items:", len(other_preferences))
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
    