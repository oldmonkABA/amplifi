import json
from openai import AsyncOpenAI
from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, **kwargs
        )
        return response.choices[0].message.content

    async def generate_structured(self, prompt: str, schema: dict, system_prompt: str | None = None, **kwargs) -> dict:
        system = (system_prompt or "") + f"\nRespond with valid JSON matching this schema: {json.dumps(schema)}"
        result = await self.generate(prompt, system_prompt=system, **kwargs)
        return json.loads(result)
