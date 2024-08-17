import re
from app.extentions.logger import Logger
from app.extentions.pdf_extractor import PdfExtracter

def extract_dob(text):
    # Regular expression for matching common date formats
    date_regex = re.compile(
        r'(\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b)|'  # Matches dates like DD-MM-YYYY or MM/DD/YYYY
        r'(\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b)|'     # Matches dates like YYYY-MM-DD
        r'(\b\d{1,2}\s\w{3,9}\s\d{2,4}\b)'        # Matches dates like 12 Jan 2023
    )

    # Find all dates in the text
    dates = date_regex.findall(text)

    # Flatten and filter out empty strings
    dates = [date for group in dates for date in group if date]
    
    if len(dates) > 0:
        return dates[0]

    return dates

def extract_phone_numbers(text):
    # Regular expression for phone numbers
    phone_regex = re.compile(r'(\d{10}|\d{12})')
    
    # Find all phone numbers in the text
    phone_numbers = phone_regex.findall(text)
    
    # Join the extracted groups into a proper phone number format
    extracted_numbers = [''.join(number) for number in phone_numbers]
    
    if len(extracted_numbers) > 0:
        return extracted_numbers[0]
    return ""

def extract_zip_code(pdfText):
    
    # Regular expression for phone numbers
    zip_regex =  re.compile(r'(?<!\d)\d{6}(?!\d)')
    
    # Find all phone numbers in the text
    zip_codes = zip_regex.findall(pdfText)
    zip_code = ''
    
    # Join the extracted groups into a proper phone number format
    extracted_zipcodes = [''.join(number) for number in zip_codes]
    if len(zip_codes) > 0:
        zip_code = extracted_zipcodes[0]
    
    return zip_code

def extract_time(text):
    # Regular expression for matching time formats
    time_regex = re.compile(
        r'\b\d{1,2}:\d{2}(:\d{2})?\s?(AM|PM|am|pm)?\b'  # Matches times like 12:30, 12:30:45, 12:30 PM
    )

    # Find all times in the text
    times = time_regex.findall(text)
    
    # Join the time parts into a proper string
    extracted_times = [''.join(time).strip() for time in times]
    
    if len(extracted_times) > 0:
        return extracted_times[0]
    
    return ""

def extract_email(text):
    # Regular expression to match common email patterns
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    
    # Find all email addresses in the text
    emails = email_regex.findall(text)
    
    if len(emails) > 0:
        return emails[0]
    return ""