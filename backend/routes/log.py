from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.data.db import get_db
from backend.services.db_service import add_log, add_food_log, get_logs_by_date_range, get_food_entries_by_date_range
from backend.dependencies import get_current_user
from models.db_models import User, Log, FoodEntry

router = APIRouter()

class LogCreate(BaseModel):
    steps: int
    sleep_hours: float
    water_intake: float
    calories: float

class FoodLogCreate(BaseModel):
    item_name: str
    calories: int
    confirmed: bool

@router.post("/log")
def create_log(log: LogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_log = add_log(db, current_user.id, log.steps, log.sleep_hours, log.water_intake, log.calories)
    if db_log is None:
        raise HTTPException(status_code=500, detail="Failed to add log")
    return {"status": "success", "log_id": db_log.id}

@router.post("/log/food")
def create_food_log(food_log: FoodLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_food_log = add_food_log(db, current_user.id, food_log.item_name, food_log.calories, food_log.confirmed)
    if db_food_log is None:
        raise HTTPException(status_code=500, detail="Failed to add food log")
    return {"status": "success", "food_log_id": db_food_log.id}

@router.get("/logs")
def get_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = get_logs_by_user_id(db, current_user.id)
    return logs

@router.get("/logs/food")
def get_food_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    food_logs = get_food_entries_by_user_id(db, current_user.id)
    return food_logs