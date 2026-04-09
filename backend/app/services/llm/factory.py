from app.services.llm.base import LLMProvider


class LLMFactory:
    def __init__(self):
        self._providers: dict[str, type[LLMProvider]] = {}
        self._instances: dict[str, LLMProvider] = {}

    def register(self, name: str, provider_class: type[LLMProvider]):
        self._providers[name] = provider_class

    def get(self, name: str, **kwargs) -> LLMProvider:
        if name not in self._providers:
            raise ValueError(f"Unknown LLM provider: {name}")
        if name not in self._instances:
            self._instances[name] = self._providers[name](**kwargs)
        return self._instances[name]
