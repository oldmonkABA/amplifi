from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.claude_provider import ClaudeProvider
from app.services.llm.together_provider import TogetherProvider
from app.services.llm.ollama_provider import OllamaProvider


class LLMFactory:
    def __init__(self):
        self._providers: dict[str, type[LLMProvider]] = {}
        self._instances: dict[str, LLMProvider] = {}

    def register(self, name: str, provider_class: type[LLMProvider]):
        self._providers[name] = provider_class

    def get(self, name: str, **kwargs) -> LLMProvider:
        if name not in self._providers:
            raise ValueError(f"Unknown LLM provider: {name}")
        key = f"{name}:{hash(frozenset(kwargs.items()))}"
        if key not in self._instances:
            self._instances[key] = self._providers[name](**kwargs)
        return self._instances[key]


def create_llm_factory() -> LLMFactory:
    factory = LLMFactory()
    factory.register("openai", OpenAIProvider)
    factory.register("claude", ClaudeProvider)
    factory.register("together", TogetherProvider)
    factory.register("ollama", OllamaProvider)
    return factory
