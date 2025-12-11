from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse
from src.domain.schemas import GenerateRequest
from src.domain.profiling import AgentProfileRequest, AgentProfileResponse
from src.domain.interfaces import QuotaExceededError
from src.services.generation_service import GenerationService
from src.services.cached_service import CachedGenerationService
from src.services.rate_limited_service import RateLimitedService
from src.services.circuit_breaker_service import CircuitBreakerService, CircuitBreakerOpenError
from src.services.profiling_service import ProfilingService
from src.infra.llm.mock_provider import MockProvider # Import to register
from src.infra.cache.memory_cache import InMemoryCache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="Aurora LLM Gateway", default_response_class=ORJSONResponse)

# Initialize Services with Decorators
cache = InMemoryCache()
base_service = GenerationService()
# Chain: Request -> RateLimit -> Cache -> CircuitBreaker -> Base
# Note: CircuitBreaker should wrap Base (protect remote calls), Cache wraps CB (serve if broken?), RateLimit wraps everything.
# Better Chain: Request -> RateLimit -> Cache -> CircuitBreaker -> Base
cb_service = CircuitBreakerService(base_service)
cached_service = CachedGenerationService(cb_service, cache)
service = RateLimitedService(cached_service, max_requests=200, window=1.0) # Increased limit for bench
profiling_service = ProfilingService()

@app.post("/generate")
async def generate(request: GenerateRequest):
    logger.info("Received generation request")
    try:
        response = await service.generate(request)
        return response
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except QuotaExceededError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except CircuitBreakerOpenError as e:
        logger.error(f"Circuit breaker open: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable (Circuit Open)")
    except Exception as e:
        logger.error(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/profiling/analyze", response_model=AgentProfileResponse)
async def analyze_agent(request: AgentProfileRequest):
    logger.info("Received profiling request")
    try:
        return profiling_service.analyze(request)
    except Exception as e:
        logger.error(f"Profiling error: {e}")
        raise HTTPException(status_code=500, detail="Internal Profiling Error")

@app.get("/health")
def health():
    return {"status": "ok"}
