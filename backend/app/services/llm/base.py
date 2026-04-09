from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        """Generate text from a prompt."""
        ...

    @abstractmethod
    async def generate_structured(
        self, prompt: str, schema: dict, system_prompt: str | None = None, **kwargs
    ) -> dict:
        """Generate structured output matching a JSON schema."""
        ...
