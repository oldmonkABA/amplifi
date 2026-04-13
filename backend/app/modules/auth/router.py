import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.modules.auth.dependencies import auth_service, get_current_user
from app.modules.auth.schemas import GoogleAuthRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def verify_google_token(token: str) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        )
        if response.status_code == 200:
            return response.json()
        return None


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    google_user = await verify_google_token(request.token)
    if google_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")

    # Find or create user
    result = await db.execute(select(User).where(User.google_id == google_user["sub"]))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=google_user["email"],
            name=google_user["name"],
            google_id=google_user["sub"],
            avatar_url=google_user.get("picture"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = auth_service.create_token(user_id=str(user.id), email=user.email)
    return TokenResponse(access_token=token)


@router.post("/dev-login", response_model=TokenResponse)
async def dev_login(db: AsyncSession = Depends(get_db)):
    """Dev-only login that bypasses Google OAuth."""
    from app.config import settings as _settings
    if not _settings.dev_mode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    from app.modules.auth.dependencies import DEV_USER_ID
    result = await db.execute(select(User).where(User.id == DEV_USER_ID))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            id=DEV_USER_ID,
            email="arun@cautilyacapital.com",
            name="Arun",
            google_id="dev-user",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return TokenResponse(access_token="dev-token")


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user
