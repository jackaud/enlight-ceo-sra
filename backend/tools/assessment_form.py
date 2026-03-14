"""Assessment form tool - generates form schemas for CEO succession readiness dimensions.

Design philosophy: content driven by Sterling Black's methodology, field types follow content.
See docs/form-design-analysis.md for detailed rationale.
"""

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from tools.base import UIFormField, UIFormSchema, UIFormResult


DIMENSION_LABELS = {
    "strategic_leadership": "Strategic Leadership",
    "stakeholder_management": "Stakeholder Management",
    "cultural_stewardship": "Cultural Stewardship",
    "crisis_leadership": "Crisis & Change Leadership",
    "operational_excellence": "Operational Excellence",
    "talent_pipeline": "Talent & Succession Pipeline",
}

# ── Shared scales (all 1-5 for consistent scoring) ──────────────

LIKERT_OPTIONS = [
    {"value": "1", "label": "1 - Strongly Disagree"},
    {"value": "2", "label": "2 - Disagree"},
    {"value": "3", "label": "3 - Neutral"},
    {"value": "4", "label": "4 - Agree"},
    {"value": "5", "label": "5 - Strongly Agree"},
]

READINESS_OPTIONS = [
    {"value": "1", "label": "1 - Not Ready"},
    {"value": "2", "label": "2 - Early Development"},
    {"value": "3", "label": "3 - Progressing"},
    {"value": "4", "label": "4 - Nearly Ready"},
    {"value": "5", "label": "5 - Ready Now"},
]

FREQUENCY_OPTIONS = [
    {"value": "1", "label": "Never"},
    {"value": "2", "label": "Rarely"},
    {"value": "3", "label": "Sometimes"},
    {"value": "4", "label": "Often"},
    {"value": "5", "label": "Always"},
]

# Derived from SB's benchmarking/stack-ranking methodology
BENCHMARK_OPTIONS = [
    {"value": "1", "label": "Below most peers at this level"},
    {"value": "2", "label": "Comparable to most peers"},
    {"value": "3", "label": "Above average — top 50%"},
    {"value": "4", "label": "Well above average — top 25%"},
    {"value": "5", "label": "Exceptional — top 10% of executives I've observed"},
]

# Derived from actual P&L responsibility tiers in enterprise organisations
PNL_SCOPE_OPTIONS = [
    {"value": "1", "label": "Limited — has not managed a significant P&L"},
    {"value": "2", "label": "Functional — manages a departmental or functional budget"},
    {"value": "3", "label": "Business Unit — owns a full business unit P&L"},
    {"value": "4", "label": "Multi-Unit — oversees multiple business units or a major division"},
    {"value": "5", "label": "Enterprise — has demonstrated enterprise-level financial stewardship"},
]

# Derived from SB's succession methodology — tests CEO mindset about talent pipeline
SUCCESSION_MATURITY_OPTIONS = [
    {"value": "1", "label": "No evidence of succession planning in their area"},
    {"value": "2", "label": "Some informal development but no structured plan"},
    {"value": "3", "label": "Has identified potential successors but development is early"},
    {"value": "4", "label": "Has a structured succession plan with candidates in development"},
    {"value": "5", "label": "Has developed ready-now successors who could step into their role"},
]


# ── Dimension form builders ─────────────────────────────────────

def _build_fields_strategic_leadership() -> list[UIFormField]:
    """Strategic Leadership: vision, long-term planning, market insight.

    SB alignment: "Strategic Thinking — Long-term vision, systems thinking,
    decision quality" from their assessment dimension framework.
    """
    return [
        UIFormField(
            name="q1",
            label="This candidate demonstrates the ability to develop and articulate enterprise-wide strategy beyond their functional area",
            type="radio",
            options=LIKERT_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q2",
            label="How would you rate this candidate's readiness to own the organisation's strategic direction as CEO?",
            type="select",
            options=READINESS_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q3",
            label="Which strategic capabilities have you observed? (Select all that apply)",
            type="checkbox",
            options=[
                {"value": "market_insight", "label": "Deep market and competitive insight"},
                {"value": "innovation", "label": "Drives innovation and digital transformation"},
                {"value": "capital_allocation", "label": "Sound capital allocation decisions"},
                {"value": "ma_experience", "label": "M&A or major transaction experience"},
                {"value": "global_perspective", "label": "Global business perspective"},
            ],
            required=False,
        ),
        # SB methodology: "benchmarking against peer cohorts" / stack ranking
        UIFormField(
            name="q4",
            label="Compared to senior executives at a similar level that you have observed, how would you rank this candidate's strategic capability?",
            type="select",
            options=BENCHMARK_OPTIONS,
            required=True,
        ),
    ]


