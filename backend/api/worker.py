import os
from celery import Celery
from backend.core.converter import extract_text, text_to_audio

app = Celery(
    "audio_task",
    backend="redis://127.0.0.1:6379/0",
    broker="redis://127.0.0.1:6379/0"
)

@app.task(name="audio-pdf")
def pdf_to_audio(pdf_path, output_path):
    try:
        text = extract_text(pdf_path=pdf_path)
        text_to_audio(text=text, output_path=output_path)
        
        if os.path.exists(pdf_path):
            os.remove(path=pdf_path)

        return {
            "status":"success",
            "file":output_path
        }

    except Exception as e:
        return {
            "status":"failed",
            "error": str(e)
        }
