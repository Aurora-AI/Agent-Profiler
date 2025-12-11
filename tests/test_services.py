import pytest
from src.services.generation_service import GenerationService
from src.domain.schemas import GenerateRequest
from src.domain.interfaces import LLMResponse

@pytest.mark.asyncio
async def test_generation_service():
    service = GenerationService()
    request = GenerateRequest(
        provider_name="mock",
        prompt="Hello",
        config={"response_delay": 0.001, "mock_response": "Service Test"}
    )

    response = await service.generate(request)
    assert response.content == "Service Test"
