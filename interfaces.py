from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, TypedDict, Generic, TypeVar
from pydantic import BaseModel, ValidationError

class ProviderMetadata(TypedDict, total=False):
    model: str
    api_version: Optional[str]
    latency: Optional[float]

@dataclass(frozen=True)
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    metadata: ProviderMetadata

class LLMError(BaseException):
    provider: str
    code: int
    details: str

class QuotaExceededError(LLMError): ...
class InvalidConfigError(LLMError): ...

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC, Generic[T]):
    @abstractmethod
    async def generate_async(
        self, 
        prompt: str, 
        params: Optional[T] = None, 
        **kwargs
    ) -> LLMResponse:
        """Gera resposta de forma assíncrona com parâmetros validados."""
        pass
