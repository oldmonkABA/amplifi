import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import create_app
from app.models.user import User
from app.models.site import Site
from app.models.content import Content


@pytest.fixture
def test_user_id():
    return str(uuid.uuid4())


@pytest.fixture
def test_site_id():
    return str(uuid.uuid4())


@pytest.fixture
def app(db_session, test_user_id):
    application = create_app()

    async def mock_get_current_user():
        user = MagicMock()
        user.id = uuid.UUID(test_user_id)
        user.email = "test@example.com"
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
async def seeded_content(db_session, test_user_id, test_site_id):
    user = User(
        id=uuid.UUID(test_user_id),
        email="test@example.com",
        name="Test",
        google_id="g-sched-1",
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

    # Create a draft content to schedule
    content = Content(
        site_id=site.id,
        user_id=user.id,
        platform="twitter",
        content_type="tweet",
        title="Schedule Me",
        body="This will be scheduled",
        status="approved",
    )
    db_session.add(content)
    await db_session.commit()

    # Create some scheduled content for calendar
    now = datetime.now(timezone.utc)
    for i in range(3):
        scheduled = Content(
            site_id=site.id,
            user_id=user.id,
            platform=["twitter", "linkedin", "blog"][i],
            content_type="post",
            title=f"Scheduled {i}",
            body=f"Scheduled content {i}",
            status="scheduled",
            scheduled_at=now + timedelta(days=i + 1),
            target_timezone="America/New_York",
        )
        db_session.add(scheduled)
    await db_session.commit()

    return {"site": site, "content": content}


@pytest.mark.asyncio
async def test_schedule_content(client, seeded_content):
    content = seeded_content["content"]
    schedule_time = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()

    response = await client.post(
        f"/api/content/{content.id}/schedule",
        json={
            "scheduled_at": schedule_time,
            "target_timezone": "America/New_York",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "scheduled"
    assert data["target_timezone"] == "America/New_York"
    assert data["scheduled_at"] is not None


@pytest.mark.asyncio
async def test_schedule_content_past_time(client, seeded_content):
    content = seeded_content["content"]
    past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    response = await client.post(
        f"/api/content/{content.id}/schedule",
        json={"scheduled_at": past_time},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_content_calendar(client, seeded_content, test_site_id):
    now = datetime.now(timezone.utc)
    start = now.isoformat()
    end = (now + timedelta(days=7)).isoformat()

    response = await client.get(
        f"/api/content/calendar?site_id={test_site_id}&start={start}&end={end}"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    # Verify they are ordered by scheduled time
    for i in range(len(data["items"]) - 1):
        assert data["items"][i]["scheduled_at"] <= data["items"][i + 1]["scheduled_at"]
