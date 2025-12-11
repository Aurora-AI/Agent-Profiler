from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TypedDict, Generic, TypeVar
from pydantic import BaseModel

class ProviderMetadata(TypedDict, total=False):
    model: str
    api_version: Optional[str]
    latency: Optional[float]

@dataclass(frozen=True)
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    metadata: ProviderMetadata = field(default_factory=ProviderMetadata)

class LLMError(BaseException):
    def __init__(self, provider: str, code: int, details: str):
        self.provider = provider
        self.code = code
        self.details = details
        super().__init__(f"[{provider}] Error {code}: {details}")

class QuotaExceededError(LLMError):
    pass

class InvalidConfigError(LLMError):
    pass

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
