import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # 測試 session 啟動時建立所有資料表
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        if transaction.is_active:
            transaction.rollback()
        session.close()
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    # 覆寫 FastAPI 的 get_db 依賴
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def test_bookmark(db_session):
    from app.models.database import Bookmark
    bookmark = Bookmark(
        url="https://example.com",
        title="Example",
        description="An example bookmark"
    )
    db_session.add(bookmark)
    db_session.commit()
    db_session.refresh(bookmark)
    return bookmark

