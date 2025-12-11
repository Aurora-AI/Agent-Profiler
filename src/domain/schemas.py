from pydantic import BaseModel, Field
from typing import Optional

class MockConfig(BaseModel):
    response_delay: float = Field(default=0.1, ge=0.0)
    mock_response: str = Field(default="Hello from Mock Provider")

class GenerateRequest(BaseModel):
    provider_name: str
    prompt: str
    api_key: str = "mock-key"
    config: Optional[dict] = None
