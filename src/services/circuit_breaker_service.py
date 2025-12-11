from src.domain.service_interfaces import GenerationServiceProtocol
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse, LLMError
import time
import asyncio

class CircuitBreakerOpenError(LLMError):
    pass

class CircuitBreakerService(GenerationServiceProtocol):
    def __init__(self, service: GenerationServiceProtocol, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self._service = service
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._failures = 0
        self._last_failure_time = 0
        self._state = "CLOSED" # CLOSED, OPEN, HALF-OPEN
        self._lock = asyncio.Lock()

    async def generate(self, request: GenerateRequest) -> LLMResponse:
        async with self._lock:
            if self._state == "OPEN":
                if time.time() - self._last_failure_time > self._recovery_timeout:
                    self._state = "HALF-OPEN"
                else:
                    raise CircuitBreakerOpenError(provider="circuit-breaker", code=503, details="Circuit is OPEN")

        try:
            response = await self._service.generate(request)

            async with self._lock:
                if self._state == "HALF-OPEN":
                    self._state = "CLOSED"
                    self._failures = 0
            return response

        except Exception as e:
            async with self._lock:
                self._failures += 1
                self._last_failure_time = time.time()
                if self._failures >= self._failure_threshold:
                    self._state = "OPEN"
            raise e
