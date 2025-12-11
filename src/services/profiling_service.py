import random
from src.domain.profiling import AgentProfileRequest, AgentProfileResponse, PsychologicalProfile
import logging

logger = logging.getLogger(__name__)

class ProfilingService:
    def analyze(self, request: AgentProfileRequest) -> AgentProfileResponse:
        logger.info(f"Analyzing profile for agent: {request.agent_id}")

        # Mock Logic: Deterministic generation based on Agent ID hash
        # In a real ambiguity scenario, I must choose a logic that is consistent and testable.
        seed = sum(ord(c) for c in request.agent_id)
        rng = random.Random(seed)

        profile = PsychologicalProfile(
            openness=rng.random(),
            conscientiousness=rng.random(),
            extraversion=rng.random(),
            agreeableness=rng.random(),
            neuroticism=rng.random(),
            risk_tolerance=rng.random()
        )

        # Determine archetype based on traits
        if profile.risk_tolerance > 0.8:
            archetype = "Maverick"
        elif profile.conscientiousness > 0.8:
            archetype = "Architect"
        else:
            archetype = "Generalist"

        return AgentProfileResponse(
            agent_id=request.agent_id,
            profile=profile,
            archetype=archetype
        )
