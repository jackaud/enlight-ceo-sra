"""WebSocket event handlers for Socket.IO."""

import uuid
import asyncio
from langchain_core.messages import HumanMessage, AIMessage

from agent.graph import DEFAULT_STATE, run_phase, apply_updates
from tools.assessment_form import DIMENSION_LABELS


def extract_text(content) -> str:
    """Extract text from AIMessage content (str or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return ""


# In-memory session storage
sessions: dict[str, dict] = {}


def get_or_create_session(session_id: str) -> dict:
    if session_id not in sessions:
        sessions[session_id] = dict(DEFAULT_STATE)
        sessions[session_id]["messages"] = []
        sessions[session_id]["collected_responses"] = {}
        sessions[session_id]["pending_form"] = {}
    return sessions[session_id]


async def handle_chat_message(sio, sid, data):
    """Handle incoming chat message from user."""
    session_id = data.get("session_id", sid)
    message = data.get("message", "")

    state = get_or_create_session(session_id)
    state["messages"].append(HumanMessage(content=message))

    await run_and_stream(sio, sid, session_id, state)


async def handle_form_submit(sio, sid, data):
    """Handle form submission from user."""
    session_id = data.get("session_id", sid)
    form_id = data.get("form_id", "")
    form_data = data.get("form_data", {})

    state = get_or_create_session(session_id)

    dimension = form_id.replace("succession-", "").replace("leadership-", "")

    state["collected_responses"][dimension] = form_data
    state["current_dimension"] = state.get("current_dimension", 0) + 1
    state["pending_form"] = {}

    dim_label = DIMENSION_LABELS.get(dimension, dimension)
    scores = []
    numeric_scores = []
    for key, value in form_data.items():
        if key.startswith("q"):
            scores.append(f"{key}={value}")
            try:
                numeric_scores.append(int(value))
            except (ValueError, TypeError):
                pass
    comment = form_data.get("comment", "")
    summary = f"User submitted {dim_label} assessment: {', '.join(scores)}"
    if comment:
        summary += f", comment: {comment}"

    # Code-level control: only ask follow-up if score is exactly 1 or 5
    has_extreme = any(s == 1 or s == 5 for s in numeric_scores)
    if has_extreme:
        summary += "\n[SYSTEM: A score of 1 or 5 was given. Ask for ONE specific example, then move on.]"
    else:
        summary += "\n[SYSTEM: All scores are moderate (2-4). Do NOT ask follow-up questions. Acknowledge briefly and show the next dimension form immediately.]"

    state["messages"].append(HumanMessage(content=summary))

    if state["current_dimension"] >= len(state["dimensions"]):
        state["phase"] = "analyzing"

    await run_and_stream(sio, sid, session_id, state)


async def handle_form_cancel(sio, sid, data):
    """Handle form skip from user."""
    session_id = data.get("session_id", sid)
    form_id = data.get("form_id", "")

    state = get_or_create_session(session_id)

    dimension = form_id.replace("succession-", "").replace("leadership-", "")
    dim_label = DIMENSION_LABELS.get(dimension, dimension)

    state["current_dimension"] = state.get("current_dimension", 0) + 1
    state["pending_form"] = {}
    state["messages"].append(HumanMessage(content=f"User skipped {dim_label} assessment"))

    if state["current_dimension"] >= len(state["dimensions"]):
        state["phase"] = "analyzing"

    await run_and_stream(sio, sid, session_id, state)


async def run_and_stream(sio, sid, session_id: str, state: dict):
    """Run the current phase and stream response to client."""
    phase_before = state.get("phase", "?")
    message_id = str(uuid.uuid4())

    # Emit chat_start
    await sio.emit("chat_start", {"message_id": message_id}, to=sid)

    # Run the phase
    updates = await run_phase(state)

    # Apply updates to session state
    new_state = apply_updates(state, updates)
    sessions[session_id] = new_state

    # Extract AI messages from updates to stream
    # Skip AIMessages that contain tool_calls — their text is just preamble
    ai_messages = []
    for msg in updates.get("messages", []):
        if isinstance(msg, AIMessage) and msg.content:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                continue
            text = extract_text(msg.content)
            if text:
                ai_messages.append(text)

    # Stream the text content
    full_text = "\n\n".join(ai_messages)
    if full_text:
        chunk_size = 10
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i + chunk_size]
            await sio.emit("chat_chunk", {
                "message_id": message_id,
                "content": chunk,
            }, to=sid)
            await asyncio.sleep(0.03)

    # Build chat_complete payload
    complete_payload = {"message_id": message_id}

    # Attach form if pending
    pending = new_state.get("pending_form")
    form_was_sent = False
    if pending and isinstance(pending, dict) and pending.get("form_schema"):
        complete_payload["ui_forms"] = [{
            "form_instance_id": str(uuid.uuid4()),
            **pending,
        }]
        form_was_sent = True

    # Attach progress if in collecting phase
    if new_state.get("phase") in ("collecting", "analyzing") or new_state.get("pending_form"):
        dims = new_state.get("dimensions", [])
        current = new_state.get("current_dimension", 0)
        completed = dims[:current]
        complete_payload["progress"] = {
            "phase": new_state.get("phase", "collecting"),
            "dimensions": [DIMENSION_LABELS.get(d, d) for d in dims],
            "current_dimension": current,
            "completed_dimensions": [DIMENSION_LABELS.get(d, d) for d in completed],
        }

    await sio.emit("chat_complete", complete_payload, to=sid)

    # Auto-run collecting ONLY on phase transition from intake → collecting (once)
    phase_after = new_state.get("phase", "?")
    if phase_before != "collecting" and phase_after == "collecting":
        await run_and_stream(sio, sid, session_id, sessions[session_id])
        return

    # Clear pending_form AFTER auto-run check to prevent re-sending on subsequent calls
    if form_was_sent:
        sessions[session_id]["pending_form"] = {}

    # If we've entered analyzing or reporting, run through to final report
    if new_state.get("phase") in ("analyzing", "reporting"):
        await auto_run_to_report(sio, sid, session_id)


async def auto_run_to_report(sio, sid, session_id: str):
    """Run remaining phases (analyzing → reporting) to completion."""
    await asyncio.sleep(1)

    state = sessions[session_id]

    # Keep running phases until we reach "complete"
    while state.get("phase") not in ("complete", None):
        message_id = str(uuid.uuid4())
        await sio.emit("chat_start", {"message_id": message_id}, to=sid)

        try:
            phase = state.get("phase")
            # Send progress hint before long-running LLM calls
            if phase == "reporting":
                await sio.emit("chat_chunk", {
                    "message_id": message_id,
                    "content": "Generating your succession readiness report...\n\n",
                }, to=sid)
            updates = await run_phase(state)
            state = apply_updates(state, updates)
            sessions[session_id] = state
        except Exception as e:
            print(f"[report] ERROR in phase={state.get('phase')}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Send error message to client
            await sio.emit("chat_chunk", {
                "message_id": message_id,
                "content": f"An error occurred generating the report. Please try refreshing. ({type(e).__name__})",
            }, to=sid)
            await sio.emit("chat_complete", {"message_id": message_id}, to=sid)
            return

        # Stream messages — skip tool_call preamble
        for msg in updates.get("messages", []):
            if isinstance(msg, AIMessage) and msg.content:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    continue
                content = extract_text(msg.content)
                if not content:
                    continue
                chunk_size = 10
                for i in range(0, len(content), chunk_size):
                    await sio.emit("chat_chunk", {
                        "message_id": message_id,
                        "content": content[i:i + chunk_size],
                    }, to=sid)
                    await asyncio.sleep(0.03)

        await sio.emit("chat_complete", {"message_id": message_id}, to=sid)

        # Brief pause between phases
        if state.get("phase") != "complete":
            await asyncio.sleep(1.5)
