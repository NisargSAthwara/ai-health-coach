from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.data.db import get_db
from backend.services.db_service import add_goal, get_goal_by_id, update_goal
from backend.services.goal_analysis import analyze_goal

router = APIRouter()

class GoalCreate(BaseModel):
    goal_description: str

@router.post("/goal/set")
async def set_goal(goal: GoalCreate, request: Request, db: Session = Depends(get_db)):
    user_id = "test_user" # This should come from authentication

    # Analyze the goal using the new service
    analysis_result = await analyze_goal(goal.goal_description)

    if analysis_result.get("clarification_needed"): # type: ignore
        return {"status": "clarification_needed", "message": analysis_result.get("message")}

    # If goal_id is present in request state, it's an update
    existing_goal_id = request.state.goal_id
    if existing_goal_id:
        db_goal = update_goal(db, existing_goal_id, goal.goal_description, analysis_result) # type: ignore
        if db_goal is None:
            raise HTTPException(status_code=500, detail="Failed to update goal")
        return {"status": "success", "message": "Goal updated successfully", "goal_id": db_goal.id}
    else:
        db_goal = add_goal(db, goal.goal_description, analysis_result) # type: ignore
        if db_goal is None:
            raise HTTPException(status_code=500, detail="Failed to add goal")
        return {"status": "success", "message": "Goal set successfully", "goal_id": db_goal.id}

@router.get("/goal/{goal_id}")
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    db_goal = get_goal_by_id(db, goal_id)
    if db_goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal