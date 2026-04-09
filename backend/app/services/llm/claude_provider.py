import json
from anthropic import AsyncAnthropic
from app.services.llm.base import LLMProvider


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        params = {
            "model": self.model,
            "max_tokens": kwargs.pop("max_tokens", 4096),
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            params["system"] = system_prompt
        params.update(kwargs)
        response = await self.client.messages.create(**params)
        return response.content[0].text

    async def generate_structured(self, prompt: str, schema: dict, system_prompt: str | None = None, **kwargs) -> dict:
        system = (system_prompt or "") + f"\nRespond with valid JSON matching this schema: {json.dumps(schema)}"
        result = await self.generate(prompt, system_prompt=system, **kwargs)
        return json.loads(result)
