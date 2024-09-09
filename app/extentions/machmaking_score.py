import pandas as pd
from app.routes import closeDbConnection, _database
from app.extentions.common_extensions import feet_to_cm, is_null_or_empty, split_list, count_matching_hobbies, remove_duplicates
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
# from app.services.match_making_service import db, cursorDb

class MatchmakingScore:
    def __init__(self):
        pass

    def get_user_preferences(self, profile_id):
        conn, cursor = _database.get_connection()
        Logger.info("Starting get_user_preferences method")
        query = f"SELECT * FROM Profiles_M WHERE Id = {profile_id}"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        #columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        Logger.debug(f"Columns retrieved")
        # closeDbConnection(conn, cursor)
        return result
    
    def get_other_preferences_except_user(self, profile_id):
        conn, cursor = _database.get_connection()
        Logger.info("Starting get_user_preferences method")
        query = f"SELECT * FROM Profiles_M WHERE Id != {profile_id}"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        #columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        Logger.debug(f"Columns retrieved")
        # closeDbConnection(conn, cursor)
        return result
    
    def get_main_matrimonial_data(self, profile_id):
        conn, cursor = _database.get_connection()
        Logger.info("Starting get_user_preferences method")
        # query = f"SELECT * FROM MatrimonialProfile_M WHERE ProfileId = {profile_id} and matching_flag = 0"
        query = f"SELECT * FROM MatrimonialProfile_M WHERE ProfileId = {profile_id}"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        # closeDbConnection(conn, cursor)
        return result
    
    def check_matchmaking_done_already(self, profile_id):
        conn, cursor = _database.get_connection()
        Logger.info("Starting match making completed data")
        query = f"SELECT * FROM MatrimonialProfile_M WHERE ProfileId = {profile_id} and matching_flag = 1"
        cursor.execute(query)
        Logger.debug(f"Executed SQL query: {query}")
        result = cursor.fetchall()
        # columns = [desc[0] for desc in self.cursor.description]
        Logger.debug(f"Fetched result from database: {result}")
        # closeDbConnection(conn, cursor)
        return result
    
    def get_other_matrimonial_data_opposite_gender(self, user_gender: str, profile_id):
        conn, cursor = _database.get_connection()
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
        # closeDbConnection(conn, cursor)
        return result
    
    def get_other_matrimonial_data_for_ids(self, user_gender: str, profileIds):
        conn, cursor = _database.get_connection()
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
        # closeDbConnection(conn, cursor)
        return result
    
    def get_already_matched_profileIds(self, profileId: int):
        conn, cursor = _database.get_connection()
        Logger.info("Retriving Already Matched Profile Ids to remove from the other profile ids")
        query = f"select OtherProfileId from MatchedProfiles_M where MainProfileId = {profileId} and IsExpired = 0"
        Logger.debug(f"Generated SQL query: {query}")
        
        cursor.execute(query)
        Logger.debug("Executed SQL query")
        result = cursor.fetchall()
        Logger.debug(f"Fetched result from database: {result}")
        # closeDbConnection(conn, cursor)
        return result

    def get_potential_matches(self, user_gender, profile_id):
        conn, cursor = _database.get_connection()
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId != {profile_id};"
        else:
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId != {profile_id};"
        
        cursor.execute(query)
        result = cursor.fetchall()
        # closeDbConnection(conn, cursor)
        # columns = [desc[0] for desc in self.cursor.description]
        return result

    def calculate_scores_matrimonial(self, main_matrimonial, other_matrimonial, preferences):
        Logger.info("Starting calculate_scores method")
        
        user_preferences = preferences["UserPreference"]
        other_preferences = preferences["OtherPreference"]
        
        final_result_matched_properties = {}
        user_dict = user_preferences
        scores = {}
        gun_scores = {}
        user_gotra = main_matrimonial.get('Gotra', '')
        user_subCaste = main_matrimonial.get('SubCaste', '')
        Logger.debug(f"Main profile: {main_matrimonial}")
        Logger.debug(f"User preferences: {user_dict}")
        
        astro_api: AstroService = None
        is_astro_method_called = False
        last_called = time.time()
        interval = 3000
        
        for other_matri_profile in other_matrimonial:
            profileId = other_matri_profile["ProfileId"]
            Logger.debug(f"Processing profile: {profileId}")
            # profile_dict = other_profile
            profile_gotra = other_matri_profile.get('Gotra', '')
            profile_subCaste = other_matri_profile.get('SubCaste', '')
            Logger.debug(f"Profile Gotra: {profile_gotra}, Profile SubCaste: {profile_subCaste}")
            if user_gotra == profile_gotra:
                scores[profileId] = 0
                Logger.debug(f"Profile {profileId} skipped due to matching Gotra")
                continue
            
            # check if users subCaste are same it other profile is not selected
            if is_null_or_empty(user_subCaste) or is_null_or_empty(profile_subCaste):
                Logger.warning(f"Profile {profileId} skipped due to null or empty SubCaste")
                continue
            elif user_subCaste == profile_subCaste:
                scores[profileId] = 0
                Logger.debug(f"Profile {profileId} skipped due to matching SubCaste or same subcaste")
                
            
            score = 0
            properties_mached = []
            matched_hobbies = []
            match_and_values = {}
            user_preference_profile = {}
            other_matrimonial_profile = {}
            user_matrimonial_profile = {}
            matchMaritalFound = False
            
            attr = "MaritalStatus"
            try:  
                other_marital_status: str = str(other_matri_profile.get(attr))
                user_marital_preference: str = str(user_dict[attr])
                
                if is_null_or_empty(user_marital_preference):
                    Logger.warning(f"This User is an google drive pdf extracted user don't have preference so skiping match making for this user. with ProfileId: {profileId}")
                    continue
                
                if is_null_or_empty(other_marital_status) or is_null_or_empty(user_marital_preference):
                    scores[profileId] = 0
                    Logger.warning(f"Profile {profileId} skipped due to null or empty Marital Status")
                    continue
                
                if other_marital_status == user_marital_preference:
                    properties_mached.append(attr)
                    # match_and_values[attr] = user_marital_preference
                    user_preference_profile[attr] = user_marital_preference
                    other_matrimonial_profile[attr] = other_marital_status
                    user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus are equal for profile {profileId}, score incremented")
                    
                elif other_marital_status.__contains__(user_marital_preference):
                    properties_mached.append(attr)
                    # match_and_values[attr] = user_marital_preference
                    user_preference_profile[attr] = user_marital_preference
                    other_matrimonial_profile[attr] = other_marital_status
                    user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus other matrimonial contains user marital status for profile {profileId}, score incremented")
                    
                elif user_marital_preference.__contains__(other_marital_status):
                    properties_mached.append(attr)
                    # match_and_values[attr] = user_marital_preference
                    user_preference_profile[attr] = user_marital_preference
                    other_matrimonial_profile[attr] = other_marital_status
                    user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus other matrimonial contains user marital status for profile {profileId}, score incremented")
                
                elif user_marital_preference == "No Preference":
                    properties_mached.append("MaritalStatus")
                    # match_and_values[attr] = user_marital_preference
                    user_preference_profile[attr] = user_marital_preference
                    other_matrimonial_profile[attr] = other_marital_status
                    user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus No preference for profile {profileId}, score incremented")
                    
                if matchMaritalFound == False:
                    scores[profileId] = 0
                    Logger.warning(f"MaritalStatus not matched for profile: {profileId}")
                    Logger.warning(f"Skiping this profile")
                    continue
                
            except Exception as e:
                Logger.error(f"Marital Error{e}")
                        
            try:   
                # location score 
                attr = "State"
                    
                if user_dict["PreferredLocation"] == "Anytown":
                    if main_matrimonial.get(attr) == other_matri_profile.get(attr):
                        properties_mached.append(attr)
                        # match_and_values[attr] = user_dict["PreferredLocation"]
                        # user_preference_profile[attr] = user_dict["PreferredLocation"]
                        other_matrimonial_profile[attr] = other_matri_profile.get(attr)
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"PreferredLocation matched (Anytown) for profile, score incremented")
                    
                elif user_dict["PreferredLocation"] == 'Within my State':
                    if main_matrimonial.get(attr) == other_matri_profile.get(attr):
                        properties_mached.append(attr)
                        # match_and_values[attr] = user_dict["PreferredLocation"]
                        # user_preference_profile[attr] = user_dict["PreferredLocation"]
                        other_matrimonial_profile[attr] = other_matri_profile.get(attr)
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"State matched for profile, score incremented")
                elif user_dict["PreferredLocation"] == 'Any State':
                    # if main_profile.get(attr) == profile_dict.get(attr):
                    properties_mached.append(attr)
                    # match_and_values[attr] = user_dict["PreferredLocation"]
                    # user_preference_profile[attr] = user_dict["PreferredLocation"]
                    other_matrimonial_profile[attr] = other_matri_profile.get(attr)
                    user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                    score += Config.MM_SCORE_5
                    Logger.debug(f"State matched for profile, score incremented")
                        
            except Exception as e:
                Logger.error(f"Location Error {e}")
                
            try:                
                # Degree score
                attr = "Education"
                    
                education = user_dict.get("Education")
                other_education = other_matri_profile.get("HighestDegree")
                
                if is_null_or_empty(education) or is_null_or_empty(other_education):
                    Logger.warning(f"User eduction : {education} or Other eduction : {other_education} may be null or empty skiping education matching.")
                    
                else:
                    education_char = education.lower()[0]
                    other_education_char = other_education.lower()[0]
                    
                    if education_char == other_education_char:
                        properties_mached.append(attr)
                        # match_and_values[attr] = education
                        user_preference_profile[attr] = education
                        other_matrimonial_profile[attr] = other_education
                        user_matrimonial_profile[attr] = main_matrimonial.get("HighestDegree")
                        score += Config.MM_SCORE_5
                        Logger.debug(f"HighestDegree matched for profile {profileId}, score incremented")
                    elif education == 'No Preference':
                        properties_mached.append(attr)
                        # match_and_values[attr] = education
                        user_preference_profile[attr] = education
                        other_matrimonial_profile[attr] = other_education
                        user_matrimonial_profile[attr] = main_matrimonial.get("HighestDegree")
                        score += Config.MM_SCORE_5
                        Logger.debug(f"No Preference {attr} for profile {profileId}, score incremented")
                            
            except Exception as e:
                Logger.error(f"Education : {education} or Other eduction : {other_education}, Error {e}")   
                
            try:
                # Occupation score
                attr = "Occupation"
                    
                preferredProfession: str = user_dict["PreferredProfession"]
                occupation: str = other_matri_profile.get("Occupation")
                
                if is_null_or_empty(occupation) or is_null_or_empty(preferredProfession):
                    Logger.warning(f"User occupation : {preferredProfession} or Other occupation : {occupation} may be null or empty skiping occupation matching.")
                
                else:                
                    if preferredProfession == 'No Preference':
                        properties_mached.append(attr)
                        # match_and_values[attr] = preferredProfession
                        # user_preference_profile[attr] = preferredProfession
                        other_matrimonial_profile[attr] = occupation
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        count = Config.MM_SCORE_10
                        Logger.debug(f"No Preference Occupation for profile {profileId}, score incremented")
                            
                    else:
                        count = Chatgpt().matching_job_title(preferredProfession, occupation)
                        if count == 0:
                            if preferredProfession.__contains__(occupation):
                                properties_mached.append(attr)
                                # match_and_values[attr] = preferredProfession
                                # user_preference_profile[attr] = preferredProfession
                                other_matrimonial_profile[attr] = occupation
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                count = Config.MM_SCORE_10
                                
                            elif occupation.__contains__(preferredProfession):
                                properties_mached.append(attr)
                                # match_and_values[attr] = preferredProfession
                                # user_preference_profile[attr] = preferredProfession
                                other_matrimonial_profile[attr] = occupation
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                count = Config.MM_SCORE_10
                                
                            elif occupation == preferredProfession:
                                properties_mached.append(attr)
                                # match_and_values[attr] = preferredProfession
                                # user_preference_profile[attr] = preferredProfession
                                other_matrimonial_profile[attr] = occupation
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                count = Config.MM_SCORE_10
                    
                Logger.debug(f"Matching job titles count: {count}")
                print("count", count)
                score += count
                        
            except Exception as e:
                Logger.error(f"Occupation Error{e}")  
                
            try:
                
                attr = "Hobbies"
                matched_hobbies_list = []
                    
                user_p_hobbies: str = user_dict["Hobbies"]
                other_m_hobbies: str = other_matri_profile.get("Hobbies")
                user_m_hobbies: str = main_matrimonial.get("Hobbies")
                other_p_hobbies: str = [other_preference for other_preference in other_preferences if other_preference["Id"] == profileId][0].get("Hobbies")
                
                if is_null_or_empty(user_p_hobbies) or is_null_or_empty(other_p_hobbies):
                    Logger.info(f"User Hobbies : {user_p_hobbies} or Other Hobbies may be null or empty : {other_p_hobbies} skiping hobbies matching.")
                
                else:
                    
                    # find match for other prefernce and user prefernce
                    matches_found, matched_hobbies = count_matching_hobbies(other_p_hobbies, user_p_hobbies)
                    if matches_found != 0:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_p_hobbies
                        other_matrimonial_profile[attr] = other_p_hobbies
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                        hobby = ','.join(matched_hobbies)
                        matched_hobbies_list.append(hobby)
                        score += Config.MM_SCORE_5
                    
                    # find match for user matrimonial and other matrimonial
                    matches_found, matched_hobbies = count_matching_hobbies(user_m_hobbies, other_m_hobbies)
                    if matches_found != 0:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_p_hobbies
                        other_matrimonial_profile[attr] = other_p_hobbies
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                        hobby = ','.join(matched_hobbies)
                        matched_hobbies_list.append(hobby)
                        score += Config.MM_SCORE_5
                    
                    # find match for user prefernce and other matrimonial
                    matches_found, matched_hobbies = count_matching_hobbies(user_p_hobbies, other_m_hobbies)
                    if matches_found != 0:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_p_hobbies
                        other_matrimonial_profile[attr] = other_p_hobbies
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                        hobby = ','.join(matched_hobbies)
                        matched_hobbies_list.append(hobby)
                        score += Config.MM_SCORE_5
                        
                    # find match for user matrimonial and other preference
                    matches_found, matched_hobbies = count_matching_hobbies(user_m_hobbies, other_p_hobbies)
                    if matches_found != 0:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_p_hobbies
                        other_matrimonial_profile[attr] = other_p_hobbies
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                        hobby = ','.join(matched_hobbies)
                        matched_hobbies_list.append(hobby)
                        score += Config.MM_SCORE_5
                        
                    matched_hobbies_str = ", ".join(matched_hobbies_list)
                    matched_hobbies_str = remove_duplicates(matched_hobbies_str)
                    
                    user_preference_profile[attr] = matched_hobbies_str
                    other_matrimonial_profile[attr] = matched_hobbies_str
                    # if matches_found == 0:
                    #     if first_5_letter_other == first_5_letter_user:
                    #         properties_mached.append(attr)
                    #         # match_and_values[attr] = user_hobbies
                    #         user_preference_profile[attr] = user_p_hobbies
                    #         other_matrimonial_profile[attr] = other_p_hobbies
                    #         score += Config.MM_SCORE_10
                    #         Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                            
                    #     elif other_p_hobbies.__contains__(user_p_hobbies):
                    #         properties_mached.append(attr)
                    #         # match_and_values[attr] = user_hobbies
                    #         user_preference_profile[attr] = user_p_hobbies
                    #         other_matrimonial_profile[attr] = other_p_hobbies
                    #         score += Config.MM_SCORE_10
                    #         Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                        
                    #     elif other_p_hobbies.__contains__(user_p_hobbies):
                    #         properties_mached.append(attr)
                    #         # match_and_values[attr] = user_hobbies
                    #         user_preference_profile[attr] = user_p_hobbies
                    #         other_matrimonial_profile[attr] = other_p_hobbies
                    #         score += Config.MM_SCORE_10
                    #         Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                            
                    #     elif other_p_hobbies == user_p_hobbies:
                    #         properties_mached.append(attr)
                    #         # match_and_values[attr] = user_hobbies
                    #         user_preference_profile[attr] = user_p_hobbies
                    #         other_matrimonial_profile[attr] = other_p_hobbies
                    #         score += Config.MM_SCORE_10
                    #         Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                            
                    #     elif user_p_hobbies == 'No Preference':
                    #         properties_mached.append(attr)
                    #         # match_and_values[attr] = user_hobbies
                    #         user_preference_profile[attr] = user_p_hobbies
                    #         other_matrimonial_profile[attr] = other_p_hobbies
                    #         score += Config.MM_SCORE_10
                    #         Logger.debug(f"No Preference hobbies for profile {profileId}, score incremented")
                            
                    # else:
                    #     score += matches_found * Config.MM_SCORE_10
                    #     properties_mached.append(attr)
                    #     # match_and_values[attr] = matched_hobbies
                    #     user_preference_profile[attr] = user_p_hobbies
                    #     other_matrimonial_profile[attr] = other_p_hobbies
                    #     Logger.debug(f"Hobbies matched for profile {profileId}, score incremented for : {matches_found} hobbies")
                        
            except Exception as e:
                Logger.error(f"Hobbies error: {e}")
                
            try:
                # Color complexion Score
                # if attr == "Complexion":
                attr = "Complexion"
                    
                desiredColor = user_dict["DesiredColorComplexion"]
                complexion = other_matri_profile.get(attr)
                
                if is_null_or_empty(desiredColor) or is_null_or_empty(complexion):
                    Logger.warning(f"User complexion : {desiredColor} or Other complexion : {complexion} may be null or empty skiping complexion matching.")
                
                else:                
                    if desiredColor == complexion:
                        properties_mached.append(attr)
                        # match_and_values[attr] = desiredColor
                        # user_preference_profile[attr] = desiredColor
                        other_matrimonial_profile[attr] = complexion
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Complexion matched for profile {profileId}, score incremented")
                        
                    elif desiredColor == 'No Preference':
                        properties_mached.append(attr)
                        # match_and_values[attr] = desiredColor
                        # user_preference_profile[attr] = desiredColor
                        other_matrimonial_profile[attr] = complexion
                        user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                        score += Config.MM_SCORE_5
                        Logger.debug(f"No Preference {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Hobbies error:{e}")
                
            # height score
            try:
                # if attr == "HeightCM":
                attr = "HeightCM"
                
                if is_null_or_empty(other_matri_profile.get(attr)):
                    Logger.warning(f"Height for profile {profileId} is null or empty")

                else:               
                    other_height: int = int(other_matri_profile.get(attr).split(".")[0])
                    user_height = user_dict.get('Height')
                    
                    if other_height < 50:
                        Logger.warning(f"Height for profile {profileId} is less than 50")
                    else:
                        if user_height == "Below 5ft":
                            if other_height < feet_to_cm(5):
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_height
                                user_preference_profile["Height"] = user_height
                                other_matrimonial_profile["Height"] = other_height
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Height matched (Below 5ft) for profile {profileId}, score incremented")

                        elif user_height == "5.0ft to 5.4ft":
                            if other_height < feet_to_cm(5.0) and other_height > feet_to_cm(5.4):
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_height
                                user_preference_profile["Height"] = user_height
                                other_matrimonial_profile["Height"] = other_height
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Height matched (5.0ft to 5.4ft) for profile {profileId}, score incremented")
                                
                        elif user_height == "5.5ft to 5.7ft":
                            Logger.debug(f"Height matched (5.8ft to 5.11ft) for profile {profileId}, score incremented")
                            if other_height < feet_to_cm(5.7) and other_height > feet_to_cm(5.5):
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_height
                                user_preference_profile["Height"] = user_height
                                other_matrimonial_profile["Height"] = other_height
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                
                        elif user_height == "5.9ft to 5.11ft":
                            Logger.debug(f"Height matched (5.9ft to 5.11ft) for profile {profileId}, score incremented")
                            if other_height < feet_to_cm(5.11) and other_height > feet_to_cm(5.9):
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_height
                                user_preference_profile["Height"] = user_height
                                other_matrimonial_profile["Height"] = other_height
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                
                        elif user_height == "Above 6ft":
                            if other_height > feet_to_cm(6):
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_height
                                user_preference_profile["Height"] = user_height
                                other_matrimonial_profile["Height"] = other_height
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Height matched (Above 6ft) for profile {profileId}, score incremented")
                                
                        elif user_height == 'No Preference':
                            properties_mached.append(attr)
                            # match_and_values[attr] = user_height
                            user_preference_profile["Height"] = user_height
                            other_matrimonial_profile["Height"] = other_height
                            user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                            score += Config.MM_SCORE_5
                            Logger.debug(f"Height matched No Preference {attr} for profile {profileId}, score incremented")
            
            except Exception as e:
                Logger.error(f"Height error: {e}")

                
            # weight score  
            try:
                # if attr == "WeightKG" :
                attr = "WeightKG"
                    
                if is_null_or_empty(other_matri_profile.get(attr)):
                    Logger.warning(f"Weight for profile {profileId} is null or empty")

                else:                
                    other_weight = int(other_matri_profile.get(attr))
                    user_weight = user_dict["Weight"]
                    
                    if other_weight < 20:
                        Logger.warning(f"Weight for profile {profileId} is less than 20")
                    
                    else:
                        if user_weight == "Less than 50kg":
                            if other_weight <= 50:
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_weight
                                user_preference_profile["Weight"] = user_weight
                                other_matrimonial_profile["Weight"] = other_weight
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Weight matched (Less than 50kg) for profile {profileId}, score incremented")

                        elif user_weight == "51kg to 60kg":
                            if other_weight <= 60 and other_weight >= 51:
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_weight
                                user_preference_profile["Weight"] = user_weight
                                other_matrimonial_profile["Weight"] = other_weight
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Weight matched (51kg to 60kg) for profile {profileId}, score incremented")
                            
                        elif user_weight == "61kg to 65kg":
                            if other_weight <= 65 and other_weight >= 61:
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_weight
                                user_preference_profile["Weight"] = user_weight
                                other_matrimonial_profile["Weight"] = other_weight
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Weight matched (61kg to 65kg) for profile {profileId}, score incremented")
                                
                        elif user_weight == "Above 65kg":
                            if other_weight >= 65:
                                properties_mached.append(attr)
                                # match_and_values[attr] = user_weight
                                user_preference_profile["Weight"] = user_weight
                                other_matrimonial_profile["Weight"] = other_weight
                                user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                                score += Config.MM_SCORE_5
                                Logger.debug(f"Weight matched (Above 65kg) for profile {profileId}, score incremented")
                                
                        elif user_weight == 'No Preference':
                            properties_mached.append(attr)
                            # match_and_values[attr] = user_weight
                            user_preference_profile["Weight"] = user_weight
                            other_matrimonial_profile["Weight"] = other_weight
                            user_matrimonial_profile[attr] = main_matrimonial.get(attr)
                            score += Config.MM_SCORE_5
                            Logger.debug(f"Weight matched (No Preference) {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Weight error: {e}")
                
            try:
                # Astro score
                dob_value = other_matri_profile.get("Dob")
                if other_matri_profile.get("Dob").__contains__("yy"):
                    Logger.warning(f"DOB for profile {dob_value} is not in correct format skiping astro point for the profileId: {profileId}")
                
                else:
                    current_time = time.time()
                    if current_time - last_called >= interval or is_astro_method_called == False:
                        astro_api = AstroService()
                        last_called = current_time
                        is_astro_method_called = True
                        
                    astro_response = astro_api.get_gunn_score(main_dict=main_matrimonial, user_dict=other_matri_profile)
                    print(f"ASTRO POINTS ARE: {astro_response.guna_milan.total_points}")
                    
                    score += int(astro_response.guna_milan.total_points)
                    gun_scores[profileId] = int(astro_response.guna_milan.total_points)
                    print(score)
                    Logger.debug(f"Astrology score added for profile {profileId}, total score: {score}") 
                    
            except Exception as e:
                
                tb = traceback.extract_tb(e.__traceback__)
                traceback.print_exc()
                
                print(f"Error: {tb}")
                Logger.error(f"Astro error {tb}")
                        
            scores[profileId] = score
            other_matrimonial_profile["Name"] = other_matri_profile["Name"]
            user_matrimonial_profile["Name"] = main_matrimonial["Name"]
            match_and_values["PropertiesMatched"] = properties_mached
            match_and_values["UserPreference"] = user_preference_profile
            match_and_values["OtherMatrimonial"] = other_matrimonial_profile
            match_and_values["UserMatrimonial"] = user_matrimonial_profile
            final_result_matched_properties[profileId] = match_and_values
            # if other_preferences[1] == profile:
            #     break
        return scores, gun_scores, final_result_matched_properties
    
    def calculate_scores_preference(self, main_matrimonial, other_preferences, user_preferences):
        Logger.info("Starting calculate_scores_preference method")
        print("WOrking For ", len(other_preferences))
        
        main_profile = main_matrimonial
        final_result_matched_properties = {}
        user_preference = user_preferences
        scores = {}
        Logger.debug(f"Main profile: {main_profile}")
        Logger.debug(f"User preferences: {user_preference}")
        
        for other_profile_preference in other_preferences:
            profileId = other_profile_preference["Id"]
            Logger.debug(f"Processing profile: {profileId}")
            
            score = 0
            properties_mached = []
            matched_hobbies = []
            match_and_values = {}
            user_preference_profile = {}
            other_preference_profile = {}
            matchMaritalFound = False
            
            attr = "MaritalStatus"
            try:  
                other_marital_status: str = str(other_profile_preference.get(attr))
                user_marital_preference: str = str(user_preference[attr])
                Logger.info(f"Other Profile MaritalStatus: {other_marital_status} for profile: {profileId}")
                
                if is_null_or_empty(other_marital_status):
                    Logger.warning(f"This User is an google drive pdf extracted user don't have preference so skiping match making for this user. with ProfileId: {profileId}")
                    continue
                
                if is_null_or_empty(other_marital_status) or is_null_or_empty(user_marital_preference):
                    scores[profileId] = 0
                    Logger.warning(f"Profile {profileId} skipped due to null or empty Marital Status ")
                    continue
                
                if other_marital_status == user_marital_preference:
                    properties_mached.append(attr)
                    # match_and_values[attr] = user_marital_preference
                    user_preference_profile[attr] = user_marital_preference
                    other_preference_profile[attr] = other_marital_status
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus are equal for profile {profileId}, score incremented")
                
                elif user_marital_preference == "No Preference":
                    properties_mached.append("MaritalStatus")
                    # match_and_values[attr] = user_marital_preference
                    user_preference_profile[attr] = user_marital_preference
                    other_preference_profile[attr] = other_marital_status
                    score += Config.MM_SCORE_5
                    matchMaritalFound = True
                    Logger.debug(f"MaritalStatus No preference for profile {profileId}, score incremented")
                    
                if matchMaritalFound == False:
                    scores[profileId] = 0
                    Logger.warning(f"MaritalStatus not matched for profile: {profileId}")
                    Logger.warning(f"Skiping this profile")
                    continue
                
            except Exception as e:
                Logger.error(f"Marital Error{e}")
                        
            try:   
                # location score 
                attr = "PreferredLocation"
                user_location = user_preferences.get(attr)
                other_location = other_profile_preference.get(attr)
                if user_location == other_location:
                    properties_mached.append(attr)
                    user_preference_profile[attr] = user_location
                    other_preference_profile[attr] = other_location
                    score += Config.MM_SCORE_5
                    Logger.debug(f"PreferredLocation matched (Anytown) for profile, score incremented")
               
                elif user_location == 'Any State':
                    properties_mached.append(attr)
                    user_preference_profile[attr] = user_location
                    other_preference_profile[attr] = other_location
                    score += Config.MM_SCORE_5
                    Logger.debug(f"PreferredLocation matched for profile, score incremented")
                        
            except Exception as e:
                Logger.error(f"PreferredLocation Error {e}")
                
            try:                
                # Degree score
                attr = "Education"
                    
                education = user_preference.get(attr)
                other_education = other_profile_preference.get(attr)
                
                if is_null_or_empty(education) or is_null_or_empty(other_education):
                    Logger.warning(f"User eduction : {education} or Other eduction : {other_education} may be null or empty skiping education matching.")
                    
                else:
                    
                    if education == other_education:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = education
                        other_preference_profile[attr] = other_education
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Education matched for profile {profileId}, score incremented")
                    elif education == 'No Preference':
                        properties_mached.append(attr)
                        user_preference_profile[attr] = education
                        other_preference_profile[attr] = other_education
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Education have No Preference {attr} for profile {profileId}, score incremented")
                            
            except Exception as e:
                Logger.error(f"Education : {education} or Other eduction : {other_education}, Error {e}")   
                
        
            try:
                attr = "FamilyType"
                    
                user_family_type: str = user_preference[attr]
                other_family_type: str = other_profile_preference.get(attr)
                
                if is_null_or_empty(user_family_type) or is_null_or_empty(user_family_type):
                    Logger.info(f"User Family type : {user_family_type} or Other family may be null or empty : {other_family_type} skiping family matching.")
                
                else:
                    if user_family_type == other_family_type:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_family_type
                        other_preference_profile[attr] = other_family_type
                        score += Config.MM_SCORE_10
                        Logger.debug(f"family type matched for profile {profileId}, score incremented")
                        
                    elif user_family_type == 'No Preference':
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_family_type
                        other_preference_profile[attr] = other_family_type
                        score += Config.MM_SCORE_10
                        Logger.debug(f"No Preference family type for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Family Type error: {e}")
                
            try:
                # Occupation score
                attr = "PreferredProfession"
                count = 0
                user_occupation: str = user_preference[attr]
                other_occupation: str = other_profile_preference.get(attr)
                
                if is_null_or_empty(user_occupation) or is_null_or_empty(other_occupation):
                    Logger.warning(f"User occupation : {user_hobbies} or Other occupation : {other_occupation} may be null or empty skiping occupation matching.")
                
                else:                
                    if user_occupation == 'No Preference':
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_occupation
                        other_preference_profile[attr] = other_occupation
                        count = Config.MM_SCORE_10
                        Logger.debug(f"No Preference Occupation for profile {profileId}, score incremented")
                            
                    else:
                        # count = Chatgpt().matching_job_title(preferredProfession, occupation)
                        # if count == 0:
                        if user_occupation.__contains__(other_occupation):
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_occupation
                            other_preference_profile[attr] = other_occupation
                            count = Config.MM_SCORE_10
                            Logger.debug(f"Occupation matched for profile {profileId}, score incremented")
                            
                        elif other_occupation.__contains__(user_occupation):
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_occupation
                            other_preference_profile[attr] = other_occupation
                            count = Config.MM_SCORE_10
                            Logger.debug(f"Occupation matched for profile {profileId}, score incremented")
                            
                        elif other_occupation == user_occupation:
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_occupation
                            other_preference_profile[attr] = other_occupation
                            count = Config.MM_SCORE_10
                            Logger.debug(f"Occupation matched for profile {profileId}, score incremented")
                    
                Logger.debug(f"Matching job titles count: {count}")
                print("count", count)
                score += count
                        
            except Exception as e:
                Logger.error(f"Occupation Error{e}")  
                
            try:
                attr = "Hobbies"
                    
                user_hobbies: str = user_preference["Hobbies"]
                other_hobbies: str = other_profile_preference.get("Hobbies")
                
                if is_null_or_empty(user_hobbies) or is_null_or_empty(other_hobbies):
                    Logger.info(f"User Hobbies : {user_hobbies} or Other Hobbies may be null or empty : {other_hobbies} skiping hobbies matching.")
                
                else:
                    first_5_letter_other = other_hobbies[:5]
                    first_5_letter_user = user_hobbies[:5]
                    matches_found, matched_hobbies = count_matching_hobbies(other_hobbies, user_hobbies)
                    
                    if matches_found == 0:
                        if first_5_letter_other == first_5_letter_user:
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_hobbies
                            other_preference_profile[attr] = other_hobbies
                            score += Config.MM_SCORE_10
                            Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                            
                        elif other_hobbies.__contains__(user_hobbies):
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_hobbies
                            other_preference_profile[attr] = other_hobbies
                            score += Config.MM_SCORE_10
                            Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                        
                        elif user_hobbies.__contains__(other_hobbies):
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_hobbies
                            other_preference_profile[attr] = other_hobbies
                            score += Config.MM_SCORE_10
                            Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                            
                        elif other_hobbies == user_hobbies:
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_hobbies
                            other_preference_profile[attr] = other_hobbies
                            score += Config.MM_SCORE_10
                            Logger.debug(f"Hobbies matched for profile {profileId}, score incremented")
                            
                        elif user_hobbies == 'No Preference':
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_hobbies
                            other_preference_profile[attr] = other_hobbies
                            score += Config.MM_SCORE_10
                            Logger.debug(f"No Preference hobbies for profile {profileId}, score incremented")
                            
                    else:
                        score += matches_found * Config.MM_SCORE_10
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_hobbies
                        other_preference_profile[attr] = other_hobbies
                        hobbiesStr = ','.join(matched_hobbies)
                        Logger.debug(f"Hobbies matched for profile {profileId}, score incremented for : {matches_found} hobbies: {hobbiesStr}")
                        
            except Exception as e:
                Logger.error(f"Hobbies error: {e}")
                
            try:
                # Color complexion Score
                attr = "DesiredColorComplexion"
                    
                desiredColor = user_preference[attr]
                complexion = other_profile_preference.get(attr)
                
                if is_null_or_empty(desiredColor) or is_null_or_empty(complexion):
                    Logger.warning(f"User complexion : {desiredColor} or Other complexion : {complexion} may be null or empty skiping complexion matching.")
                
                else:                
                    if desiredColor == complexion:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = desiredColor
                        other_preference_profile[attr] = complexion
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Complexion matched for profile {profileId}, score incremented")
                        
                    elif desiredColor == 'No Preference':
                        properties_mached.append(attr)
                        user_preference_profile[attr] = desiredColor
                        other_preference_profile[attr] = complexion
                        score += Config.MM_SCORE_5
                        Logger.debug(f"No Preference {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Hobbies error:{e}")
                
            # height score
            try:
                attr = "Height"
                
                user_height = user_preference.get(attr)
                other_height = other_profile_preference.get(attr)
                if is_null_or_empty(other_profile_preference.get(attr)):
                    Logger.warning(f"Height for profile {profileId} is null or empty")

                else:               
                    if user_height == other_height:
                        properties_mached.append(attr)
                        user_preference_profile["Height"] = user_height
                        other_preference_profile["Height"] = other_height
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Height matched ({user_height}) for profile {profileId}, score incremented")

                    elif user_height == 'No Preference':
                        properties_mached.append(attr)
                        user_preference_profile["Height"] = user_height
                        other_preference_profile["Height"] = other_height
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Height matched No Preference {attr} for profile {profileId}, score incremented")
            
            except Exception as e:
                Logger.error(f"Height error: {e}")

                
            # weight score  
            try:
                attr = "Weight"
                user_weight = user_preference.get(attr)
                other_weight = other_profile_preference.get(attr)
                    
                if is_null_or_empty(user_weight) or is_null_or_empty(other_weight):
                    Logger.warning(f"Weight for profile {profileId} is null or empty otherWeight: {other_weight} and userWeight: {user_weight}")

                else:                
                        if user_weight == other_weight:
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_weight
                            other_preference_profile[attr] = other_weight
                            score += Config.MM_SCORE_5
                            Logger.debug(f"Weight matched ({user_weight}) for profile {profileId}, score incremented")

                                
                        elif user_weight == 'No Preference':
                            properties_mached.append(attr)
                            user_preference_profile[attr] = user_weight
                            other_preference_profile[attr] = other_weight
                            score += Config.MM_SCORE_5
                            Logger.debug(f"Weight matched (No Preference) {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Weight error: {e}")
                
            try:
                attr = "DesiredFamilyBackground"
                user_family_background = user_preference.get(attr)
                other_family_background = other_profile_preference.get(attr)
                    
                if is_null_or_empty(user_family_background) or is_null_or_empty(other_family_background):
                    Logger.warning(f"Family background for profile {profileId} is null or empty otherFamilyBackground: {other_family_background} and userFamilyBackground: {user_family_background}")

                else:                
                    if user_family_background == other_family_background:
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_family_background
                        other_preference_profile[attr] = other_family_background
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Family background matched ({user_family_background}) for profile {profileId}, score incremented")

                            
                    elif user_family_background == 'No Preference':
                        properties_mached.append(attr)
                        user_preference_profile[attr] = user_family_background
                        other_preference_profile[attr] = other_family_background
                        score += Config.MM_SCORE_5
                        Logger.debug(f"Family Backgound matched (No Preference) {attr} for profile {profileId}, score incremented")
                        
            except Exception as e:
                Logger.error(f"Desired Family Background error: {e}")
                
            scores[profileId] = score
            match_and_values["MatchedHobbies"] = matched_hobbies
            match_and_values["MatchedProperties"] = properties_mached
            match_and_values["UserPreference"] = user_preference_profile
            match_and_values["OtherPreference"] = other_preference_profile
            final_result_matched_properties[profileId] = match_and_values
            #     break
        return scores, final_result_matched_properties
    
    

    def find_all_matches(self, profile_id, other_profiles = None):
        db, cursorDb = _database.get_connection()
        Logger.info(f"Starting find_all_matches for profile_id: {profile_id}")
        user_preferences = self.get_user_preferences(profile_id)
        if len(user_preferences) == 0:
            Logger.warning(f"User Preferance data or Profile data not found for the user id: {profile_id}")
            return pd.DataFrame(), {}, {}
        
        user_preferences = user_preferences[0]
        
        other_preferences = self.get_other_preferences_except_user(profile_id)
        if len(other_preferences) == 0:
            Logger.warning(f"User Preferance data or Profile data not found for the user id: {profile_id}")
            return pd.DataFrame(), {}, {}
        
        main_matrimonial = self.get_main_matrimonial_data(profile_id)
        if len(main_matrimonial)==0:
            print("NO User Found")
            Logger.warning(f"No matrimonial found for user ID: {profile_id} or may be that already done matchmaking")
            
            # matchedMakingStatus = self.check_matchmaking_done_already(profile_id)
            # if len(matchedMakingStatus) != 0:
            #     Logger.warning(f"Match making already competed for this profile id: {profile_id} updating status in queued.")
            #     cursorDb.execute(querys.UpdateMatchQueuedFlag(matched_flag=1, profileId=profile_id, processing_flag=0))
            #     db.commit()  
            # return pd.DataFrame(), {}, {}
        
        
        main_matrimonial = main_matrimonial[0]
        
        main_matrimonial_gender = main_matrimonial['Gender'] if len(main_matrimonial) > 0 else ''
        
        scores_preference: list = []
        scores_preference, match_and_values_preference = self.calculate_scores_preference(main_matrimonial, other_preferences, user_preferences)
        scores_preference = {key: value for key, value in scores_preference.items() if value != 0}
        
        other_profiles = scores_preference.keys()
        if other_profiles == None or len(other_profiles) == 0:
            other_matrimonial = self.get_other_matrimonial_data_opposite_gender(main_matrimonial_gender, profile_id)
        else:
            other_profile_id_list  = ', '.join(str(num) for num in other_profiles)
            other_matrimonial = self.get_other_matrimonial_data_for_ids(main_matrimonial_gender, other_profile_id_list)
        
        print("TOtal itesm:", len(other_matrimonial))
        if len(other_matrimonial) == 0:
            Logger.warning(f"NO Other User Found for Matchmaking With Opposite Gender: {main_matrimonial_gender}")
            cursorDb.execute(querys.UpdateMatchQueuedFlag(matched_flag=0, profileId=profile_id, processing_flag=0))
            return pd.DataFrame(), {}, {}
        
        # remove ids that has already match making done
        try:
            alreadyMatched = self.get_already_matched_profileIds(profile_id)
            Logger.info(f"Already Matched: {alreadyMatched}")
            
            if len(alreadyMatched) > 0:
                for alreadyMatchedId in alreadyMatched:
                    for item in other_matrimonial:
                        if item['ProfileId'] == alreadyMatchedId["OtherProfileId"]:
                            Logger.warning(f"Removing already matched profile id: {alreadyMatchedId['OtherProfileId']}")
                            other_matrimonial.remove(item)
        except Exception as e:
            Logger.error(f"Error while removing already matched profiles: {e}")
        # return
        # print("Total items:", len(other_matrimonial))
        Logger.info(f"Starting to calculate scores for profile_id: {profile_id} with matrimonial {other_matrimonial}")
        res = MultiProcess()
        
        # scores, gun_scores = res.process(self.calculate_scores,main_matrimonial, other_preferences, user_preferences)
        # scores_preference, match_and_values = self.calculate_scores_preference(main_matrimonial, other_preferences, user_preferences)
        
        # scores, gun_scores, match_and_values = self.calculate_scores_matrimonial(main_matrimonial, other_matrimonial, user_preferences)
        preferences = {}
        preferences["UserPreference"] = user_preferences
        preferences["OtherPreference"] = other_preferences
        
        scores, gun_scores, match_and_values = self.calculate_scores_matrimonial(main_matrimonial, other_matrimonial, preferences)
        # scores, gun_scores, match_and_values = res.process(self.calculate_scores_matrimonial,main_matrimonial, other_matrimonial, preferences)
        
        for key, value in scores_preference.items():
            if scores.__contains__(key):
                print(key, value)
                Logger.info(f"Adding preference score: {value} for profile_id: {key} to main score")
                scores[key] = value + scores[key]
            
        for key, value in match_and_values.items():
            print(key, value)
            if match_and_values.__contains__(key):
                other_preference = match_and_values_preference[key]["OtherPreference"]
                user_preference = match_and_values_preference[key]["UserPreference"]
                user_preference_main = match_and_values[key]["UserPreference"]
                
                comibed_preference = {**user_preference, **user_preference_main}
                final_user_preference = {**user_preference_main, **comibed_preference}
                
                match_and_values[key]["UserPreference"] = final_user_preference
                match_and_values[key]["OtherPreference"] = other_preference
                Logger.info(f"Adding preference score: {value} for profile_id: {key} to main preference")
            
        
        print(scores)
        Logger.info(f"Scores calculated for profile_id: {profile_id}")
        Logger.debug(f"Calculated scores: {scores}")
    
        scores_df = pd.DataFrame(scores.items(), columns=['ProfileId', 'Score'])
        sorted_scores_df = scores_df.sort_values(by='Score', ascending=False)
        
        Logger.info(f"Sorted scores for profile_id {profile_id} obtained")
        Logger.debug(f"Sorted scores DataFrame: {sorted_scores_df}")
        return sorted_scores_df.to_dict(orient='records'), gun_scores, match_and_values
    