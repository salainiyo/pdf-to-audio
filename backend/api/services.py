import shutil
import os
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from celery.result import AsyncResult

from backend.core.converter import text_to_audio, extract_text
from backend.api.worker import pdf_to_audio, app as celery_app

convert_router = APIRouter()

@convert_router.post("/convert")
async def convert_job(file:UploadFile=File(...)):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File not found")
    
    pdf_path = f"temp_{file.filename}"
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path = f"{file.filename.replace(".pdf", " ").strip()}.mp3"
    task = pdf_to_audio.delay(pdf_path, output_path)
    return {
        "task_id":task.id,
        "message":"Task received successfully"
    }

@convert_router.get("/convert/status")
async def convert_status(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == "PENDING":
        return {"status":"Pending", "message":"Waiting for worker to complete task"}
    
    elif task_result.state == "SUCCESS":
        result_data = task_result.result
        return {
            "status":"Success",
            "message":"Task completed",
            "file":result_data.get("file")
        }
    
    elif task_result.state == "FAILURE":
        return {
            "status":"Failed",
            "error":str(task_result.info)
        }
    else:
        return {
            "message":str(task_result.state)
        }
    
@convert_router.get("/download/{filename}")
async def audio_download(filename):
    if not filename:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(filename, media_type="audio/mpeg", filename=filename)
