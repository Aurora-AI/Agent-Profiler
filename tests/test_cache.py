import pytest
import asyncio
from src.infra.cache.memory_cache import InMemoryCache
from src.services.generation_service import GenerationService
from src.services.cached_service import CachedGenerationService
from src.domain.schemas import GenerateRequest

@pytest.mark.asyncio
async def test_memory_cache():
    cache = InMemoryCache()
    await cache.set("key", "value", ttl=1)

    assert await cache.get("key") == "value"
    assert await cache.get("miss") is None

@pytest.mark.asyncio
async def test_memory_cache_expiry():
    cache = InMemoryCache()
    await cache.set("key", "value", ttl=0.1)
    await asyncio.sleep(0.2)
    assert await cache.get("key") is None

@pytest.mark.asyncio
async def test_service_caching_behavior():
    cache = InMemoryCache()
    base_service = GenerationService()
    service = CachedGenerationService(base_service, cache)

    request = GenerateRequest(
        provider_name="mock",
        prompt="CacheTest",
        config={"response_delay": 0.0, "mock_response": "Cached"}
    )

    # First call (Miss)
    resp1 = await service.generate(request)
    assert resp1.content == "Cached"

    # Check if key is in cache
    key = service._generate_cache_key(request)
    assert await cache.get(key) == "Cached"

    # Second call (Hit) - Verify it comes from cache logic
    resp2 = await service.generate(request)
    assert resp2.content == "Cached"
    assert resp2.metadata['model'] == "cache"
