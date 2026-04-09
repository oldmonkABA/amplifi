import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.claude_provider import ClaudeProvider


@pytest.mark.asyncio
async def test_openai_generate():
    provider = OpenAIProvider(api_key="test-key")

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Generated text"

    with patch.object(provider.client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_response):
        result = await provider.generate("Write something")

    assert result == "Generated text"


@pytest.mark.asyncio
async def test_claude_generate():
    provider = ClaudeProvider(api_key="test-key")

    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Generated text"

    with patch.object(provider.client.messages, "create", new_callable=AsyncMock, return_value=mock_response):
        result = await provider.generate("Write something")

    assert result == "Generated text"
