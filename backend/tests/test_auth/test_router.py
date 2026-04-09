import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

from app.main import create_app


@pytest.fixture
def app(db_engine):
    from app.database import get_db
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    test_app = create_app()
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_google_auth_success(client, db_session):
    mock_google_response = {
        "sub": "google-user-123",
        "email": "user@gmail.com",
        "name": "Test User",
        "picture": "https://example.com/pic.jpg",
    }

    with patch("app.modules.auth.router.verify_google_token", return_value=mock_google_response):
        response = await client.post("/api/auth/google", json={"token": "fake-google-token"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_google_auth_invalid_token(client):
    with patch("app.modules.auth.router.verify_google_token", return_value=None):
        response = await client.post("/api/auth/google", json={"token": "bad-token"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_unauthorized(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
