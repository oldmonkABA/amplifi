import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.modules.auth.service import AuthService

security = HTTPBearer()

auth_service = AuthService(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
    jwt_expiry_minutes=settings.jwt_expiry_minutes,
)

DEV_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    # Dev mode: accept any token starting with "dev-"
    if settings.dev_mode and credentials.credentials.startswith("dev-"):
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
        return user

    payload = auth_service.verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
