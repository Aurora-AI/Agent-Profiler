import pytest
from src.domain.interfaces import LLMResponse, ProviderMetadata
from src.infra.llm.mock_provider import MockProvider
from src.core.factory import ProviderFactory
from src.domain.schemas import MockConfig

@pytest.mark.asyncio
async def test_mock_provider_generation():
    provider = MockProvider(api_key="test", response_delay=0.01, mock_response="Test Response")
    response = await provider.generate_async("Hello")

    assert isinstance(response, LLMResponse)
    assert response.content == "Test Response"
    assert response.metadata['latency'] == 0.01

def test_factory_registration():
    # MockProvider is registered upon import in test setup or main
    provider = ProviderFactory.create("mock", "key", {"response_delay": 0.0})
    assert isinstance(provider, MockProvider)

def test_factory_invalid_provider():
    with pytest.raises(ValueError):
        ProviderFactory.create("nonexistent", "key")
