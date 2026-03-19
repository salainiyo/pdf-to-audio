import pytest
from sqlmodel import create_engine, StaticPool, SQLModel, Session
from fastapi.testclient import TestClient

from backend.models.users import User

database_url = "sqlite://"
engine = create_engine(url=database_url, connect_args={"check_same_thread":False}, poolclass=StaticPool)

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
    
    from backend.main import app
    from backend.database.db import get_session
    app.dependency_overrides[get_session] = session_overrides

    if hasattr(app.state, "limiter"):
        app.state.limiter.enabled = False

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()