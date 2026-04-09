import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.models.user import User
from app.models.site import Site
from app.models.content import Content, ContentGroup


@pytest.fixture
def test_user_id():
    return str(uuid.uuid4())


@pytest.fixture
def test_site_id():
    return str(uuid.uuid4())


@pytest.fixture
def app(db_session, test_user_id, test_site_id):
    """Create app with overridden dependencies."""
    application = create_app()

    # Mock auth dependency
    async def mock_get_current_user():
        user = MagicMock()
        user.id = uuid.UUID(test_user_id)
        user.email = "test@example.com"
        return user

    # Mock DB dependency
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
        google_id="g-router-1",
    )
    db_session.add(user)
    await db_session.commit()

    site = Site(
        id=uuid.UUID(test_site_id),
        user_id=user.id,
        url="https://example.com",
        name="Example",
    )
    db_session.add(site)
    await db_session.commit()
    return site


@pytest.mark.asyncio
async def test_create_content(client, seeded_site, test_site_id):
    response = await client.post(
        "/api/content/",
        json={
            "site_id": test_site_id,
            "platform": "twitter",
            "content_type": "tweet",
            "title": "Test Tweet",
            "body": "Hello world from Amplifi!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["platform"] == "twitter"
    assert data["title"] == "Test Tweet"
    assert data["status"] == "draft"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_content_invalid_platform(client, seeded_site, test_site_id):
    response = await client.post(
        "/api/content/",
        json={
            "site_id": test_site_id,
            "platform": "tiktok",
            "content_type": "video",
            "title": "Test",
            "body": "Hello",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_content(client, seeded_site, test_site_id, db_session, test_user_id):
    for i in range(3):
        content = Content(
            site_id=uuid.UUID(test_site_id),
            user_id=uuid.UUID(test_user_id),
            platform="twitter",
            content_type="tweet",
            title=f"Tweet {i}",
            body=f"Content {i}",
            status="draft",
        )
        db_session.add(content)
    await db_session.commit()

    response = await client.get(f"/api/content/?site_id={test_site_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_content_filter_by_platform(
    client, seeded_site, test_site_id, db_session, test_user_id
):
    for platform in ["twitter", "twitter", "linkedin"]:
        content = Content(
            site_id=uuid.UUID(test_site_id),
            user_id=uuid.UUID(test_user_id),
            platform=platform,
            content_type="post",
            title=f"{platform} post",
            body="Content",
            status="draft",
        )
        db_session.add(content)
    await db_session.commit()

    response = await client.get(
        f"/api/content/?site_id={test_site_id}&platform=twitter"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_get_content_by_id(client, seeded_site, test_site_id, db_session, test_user_id):
    content = Content(
        site_id=uuid.UUID(test_site_id),
        user_id=uuid.UUID(test_user_id),
        platform="linkedin",
        content_type="post",
        title="LinkedIn Post",
        body="Great insights",
        status="draft",
    )
    db_session.add(content)
    await db_session.commit()

    response = await client.get(f"/api/content/{content.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "LinkedIn Post"


@pytest.mark.asyncio
async def test_get_content_not_found(client, seeded_site):
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/content/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_content(client, seeded_site, test_site_id, db_session, test_user_id):
    content = Content(
        site_id=uuid.UUID(test_site_id),
        user_id=uuid.UUID(test_user_id),
        platform="twitter",
        content_type="tweet",
        title="Original Title",
        body="Original body",
        status="draft",
    )
    db_session.add(content)
    await db_session.commit()

    response = await client.patch(
        f"/api/content/{content.id}",
        json={"title": "Updated Title", "body": "Updated body"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Updated body"


@pytest.mark.asyncio
async def test_approve_content(client, seeded_site, test_site_id, db_session, test_user_id):
    content = Content(
        site_id=uuid.UUID(test_site_id),
        user_id=uuid.UUID(test_user_id),
        platform="twitter",
        content_type="tweet",
        title="Pending Tweet",
        body="Approve me",
        status="draft",
    )
    db_session.add(content)
    await db_session.commit()

    response = await client.post(f"/api/content/{content.id}/approve")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


@pytest.mark.asyncio
async def test_reject_content(client, seeded_site, test_site_id, db_session, test_user_id):
    content = Content(
        site_id=uuid.UUID(test_site_id),
        user_id=uuid.UUID(test_user_id),
        platform="twitter",
        content_type="tweet",
        title="Bad Tweet",
        body="Reject me",
        status="draft",
    )
    db_session.add(content)
    await db_session.commit()

    response = await client.post(f"/api/content/{content.id}/reject")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_delete_content(client, seeded_site, test_site_id, db_session, test_user_id):
    content = Content(
        site_id=uuid.UUID(test_site_id),
        user_id=uuid.UUID(test_user_id),
        platform="twitter",
        content_type="tweet",
        title="Delete Me",
        body="Gone soon",
        status="draft",
    )
    db_session.add(content)
    await db_session.commit()

    response = await client.delete(f"/api/content/{content.id}")
    assert response.status_code == 204

    response = await client.get(f"/api/content/{content.id}")
    assert response.status_code == 404
