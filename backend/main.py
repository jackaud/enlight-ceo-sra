"""FastAPI + Socket.IO entry point."""

import os
import traceback
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# CORS: allow localhost + deployed frontend
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:7100,http://localhost:7101"
).split(",")

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=ALLOWED_ORIGINS,
)

# Create FastAPI app
app = FastAPI(title="EnlightIn API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wrap with Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)


@app.get("/health")
async def health():
    from agent.nodes import LLM_MODE
    return {"status": "ok", "llm_mode": LLM_MODE}


@app.get("/llm-mode")
async def get_llm_mode():
    import agent.nodes as nodes
    return {"mode": nodes.LLM_MODE}


@app.post("/llm-mode/{mode}")
async def set_llm_mode(mode: str):
    import agent.nodes as nodes
    if mode not in ("mock", "haiku", "sonnet"):
        from fastapi import HTTPException
        raise HTTPException(400, f"Invalid mode: {mode}. Use mock/haiku/sonnet")
    nodes.LLM_MODE = mode
    return {"mode": mode, "message": f"Switched to {mode}"}


@app.get("/form-mode")
async def get_form_mode():
    from tools.assessment_form import FORM_MODE
    return {"mode": FORM_MODE}


@app.post("/form-mode/{mode}")
async def set_form_mode(mode: str):
    import tools.assessment_form as af
    if mode not in ("static", "dynamic"):
        from fastapi import HTTPException
        raise HTTPException(400, f"Invalid mode: {mode}. Use static/dynamic")
    af.FORM_MODE = mode
    return {"mode": mode, "message": f"Switched to {mode}"}


# Socket.IO event handlers
GREETING = (
    "Welcome to **EnlightIn**, the AI-powered CEO succession planning platform "
    "by Sterling Black — the gold standard in board, CEO and C-Suite leadership development.\n\n"
    "I'll guide you through a comprehensive **CEO Succession Readiness Assessment** "
    "to evaluate an internal candidate's preparedness for the CEO role. "
    "To get started, please tell me:\n\n"
    "- **Your role** on the board (e.g. Board Chair, Non-Executive Director, CHRO)\n"
    "- **The candidate** you'd like to assess (name and current role)\n"
    "- **The succession context** (planned retirement, emergency preparedness, etc.)\n\n"
    "You can also just say something like: "
    "*\"I'm the Board Chair of TechCorp. Our CEO plans to retire in 18 months "
    "and I'd like to assess our CFO Sarah Mitchell as a succession candidate.\"*"
)


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def request_greeting(sid, data):
    """Client requests the initial greeting after listeners are ready."""
    import uuid, asyncio
    message_id = str(uuid.uuid4())
    await sio.emit("chat_start", {"message_id": message_id}, to=sid)
    chunk_size = 12
    for i in range(0, len(GREETING), chunk_size):
        await sio.emit("chat_chunk", {
            "message_id": message_id,
            "content": GREETING[i:i + chunk_size],
        }, to=sid)
        await asyncio.sleep(0.02)
    await sio.emit("chat_complete", {"message_id": message_id}, to=sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def chat_message(sid, data):
    try:
        from websocket.handlers import handle_chat_message
        await handle_chat_message(sio, sid, data)
    except Exception as e:
        print(f"[chat_message] ERROR: {e}", flush=True)
        traceback.print_exc()


@sio.event
async def form_submit(sid, data):
    try:
        from websocket.handlers import handle_form_submit
        await handle_form_submit(sio, sid, data)
    except Exception as e:
        print(f"[form_submit] ERROR: {e}", flush=True)
        traceback.print_exc()


@sio.event
async def form_cancel(sid, data):
    try:
        from websocket.handlers import handle_form_cancel
        await handle_form_cancel(sio, sid, data)
    except Exception as e:
        print(f"[form_cancel] ERROR: {e}", flush=True)
        traceback.print_exc()


# For running with uvicorn
app = socket_app
