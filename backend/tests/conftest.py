import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.db import get_session
from backend.models.users import *
from backend.core.rate_limiting import limiter

database_url = "sqlite://"
engine = create_engine(url=database_url,
                       connect_args={"check_same_thread":False},
                       poolclass=StaticPool)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def session_overrides():
        return session
    
    app.dependency_overrides[get_session] = session_overrides
    limiter.enabled = False
    
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()