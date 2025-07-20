from typing import Optional
from pydantic import BaseModel, Field
import openai
from ..core.interfaces import LLMProvider, LLMResponse, ProviderMetadata, QuotaExceededError
from ..core.factory import ProviderFactory

class OpenAIParams(BaseModel):
    model: str = "gpt-4-turbo"
    temperature: float = Field(0.7, ge=0, le=2)
    top_p: float = Field(1.0, ge=0, le=1)

@ProviderFactory.register("openai", OpenAIParams)
class OpenAIAdapter(LLMProvider[OpenAIParams]):
    def __init__(self, api_key: str, **validated_config):
        self.client = openai.AsyncClient(api_key=api_key)
        self.config = validated_config
        self.default_params = OpenAIParams(**validated_config)

    async def generate_async(
        self,
        prompt: str,
        params: Optional[OpenAIParams] = None,
        **_
    ) -> LLMResponse:
        try:
            # Combina parâmetros padrão com override
            update_data = params.model_dump() if params else {}
            effective_params = self.default_params.model_copy(update=update_data)
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                **effective_params.model_dump()
            )
            content = getattr(response.choices[0].message, "content", "") or ""
            usage = getattr(response, "usage", None)
            prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
            completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
            total_tokens = getattr(usage, "total_tokens", 0) if usage else 0
            latency = getattr(response, "response_ms", None)
            metadata = ProviderMetadata(
                model=effective_params.model,
                latency=latency / 1000 if latency is not None else None
            )
            return LLMResponse(
                content=content,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                metadata=metadata
            )
        except openai.RateLimitError:
            raise QuotaExceededError(provider="openai", code=429, details="Rate limit exceeded")
