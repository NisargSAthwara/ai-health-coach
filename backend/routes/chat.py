import asyncio

from fastapi import APIRouter, HTTPException, Depends ,Request
from pydantic import BaseModel
import asyncio

from fastapi import APIRouter, HTTPException, Depends ,Request
from pydantic import BaseModel
from typing import List, Tuple, Optional
from fastapi.responses import StreamingResponse

def contains_health_keywords(message: str) -> bool:
    health_keywords = ["diet", "bmi", "bmr", "nutrition", "weight loss", "gain weight", "calories", "health", "exercise", "workout"]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in health_keywords)

from backend.services.planner import run_assistant, AgentState, run_qa_assistant # Assuming run_assistant can be adapted for streaming
from langchain_core.messages import HumanMessage, AIMessage
from ..services import db_service
from sqlalchemy.orm import Session
from backend.data.db import get_db
from backend.dependencies import get_current_user
from models.db_models import User
from datetime import datetime, timedelta

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

async def get_user_context(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    user_profile = db_service.get_user_profile(db, user_id)
    current_goal = db_service.get_goal_by_user_id(db, user_id)
    
    # Get recent logs and food entries for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    recent_logs = db_service.get_logs_by_date_range(db, user_id, start_date, end_date)
    recent_food_entries = db_service.get_food_entries_by_date_range(db, user_id, start_date, end_date)

    return {
        "user_profile": user_profile.to_dict() if user_profile else None,
        "goal": current_goal.to_dict() if current_goal else None,
        "recent_logs": [log.to_dict() for log in recent_logs if log is not None],
        "recent_food_entries": [food.to_dict() for food in recent_food_entries if food is not None],
    }



async def stream_response_generator(user_input: str, session_id: str, history_tuples: List[Tuple[str,str]], user_context: Optional[dict] = None):
    """Runs the assistant and streams the response sentence by sentence or chunk by chunk."""
    # This is a simplified streaming example. 
    # True streaming from LangGraph requires more complex handling of intermediate steps 
    # and potentially yield intermediate thoughts or final response chunks.

    # For now, we'll get the full response and then "simulate" streaming it.
    # A more advanced version would involve `ainvoke` on the graph and processing an AsyncIterator.

    try:
        if user_context:
            # Context-aware mode
            full_response = run_assistant(user_input, chat_history=history_tuples)
            # , user_context=user_context
        else:
            # Q&A mode (or generic if user not logged in)
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
async def stream_chat_endpoint(payload: ChatMessageInput, db: Session = Depends(get_db)):
    # , user_context: dict = Depends(get_user_context)
    """Receives a user message, processes it with the AI assistant, and streams the response."""
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
        # , user_context
        media_type="text/event-stream")


@router.post("/chat", response_model=ChatMessageOutput, tags=["Chat"])
async def chat_endpoint(payload: ChatMessageInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> ChatMessageOutput:
    """Receives a user message, processes it with the AI assistant, and returns a response."""
    user_input = payload.message
    session_id = payload.session_id
    
    # Retrieve history for the session or use provided history
    current_history_tuples = chat_histories.get(session_id, [])
    if payload.chat_history:
        current_history_tuples = payload.chat_history
        chat_histories[session_id] = current_history_tuples

    if not current_user:
        if contains_health_keywords(user_input):
            return ChatMessageOutput(response="To get personalized health advice, please login and set a goal using the 'Set Goal' button.", session_id=session_id, updated_chat_history=current_history_tuples)
        response_text = await asyncio.to_thread(run_qa_assistant, user_input, chat_history=current_history_tuples)
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        chat_histories[session_id].append((user_input, response_text))
        return ChatMessageOutput(response=response_text, session_id=session_id, updated_chat_history=chat_histories[session_id])

    goal = db_service.get_goal_by_user_id(db, current_user.id)
    if not goal:
        if contains_health_keywords(user_input):
            return ChatMessageOutput(response="Welcome! It looks like you haven't set a health goal yet. Please set one to get personalized advice.", session_id=session_id, updated_chat_history=current_history_tuples)
        response_text = await asyncio.to_thread(run_qa_assistant, user_input, chat_history=current_history_tuples)
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        chat_histories[session_id].append((user_input, response_text))
        return ChatMessageOutput(response=response_text, session_id=session_id, updated_chat_history=chat_histories[session_id])

    # If goal is set, proceed with assistant
    user_context = await asyncio.to_thread(get_user_context, db, current_user)
    response_text = await asyncio.to_thread(run_assistant, user_input, chat_history=current_history_tuples)

    # Update chat history
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    chat_histories[session_id].append((user_input, response_text))

    return ChatMessageOutput(
        response=response_text,
        session_id=session_id,
        updated_chat_history=chat_histories[session_id]
    )


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