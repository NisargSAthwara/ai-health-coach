from fastapi import FastAPI
from backend.routes import chat, auth
from backend.routes import goal, log, ocr, summary
from backend.data.db import Base, engine
from backend.data.init_db import init_tables
from fastapi.middleware.cors import CORSMiddleware
from backend.middleware.goal_middleware import GoalContextMiddleware

# Create database tables
init_tables()

app = FastAPI(
    title="AI Health Assistant Backend",
    description="Backend for the AI Health Assistant, providing chat and health-related functionalities.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GoalContextMiddleware)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1")
app.include_router(goal.router, prefix="/api/v1")
app.include_router(log.router, prefix="/api/v1")
app.include_router(ocr.router, prefix="/api/v1")
app.include_router(summary.router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "message": "AI Health Assistant is running."}

if __name__ == "__main__":
    # This is for local development running directly with `python main.py`
    # Ensure GEMINI_API_KEY is available in your environment or .env file
    if not GEMINI_API_KEY:
        print("CRITICAL: GEMINI_API_KEY not found. Please set it in your .env file or environment variables.")
        exit(1)
    
    print("Starting AI Health Assistant server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

import logging
logging.basicConfig(level=logging.DEBUG)