def _build_fields_stakeholder_management() -> list[UIFormField]:
    """Stakeholder Management: board relations, investor communication, external engagement.

    SB alignment: "Managing up, cross-functional collaboration, influence" +
    CEO coaching expert network (crisis comms, governance, government relations).
    """
    return [
        UIFormField(
            name="q1",
            label="This candidate communicates with the board and key external stakeholders with clarity, transparency, and appropriate gravitas",
            type="radio",
            options=LIKERT_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q2",
            label="How frequently has this candidate presented to or directly engaged with the board?",
            type="select",
            options=FREQUENCY_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q3",
            label="Which stakeholder groups has this candidate successfully managed?",
            type="multiselect",
            options=[
                {"value": "board", "label": "Board of Directors"},
                {"value": "investors", "label": "Investors / Shareholders"},
                {"value": "regulators", "label": "Government / Regulators"},
                {"value": "media", "label": "Media / Public Relations"},
                {"value": "customers", "label": "Major Clients / Customers"},
                {"value": "unions", "label": "Unions / Employee Representatives"},
            ],
            required=True,
        ),
        UIFormField(
            name="comment",
            label="Any observations about how this candidate handles high-stakes stakeholder situations? (Optional)",
            type="textarea",
            required=False,
            placeholder="e.g. Successfully navigated the regulatory inquiry by building direct rapport with the regulator...",
        ),
    ]


def _build_fields_cultural_stewardship() -> list[UIFormField]:
    """Cultural Stewardship: values alignment, culture shaping, change leadership.

    SB alignment: "Change Management — Driving change, managing resistance,
    communicating vision" + Custom Success Profiling values alignment.
    """
    return [
        UIFormField(
            name="q1",
            label="This candidate embodies the organisation's values and actively shapes a positive leadership culture",
            type="radio",
            options=LIKERT_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q2",
            label="How would you rate this candidate's ability to lead large-scale cultural or organisational change?",
            type="select",
            options=READINESS_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q3",
            label="Which cultural leadership traits have you observed?",
            type="checkbox",
            options=[
                {"value": "values_driven", "label": "Consistently values-driven in decision making"},
                {"value": "inclusive", "label": "Champions diversity, equity and inclusion"},
                {"value": "trust_builder", "label": "Builds trust across all levels of the organisation"},
                {"value": "change_agent", "label": "Effective change agent — brings people along through transitions"},
            ],
            required=False,
        ),
    ]


def _build_fields_crisis_leadership() -> list[UIFormField]:
    """Crisis & Change Leadership: crisis response, resilience, composure under pressure.

    SB alignment: CEO coaching 24/7 crisis support, expert network (crisis
    communications, governance, legal). Sterling Black explicitly positions
    crisis readiness as a core CEO capability requiring ongoing support.
    """
    return [
        UIFormField(
            name="q1",
            label="This candidate remains composed and decisive under significant pressure or crisis",
            type="radio",
            options=LIKERT_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q2",
            label="Rate this candidate's overall readiness to lead the organisation through a major crisis as CEO",
            type="select",
            options=READINESS_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q3",
            label="Has this candidate successfully navigated any of the following? (Select all that apply)",
            type="checkbox",
            options=[
                {"value": "financial_crisis", "label": "Financial downturn or restructuring"},
                {"value": "pr_crisis", "label": "Reputational or public relations crisis"},
                {"value": "regulatory", "label": "Regulatory investigation or compliance issue"},
                {"value": "market_disruption", "label": "Market disruption or major competitive threat"},
                {"value": "people_crisis", "label": "Major people or leadership issue"},
            ],
            required=False,
        ),
        UIFormField(
            name="comment",
            label="Describe a situation where this candidate demonstrated crisis leadership (Optional)",
            type="textarea",
            required=False,
            placeholder="e.g. During the supply chain disruption, they quickly mobilised a cross-functional response team...",
        ),
    ]


