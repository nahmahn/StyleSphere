from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Optional
from .core.models import ChatRequest, ChatResponse
from .core.services import orchestrator_agent




app = FastAPI(title="Style-RAG Visual Agentic API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request_json: str = Form(...),
    image_file: Optional[UploadFile] = File(None)
):
    chat_request = ChatRequest(**json.loads(chat_request_json))
    image_bytes = await image_file.read() if image_file else None
    
    response_text, items_metadata, new_state = orchestrator_agent(
        query=chat_request.message, history=chat_request.history,
        state=chat_request.state, image_bytes=image_bytes
    )
    return ChatResponse(response=response_text, items=items_metadata, state=new_state)

# This serves your local clothing images for the product cards
app.mount("/images", StaticFiles(directory="data/train/cloth"), name="images")
# This serves the frontend HTML, CSS, and JS files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")