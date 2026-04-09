import os
import pytest


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-client-secret")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:3000")

    from app.config import Settings
    s = Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        jwt_secret="test-secret",
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        frontend_url="http://localhost:3000",
    )

    assert s.database_url == "postgresql+asyncpg://test:test@localhost/test"
    assert s.jwt_secret == "test-secret"
    assert s.default_llm_provider == "openai"


def test_settings_optional_llm_keys():
    from app.config import Settings
    s = Settings(
        database_url="postgresql+asyncpg://test:test@localhost/test",
        redis_url="redis://localhost:6379/0",
        jwt_secret="test-secret",
        google_client_id="test-client-id",
        google_client_secret="test-client-secret",
        frontend_url="http://localhost:3000",
    )
    assert s.openai_api_key is None
    assert s.anthropic_api_key is None
    assert s.together_api_key is None
    assert s.ollama_base_url == "http://localhost:11434"
