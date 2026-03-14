"""Confirm intake tool - signals that background info collection is complete."""

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class ConfirmIntakeInput(BaseModel):
    leader_name: str = Field(description="Name of the CEO succession candidate")
    leader_role: str = Field(description="Candidate's current role (e.g. CFO, COO)")
    evaluator_role: str = Field(
        description="Assessor's board role (e.g. Board Chair, Non-Executive Director, CHRO)"
    )
    dimensions: list[str] = Field(
        description="Assessment dimension keys, e.g. ['strategic_leadership', 'stakeholder_management', ...]"
    )


class ConfirmIntakeTool(BaseTool):
    name: str = "confirm-intake"
    description: str = (
        "Confirm that succession assessment background information has been collected and proceed to the assessment phase. "
        "Call this tool once you have the candidate's name, current role, the assessor's board role, and the assessment dimensions."
    )
    args_schema: type[BaseModel] = ConfirmIntakeInput

    def _run(
        self,
        leader_name: str,
        leader_role: str,
        evaluator_role: str,
        dimensions: list[str],
    ) -> str:
        return (
            f"Succession assessment confirmed:\n"
            f"Candidate: {leader_name} ({leader_role})\n"
            f"Assessor: {evaluator_role}\n"
            f"Dimensions: {', '.join(dimensions)}\n"
            f"Ready to begin dimension-by-dimension assessment."
        )
