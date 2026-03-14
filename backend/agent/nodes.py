"""LangGraph node implementations for each assessment phase — CEO Succession."""

import json
import os
import uuid
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agent.state import AssessmentState
from agent.prompts import INTAKE_PROMPT, COLLECTING_PROMPT_TEMPLATE, REPORTING_PROMPT_TEMPLATE, COMPLETE_PROMPT_TEMPLATE
from tools.confirm_intake import ConfirmIntakeTool
from tools.assessment_form import AssessmentFormTool, DIMENSION_LABELS
from tools.ml_prediction import mock_predict

# LLM_MODE: mock | haiku | sonnet (default: mock)
LLM_MODE = os.getenv("LLM_MODE", "mock")

MODEL_MAP = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-20250514",
}

DEFAULT_DIMENSIONS = [
    "strategic_leadership", "stakeholder_management", "cultural_stewardship",
    "crisis_leadership", "operational_excellence", "talent_pipeline",
]


def get_llm():
    model = MODEL_MAP.get(LLM_MODE, MODEL_MAP["sonnet"])
    return ChatAnthropic(
        model=model,
        temperature=0.7,
        max_tokens=1024,
    )


def is_mock():
    return LLM_MODE == "mock"


# ── Mock responses ──────────────────────────────────────────────

MOCK_INTAKE_REPLY = (
    "Thank you. Let me confirm the assessment details:\n\n"
    "- **Candidate**: {name} ({role})\n"
    "- **Your role**: {evaluator_role}\n"
    "- **Assessment type**: CEO Succession Readiness — 6 dimensions\n\n"
    "Sterling Black's research shows that well-assessed internal candidates "
    "outperform external CEO hires — averaging 8.7 vs 7.3 years in tenure. "
    "Let's begin the assessment."
)

MOCK_COLLECTING_INTRO = (
    "Now assessing dimension {idx}: **{dim_label}**\n\n"
    "Please rate this candidate's CEO readiness based on your direct observations."
)

MOCK_FOLLOWUP_NORMAL = "Thank you for your assessment. Let's move on to the next dimension."

MOCK_FOLLOWUP_EXTREME = (
    "I noticed you gave a particularly strong rating on one of the items. "
    "Could you share a specific example to illustrate? "
    "This will help us provide more targeted development recommendations."
)

MOCK_REPORT_TEMPLATE = """CEO Succession Readiness Assessment complete. Here is the report for **{name}** ({role}):

**Overall Readiness Score: {overall}/100 — {readiness}**

**Dimension Scores:**
{dim_rows}

**Key Strengths**: {strengths}
**Critical Development Gaps**: {dev_areas}

**Development Recommendations**:
{suggestions}

*Note: This is a preliminary assessment based on a single evaluator (confidence: 65%). A full Sterling Black engagement would include psychometric profiling, 360° feedback, and structured interviews across all 10 touchpoints for a comprehensive succession readiness evaluation.*

Would you like to discuss any dimension in more detail, or explore development planning for this candidate?"""


def _make_row(label: str, score: int, rating: str) -> str:
    return f"- **{label}**: {score}/100 ({rating})"


# ── Node implementations ────────────────────────────────────────

async def intake_node(state: AssessmentState) -> dict:
    """Intake phase: collect succession assessment background via conversation."""
    if is_mock():
        return _mock_intake(state)

    llm = get_llm()
    tools = [ConfirmIntakeTool()]
    llm_with_tools = llm.bind_tools(tools)

    system = SystemMessage(content=INTAKE_PROMPT)
    messages = [system] + state["messages"]

    response = await llm_with_tools.ainvoke(messages)

    # Check if LLM called confirm-intake tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call["name"] == "confirm-intake":
            args = tool_call["args"]
            tool = tools[0]
            tool_result = tool.invoke(tool_call["args"])

            tool_msg = ToolMessage(
                content=tool_result,
                tool_call_id=tool_call["id"],
            )

            follow_up_messages = [system] + state["messages"] + [response, tool_msg]
            follow_up = await llm.ainvoke(follow_up_messages)

            return {
                "messages": [response, tool_msg, follow_up],
                "phase": "collecting",
                "target_leader": {
                    "name": args["leader_name"],
                    "role": args["leader_role"],
                },
                "evaluator_role": args["evaluator_role"],
                "dimensions": args["dimensions"],
                "current_dimension": 0,
                "collected_responses": {},
            }

    return {"messages": [response]}


