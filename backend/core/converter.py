from pypdf import PdfReader
from gtts import gTTS
import os


def extract_text(pdf_path: str):
    """Function that reads pdf by taking pdf path and returning the text"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError("File not found")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted_text = page.extract_text().replace("/n", " ").replace("/r", " ").strip()
        text += extracted_text + " "

    return text

def text_to_audio(text:str, output_path:str, language="en"):
    if not text:
        raise ValueError("No text provided")
    audio = gTTS(text=text, lang=language, slow=False)
    audio.save(output_path)