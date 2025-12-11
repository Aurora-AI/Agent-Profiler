from typing import Protocol
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse

class GenerationServiceProtocol(Protocol):
    async def generate(self, request: GenerateRequest) -> LLMResponse:
        ...