def _mock_intake(state: AssessmentState) -> dict:
    """Mock intake: parse user message for candidate info, skip LLM."""
    user_msg = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            user_msg = msg.content
            break

    # Default values for mock mode
    name = "Sarah Mitchell"
    role = "CFO"
    evaluator_role = "Board Chair"

    # Simple heuristic: look for "assess/evaluate <Name>" pattern
    msg_lower = user_msg.lower()
    for keyword in ["assess", "evaluate", "review", "candidate"]:
        if keyword in msg_lower:
            after = user_msg.split(keyword, 1)[-1].strip(" ,.")
            if after:
                parts = after.split(",")[0].split(".")[0].strip()
                for filler in ["our", "my", "the", "a", "an", "is"]:
                    parts = " ".join(
                        w for w in parts.split()
                        if w.lower() != filler
                    )
                for rw in ["CFO", "COO", "CTO", "CEO", "VP", "President", "Managing Director", "Division Head"]:
                    if rw.lower() in parts.lower():
                        role = rw
                        parts = parts.lower().replace(rw.lower(), "").strip(" ,")
                if parts.strip():
                    name = parts.strip().title()
            break

    reply = MOCK_INTAKE_REPLY.format(
        name=name, role=role, evaluator_role=evaluator_role,
    )

    return {
        "messages": [AIMessage(content=reply)],
        "phase": "collecting",
        "target_leader": {"name": name, "role": role},
        "evaluator_role": evaluator_role,
        "dimensions": DEFAULT_DIMENSIONS,
        "current_dimension": 0,
        "collected_responses": {},
    }


async def collecting_node(state: AssessmentState) -> dict:
    """Collecting phase: show assessment forms for each dimension."""
    dimensions = state["dimensions"]
    current_idx = state["current_dimension"]

    if current_idx >= len(dimensions):
        return {"phase": "analyzing"}

    current_dim = dimensions[current_idx]
    current_label = DIMENSION_LABELS.get(current_dim, current_dim)

    if is_mock():
        return _mock_collecting(state, current_dim, current_label, current_idx)

    llm = get_llm()
    tools = [AssessmentFormTool()]
    llm_with_tools = llm.bind_tools(tools)

    completed = [DIMENSION_LABELS.get(d, d) for d in dimensions[:current_idx]]

    prompt = COLLECTING_PROMPT_TEMPLATE.format(
        leader_name=state["target_leader"]["name"],
        leader_role=state["target_leader"]["role"],
        evaluator_role=state["evaluator_role"],
        current_dimension_name=current_label,
        current_index=current_idx + 1,
        total_dimensions=len(dimensions),
        completed_dimensions=", ".join(completed) if completed else "None",
    )

    system = SystemMessage(content=prompt)
    messages = [system] + state["messages"]

    response = await llm_with_tools.ainvoke(messages)

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        if tool_call["name"] == "show-assessment-form":
            tool = tools[0]
            tool_result = tool.invoke(tool_call["args"])

            tool_msg = ToolMessage(
                content=json.dumps(tool_result, ensure_ascii=False),
                tool_call_id=tool_call["id"],
            )

            follow_up_messages = [system] + state["messages"] + [response, tool_msg]
            follow_up = await llm.ainvoke(follow_up_messages)

            return {
                "messages": [response, tool_msg, follow_up],
                "pending_form": tool_result,
            }

    # Fallback: LLM didn't call the tool — generate form directly
    tool = AssessmentFormTool()
    form_result = tool.invoke({
        "dimension": current_dim,
        "target_leader_id": state["target_leader"].get("name", ""),
        "evaluator_role": state["evaluator_role"],
    })
    return {
        "messages": [response],
        "pending_form": form_result,
    }


