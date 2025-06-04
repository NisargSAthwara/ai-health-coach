from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.data.db import get_db
from ..services.db_service import add_log, add_food_log

router = APIRouter()

class LogCreate(BaseModel):
    user_id: str
    steps: int
    sleep_hours: float
    water_intake: float
    calories: float

class FoodLogCreate(BaseModel):
    user_id: str
    item_name: str
    calories: int
    confirmed: bool

@router.post("/log")
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db_log = add_log(db, log.user_id, log.steps, log.sleep_hours, log.water_intake, log.calories)
    if db_log is None:
        raise HTTPException(status_code=500, detail="Failed to add log")
    return {"status": "success", "log_id": db_log.id}

@router.post("/log/food")
def create_food_log(food_log: FoodLogCreate, db: Session = Depends(get_db)):
    db_food_log = add_food_log(db, food_log.user_id, food_log.item_name, food_log.calories, food_log.confirmed)
    if db_food_log is None:
        raise HTTPException(status_code=500, detail="Failed to add food log")
    return {"status": "success", "food_log_id": db_food_log.id}