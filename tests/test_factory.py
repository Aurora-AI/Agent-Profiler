import pytest
from profiler.core.factory import ProviderFactory
from profiler.core.interfaces import LLMProvider, InvalidConfigError

from typing import Optional
from pydantic import BaseModel

class DummyParams(BaseModel):
    foo: str


from profiler.core.interfaces import LLMResponse


class DummyProvider(LLMProvider[DummyParams]):
    def __init__(self, api_key: str, **validated_config):
        self.api_key = api_key
        self.config = validated_config
    async def generate_async(
        self,
        prompt: str,
        params: Optional[DummyParams] = None,
        **_
    ) -> LLMResponse:
        params = params or DummyParams(foo="")
        return LLMResponse(
            content="dummy",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            metadata={}
        )

ProviderFactory.register("dummy", DummyParams)(DummyProvider)

def test_factory_register_and_create():
    provider = ProviderFactory.create("dummy", api_key="123", config={"foo": "bar"})
    assert isinstance(provider, DummyProvider)
    assert provider.api_key == "123"
    assert provider.config["foo"] == "bar"

def test_factory_invalid_config():
    with pytest.raises(InvalidConfigError):
        ProviderFactory.create("dummy", api_key="123")
