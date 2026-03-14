"""Assessment flow controller - manages phase transitions and node dispatch."""

from agent.state import AssessmentState
from agent.nodes import (
    intake_node,
    collecting_node,
    analyzing_node,
    reporting_node,
    complete_node,
)

# Default initial state
DEFAULT_STATE: AssessmentState = {
    "messages": [],
    "phase": "intake",
    "target_leader": {},
    "evaluator_role": "",
    "dimensions": [],
    "current_dimension": 0,
    "collected_responses": {},
    "ml_result": {},
    "pending_form": {},
}

# Phase to node mapping
PHASE_NODES = {
    "intake": intake_node,
    "collecting": collecting_node,
    "analyzing": analyzing_node,
    "reporting": reporting_node,
    "complete": complete_node,
}


async def run_phase(state: AssessmentState) -> dict:
    """Run the current phase node and return state updates."""
    phase = state.get("phase", "intake")
    node_fn = PHASE_NODES.get(phase)
    if not node_fn:
        return {}

    updates = await node_fn(state)
    return updates


def apply_updates(state: AssessmentState, updates: dict) -> AssessmentState:
    """Apply node output updates to state."""
    new_state = dict(state)
    for key, value in updates.items():
        if key == "messages":
            new_state["messages"] = list(state.get("messages", [])) + value
        else:
            new_state[key] = value
    return new_state
