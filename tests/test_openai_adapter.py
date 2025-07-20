import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from profiler.adapters.openai_adapter import OpenAIAdapter, OpenAIParams
from profiler.core.factory import ProviderFactory
from profiler.core.interfaces import LLMResponse, QuotaExceededError

@pytest.mark.asyncio
async def test_openai_adapter_success():
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock()]
    mock_response.choices[0].message.content = "Hello!"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    mock_response.response_ms = 1000
    mock_client.chat.completions.create.return_value = mock_response
    with patch("openai.AsyncClient", return_value=mock_client):
        adapter = ProviderFactory.create(
            "openai",
            api_key="test",
            config={"model": "gpt-4-turbo", "temperature": 0.7, "top_p": 1.0}
        )
        params = OpenAIParams(model="gpt-4-turbo", temperature=0.7, top_p=1.0)
        response = await adapter.generate_async("Oi!", params)
        assert isinstance(response, LLMResponse)
        assert response.content == "Hello!"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 20
        assert response.total_tokens == 30
        assert response.metadata.get("model", "") == "gpt-4-turbo"
        assert response.metadata.get("latency", 0) == 1.0

@pytest.mark.asyncio
async def test_openai_adapter_quota_exceeded():
    mock_client = AsyncMock()
    mock_client.chat.completions.create.side_effect = Exception("RateLimitError")
    with patch("openai.AsyncClient", return_value=mock_client):
        adapter = ProviderFactory.create(
            "openai",
            api_key="test",
            config={"model": "gpt-4-turbo", "temperature": 0.7, "top_p": 1.0}
        )
        params = OpenAIParams(model="gpt-4-turbo", temperature=0.7, top_p=1.0)
        with pytest.raises(Exception):
            await adapter.generate_async("Oi!", params)
