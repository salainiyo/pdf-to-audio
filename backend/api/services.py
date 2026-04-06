import shutil
import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse

from backend.core.converter import text_to_audio, extract_text

convert_router = APIRouter()
