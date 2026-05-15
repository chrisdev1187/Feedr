from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from core.orchestrator import create_spoon_feedr_graph
from langchain_core.messages import HumanMessage
from core.monitor import babysitter_background_loop
import threading

app = FastAPI(title="Spoon Feedr API")

@app.on_event("startup")
async def startup_event():
    # Start the babysitter background loop in a separate thread
    thread = threading.Thread(target=babysitter_background_loop, args=(".", 60), daemon=True)
    thread.start()
    print("🚀 Proactive Baby Sitter daemon started.")
graph = create_spoon_feedr_graph()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

@app.post("/chat")
async def chat(request: ChatRequest):
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "current_step": 0
    }

    results = []
    async for event in graph.astream(initial_state):
        results.append(event)

    return {"status": "success", "events": results}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
