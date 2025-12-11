from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class PsychologicalProfile(BaseModel):
    openness: float = Field(..., ge=0.0, le=1.0)
    conscientiousness: float = Field(..., ge=0.0, le=1.0)
    extraversion: float = Field(..., ge=0.0, le=1.0)
    agreeableness: float = Field(..., ge=0.0, le=1.0)
    neuroticism: float = Field(..., ge=0.0, le=1.0)
    risk_tolerance: float = Field(..., ge=0.0, le=1.0)

class AgentProfileRequest(BaseModel):
    agent_id: str
    activity_log: Optional[List[str]] = None

class AgentProfileResponse(BaseModel):
    agent_id: str
    profile: PsychologicalProfile
    archetype: str
