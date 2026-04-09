import uuid
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.models.user import User
from app.models.site import Site


@pytest.fixture
def test_user_id():
    return str(uuid.uuid4())


@pytest.fixture
def test_site_id():
    return str(uuid.uuid4())


@pytest.fixture
def app(db_session, test_user_id, test_site_id):
    application = create_app()

    async def mock_get_current_user():
        user = MagicMock()
        user.id = uuid.UUID(test_user_id)
        user.email = "test@example.com"
        user.default_llm_provider = "openai"
        user.openai_api_key = "test-key"
        user.anthropic_api_key = None
        user.together_api_key = None
        user.ollama_base_url = None
        return user

    async def mock_get_db():
        yield db_session

    from app.modules.auth.dependencies import get_current_user
    from app.database import get_db

    application.dependency_overrides[get_current_user] = mock_get_current_user
    application.dependency_overrides[get_db] = mock_get_db

    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def seeded_site(db_session, test_user_id, test_site_id):
    user = User(
        id=uuid.UUID(test_user_id),
        email="test@example.com",
        name="Test",
        google_id="g-gen-1",
    )
    db_session.add(user)
    await db_session.commit()

    site = Site(
        id=uuid.UUID(test_site_id),
        user_id=user.id,
        url="https://example.com",
        name="Example",
        description="A test product",
        niche="technology",
    )
    db_session.add(site)
    await db_session.commit()
    return site


@pytest.mark.asyncio
async def test_generate_content_endpoint(client, seeded_site, test_site_id):
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "Just launched something amazing! Check it out. #tech #launch"

    with patch("app.modules.content.router.create_llm_factory") as mock_factory_fn:
        mock_factory_fn.return_value.get.return_value = mock_llm
        response = await client.post(
            "/api/content/generate",
            json={
                "site_id": test_site_id,
                "platform": "twitter",
                "content_type": "tweet",
                "topic": "Product launch",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "twitter"
    assert data["status"] == "draft"
    assert "launch" in data["body"].lower()


@pytest.mark.asyncio
async def test_generate_content_with_keywords(client, seeded_site, test_site_id):
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = "AI marketing automation is the future. Here is why..."

    with patch("app.modules.content.router.create_llm_factory") as mock_factory_fn:
        mock_factory_fn.return_value.get.return_value = mock_llm
        response = await client.post(
            "/api/content/generate",
            json={
                "site_id": test_site_id,
                "platform": "linkedin",
                "content_type": "post",
                "topic": "AI in marketing",
                "tone": "authoritative",
                "keywords": ["ai marketing", "automation"],
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "linkedin"


@pytest.mark.asyncio
async def test_generate_content_site_not_found(client, seeded_site):
    fake_site_id = str(uuid.uuid4())
    mock_llm = AsyncMock()

    with patch("app.modules.content.router.create_llm_factory") as mock_factory_fn:
        mock_factory_fn.return_value.get.return_value = mock_llm
        response = await client.post(
            "/api/content/generate",
            json={
                "site_id": fake_site_id,
                "platform": "twitter",
                "content_type": "tweet",
                "topic": "Test",
            },
        )

    assert response.status_code == 404
