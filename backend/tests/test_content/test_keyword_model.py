import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.site import Site
from app.models.keyword import Keyword


@pytest.mark.asyncio
async def test_create_keyword(db_session):
    user = User(email="kw@example.com", name="KW User", google_id="kw-1")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    keyword = Keyword(
        site_id=site.id,
        term="ai marketing automation",
        search_volume=12000,
        difficulty=45,
        current_ranking=None,
        source="llm_research",
    )
    db_session.add(keyword)
    await db_session.commit()

    result = await db_session.execute(
        select(Keyword).where(Keyword.term == "ai marketing automation")
    )
    saved = result.scalar_one()
    assert saved.site_id == site.id
    assert saved.search_volume == 12000
    assert saved.difficulty == 45
    assert saved.current_ranking is None
    assert saved.source == "llm_research"
    assert saved.id is not None


@pytest.mark.asyncio
async def test_keyword_with_ranking(db_session):
    user = User(email="kw2@example.com", name="KW2 User", google_id="kw-2")
    db_session.add(user)
    await db_session.commit()

    site = Site(user_id=user.id, url="https://example.com", name="Example")
    db_session.add(site)
    await db_session.commit()

    keyword = Keyword(
        site_id=site.id,
        term="marketing saas",
        search_volume=8000,
        difficulty=60,
        current_ranking=15,
        source="search_console",
        related_terms=["marketing software", "saas marketing tools"],
    )
    db_session.add(keyword)
    await db_session.commit()

    result = await db_session.execute(
        select(Keyword).where(Keyword.term == "marketing saas")
    )
    saved = result.scalar_one()
    assert saved.current_ranking == 15
    assert saved.related_terms == ["marketing software", "saas marketing tools"]


@pytest.mark.asyncio
async def test_keyword_unique_per_site(db_session):
    """Two different sites can track the same keyword term."""
    user = User(email="kw3@example.com", name="KW3 User", google_id="kw-3")
    db_session.add(user)
    await db_session.commit()

    site1 = Site(user_id=user.id, url="https://site1.com", name="Site 1")
    site2 = Site(user_id=user.id, url="https://site2.com", name="Site 2")
    db_session.add_all([site1, site2])
    await db_session.commit()

    kw1 = Keyword(site_id=site1.id, term="ai tools", search_volume=5000, difficulty=30)
    kw2 = Keyword(site_id=site2.id, term="ai tools", search_volume=5000, difficulty=30)
    db_session.add_all([kw1, kw2])
    await db_session.commit()

    result = await db_session.execute(select(Keyword).where(Keyword.term == "ai tools"))
    all_kws = result.scalars().all()
    assert len(all_kws) == 2
