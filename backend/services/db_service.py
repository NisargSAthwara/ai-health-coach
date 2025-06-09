from typing import Optional
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta
from models.db_models import Goal, FoodEntry, User, Log
from backend.schemas import UserCreate
from backend.services.auth_service import get_password_hash

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_profile(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, hashed_password: str, name: str):
    db_user = User(email=email, password=hashed_password, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_goal(db: Session, user_id: int, goal_text: str, goal_type: str, target_weight: Optional[float] = None, timeframe: Optional[str] = None, activity_level: Optional[str] = None, preferences: Optional[str] = None, allergies: Optional[str] = None, analysis_result: dict = None, current_weight: Optional[float] = None, height: Optional[float] = None, age: Optional[int] = None, gender: Optional[str] = None, calculated_bmi: Optional[float] = None, calculated_bmr: Optional[float] = None):
    try:
        db_goal = Goal(
            user_id=user_id,
            goal_text=goal_text,
            analysis_result=json.dumps(analysis_result),
            current_weight=current_weight,
            height=height,
            age=age,
            gender=gender,
            calculated_bmi=calculated_bmi,
            calculated_bmr=calculated_bmr,
            goal_type=goal_type,
            target_weight=target_weight,
            timeframe=timeframe,
            activity_level=activity_level,
            preferences=preferences,
            allergies=allergies
        )
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"Error adding goal: {e}")
        return None

def get_goal_by_id(db: Session, goal_id: int):
    db_goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if db_goal and db_goal.analysis_result:
        db_goal.analysis_result = json.loads(db_goal.analysis_result)
    return db_goal

def update_goal(db: Session, goal_id: int, goal_text: str, goal_type: Optional[str] = None, target_weight: Optional[float] = None, timeframe: Optional[str] = None, activity_level: Optional[str] = None, preferences: Optional[str] = None, allergies: Optional[str] = None, analysis_result: dict = None, current_weight: Optional[float] = None, height: Optional[float] = None, age: Optional[int] = None, gender: Optional[str] = None, calculated_bmi: Optional[float] = None, calculated_bmr: Optional[float] = None):
    try:
        db_goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if db_goal:
            db_goal.goal_text = goal_text
            db_goal.analysis_result = json.dumps(analysis_result)
            db_goal.current_weight = current_weight
            db_goal.height = height
            db_goal.age = age
            db_goal.gender = gender
            db_goal.calculated_bmi = calculated_bmi
            db_goal.calculated_bmr = calculated_bmr
            db_goal.goal_type = goal_type if goal_type is not None else db_goal.goal_type
            db_goal.target_weight = target_weight if target_weight is not None else db_goal.target_weight
            db_goal.timeframe = timeframe if timeframe is not None else db_goal.timeframe
            db_goal.activity_level = activity_level if activity_level is not None else db_goal.activity_level
            db_goal.preferences = preferences if preferences is not None else db_goal.preferences
            db_goal.allergies = allergies if allergies is not None else db_goal.allergies
            db.commit()
            db.refresh(db_goal)
        return db_goal
    except Exception as e:
        db.rollback()
        print(f"Error updating goal: {e}")
        return None


def add_log(db: Session, user_id: int, steps: int, sleep_hours: float, water_intake: float, calories: float):
    try:
        db_log = Log(user_id=user_id, steps=steps, sleep_hours=sleep_hours, water_intake=water_intake, calories=calories)
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        print(f"Error adding log: {e}")
        return None

def add_food_log(db: Session, user_id: int, item_name: str, calories: int, confirmed: bool):
    try:
        db_food_entry = FoodEntry(user_id=user_id, item_name=item_name, calories=calories, confirmed=confirmed)
        db.add(db_food_entry)
        db.commit()
        db.refresh(db_food_entry)
        return db_food_entry
    except Exception as e:
        db.rollback()
        print(f"Error adding food log: {e}")
        return None

def get_logs_by_date_range(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    try:
        logs = db.query(Log).filter(Log.user_id == user_id, Log.created_at >= start_date, Log.created_at <= end_date).all()
        return logs
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return []

def get_food_entries_by_date_range(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    try:
        food_entries = db.query(FoodEntry).filter(FoodEntry.user_id == user_id, FoodEntry.created_at >= start_date, FoodEntry.created_at <= end_date).all()
        return food_entries
    except Exception as e:
        print(f"Error retrieving food entries: {e}")
        return []

def get_goal_by_user_id(db: Session, user_id: int):
    try:
        db_goal = db.query(Goal).filter(Goal.user_id == user_id).order_by(Goal.created_at.desc()).first()
        if db_goal and db_goal.analysis_result:
            db_goal.analysis_result = json.loads(db_goal.analysis_result)
        return db_goal
    except Exception as e:
        print(f"Error retrieving goal by user ID: {e}")
        return None