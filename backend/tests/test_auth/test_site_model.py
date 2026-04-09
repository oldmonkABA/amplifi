import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site


@pytest.mark.asyncio
async def test_create_site(db_session):
    user = User(email="test@example.com", name="Test", google_id="g-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(
        user_id=user.id,
        url="https://www.dafinstro.com",
        name="DaFinsTro",
        description="Vedic astrology stock market analytics",
        niche="finance",
        target_geographies=["IN"],
        target_timezones=["Asia/Kolkata"],
    )
    db_session.add(site)
    await db_session.commit()

    result = await db_session.execute(select(Site).where(Site.url == "https://www.dafinstro.com"))
    saved = result.scalar_one()

    assert saved.name == "DaFinsTro"
    assert saved.user_id == user.id
    assert saved.target_geographies == ["IN"]
    assert saved.target_timezones == ["Asia/Kolkata"]


@pytest.mark.asyncio
async def test_site_scraped_data_nullable(db_session):
    user = User(email="test3@example.com", name="Test", google_id="g-3")
    db_session.add(user)
    await db_session.commit()

    site = Site(
        user_id=user.id,
        url="https://example.com",
        name="Example",
    )
    db_session.add(site)
    await db_session.commit()

    result = await db_session.execute(select(Site).where(Site.url == "https://example.com"))
    saved = result.scalar_one()

    assert saved.scraped_data is None
    assert saved.target_geographies is None
