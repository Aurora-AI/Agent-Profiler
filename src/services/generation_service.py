from src.core.factory import ProviderFactory
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse, ProviderMetadata
from src.domain.cache_interface import CacheProvider
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(self, cache: CacheProvider = None):
        self.cache = cache

    def _generate_cache_key(self, request: GenerateRequest) -> str:
        # Create a unique key based on provider, prompt, and config
        raw = f"{request.provider_name}:{request.prompt}:{json.dumps(request.config, sort_keys=True)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def generate(self, request: GenerateRequest) -> LLMResponse:
        logger.info(f"Service started generation for provider: {request.provider_name}")

        cache_key = self._generate_cache_key(request) if self.cache else None

        # Try Cache
        if self.cache:
            cached_content = await self.cache.get(cache_key)
            if cached_content:
                logger.info("Cache hit")
                return LLMResponse(
                    content=cached_content,
                    # We estimate tokens for cached content or store metadata in cache (simplified here)
                    prompt_tokens=len(request.prompt.split()),
                    completion_tokens=len(cached_content.split()),
                    total_tokens=len(request.prompt.split()) + len(cached_content.split()),
                    metadata=ProviderMetadata(model="cache", latency=0.0)
                )

        try:
            provider = ProviderFactory.create(
                provider_name=request.provider_name,
                api_key=request.api_key,
                config=request.config
            )

            response = await provider.generate_async(request.prompt)

            # Set Cache
            if self.cache and response.content:
                await self.cache.set(cache_key, response.content, ttl=60)

            logger.info("Service completed generation successfully")
            return response

        except Exception as e:
            logger.error(f"Service failed: {str(e)}")
            raise e
