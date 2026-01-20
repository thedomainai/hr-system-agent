"""Agent modules for HR policy design."""

from .compensation_designer import CompensationDesignerAgent
from .context_collector import ContextCollectorAgent
from .evaluation_designer import EvaluationDesignerAgent
from .grading_designer import GradingDesignerAgent
from .talent_profile_generator import TalentProfileGeneratorAgent

__all__ = [
    "ContextCollectorAgent",
    "TalentProfileGeneratorAgent",
    "GradingDesignerAgent",
    "EvaluationDesignerAgent",
    "CompensationDesignerAgent",
]

# Agent type to class mapping
AGENT_REGISTRY = {
    "context_collector": ContextCollectorAgent,
    "talent_profile_generator": TalentProfileGeneratorAgent,
    "grading_designer": GradingDesignerAgent,
    "evaluation_designer": EvaluationDesignerAgent,
    "compensation_designer": CompensationDesignerAgent,
}


def get_agent_class(agent_type: str) -> type:
    """Get agent class by type name."""
    if agent_type not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return AGENT_REGISTRY[agent_type]
