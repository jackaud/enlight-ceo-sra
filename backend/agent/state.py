"""Assessment state definition for LangGraph — CEO Succession Readiness."""

from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class AssessmentState(TypedDict):
    messages: Annotated[list, add_messages]  # Conversation history
    phase: str  # intake | collecting | analyzing | reporting | complete
    target_leader: dict  # {"name": "Sarah Mitchell", "role": "CFO"} — the succession candidate
    evaluator_role: str  # Assessor's board role, e.g. "Board Chair", "Non-Executive Director"
    dimensions: list[str]  # CEO readiness dimensions to assess
    current_dimension: int  # Current dimension index
    collected_responses: dict  # {"strategic_leadership": {"q1": 4, ...}, ...}
    ml_result: dict  # ML prediction result
    pending_form: dict  # Form waiting for user submission
