import time
import asyncio
from typing import Dict, Optional, Tuple
from src.domain.cache_interface import CacheProvider

class InMemoryCache(CacheProvider):
    def __init__(self):
        # Stores key -> (value, expiry_timestamp)
        self._store: Dict[str, Tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            data = self._store.get(key)
            if not data:
                return None

            value, expiry = data
            if time.time() > expiry:
                del self._store[key]
                return None

            return value

    async def set(self, key: str, value: str, ttl: int = 60) -> None:
        async with self._lock:
            expiry = time.time() + ttl
            self._store[key] = (value, expiry)
