import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from pathlib import Path

from backend.core.dependencies import check_null_env

BACKEND_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BACKEND_DIR / "pdf_to_audio.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})

def get_session():
    with Session(engine) as session:
        yield session
