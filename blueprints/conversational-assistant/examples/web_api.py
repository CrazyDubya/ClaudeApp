"""
Web API Conversational Assistant

A FastAPI-based web chat API example of the conversational-assistant blueprint.
Demonstrates REST API with session management and streaming responses.

Requirements:
    pip install fastapi uvicorn sse-starlette

Run:
    uvicorn web_api:app --reload
"""

import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from anthropic import Anthropic

# Check for FastAPI before importing
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


# Session storage (in-memory for demo; use Redis/DB in production)
sessions: dict[str, list[dict]] = {}

# System prompt
SYSTEM_PROMPT = """You are a helpful AI assistant accessible via API.
Be concise and accurate in your responses.
Format responses appropriately for programmatic consumption."""


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    message_count: int


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, list[dict]]:
    """Get existing session or create a new one."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    new_id = str(uuid.uuid4())
    sessions[new_id] = []
    return new_id, sessions[new_id]


def create_app() -> "FastAPI":
    """Create and configure the FastAPI application."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not installed. Run: pip install fastapi uvicorn")

    app = FastAPI(
        title="Conversational Assistant API",
        description="A Claude-powered chat API with session management",
        version="1.0.0",
    )

    client = Anthropic()

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """
        Send a message and get a response.

        Args:
            request: Chat request with message and optional session_id

        Returns:
            ChatResponse with the assistant's response
        """
        session_id, history = get_or_create_session(request.session_id)

        # Add user message
        history.append({"role": "user", "content": request.message})

        if request.stream:
            # Return streaming response
            return StreamingResponse(
                stream_response(client, history, session_id),
                media_type="text/event-stream",
            )

        # Non-streaming response
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=history,
        )

        assistant_message = response.content[0].text
        history.append({"role": "assistant", "content": assistant_message})

        return ChatResponse(
            response=assistant_message,
            session_id=session_id,
            message_count=len(history),
        )

    @app.post("/chat/stream")
    async def chat_stream(request: ChatRequest):
        """Stream a chat response using Server-Sent Events."""
        session_id, history = get_or_create_session(request.session_id)
        history.append({"role": "user", "content": request.message})

        return StreamingResponse(
            stream_response(client, history, session_id),
            media_type="text/event-stream",
        )

    @app.get("/session/{session_id}")
    async def get_session(session_id: str):
        """Get conversation history for a session."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "messages": sessions[session_id],
            "message_count": len(sessions[session_id]),
        }

    @app.delete("/session/{session_id}")
    async def delete_session(session_id: str):
        """Delete a session."""
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        del sessions[session_id]
        return {"status": "deleted", "session_id": session_id}

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "active_sessions": len(sessions)}

    return app


async def stream_response(client: Anthropic, history: list, session_id: str):
    """Generator for streaming responses."""
    full_response = ""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=history,
    ) as stream:
        for text in stream.text_stream:
            full_response += text
            yield f"data: {text}\n\n"

    # Store complete response
    history.append({"role": "assistant", "content": full_response})
    yield f"data: [DONE]\n\n"


# Create app instance
if FASTAPI_AVAILABLE:
    app = create_app()
else:
    app = None


if __name__ == "__main__":
    if os.environ.get("FORGE_VALIDATION_MODE"):
        print("✓ Example validated (syntax check only)")
    elif not FASTAPI_AVAILABLE:
        print("FastAPI not installed. Run: pip install fastapi uvicorn sse-starlette")
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
