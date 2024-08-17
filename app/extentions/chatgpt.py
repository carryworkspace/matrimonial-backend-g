import openai
import time
import asyncio
from openai import OpenAI
from config import Config
from app.extentions.pdf_extractor import PdfExtracter
from app.extentions.logger import Logger 
from app.utils import contains_any
import json
import re


class Chatgpt:
    def __init__(self):
        self.client = OpenAI(api_key=Config.CHAT_GPT_API_KEY)
        self.tries = 0
    
    def chat(self,text, payload):
        self.tries = 0
        
        msg = f"please read this text {text} and fill the provided json payload : {payload} and correct the formatting of dob - yyyy-MM-dd and height in cm from fts and time in 24 hours format and fill subcaste withh help of name and please fill gender using name only and please fill the state city country and address and mobile or phone number mandatory and fill all fields of the payload json and if subCaste not provided leave empty and  and return json content only"
        Logger.info("Chatgpt Requesting your message..... waiting for response")
        response = self.client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[{
        "role": "user",
        "content": [
                {
                "type": "text",
                "text": msg
                }
            ]
        }],
        temperature=1,
        max_tokens=10000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        chatgpt_response = response.choices[0].message.content
        Logger.info("Received response from OpenAI")
        Logger.debug(f"Response From GPT: {chatgpt_response}")
        

        exeption, chatgpt_response = self.IsResponseHaveError(chatgpt_response) 
        
                
        errorList = ["sorry, ", "i'm sorry, ", "i am sorry, ", "apologize"]
        # while (contains_any(chatgpt_response.lower(), errorList) or exeption) and self.tries < 3:
        while exeption and self.tries < 3:
            self.tries += 1
            chatgpt_response = self.chatAgain(text, payload)
            
            exeption, chatgpt_response = self.IsResponseHaveError(chatgpt_response)
            time.sleep(1)
            Logger.info("Retrying response from OpenAI")
            
        return chatgpt_response
    
    def IsResponseHaveError(self, response: str):
        exeption = False
        try:
                json.loads(response)
                exeption = False
        except:
            chatgpt_response_filtered = re.search(r'\{.*\}', response, re.DOTALL)
        
            if chatgpt_response_filtered:
                response = chatgpt_response_filtered.group(0)
                try:
                    json.loads(response)
                    exeption = False
                except:
                    exeption = True
            else: 
                exeption = True
        return exeption, response
    
    def chatAgain(self,text, payload):
        
        msg = f"please read this text {text} and fill the provided json payload : {payload} and correct the formatting of dob - yyyy-MM-dd and height in cm from fts and time in 24 hours format and fill subcaste withh help of name and please fill gender using name only and please fill the state city country and address and mobile or phone number mandatory and fill all fields of the payload json and if subCaste not provided leave empty and  and return json content only"
        Logger.info("Chatgpt Requesting your message..... waiting for response")
        response = self.client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[{
        "role": "user",
        "content": [
                {
                "type": "text",
                "text": msg
                }
            ]
        }],
        temperature=1,
        max_tokens=10000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        chatgpt_response = response.choices[0].message.content
        Logger.info("Received response from OpenAI")
        Logger.debug(f"Response From GPT: {chatgpt_response}")
        
        return chatgpt_response
    


    industries = [
    "Accounting/Finance",
    "Administrative/Clerical",
    "Advertising/Marketing/PR",
    "Aerospace/Defense",
    "Agriculture/Forestry",
    "Architecture/Design",
    "Arts/Entertainment/Media",
    "Automotive",
    "Biotechnology",
    "Business Development",
    "Retail/Wholesale/Business",  
    "Construction/Facilities",
    "Consulting",
    "Customer Service",
    "Education/Training",
    "Energy/Utilities",
    "Engineering",
    "Environmental",
    "Executive Management",
    "Fashion",
    "Financial Services",
    "Food Services/Hospitality",
    "Government/Public Sector",
    "Healthcare",
    "Human Resources",
    "Information Technology",
    "Insurance",
    "Internet/E-commerce",
    "Legal",
    "Logistics/Transportation",
    "Manufacturing",
    "Nonprofit/NGO",
    "Pharmaceutical/Biotech",
    "Real Estate",
    "Retail/Wholesale",
    "Sales",
    "Science/Research",
    "Security/Law Enforcement",
    "Sports/Recreation",
    "Telecommunications",
    "Tourism/Travel",
    "Trades/Skilled Labor",
    "Writing/Editing/Publishing"
    ]

    def categorize_job_title(self,text):
        msg = f"Please categorize the following job title into the most appropriate category from the list provided: {text}. Categories include: {{{', '.join(self.industries)}}}. Just write the category name from the list above. If the job title specifically describes itself as a business, please write 'Business'.  If a job title can be in multiple categories and also belongs to Information Technology, prioritize Information Technology unless it specifically describes itself as a business."
        Logger.info("Requesting categorization of job title... waiting for response")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": msg
                    }
                ]
            }],
            temperature = 1,
            max_tokens = 1000,
            top_p = 1,
            frequency_penalty = 0,
            presence_penalty = 0
        )
        Logger.info("Received categorization response")
        return response.choices[0].message.content
    




    def matching_job_title(self,text1,text2):
        msg = f"Please categorize the following job title into the most appropriate category from the list provided: {text1} and {text2}. Categories include: {{{', '.join(self.industries)}}}. Just write the category name from the list above. If the job title specifically describes itself as a business, please write 'Business'.  If a job title can be in multiple categories and also belongs to Information Technology, prioritize Information Technology unless it specifically describes itself as a business."

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": msg
                    }
                ]
            }],
            temperature = 1,
            max_tokens = 1000,
            top_p = 1,
            frequency_penalty = 0,
            presence_penalty = 0
        )
        categorized_category = response.choices[0].message.content.strip()
        Logger.info("Received categorized category")

        category_text1 = self.categorize_job_title(text1)
        category_text2 = self.categorize_job_title(text2)

        if category_text1 == category_text2 == categorized_category:
            Logger.info("Category Matched")
            return Config.MM_SCORE_10
        else:
            Logger.info("Category not Matched")
            return 0
    
    def new_conversation(self):
        self.client = OpenAI(api_key=Config.CHAT_GPT_API_KEY)


# print(Chatgpt().matching_job_title("software tester","lawyer"))
