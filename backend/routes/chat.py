import asyncio

from fastapi import APIRouter, HTTPException, Depends ,Request
from pydantic import BaseModel
from typing import List, Tuple, Optional
from fastapi.responses import StreamingResponse

from backend.services.planner import run_assistant, AgentState, run_qa_assistant # Assuming run_assistant can be adapted for streaming
from langchain_core.messages import HumanMessage, AIMessage
from backend.services.db_service import get_goal_by_id
from sqlalchemy.orm import Session
from backend.data.db import get_db

router = APIRouter()

class ChatMessageInput(BaseModel):
    message: str
    session_id: Optional[str] = "default_session" # Simple session management
    # In a real app, chat_history might be managed server-side per session_id
    chat_history: Optional[List[Tuple[str, str]]] = [] # (Human, AI) tuples

class ChatMessageOutput(BaseModel):
    response: str
    session_id: str
    updated_chat_history: List[Tuple[str, str]]

# A simple in-memory store for chat histories by session_id
# WARNING: This is not suitable for production. Use a proper database or cache.
chat_histories = {}

def get_current_goal(request: Request, db: Session = Depends(get_db)):
    goal_id = request.state.goal_id
    if goal_id:
        return get_goal_by_id(db, goal_id)
    return None

async def stream_response_generator(user_input: str, session_id: str, history_tuples: List[Tuple[str,str]], current_goal: Optional[dict] = None):
    """Runs the assistant and streams the response sentence by sentence or chunk by chunk."""
    # This is a simplified streaming example. 
    # True streaming from LangGraph requires more complex handling of intermediate steps 
    # and potentially yield intermediate thoughts or final response chunks.

    # For now, we'll get the full response and then "simulate" streaming it.
    # A more advanced version would involve `ainvoke` on the graph and processing an AsyncIterator.

    try:
        if current_goal:
            # Goal-oriented mode
            full_response = run_assistant(user_input, chat_history=history_tuples, current_goal=current_goal)
        else:
            # Q&A mode
            full_response = run_qa_assistant(user_input, chat_history=history_tuples)

        # Simulate streaming by splitting the response (e.g., by sentences or newlines)
        # This is NOT true LLM streaming, but demonstrates the mechanism for FastAPI
        sentences = full_response.split('\n') # Example: split by newline
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                yield f"data: {sentence.strip()}\n\n"
                await asyncio.sleep(0.1) # Simulate delay between chunks
            if i < len(sentences) - 1 and sentences[i+1].strip(): # Add newline if next sentence is not blank
                 yield f"data: \n\n" # Represents a newline in SSE
                 await asyncio.sleep(0.05)

        # Update chat history after successful generation
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        chat_histories[session_id].append((user_input, full_response))

    except Exception as e:
          print(f"Error during response generation: {e}")
          yield f"data: Error: Could not process your request.\n\n"
    finally:
        yield "data: [DONE]\n\n" # Signal stream completion

@router.post("/chat/stream", tags=["Chat"])
async def stream_chat_endpoint(payload: ChatMessageInput, request: Request, db: Session = Depends(get_db)):
    """Receives a user message, processes it with the AI assistant, and streams the response."""
    session_id = payload.session_id or "default_session"
    
    # Retrieve history for the session or use provided history
    current_history_tuples = chat_histories.get(session_id, [])
    if payload.chat_history: # If client sends history, it might override server's or be used if server has none
        # Decide on a strategy: merge, prefer client, prefer server
        # For simplicity, let's use client's if provided, else server's
        current_history_tuples = payload.chat_history 
        chat_histories[session_id] = current_history_tuples # Update server's knowledge

    current_goal = get_current_goal(request, db)

    return StreamingResponse(
        stream_response_generator(payload.message, session_id, current_history_tuples, current_goal),
        media_type="text/event-stream"
    ),"""Receives a user message, processes it with the AI assistant, and streams the response."""
    session_id = payload.session_id or "default_session"
    
    # Retrieve history for the session or use provided history
    current_history_tuples = chat_histories.get(session_id, [])
    if payload.chat_history: # If client sends history, it might override server's or be used if server has none
        # Decide on a strategy: merge, prefer client, prefer server
        # For simplicity, let's use client's if provided, else server's
        current_history_tuples = payload.chat_history 
        chat_histories[session_id] = current_history_tuples # Update server's knowledge

    return StreamingResponse(
        stream_response_generator(payload.message, session_id, current_history_tuples),
        media_type="text/event-stream"
    )

@router.post("/chat", response_model=ChatMessageOutput, tags=["Chat"])
async def chat_endpoint(payload: ChatMessageInput, request: Request, db: Session = Depends(get_db)) -> ChatMessageOutput:
    """Receives a user message, processes it with the AI assistant, and returns a response."""
    session_id = payload.session_id
    
    # Retrieve history for the session or use provided history
    current_history_tuples = chat_histories.get(session_id, [])
    if payload.chat_history:
        current_history_tuples = payload.chat_history
        chat_histories[session_id] = current_history_tuples

    current_goal = get_current_goal(request, db)

    try:
        # Run the synchronous run_assistant in a separate thread to avoid blocking the event loop
        if current_goal:
            response_text = await asyncio.to_thread(run_assistant, payload.message, chat_history=current_history_tuples, current_goal=current_goal)
        else:
            response_text = await asyncio.to_thread(run_qa_assistant, payload.message, chat_history=current_history_tuples)
        
        # Update chat history
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        chat_histories[session_id].append((payload.message, response_text))
        
        return ChatMessageOutput(
            response=response_text,
            session_id=session_id,
            updated_chat_history=chat_histories[session_id]
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing your request: {str(e)}")

@router.get("/chat/history/{session_id}", tags=["Chat"])
def get_chat_history(session_id: str) -> List[Tuple[str, str]]:
    """Retrieves the chat history for a given session ID."""
    return chat_histories.get(session_id, [])

# Example of how one might try to adapt the planner for true async streaming if it were async
# async def stream_from_async_planner(user_input: str, history_messages: List[BaseMessage]):
#     initial_state = AgentState(
#         input=user_input,
#         chat_history=history_messages, 
#         # ... other fields initialized ...
#     )
#     async for event in app.astream_events(initial_state, version="v1"):
#         kind = event["event"]
#         if kind == "on_chat_model_stream":
#             content = event["data"]["chunk"].content
#             if content:
#                 yield f"data: {content}\n\n"
#         elif kind == "on_tool_end":
#             # You might want to yield information about tool usage
#             tool_output = event["data"].get("output")
#             # yield f"data: [Tool Output: {tool_output[:50]}...]\n\n"
#     yield "data: [DONE]\n\n"