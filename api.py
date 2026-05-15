"""
FastAPI backend for Spoon Feedr.
Exposes the orchestrator via a REST API and handles proactive background services.
"""

import os
import json
import threading
import uuid
from typing import List, Optional

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from core.orchestrator import create_spoon_feedr_graph
from core.monitor import babysitter_background_loop

app = FastAPI(title="Spoon Feedr API")

@app.on_event("startup")
async def startup_event():
    """Starts the proactive babysitter background service on API startup."""
    # Start the babysitter background loop in a separate thread
    thread = threading.Thread(target=babysitter_background_loop, args=(".", 60), daemon=True)
    thread.start()
    print("🚀 Proactive Baby Sitter daemon started.")

graph = create_spoon_feedr_graph()

class ChatRequest(BaseModel):
    """Pydantic model for chat requests."""
    message: str
    session_id: Optional[str] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    """Streams a chat request through the LangGraph orchestrator using a streaming response."""
    # Generate a unique session ID if none provided
    session_id = request.session_id or str(uuid.uuid4())

    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "current_step": 0,
        "session_id": session_id
    }

    async def event_generator():
        async for event in graph.astream(initial_state):
            # Serialize event and yield as SSE-like data
            # Using simple newline-separated JSON for robustness
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Default to loopback for security, configurable via HOST env var
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"📡 Starting Spoon Feedr API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
