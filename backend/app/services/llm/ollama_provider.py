import json
import httpx
from app.services.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

    async def generate_structured(self, prompt: str, schema: dict, system_prompt: str | None = None, **kwargs) -> dict:
        system = (system_prompt or "") + f"\nRespond with valid JSON matching this schema: {json.dumps(schema)}"
        result = await self.generate(prompt, system_prompt=system, **kwargs)
        return json.loads(result)
