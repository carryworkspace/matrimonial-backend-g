import requests
import json
from geopy.geocoders import Photon
from app.routes import closeDbConnection, _database
from app.extentions.common_extensions import is_null_or_empty
from app.models.astrological_model import AstrologicalDataModel
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.extentions.logger import Logger
from config import Config
import time
import math

class AstroService:
    def __init__(self):
        Logger.debug("Initializing AstroService...")
        self.base_url = Config.BASE_URL
        Logger.debug(f"Base URL set to: {self.base_url}", )
        self.access_token = self.get_token()
        Logger.debug(f"Access token retrieved: {self.access_token}" )
        self.conn, self.cursor = _database.get_connection()
        Logger.debug("Database connection established.")

    def get_token(self):
        Logger.debug("Fetching access token...")
        data = {
        "grant_type": Config.GRANT_TYPE,
        "client_id": Config.CLIENT_ID,
        "client_secret": Config.CLIENT_SECRET
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(f"{self.base_url}/token", data=json.dumps(data), headers=headers)
        json_response = response.json()
        Logger.info("Access token retrieved successfully.")
        return json_response["access_token"]

    def get_astro_data(self, datetime: str, latitude: str, longtitude: str):
        Logger.debug("Fetching astrology data...")
        # timestamp = "2024-06-25T12:20:12+05:30"

        encoded_timestamp = datetime.replace('+', '%2B')
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(f"{self.base_url}{Config.END_POINT}?ayanamsa=1&coordinates={latitude},{longtitude}&datetime={encoded_timestamp}", headers=headers)
        json_response = response.json()
        Logger.info("Astrology data retrieved successfully.")
        return json_response    
    
    def get_astro_data_for_male_and_female(self, boy_detail: dict, girl_detail: dict):
        
        # Increment the request count
    
        # Add the sleep time based on the number of requests
        # if Config.REQUEST == 0:
        #     Config.START_TIME = time.time()
        
        
        # Config.END_TIME = time.time()
        if Config.REQUEST >= 60:
            # total_time_taken = Config.END_TIME - Config.START_TIME
            sleep_time = 60
        #     print("Total Time Taken: ", total_time_taken)
        #     sleep_time =  60 - math.floor(total_time_taken)
            print(f"Sleeping for {sleep_time} /seconds.")
            Config.REQUEST = 0
            time.sleep(sleep_time)
        else:
            Config.REQUEST += 1
            print("No additional sleep needed.")

        # Handle the request (placeholder for your actual request handling logic)
        print("Handling request number", Config.REQUEST)
            
        
        Logger.debug("Fetching astrology data for male and female...")
        # timestamp = "2024-06-25T12:20:12+05:30"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            'boy_dob': f"{boy_detail['dob']}T{boy_detail['tob']}:00+05:30",
            'girl_dob': f"{girl_detail['dob']}T{girl_detail['tob']}:00+05:30",
            'girl_coordinates': girl_detail['cordinates'],
            'boy_coordinates': boy_detail['cordinates'],
            'ayanamsa': 1
    }
        response = requests.get(f"{self.base_url}/v2/astrology/kundli-matching", params=params, headers=headers)
        json_response = response.json()
        Logger.info("Astrology data for male and female retrieved successfully.")
        print(json_response)
        return json_response 

    def get_coordinates(self,address: str):
        Logger.debug(f"Fetching coordinates for address: {address}")
        geolocator = Photon(user_agent="geoapiExercises")
        try:
            location = geolocator.geocode(address)
            if location == None:
                Logger.warning(f"No coordinates found for exact address: {address}. Attempting alternative lookup.")
                first, address = address.split(',', 1)
                location = geolocator.geocode(f"{address}")
            if location:
                Logger.info(f"Coordinates found for address")
                return location.latitude, location.longitude
            else:
                Logger.warning(f"No coordinates found for address: {address}")
                return 19.07, 72.87
        except Exception as e:
            return 19.07, 72.87
    
    def get_main_matrimonial_data(self, profile_id):
        query = f"SELECT * FROM MatrimonialProfile_M WHERE ProfileId = {profile_id} and astro_flag = 0"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        Logger.info(f"Matrimonial data fetched successfully for ProfileId: {profile_id}")
        return result[0]
    
    
    def get_other_matrimonial_data(self, user_gender: str, profile_id):
        user_gender = user_gender[0]
        if user_gender.lower() == 'male':
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'female' AND ProfileId != {profile_id};"
        else:
            query = f"SELECT * FROM MatrimonialProfile_M WHERE Gender = 'male' AND ProfileId != {profile_id};"
        
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        Logger.info("Fetched other matrimonial data successfully.")
        return result
        
    def get_and_insert_astrological_data(self, profileId: int): 
        user_dict = self.get_main_matrimonial_data(profileId)
        
        other_dictList = self.get_other_matrimonial_data(user_dict["Gender"], profileId)
        main_address = user_dict.get('Address', None)
        main_date = user_dict.get('Dob', None)
        main_time = user_dict.get('time', None)
        if is_null_or_empty(main_address):
            main_address = f"{user_dict.get('City', '')}, {user_dict.get('State', '')}, {user_dict.get('Country', '')}"
        
        if is_null_or_empty(main_date):
            main_date = '2024-06-25'
        
        if is_null_or_empty(main_time):
            main_time = "14:20"
        
        main_lat, main_lon = self.get_coordinates(main_address)
        main_profile_object = {
            'dob': main_date,
            'tob': main_time,
            'cordinates': f"{main_lat},{main_lon}",
        }
        
        for other_dict in other_dictList:
            other_address = other_dict.get('Address', None)
            other_date = user_dict.get('Dob', None)
            other_time = user_dict.get('time', None)
                
            if is_null_or_empty(other_address):
                Logger.warning(f"Failed to fetch coordinates for other address: {other_address}")
                other_address = f"{user_dict.get('City', '')}, {user_dict.get('State', '')}, {user_dict.get('Country', '')}"
        
            if is_null_or_empty(other_date):
                Logger.warning(f"Failed to fetch date: {other_date}")
                other_date = '2024-06-25'
            
            if is_null_or_empty(other_time):
                Logger.warning(f"Failed to fetch time: {other_time}")
                other_time = "14:20"

            
            other_lat, other_lon = self.get_coordinates(other_address)
            other_profile_object = {
            'dob': other_date,
            'tob': other_time,
            'cordinates': f"{other_lat},{other_lon}",
        }
            
            if other_lat and other_lon:
                
                astro_data = self.get_astro_data_for_male_and_female(main_profile_object, other_profile_object)
                astro_dict = AstrologicalDataModel.fill_model(astro_data)
                Logger.info(f"Astrological data processed successfully for profiles {profileId} and {other_dict['ProfileId']}")
                return astro_data["data"]
            else:
                Logger.warning(f"Failed to get astrological data for profiles {profileId} and {other_dict['ProfileId']}")
                return None
    
    def get_gunn_score(self, main_dict: dict, user_dict: dict):
        
        main_address = main_dict.get('City', None)
        main_date = main_dict.get('Dob', None)
        main_time = main_dict.get('Time', None)
        if is_null_or_empty(main_address):
            Logger.warning(f"Failed to fetch coordinates for address")
            main_address = f"{main_dict.get('City', '')}, {main_dict.get('State', '')}, {main_dict.get('Country', '')}"
        
        if is_null_or_empty(main_date):
            Logger.warning(f"Failed to fetch astrology main profile date of birth. setting up default date")
            main_date = '2024-06-25'
        
        if is_null_or_empty(main_time):
            Logger.warning(f"Failed to fetch astrology main profile time. setting up default time")
            main_time = "14:20"
        
        main_lat, main_lon = self.get_coordinates(main_address)
        main_profile_object = {
            'dob': main_date,
            'tob': main_time,
            'cordinates': f"{main_lat},{main_lon}",
        }
        other_address = user_dict.get('City', None)
        other_date = user_dict.get('Dob', None)
        other_time = user_dict.get('Time', None)
            
        if is_null_or_empty(other_address):
            Logger.warning("Other profile address is missing or empty, setting default address.")
            other_address = f"{user_dict.get('City', '')}, {user_dict.get('State', '')}, {user_dict.get('Country', '')}"
    
        if is_null_or_empty(other_date):
            Logger.warning("Other profile date of birth is missing or empty, setting default date.")
            other_date = '2024-06-25'
        
        if is_null_or_empty(other_time):
            Logger.warning("Other profile time is missing or empty, setting default time.")
            other_time = "14:20"

        
        other_lat, other_lon = self.get_coordinates(other_address)
        
        other_profile_object = {
        'dob': other_date,
        'tob': other_time,
        'cordinates': f"{other_lat},{other_lon}",
        }
        # print("OTHER",other_profile_object)
        if other_lat and other_lon:
            astro_data = self.get_astro_data_for_male_and_female(main_profile_object, other_profile_object)
            # user_dict.update(astro_data)
            # print(astro_data)
            try:
                status = astro_data['status']
                if status == 'error':
                    sufficient_balance = astro_data['errors'][0]['detail'].__contains__('sufficient credit balance')
                    # print("SUFFICIENT BALANCE: ", sufficient_balance)
                    if sufficient_balance:
                        Logger.error("Astro Api Credit balance has over you need to renew the plan. or you don't have enough balance to make requet.")
                else: 
                    astro_data = astro_data["data"]
                    astro_dict = AstrologicalDataModel.fill_model(astro_data)
                    Logger.info("Astrological data processed successfully.")
                    # print(astro_dict.__dict__)
                    return astro_dict
            except Exception as e:
                print("There is an error in status and details", e)
                Logger.error("invalid keys in astro data response status or detail")
            
                
        else:
            Logger.info("Astrological data not processed successfully.")
            return None
    
#res = AstroService().get_astro_data_for_male_and_female()
#print(res)