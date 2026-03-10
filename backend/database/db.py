import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

from core.dependencies import check_null_env

load_dotenv()
DATABASE_URL = check_null_env(os.getenv("DATABASE_URL"))
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False})

def get_session():
    with Session(engine) as session:
        yield session
