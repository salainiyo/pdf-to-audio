import os
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from celery.result import AsyncResult

from backend.api.worker import pdf_to_audio, app as celery_app
from backend.core.rate_limiting import limiter

convert_router = APIRouter()

UPLOAD_DIR = Path("media_files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@convert_router.post("/convert")
@limiter.limit("5/minute")
async def convert_job(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File not found")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")
    
    job_id = str(uuid.uuid4())
    pdf_path = UPLOAD_DIR / f"{job_id}.pdf"
    output_path = UPLOAD_DIR / f"{job_id}.mp3"

    with open(pdf_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # Read in 1MB chunks
            buffer.write(chunk)

    task = pdf_to_audio.delay(str(pdf_path), str(output_path))
    
    return {
        "task_id": task.id,
        "job_id": job_id,
        "message": "Task received successfully"
    }

@convert_router.get("/convert/status")
async def convert_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == "PENDING":
        return {"status": "Pending", "message": "Waiting for worker to complete task"}
    
    elif task_result.state == "SUCCESS":
        result_data = task_result.result or {}
        return {
            "status": "Success",
            "message": "Task completed",
            "file": result_data.get("file")
        }
    
    elif task_result.state == "FAILURE":
        return {
            "status": "Failed",
            "error": str(task_result.info)
        }
    else:
        return {
            "status": task_result.state,
            "message": "Task in progress"
        }
    
@convert_router.get("/download/{job_id}")
async def audio_download(job_id: str):
    safe_filename = f"{job_id}.mp3"
    file_path = UPLOAD_DIR / safe_filename
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found or not ready")
        
    return FileResponse(
        path=file_path, 
        media_type="audio/mpeg", 
        filename=safe_filename
    )