import uuid
import pytest

from app.modules.auth.service import AuthService


def test_create_jwt_token():
    service = AuthService(jwt_secret="test-secret", jwt_algorithm="HS256", jwt_expiry_minutes=60)
    user_id = uuid.uuid4()
    token = service.create_token(user_id=str(user_id), email="test@example.com")
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_jwt_token():
    service = AuthService(jwt_secret="test-secret", jwt_algorithm="HS256", jwt_expiry_minutes=60)
    user_id = str(uuid.uuid4())
    token = service.create_token(user_id=user_id, email="test@example.com")
    payload = service.verify_token(token)
    assert payload["sub"] == user_id
    assert payload["email"] == "test@example.com"


def test_verify_invalid_token():
    service = AuthService(jwt_secret="test-secret", jwt_algorithm="HS256", jwt_expiry_minutes=60)
    payload = service.verify_token("invalid-token")
    assert payload is None
