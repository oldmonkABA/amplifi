import pytest

from app.services.llm.factory import create_llm_factory


def test_create_factory_registers_all_providers():
    factory = create_llm_factory()
    assert "openai" in factory._providers
    assert "claude" in factory._providers
    assert "together" in factory._providers
    assert "ollama" in factory._providers


def test_create_factory_get_openai():
    factory = create_llm_factory()
    provider = factory.get("openai", api_key="test")
    assert provider is not None


def test_create_factory_get_ollama():
    factory = create_llm_factory()
    provider = factory.get("ollama", base_url="http://localhost:11434")
    assert provider is not None
