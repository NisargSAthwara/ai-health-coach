from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.data.db import get_db
from ..services.db_service import add_food_log
from models.db_models import OCRLog

router = APIRouter()

class FoodEntryConfirm(BaseModel):
    user_id: str
    item_name: str
    calories: int
    confirmed: bool

@router.post("/ocr/confirm")
def confirm_food_entry(food_entry: FoodEntryConfirm, db: Session = Depends(get_db)):
    db_food_entry = add_food_log(db, food_entry.user_id, food_entry.item_name, food_entry.calories, food_entry.confirmed)
    if db_food_entry is None:
        raise HTTPException(status_code=500, detail="Failed to confirm food entry")
    return {"status": "success", "food_entry_id": db_food_entry.id}