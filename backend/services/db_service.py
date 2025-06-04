from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta
from models.db_models import Goal, Log, FoodEntry

def add_goal(db: Session, goal_description: str, analysis_result: dict = None):
    try:
        db_goal = Goal(goal_text=goal_description, analysis_result=json.dumps(analysis_result))
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal
    except Exception as e:
        db.rollback()
        print(f"Error adding goal: {e}")
        return None

def get_goal_by_id(db: Session, goal_id: int):
    db_goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if db_goal and db_goal.analysis_result:
        db_goal.analysis_result = json.loads(db_goal.analysis_result)
    return db_goal

def update_goal(db: Session, goal_id: int, new_goal_description: str, new_analysis_result: dict = None):
    try:
        db_goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if db_goal:
            db_goal.goal_text = new_goal_description
            db_goal.analysis_result = json.dumps(new_analysis_result)
            db.commit()
            db.refresh(db_goal)
        return db_goal
    except Exception as e:
        db.rollback()
        print(f"Error updating goal: {e}")
        return None



def add_log(db: Session, user_id: str, steps: int, sleep_hours: float, water_intake: float, calories: float):
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

def add_food_log(db: Session, user_id: str, item_name: str, calories: int, confirmed: bool):
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

def get_logs_by_date_range(db: Session, user_id: str, start_date: datetime, end_date: datetime):
    try:
        logs = db.query(Log).filter(Log.user_id == user_id, Log.created_at >= start_date, Log.created_at <= end_date).all()
        return logs
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return []

def get_food_entries_by_date_range(db: Session, user_id: str, start_date: datetime, end_date: datetime):
    try:
        food_entries = db.query(FoodEntry).filter(FoodEntry.user_id == user_id, FoodEntry.created_at >= start_date, FoodEntry.created_at <= end_date).all()
        return food_entries
    except Exception as e:
        print(f"Error retrieving food entries: {e}")
        return []