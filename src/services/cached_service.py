from src.domain.service_interfaces import GenerationServiceProtocol
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse, ProviderMetadata
from src.domain.cache_interface import CacheProvider
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class CachedGenerationService(GenerationServiceProtocol):
    def __init__(self, service: GenerationServiceProtocol, cache: CacheProvider):
        self._service = service
        self._cache = cache

    def _generate_cache_key(self, request: GenerateRequest) -> str:
        raw = f"{request.provider_name}:{request.prompt}:{json.dumps(request.config, sort_keys=True)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def generate(self, request: GenerateRequest) -> LLMResponse:
        cache_key = self._generate_cache_key(request)

        # Try Cache
        cached_content = await self._cache.get(cache_key)
        if cached_content:
            logger.info("Cache hit (Decorator)")
            return LLMResponse(
                content=cached_content,
                prompt_tokens=len(request.prompt.split()),
                completion_tokens=len(cached_content.split()),
                total_tokens=len(request.prompt.split()) + len(cached_content.split()),
                metadata=ProviderMetadata(model="cache", latency=0.0)
            )

        # Delegate
        response = await self._service.generate(request)

        # Set Cache
        if response.content:
            await self._cache.set(cache_key, response.content, ttl=60)

        return response