def _mock_collecting(state, current_dim, current_label, current_idx):
    """Mock collecting: generate form directly, check for follow-up on previous submission."""
    messages_out = []

    # Check if last message was a form submission — generate follow-up
    last_msg = state["messages"][-1] if state["messages"] else None
    if last_msg and isinstance(last_msg, HumanMessage) and "submitted" in last_msg.content.lower():
        has_extreme = any(f"q{i}=1" in last_msg.content or f"q{i}=5" in last_msg.content
                         for i in range(1, 5))
        if has_extreme:
            messages_out.append(AIMessage(content=MOCK_FOLLOWUP_EXTREME))
        else:
            messages_out.append(AIMessage(content=MOCK_FOLLOWUP_NORMAL))

    # Show intro + form for current dimension
    intro = MOCK_COLLECTING_INTRO.format(
        idx=current_idx + 1, dim_label=current_label,
    )
    messages_out.append(AIMessage(content=intro))

    # Generate form via tool
    tool = AssessmentFormTool()
    form_result = tool.invoke({
        "dimension": current_dim,
        "target_leader_id": state["target_leader"].get("name", ""),
        "evaluator_role": state["evaluator_role"],
    })

    return {
        "messages": messages_out,
        "pending_form": form_result,
    }


async def analyzing_node(state: AssessmentState) -> dict:
    """Analyzing phase: run mock ML prediction."""
    result = mock_predict(state["collected_responses"])
    return {
        "ml_result": result,
        "phase": "reporting",
        "messages": [AIMessage(content="Analysing succession readiness data, please wait...")],
    }


async def reporting_node(state: AssessmentState) -> dict:
    """Reporting phase: present succession readiness results."""
    if is_mock():
        return _mock_reporting(state)

    llm = get_llm()

    prompt = REPORTING_PROMPT_TEMPLATE.format(
        leader_name=state["target_leader"]["name"],
        leader_role=state["target_leader"]["role"],
        ml_result=json.dumps(state["ml_result"], ensure_ascii=False, indent=2),
    )

    system = SystemMessage(content=prompt)
    messages = [system] + state["messages"]

    response = await llm.ainvoke(messages)
    return {
        "messages": [response],
        "phase": "complete",
    }


def _mock_reporting(state: AssessmentState) -> dict:
    """Mock reporting: format ML result as succession readiness report."""
    ml = state.get("ml_result", {})
    name = state.get("target_leader", {}).get("name", "Candidate")
    role = state.get("target_leader", {}).get("role", "")

    dim_rows = "\n".join(
        _make_row(label, data["score"], data["rating"])
        for label, data in ml.get("dimension_scores", {}).items()
    )
    suggestions = "\n".join(
        f"{i}. {s}" for i, s in enumerate(ml.get("suggestions", []), 1)
    )

    report = MOCK_REPORT_TEMPLATE.format(
        name=name,
        role=role,
        overall=ml.get("overall_score", 50),
        readiness=ml.get("readiness", "Developing"),
        dim_rows=dim_rows,
        strengths=", ".join(ml.get("strengths", [])),
        dev_areas=", ".join(ml.get("development_gaps", [])),
        suggestions=suggestions,
    )

    return {
        "messages": [AIMessage(content=report)],
        "phase": "complete",
    }


MOCK_COMPLETE_REPLY = (
    "Thank you for your question. Based on the succession readiness assessment, "
    "I'd recommend focusing on the identified development gaps through "
    "targeted executive coaching and structured board exposure.\n\n"
    "Sterling Black's CEO coaching programme pairs candidates with experienced "
    "former CEOs who provide expert guidance on the specific areas identified. "
    "If you'd like to discuss any dimension in more detail, "
    "or explore how a full 10-touchpoint assessment would deepen these insights, "
    "just let me know."
)


async def complete_node(state: AssessmentState) -> dict:
    """Post-report phase: answer follow-up questions about succession readiness."""
    if is_mock():
        return {"messages": [AIMessage(content=MOCK_COMPLETE_REPLY)]}

    llm = get_llm()

    prompt = COMPLETE_PROMPT_TEMPLATE.format(
        leader_name=state["target_leader"]["name"],
        leader_role=state["target_leader"]["role"],
        ml_result=json.dumps(state["ml_result"], ensure_ascii=False, indent=2),
    )

    system = SystemMessage(content=prompt)
    messages = [system] + state["messages"]

    response = await llm.ainvoke(messages)
    return {"messages": [response]}


# Routing functions
def route_after_intake(state: AssessmentState) -> str:
    if state.get("phase") == "collecting":
        return "collecting"
    return "intake"


def route_after_collecting(state: AssessmentState) -> str:
    if state.get("phase") == "analyzing":
        return "analyzing"
    dimensions = state.get("dimensions", [])
    current = state.get("current_dimension", 0)
    if current >= len(dimensions):
        return "analyzing"
    return "collecting"
