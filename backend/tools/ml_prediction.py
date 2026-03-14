"""Mock ML prediction tool for CEO succession readiness assessment."""

import random
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from tools.assessment_form import DIMENSION_LABELS


class MLPredictionInput(BaseModel):
    assessment_data: dict = Field(description="Collected assessment data across dimensions")


class MLPredictionTool(BaseTool):
    name: str = "ml-succession-prediction"
    description: str = "Analyse collected assessment data and generate a CEO succession readiness report"
    args_schema: type[BaseModel] = MLPredictionInput

    def _run(self, assessment_data: dict) -> dict:
        return mock_predict(assessment_data)


def _readiness_level(score: int) -> str:
    """Classify readiness based on overall score."""
    if score >= 75:
        return "Ready Now"
    elif score >= 55:
        return "Ready in 1-2 Years"
    else:
        return "Developing"


def _dimension_rating(score: int) -> str:
    """Rate individual dimension performance."""
    if score >= 70:
        return "Strong"
    elif score >= 50:
        return "Adequate"
    elif score >= 30:
        return "Development Needed"
    else:
        return "Critical Gap"


def mock_predict(assessment_data: dict) -> dict:
    """Mock ML prediction: weighted average + random perturbation for succession readiness."""
    all_dimensions = list(DIMENSION_LABELS.keys())
    dimension_scores = {}

    for dim_key in all_dimensions:
        responses = assessment_data.get(dim_key, {})
        scores = []
        for key, value in responses.items():
            if key.startswith("q") and key[1:].isdigit():
                try:
                    scores.append(int(value))
                except (ValueError, TypeError):
                    continue

        if scores:
            avg = sum(scores) / len(scores)
            base_score = (avg - 1) / 4 * 100
            perturbation = random.uniform(-8, 8)
            score = max(0, min(100, round(base_score + perturbation)))
        else:
            # Skipped or missing dimension — generate random score
            score = random.randint(40, 70)

        dimension_scores[dim_key] = score

    all_scores = list(dimension_scores.values())
    overall_score = round(sum(all_scores) / len(all_scores)) if all_scores else 50

    readiness = _readiness_level(overall_score)

    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
    strengths = [DIMENSION_LABELS.get(k, k) for k, v in sorted_dims[:2]]
    development_gaps = [DIMENSION_LABELS.get(k, k) for k, v in sorted_dims[-2:]]

    suggestions = _generate_suggestions(sorted_dims[-2:], readiness)

    return {
        "overall_score": overall_score,
        "readiness": readiness,
        "dimension_scores": {
            DIMENSION_LABELS.get(k, k): {"score": v, "rating": _dimension_rating(v)}
            for k, v in dimension_scores.items()
        },
        "strengths": strengths,
        "development_gaps": development_gaps,
        "suggestions": suggestions,
        "confidence": 0.65,
    }


def _generate_suggestions(weak_dims: list[tuple[str, int]], readiness: str) -> list[str]:
    """Generate development suggestions based on weak dimensions and readiness level."""
    suggestion_map = {
        "strategic_leadership": [
            "Assign the candidate to lead a major strategic initiative (e.g. market entry, M&A) with board-level reporting",
            "Arrange structured exposure to the board's strategy committee and investor presentations",
        ],
        "stakeholder_management": [
            "Create opportunities for the candidate to present at board meetings and engage with key shareholders",
            "Pair with an experienced Board Chair or NED for mentored stakeholder engagement",
        ],
        "cultural_stewardship": [
            "Task the candidate with leading a significant cultural or transformation initiative across business units",
            "Engage Sterling Black's CEO coaching programme to develop authentic leadership presence and values alignment",
        ],
        "crisis_leadership": [
            "Include the candidate in crisis simulation exercises and business continuity planning at the enterprise level",
            "Assign a Sterling Black CEO coach who has navigated similar crisis scenarios to provide real-time mentoring",
        ],
        "operational_excellence": [
            "Expand the candidate's P&L responsibility to include additional business units or geographies",
            "Commission a strategic project that requires end-to-end enterprise-level execution and board reporting",
        ],
        "talent_pipeline": [
            "Task the candidate with building a succession plan for their own direct reports and presenting it to the board",
            "Assign leadership of a cross-functional talent review process to build enterprise-wide people capability",
        ],
    }

    suggestions = []
    for dim_key, _ in weak_dims:
        suggestions.extend(suggestion_map.get(dim_key, [f"Focus on developing {dim_key} capability"]))

    # Add readiness-specific suggestion
    if readiness == "Ready Now":
        suggestions.append("Begin structured CEO transition planning including shadow CEO arrangements and stakeholder introduction")
    elif readiness == "Ready in 1-2 Years":
        suggestions.append("Implement a 12-18 month accelerated development programme with quarterly board progress reviews")
    else:
        suggestions.append("Consider a 2-3 year development pathway with interim milestones, and evaluate additional internal or external candidates")

    return suggestions[:5]
