
import PyPDF2
import fitz
from app.extentions.logger import Logger 

class PdfExtracter:
    def __init__(self):
        pass

    @staticmethod
    def extract_text_from_pdf(file):
        text = ""
        Logger.info(f"Opening PDF file: {file}")
        with open(file, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                Logger.info(f"PDF file contains {page_num} pages")
                page = reader.pages[page_num]
                text += page.extract_text()
        
        Logger.info("Text extraction from PDF successful")
        return text
    
    @staticmethod
    def extract_text_from_pdf_url(url):
        text = ""
        Logger.info(f"Downloading PDF from URL: {url}")
        doc = fitz.open(url)
        Logger.info("Opening PDF document")
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)  # load a page
            Logger.info(f"Extracting text from page")
            text += page.get_text("text")
            Logger.info("Text extraction from PDF completed successfully")
        return text 

        