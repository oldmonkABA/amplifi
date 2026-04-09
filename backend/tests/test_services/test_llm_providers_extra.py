import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.llm.together_provider import TogetherProvider
from app.services.llm.ollama_provider import OllamaProvider


@pytest.mark.asyncio
async def test_together_generate():
    provider = TogetherProvider(api_key="test-key")

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Together response"

    with patch.object(provider.client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_response):
        result = await provider.generate("Write something")

    assert result == "Together response"


@pytest.mark.asyncio
async def test_ollama_generate():
    provider = OllamaProvider(base_url="http://localhost:11434")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": {"content": "Ollama response"}}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
        result = await provider.generate("Write something")

    assert result == "Ollama response"
