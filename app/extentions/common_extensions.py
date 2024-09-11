from config import Config
import hashlib
import datetime
import random
from flask import Request
import string
import json
import jwt
import os
from .pdf_extractor import PdfExtracter
from .chatgpt import Chatgpt
from app.extentions.logger import Logger 
import socket
import re
from app.extentions.regex_extraction import *

users_otp = {}
query_payload = payload = {
    "name": "",
    "gender": "",
    "dob": "",
    "time":"",
    "heightCM": "",
    "weightKG": "",
    "bloodGroup": "",
    "complexion": "",
    "motherTongue": "",
    "maritalStatus": "",
    "subCaste": "",
    "gotra": "",
    "address": "",
    "phoneNumber": "",
    "email": "",
    "city": "",
    "state": "",
    "country": "",
    "zipCode": "",
    "fatherName": "",
    "motherName": "",
    "highestDegree": "",
    "institution": "",
    "yearOfPassing": "",
    "additionalQualification": "",
    "occupation": "",
    "occupationCompany": "",
    "occupationLocation": "",
    "annualIncomeINR": "",
    "hobbies": "",
    "languagesKnown": "",
    "aboutMe": ""
}






def GetMD5Hash(text: str):
    Logger.debug(f"Starting GetMD5Hash function with input: {text}")
    hash_object = hashlib.md5()
    hash_object.update(text.encode())
    Logger.debug(f"Text hashed successfully: {text}")
    return hash_object.hexdigest()

def get_project_root():
    current_dir = os.path.abspath(os.getcwd())
    while not os.path.exists(os.path.join(current_dir, 'app')):
        current_dir = os.path.dirname(current_dir)
        if current_dir == os.path.dirname(current_dir):
            # Reached the root directory without finding the marker file
            raise Exception("Marker file not found in project hierarchy")
    Logger.info(f"Project root directory found: {current_dir}")
    return current_dir

def is_null_or_empty(text):
    text = str(text)
    if text == None:
        Logger.debug(f"Checking if text is null or empty: {text}")
        return True
    if text == "":
        Logger.debug("Text is null or empty")
        return True
    if text == " ":
        Logger.debug("Text is not null or empty")
        return True
    if text == "None":
        Logger.debug("Text is not null or empty")
        return True
    if text == "null":
        Logger.debug("Text is not null or empty")
        return True
    if text == "Null":
        Logger.debug("Text is not null or empty")
    if text == '0':
        return True
    return False

def is_number_zero(text):
    try:
        Logger.debug(f"Checking if '{text}' is a number zero")
        if(bool(text) == True or bool(text) == False):
            Logger.debug(f"'{text}' is a boolean value, returning False")
            return False
        
        number = int(text)
        if number == 0:
            Logger.debug(f"'{text}' is zero")
            return True
        Logger.debug(f"'{text}' is not zero")
        return False
    except Exception as e:
        Logger.error(f"Exception occur in is_number_zero function {e}")
        return False

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        Logger.debug(f"Generating payload for user ID: {user_id}")
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days = Config.JWT_AUTH_EXPIRE_DAY, seconds = Config.JWT_AUTH_EXPIRE_MINUTE, minutes = Config.JWT_AUTH_EXPIRE_SECOND),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        Logger.debug(f"Encoding JWT token with payload: {payload}")
        Logger.info(f"Auth token generated successfully for user ID: {user_id}")
        return jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        Logger.error(f"Error occurred while generating auth token for user ID {e}")
        return e
    

