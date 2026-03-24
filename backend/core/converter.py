from pypdf import PdfReader
import os


def extract_text(pdf_path: str):
    if not pdf_path:
        raise FileNotFoundError("File not found")