from src.core.factory import ProviderFactory
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse
import logging

logger = logging.getLogger(__name__)

class GenerationService:
    async def generate(self, request: GenerateRequest) -> LLMResponse:
        logger.info(f"Service started generation for provider: {request.provider_name}")

        try:
            provider = ProviderFactory.create(
                provider_name=request.provider_name,
                api_key=request.api_key,
                config=request.config
            )

            response = await provider.generate_async(request.prompt)
            logger.info("Service completed generation successfully")
            return response

        except Exception as e:
            logger.error(f"Service failed: {str(e)}")
            raise e
