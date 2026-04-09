import pytest

from app.services.llm.base import LLMProvider
from app.services.llm.factory import LLMFactory


def test_llm_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_factory_register_and_get():
    class FakeProvider(LLMProvider):
        async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
            return "fake response"

        async def generate_structured(self, prompt: str, schema: dict, system_prompt: str | None = None, **kwargs) -> dict:
            return {"result": "fake"}

    factory = LLMFactory()
    factory.register("fake", FakeProvider)
    provider = factory.get("fake")
    assert isinstance(provider, FakeProvider)


def test_factory_get_unknown_provider():
    factory = LLMFactory()
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        factory.get("nonexistent")
