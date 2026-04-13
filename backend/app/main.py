from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (dev convenience)
    from app.database import engine
    from app.models.base import Base
    # Import all models so they register with Base.metadata
    import app.models.user  # noqa
    import app.models.content  # noqa
    import app.models.keyword  # noqa
    import app.models.site  # noqa
    import app.models.email_campaign  # noqa
    import app.models.subscriber  # noqa
    import app.models.ad  # noqa
    import app.models.metric  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if settings.dev_mode:
        # Create dev user and default site
        from app.database import async_session
        from app.models.user import User
        from app.models.site import Site
        from app.modules.auth.dependencies import DEV_USER_ID
        import uuid

        DEV_SITE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")

        async with async_session() as session:
            from sqlalchemy import select
            user = (await session.execute(select(User).where(User.id == DEV_USER_ID))).scalar_one_or_none()
            if user is None:
                user = User(id=DEV_USER_ID, email="arun@cautilyacapital.com", name="Arun", google_id="dev-user")
                session.add(user)

            site = (await session.execute(select(Site).where(Site.id == DEV_SITE_ID))).scalar_one_or_none()
            if site is None:
                site = Site(id=DEV_SITE_ID, user_id=DEV_USER_ID, url="https://cautilyacapital.com", name="Cautilya Capital")
                session.add(site)

            await session.commit()

        print("\n  *** DEV MODE ***")
        print("  Auth bypass enabled — POST /api/auth/dev-login for a token")
        print(f"  Default site ID: {DEV_SITE_ID}")
        print(f"  Database: {settings.database_url}")
        print(f"  OpenAI key: {'set' if settings.openai_api_key else 'NOT SET'}\n")

    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Amplifi", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Return JSON errors instead of plain text (so CORS headers are preserved)
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import traceback

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    from app.modules.auth.router import router as auth_router
    app.include_router(auth_router)

    from app.modules.content.router import router as content_router
    app.include_router(content_router)

    from app.modules.ads.router import router as ads_router
    app.include_router(ads_router)

    from app.modules.analytics.router import router as analytics_router
    app.include_router(analytics_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
