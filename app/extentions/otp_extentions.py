import requests
import json
from app.extentions.logger import Logger 

def send_otp():
    form_data = {
    'phone_country': "+91",
    'phone_no': "7505954930",
    'client_id': "11304601485875195718"
    }

    headers = {
    'Content-Type': 'multipart/form-data', 
}
    Logger.info("Sending OTP request to external service")
    response = requests.post('https://auth.phone.email/submit-login', data=form_data, headers=headers)
    Logger.info("Received response from OTP service")
    Logger.debug(f"Response headers: {response.headers}")
    Logger.debug(f"Response JSON: {response.json()}")
    
    responseDict = json.loads(response.text)
    Logger.debug(f"Parsed response JSON: {responseDict}")
    

def verify_otp():
    form_data = {
    'otp': "625222",
    'device': "",
    'business_name': "miiscoLLP",
    'redirect_url': "https://instagram.com",
    'client_id': "11304601485875195718"
}

    headers = {
    'Cookie': 'PHPSESSID=spn1btvej21hs4vs34onk4is1a;'
}
    Logger.info("Sending OTP verification request to external service")
    response = requests.post('https://auth.phone.email/verify-login', files=form_data, headers=headers)
    Logger.info("Received response from OTP verification service")
    responseDict = json.loads(response.text)
    Logger.debug(f"Response JSON: {responseDict}")
    # print(responseDict)

def generate_otp():
    import random
    Logger.info(f"Generated OTP")
    return random.randint(1000, 9999)

# verify_otp()