from collections import defaultdict
from .interfaces import LLMProvider, InvalidConfigError
from pydantic import BaseModel, ValidationError


from typing import Any, Dict, Type, Optional

class ProviderFactory:
    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, provider_name: str, config_schema: Type[BaseModel]):
        def wrapper(provider_cls: Type[LLMProvider]):
            if not issubclass(provider_cls, LLMProvider):
                raise TypeError("Provider deve herdar de LLMProvider")
            cls._registry[provider_name] = {
                'class': provider_cls,
                'schema': config_schema
            }
            return provider_cls
        return wrapper

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str,
        config: Optional[Dict[str, Any]] = None
    ) -> LLMProvider:
        if provider_name not in cls._registry:
            raise ValueError(f"Provedor não registrado: {provider_name}")
        provider_data = cls._registry[provider_name]
        schema = provider_data.get('schema')
        if not schema:
            raise InvalidConfigError(provider=provider_name, code=400, details="Schema de configuração ausente")
        try:
            validated_config = schema(**(config or {})).model_dump()
            return provider_data['class'](api_key, **validated_config)
        except ValidationError as e:
            raise InvalidConfigError(
                provider=provider_name,
                code=400,
                details=f"Configuração inválida: {e.errors()}"
            )
