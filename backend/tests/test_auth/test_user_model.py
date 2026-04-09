import pytest
from sqlalchemy import select

from app.models.user import User


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        email="test@example.com",
        name="Test User",
        google_id="google-123",
        avatar_url="https://example.com/avatar.jpg",
    )
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.email == "test@example.com"))
    saved = result.scalar_one()

    assert saved.email == "test@example.com"
    assert saved.name == "Test User"
    assert saved.google_id == "google-123"
    assert saved.id is not None
    assert saved.created_at is not None


@pytest.mark.asyncio
async def test_user_llm_keys_nullable(db_session):
    user = User(
        email="test2@example.com",
        name="Test User 2",
        google_id="google-456",
    )
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.email == "test2@example.com"))
    saved = result.scalar_one()

    assert saved.openai_api_key is None
    assert saved.anthropic_api_key is None
    assert saved.together_api_key is None
    assert saved.ollama_base_url is None
    assert saved.default_llm_provider == "openai"
