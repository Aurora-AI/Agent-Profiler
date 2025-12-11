from abc import ABC, abstractmethod
from typing import Optional

class CacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = 60) -> None:
        pass
