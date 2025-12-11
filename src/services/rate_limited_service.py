from src.domain.service_interfaces import GenerationServiceProtocol
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse, QuotaExceededError
import time
import asyncio

class RateLimitedService(GenerationServiceProtocol):
    def __init__(self, service: GenerationServiceProtocol, max_requests: int = 100, window: float = 1.0):
        self._service = service
        self._max_requests = max_requests
        self._window = window
        self._tokens = max_requests
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def generate(self, request: GenerateRequest) -> LLMResponse:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            self._tokens = min(self._max_requests, self._tokens + elapsed * (self._max_requests / self._window))
            self._last_update = now

            if self._tokens < 1:
                raise QuotaExceededError(provider="ratelimit", code=429, details="Rate limit exceeded")

            self._tokens -= 1

        return await self._service.generate(request)
