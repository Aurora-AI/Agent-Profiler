from fastapi import FastAPI, HTTPException
from src.domain.schemas import GenerateRequest
from src.services.generation_service import GenerationService
from src.infra.llm.mock_provider import MockProvider # Import to register
from src.infra.cache.memory_cache import InMemoryCache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="Aurora LLM Gateway")

# Initialize Cache
cache = InMemoryCache()
service = GenerationService(cache=cache)

@app.post("/generate")
async def generate(request: GenerateRequest):
    logger.info("Received generation request")
    try:
        response = await service.generate(request)
        return response
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/health")
def health():
    return {"status": "ok"}
