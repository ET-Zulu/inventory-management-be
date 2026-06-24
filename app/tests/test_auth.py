import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.core.database import get_session
from app.model.user import User
from app.model.refresh_token import RefreshToken
from app.core.security import get_password_hash
from app.model.enums import UserRole

# Setup SQLite in-memory DB for tests
sqlite_file_name = "sqlite:///./test.db"
engine = create_engine(sqlite_file_name, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=get_password_hash("StrongPassword123!"),
        role=UserRole.ADMIN,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def test_login(client: TestClient, test_user: User):
    response = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "StrongPassword123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == test_user.email

def test_refresh_token_and_logout(client: TestClient, test_user: User, session: Session):
    # 1. Login to get refresh token
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "StrongPassword123!"
    })
    refresh_token = login_resp.json()["refresh_token"]

    # 2. Refresh token
    refresh_resp = client.post("/api/v1/auth/refresh-token", json={
        "refresh_token": refresh_token
    })
    assert refresh_resp.status_code == 200
    new_refresh_token = refresh_resp.json()["refresh_token"]
    assert new_refresh_token != refresh_token

    # 3. Logout with new token
    logout_resp = client.post("/api/v1/auth/logout", json={
        "refresh_token": new_refresh_token
    })
    assert logout_resp.status_code == 200

    # 4. Try refresh again (should fail)
    fail_refresh = client.post("/api/v1/auth/refresh-token", json={
        "refresh_token": new_refresh_token
    })
    assert fail_refresh.status_code == 401

def test_invite_email(client: TestClient, test_user: User):
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "StrongPassword123!"
    })
    access_token = login_resp.json()["access_token"]
    
    # Send invite
    invite_resp = client.post(
        "/api/v1/auth/invite",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "email": "new_operator@example.com",
            "role": "operator"
        }
    )
    assert invite_resp.status_code == 200
    assert "invite_token" in invite_resp.json()
