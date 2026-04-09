from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError


class AuthService:
    def __init__(self, jwt_secret: str, jwt_algorithm: str, jwt_expiry_minutes: int):
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.jwt_expiry_minutes = jwt_expiry_minutes

    def create_token(self, user_id: str, email: str) -> str:
        expires = datetime.now(timezone.utc) + timedelta(minutes=self.jwt_expiry_minutes)
        payload = {"sub": user_id, "email": email, "exp": expires}
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def verify_token(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except JWTError:
            return None
