import asyncio
from typing import Optional
from src.domain.interfaces import LLMProvider, LLMResponse, ProviderMetadata
from src.core.factory import ProviderFactory
from src.domain.schemas import MockConfig
import logging

logger = logging.getLogger(__name__)

@ProviderFactory.register("mock", MockConfig)
class MockProvider(LLMProvider[MockConfig]):
    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        # We need to parse kwargs back to MockConfig to be type safe, or just use them
        # Since the factory validates them, we can trust them or re-validate.
        # For simplicity here, we assume valid data from factory.
        self.config = MockConfig(**kwargs)

    async def generate_async(
        self,
        prompt: str,
        params: Optional[MockConfig] = None,
        **kwargs
    ) -> LLMResponse:
        logger.info(f"MockProvider generating response for prompt: {prompt[:20]}...")

        # Simulate Network Latency
        await asyncio.sleep(self.config.response_delay)

        return LLMResponse(
            content=self.config.mock_response,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(self.config.mock_response.split()),
            total_tokens=len(prompt.split()) + len(self.config.mock_response.split()),
            metadata=ProviderMetadata(model="mock-v1", latency=self.config.response_delay)
        )