def _build_fields_operational_excellence() -> list[UIFormField]:
    """Operational Excellence: execution, resource allocation, performance management.

    SB alignment: "Execution — Goal orientation, resource allocation, delivery capability".
    q2 uses a P&L scope scale instead of a generic 1-10 number — maps to actual
    enterprise tiers of financial responsibility, which is what a board needs to
    assess for CEO readiness.
    """
    return [
        UIFormField(
            name="q1",
            label="This candidate consistently delivers results and drives operational performance across their area of responsibility",
            type="radio",
            options=LIKERT_OPTIONS,
            required=True,
        ),
        # Business-meaningful P&L scope tiers instead of abstract 1-10
        UIFormField(
            name="q2",
            label="What level of P&L responsibility has this candidate demonstrated?",
            type="radio",
            options=PNL_SCOPE_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q3",
            label="Which operational capabilities has this candidate demonstrated?",
            type="multiselect",
            options=[
                {"value": "pnl_delivery", "label": "Consistent P&L delivery against targets"},
                {"value": "transformation", "label": "Business transformation or turnaround"},
                {"value": "scaling", "label": "Scaling operations significantly"},
                {"value": "tech_adoption", "label": "Technology and digital adoption"},
                {"value": "cost_optimisation", "label": "Cost optimisation without sacrificing quality"},
            ],
            required=True,
        ),
    ]


def _build_fields_talent_pipeline() -> list[UIFormField]:
    """Talent & Succession Pipeline: team building, talent development, succession mindset.

    SB alignment: "Talent Leadership — Team building, talent development, delegation"
    + SB's core succession philosophy. q3 tests whether the candidate themselves
    thinks about succession — a key indicator of CEO-level leadership maturity.
    This directly reflects SB's methodology where succession planning is not a
    one-time event but an ongoing leadership responsibility.
    """
    return [
        UIFormField(
            name="q1",
            label="This candidate actively builds leadership capability and develops successors for key roles",
            type="radio",
            options=LIKERT_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q2",
            label="How would you rate this candidate's track record of building high-performing executive teams?",
            type="select",
            options=READINESS_OPTIONS,
            required=True,
        ),
        # SB succession philosophy: a great CEO builds their own pipeline
        UIFormField(
            name="q3",
            label="Has this candidate developed a credible succession plan for their own current role?",
            type="select",
            options=SUCCESSION_MATURITY_OPTIONS,
            required=True,
        ),
        UIFormField(
            name="q4",
            label="Which talent leadership behaviours have you observed?",
            type="checkbox",
            options=[
                {"value": "talent_magnet", "label": "Attracts and retains top talent"},
                {"value": "develops_leaders", "label": "Develops direct reports into senior leaders"},
                {"value": "tough_calls", "label": "Makes tough people decisions when needed"},
                {"value": "cross_functional", "label": "Builds effective cross-functional teams"},
            ],
            required=False,
        ),
        UIFormField(
            name="comment",
            label="Any observations about this candidate's ability to build and lead an executive team? (Optional)",
            type="textarea",
            required=False,
            placeholder="e.g. Built the entire APAC leadership team from scratch and three of them are now in global roles...",
        ),
    ]


DIMENSION_BUILDERS = {
    "strategic_leadership": _build_fields_strategic_leadership,
    "stakeholder_management": _build_fields_stakeholder_management,
    "cultural_stewardship": _build_fields_cultural_stewardship,
    "crisis_leadership": _build_fields_crisis_leadership,
    "operational_excellence": _build_fields_operational_excellence,
    "talent_pipeline": _build_fields_talent_pipeline,
}


class AssessmentFormInput(BaseModel):
    dimension: str = Field(description="The dimension key to assess, e.g. strategic_leadership, crisis_leadership")
    target_leader_id: str = Field(description="Identifier of the candidate being assessed")
    evaluator_role: str = Field(description="Assessor's board role, e.g. Board Chair, Non-Executive Director")


class AssessmentFormTool(BaseTool):
    name: str = "show-assessment-form"
    description: str = "Display the succession readiness questionnaire for a specific CEO-readiness dimension."
    args_schema: type[BaseModel] = AssessmentFormInput

    def _run(self, dimension: str, target_leader_id: str, evaluator_role: str) -> dict:
        label = DIMENSION_LABELS.get(dimension, dimension)
        builder = DIMENSION_BUILDERS.get(dimension)
        if builder:
            fields = builder()
        else:
            fields = [
                UIFormField(name="q1", label=f"Rate this candidate's {label.lower()}", type="select",
                            options=LIKERT_OPTIONS, required=True),
                UIFormField(name="comment", label="Comments (Optional)", type="textarea", required=False),
            ]

        form_result = UIFormResult(
            form_schema=UIFormSchema(
                form_id=f"succession-{dimension}",
                title=f"CEO Succession Readiness — {label}",
                fields=fields,
                submit_label="Submit",
                cancel_label="Skip Dimension",
            ),
            prefill={"dimension": dimension},
            context={"evaluator_role": evaluator_role, "dimension": dimension},
        )
        return form_result.model_dump()