def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        Logger.debug("Decoding JWT token")
        payload = jwt.decode(auth_token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        Logger.info("JWT token decoded successfully")
        return payload['sub']
    except jwt.ExpiredSignatureError:
        Logger.error("Signature expired. Please log in again.")
        return "Signature expired. Please log in again."
    except jwt.InvalidTokenError:
        Logger.error("Invalid token. Please log in again.")
        return "Invalid token. Please log in again."
    
    
def get_random_name(phone):
    
    if is_null_or_empty(phone):
        phone = '1234'
    # Define the character sets for first and last names
    Logger.debug(f"Generating random name for phone number: {phone}")
    nameKey = str(phone)
    vowels = "aeiou"
    consonants = "".join(set(string.ascii_lowercase) - set(vowels))

    # Generate a random first name
    first_name_length = random.randint(4, 8)
    first_name = "".join(random.choice(consonants) + random.choice(vowels) for _ in range(first_name_length))

    # Capitalize the first letter of each name
    first_name = first_name.capitalize()

    # Combine the first and last names
    full_name = f"{first_name + nameKey[0:4]}"
    Logger.info(f"Generated random name: {full_name}")

    return full_name

def get_phone_number(phone:str):
    try:
        if is_null_or_empty(phone):
            return 0

        
        phone = phone.replace("-", "")
        phone = phone.replace("#", "")
        phone = phone.replace("*", "")
        phone = phone.replace(" ", "")
        phone = phone.replace("_", "")
        if phone.__contains__("+91"):
                phone = phone.replace("+91", "")
        
        if len(phone) > 15:
            
            parts = re.split(r"[,/]", phone)
            return int(parts[0])
        else:
            return int(phone)
    except:
        try:
            return int(phone.replace("+91", ""))
        except:
            return 0

def generate_random_number(length: int = 4):
    if length <= 0:
        raise ValueError("Length must be a positive integer.")
    Logger.debug(f"Generating random number with length: {length}")
    
    # The range to choose from: 10^(length-1) to (10^length)-1
    start = 10**(length-1)
    end = (10**length) - 1
    Logger.info(f"Generated random number: {start}")
    
    return random.randint(start, end)


def check_request_authorized(request: Request):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            Logger.error("Bearer token malformed")
            return json.dumps({"status": "failed", "message": "Bearer token malformed"}), 401
    else:
        auth_token = ''
    
    if auth_token:
        decoded_token: str = decode_auth_token(auth_token)
        Logger.debug(f"Decoded token: {decoded_token}")
        
        if "Signature expired" in str(decoded_token):
            Logger.error("Token expired. Please log in again")
            return json.dumps({"status": "failed", "message": "Token expired. Please log in again"}), 401
        elif "Invalid token" in str(decoded_token):
            Logger.error("Invalid token. Please log in again")
            return json.dumps({"status": "failed", "message": "Invalid token. Please log in again"}), 401
        else:
            Logger.info("Token validated successfully")
            return ""
    else:
        Logger.error("Token is missing")
        return json.dumps({"error": "Token is missing!"}), 401


def validate_data(data, key: str):
    errors = {}
    try:
        Logger.debug(f"Validating {key} in data")
        if key not in data:
            errors[key] = f"{key} field is required"
            Logger.error(f"{key} field is required")
        elif is_null_or_empty(data[key]):
            errors[key] = f"{key} cannot be null or empty"
            Logger.error(f"{key} cannot be null or empty")
        elif str(data[key]).isnumeric() == False:
            errors[key] = f"please fill numbers only"
            Logger.error(f"Invalid data format for {key}: Please fill numbers only")
            
        if len(errors) != 0:
            return json.dumps({"status": "failed", 'message':errors[key]}), 400
        else:
            return None
    except Exception as e:
        Logger.error(f"Validation error: {e}")
        return json.dumps({"status": "failed", 'message': f"Something went wrong {e}"}), 400
    
def validate_string_data(data, key: str):
    errors = {}
    try:
        Logger.debug(f"Validating {key} in data: {data}")
        if key not in data:
            errors[key] = f"{key} field is required"
            Logger.error(f"{key} field is required")
        elif is_null_or_empty(data[key]):
            errors[key] = f"{key} cannot be null or empty"
            Logger.error(f"{key} cannot be null or empty")
        if len(errors) != 0:
            Logger.error(f"Validation failed for {key}: {errors[key]}")
            return json.dumps({'error':errors[key]}), 400
        else:
            Logger.info(f"{key} validated successfully")
            return None
    except Exception as e:
        Logger.error(f"Validation error: {e}")
        return json.dumps({'error': f"Something went wrong {e}"}), 400
    
def validate_phone_number(phone: int) -> str:
    key = 'phone'
    errors = {}
    try:
        Logger.debug(f"Validating {key}: {phone}")
        if len(str(phone)) <=9:
            errors[key] = f"Invalid {key} number. Please fill correctly"
            Logger.error(f"Invalid {key} number: {phone}")
        if len(errors) != 0:
            Logger.error(f"Validation failed for {key}: {errors[key]}")
            return json.dumps({"status": "failed", 'message':errors[key]}), 400
        else:
            Logger.info(f"{key} validated successfully: {phone}")
            return None
    except Exception as e:
        Logger.error(f"Validation error: {e}")
        return json.dumps({"status": "failed", 'message': f"Something went wrong {e}"}), 400
    
def chatgpt_pdf_to_json(pdfFilePath) -> str:
    payload = query_payload
    chatgpt = Chatgpt()
    pdfText = PdfExtracter.extract_text_from_pdf_url(pdfFilePath)
    if len(pdfText) < 100:
        Logger.error("PDF text is too short to process")
        return ""
    Logger.debug(f"Extracted PDF text: {pdfText}")
    response = chatgpt.chat(pdfText, payload)
    Logger.info(f"Data Fetched: {response}")
    return response

def extract_text_from_pdf(pdfFilePath):
    pdfText = PdfExtracter.extract_text_from_pdf_url(pdfFilePath)
    if len(pdfText) < 100:
        Logger.error("PDF text is too short to process")
        return ""
    Logger.debug(f"Extracted PDF text: {pdfText}")
    return pdfText
    

# def get_phone_number_by_regex_from_pdf(pdfFilePath) -> str:
#     pdfText = PdfExtracter.extract_text_from_pdf_url(pdfFilePath)
#     if len(pdfText) < 100:
#         Logger.error("PDF text is too short to process")
#         return ""
#     Logger.debug(f"Extracted PDF text: {pdfText}")
#     phone_numbers = extract_phone_numbers(pdfText)
#     phone_number = ""
#     try:
#         phone_number = phone_numbers[0]
#     except:
#         phone_number
#     return phone_number

# def extract_phone_numbers(text):
#     # Regular expression for phone numbers
#     phone_regex = re.compile(r'(\d{10}|\d{12})')
    
#     # Find all phone numbers in the text
#     phone_numbers = phone_regex.findall(text)
    
#     # Join the extracted groups into a proper phone number format
#     extracted_numbers = [''.join(number) for number in phone_numbers]
    
#     return extracted_numbers

def extract_zip_code(pdfFilePath):
    pdfText = PdfExtracter.extract_text_from_pdf_url(pdfFilePath)
    if len(pdfText) < 100:
        Logger.error("PDF text is too short to process")
        return ""
    Logger.debug(f"Extracted PDF text: {pdfText}")
    
    # Regular expression for phone numbers
    phone_regex =  re.compile(r'(?<!\d)\d{6}(?!\d)')
    
    # Find all phone numbers in the text
    zip_codes = phone_regex.findall(pdfText)
    zip_code = ''
    
    # Join the extracted groups into a proper phone number format
    extracted_zipcodes = [''.join(number) for number in zip_codes]
    if len(zip_codes) > 0:
        zip_code = extracted_zipcodes[0]
    
    return zip_code

def chatgpt_pdf_to_database_query_json(pdfFilePath) -> str:
    chatgpt = Chatgpt()
    pdfText = PdfExtracter.extract_text_from_pdf_url(pdfFilePath)
    response = chatgpt.chat(pdfText, query_payload)
    Logger.debug(f"ChatGPT response: {response}")
    return response

def check_missing_keys(data, keys: list):
    Logger.info("Starting check_missing_keys function")
    errors = {}
    for key in keys:
        Logger.debug(f"Checking key: {key}")
        if key not in data:
            errors[key] = f"{key} field is required"
            Logger.debug(f"Key '{key}' is missing in data")
        elif is_null_or_empty(data[key]) or is_number_zero(data[key]):
            errors[key] = f"{key} cannot be null or empty"
            Logger.debug(f"Key '{key}' is null, empty, or zero")

    if len(errors) != 0:
        Logger.warning("Validation failed, returning error response")
        return json.dumps({"status": "failed", 'message':errors}), 400
    else:
        Logger.info("Validation successful, no missing keys found")
        return None

def check_single_missing_key(data, key: str):
    Logger.info("Starting check_single_missing_key function")
    errors = {}
    if key not in data:
        errors[key] = f"{key} field is required"
        Logger.debug(f"Key '{key}' is missing in data")
    elif is_null_or_empty(data[key]) or is_number_zero(data[key]):
        errors[key] = f"{key} cannot be null or empty"
        Logger.debug(f"Key '{key}' is null, empty, or zero")

    if len(errors) != 0:
        Logger.warning("Validation failed, returning error response")
        return json.dumps({"status": "failed", 'message':errors}), 400
    else:
        Logger.info("Validation successful, no missing key found")
        return None


def compare_profiles(main_profile, other_profiles):
    def calculate_similarity(main, other):
        score = 0

        # Compare Nakshatra
        Logger.debug(f"Comparing Nakshatra: Main - {main['nakshatra']['id']}, Other - {other['nakshatra']['id']}")
        if main['nakshatra']['id'] == other['nakshatra']['id']:
            score += 20
        
        # Compare Chandra Rasi
        Logger.debug(f"Comparing Chandra Rasi: Main - {main['chandra_rasi']['id']}, Other - {other['chandra_rasi']['id']}")
        if main['chandra_rasi']['id'] == other['chandra_rasi']['id']:
            score += 20
        
        # Compare Soorya Rasi
        Logger.debug(f"Comparing Soorya Rasi: Main - {main['soorya_rasi']['id']}, Other - {other['soorya_rasi']['id']}")
        if main['soorya_rasi']['id'] == other['soorya_rasi']['id']:
            score += 20
        
        # Compare Zodiac
        Logger.debug(f"Comparing Zodiac: Main - {main['zodiac']['id']}, Other - {other['zodiac']['id']}")
        if main['zodiac']['id'] == other['zodiac']['id']:
            score += 10
        
        # Compare Additional Info (some key attributes)
        main_additional = main['additional_info']
        other_additional = other['additional_info']
        Logger.debug(f"Comparing Deity: Main - {main_additional['deity']}, Other - {other_additional['deity']}")
        if main_additional['deity'] == other_additional['deity']:
            score += 5
        Logger.debug(f"Comparing Ganam: Main - {main_additional['ganam']}, Other - {other_additional['ganam']}")
        if main_additional['ganam'] == other_additional['ganam']:
            score += 5
        Logger.debug(f"Comparing Animal Sign: Main - {main_additional['animal_sign']}, Other - {other_additional['animal_sign']}")
        if main_additional['animal_sign'] == other_additional['animal_sign']:
            score += 5
        Logger.debug(f"Comparing Nadi: Main - {main_additional['nadi']}, Other - {other_additional['nadi']}")
        if main_additional['nadi'] == other_additional['nadi']:
            score += 5
        
        return score

    # Calculate similarity scores for all other profiles
    scores = []
    for profile in other_profiles:
        Logger.info(f"Calculating similarity for profile: {profile}")
        similarity_score = calculate_similarity(main_profile, profile)
        scores.append((profile, similarity_score))
    
    # Sort profiles based on similarity score (descending)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 3 matches
    top_matches = scores[:3]
    Logger.info(f"Top 3 matches: {top_matches}")
    return top_matches

def feet_to_cm(feet):
    return int(feet * 30.48)

def sendMessage(number: int, msg: str):
    pass

def split_list(input_list, chunk_size):
    Logger.info(f"Splitting list into chunks of size {chunk_size}")
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

def calculate_age(dob, format = '%Y-%m-%d'):
    birth_date = datetime.datetime.strptime(dob, '%Y-%m-%d')
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def cm_to_feet(feet):
    feet = int(feet)
    return float(feet / 30.48)

def detect_environment():
    # Get the remote IP address of the client making the request
    ip_addresses = socket.gethostbyname_ex(socket.gethostname())[2]
    for ip in ip_addresses:
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'):
            return 'local'
    return "server"
    
def count_matching_hobbies(field1, field2):
# Split each field by commas and strip any leading/trailing whitespace
    hobbies1 = set(hobby.strip().lower() for hobby in field1.split(','))
    hobbies2 = set(hobby.strip().lower() for hobby in field2.split(','))

    # Find the intersection of both sets (common hobbies)
    common_hobbies = hobbies1 & hobbies2

    # Return the number of matched hobbies
    return len(common_hobbies), list(common_hobbies)

def get_score_percentage(score):
    total_points = 150
    percentage = (score / total_points) * 100
    return percentage

def remove_duplicates(input_string):
    # Split the string into a list of words
    words = input_string.split(",")
    
    # Initialize a set to keep track of seen words and a list for result
    seen = set()
    result = []
    
    # Iterate through the words
    for word in words:
        word: str = word.strip()
        if word not in seen:
            seen.add(word)   # Add the word to the seen set
            result.append(word)  # Append the word to the result list
    
    # Join the words back into a single string
    return ", ".join(result)

# Example usage
print(detect_environment())