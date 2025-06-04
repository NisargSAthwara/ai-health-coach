from fastapi import APIRouter, Depends, HTTPException 
from typing import Optional
from sqlalchemy.orm import Session
from backend.data.db import get_db
from ..services.db_service import get_logs_by_date_range, get_food_entries_by_date_range, get_goal_by_id
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
def get_summary(user_id: str, db: Session = Depends(get_db), goal_id: Optional[int] = None):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1) # Daily summary
    
    logs = get_logs_by_date_range(db, user_id, start_date, end_date)
    food_entries = get_food_entries_by_date_range(db, user_id, start_date, end_date)
    
    total_steps = sum([log.steps for log in logs]) if logs else 0
    avg_sleep_hours = sum([log.sleep_hours for log in logs]) / len(logs) if logs else 0
    avg_water_intake = sum([log.water_intake for log in logs]) / len(logs) if logs else 0
    total_calories_logged = sum([log.calories for log in logs]) if logs else 0
    total_food_calories = sum([entry.calories for entry in food_entries]) if food_entries else 0
    
    total_calories_consumed = total_calories_logged + total_food_calories

    goal_progress = {}
    daily_tip = "Keep up the great work! Consistency is key to achieving your health goals."

    if goal_id:
        goal = get_goal_by_id(db, goal_id)
        if goal and goal.analysis_result:
            analysis = goal.analysis_result
            target_calories = analysis.get("target_calories", 0)
            target_water = analysis.get("target_water_intake_liters", 0)
            target_sleep = analysis.get("target_sleep_hours", 0)
            target_steps = analysis.get("target_steps", 0)

            if target_calories > 0:
                calorie_progress = (total_calories_consumed / target_calories) * 100
                goal_progress["calories"] = {"current": total_calories_consumed, "target": target_calories, "progress": min(100, calorie_progress)}
                if total_calories_consumed > target_calories:
                    daily_tip = "You've exceeded your calorie target today. Consider adjusting your intake for tomorrow."

            if target_water > 0:
                water_progress = (avg_water_intake / target_water) * 100
                goal_progress["water"] = {"current": avg_water_intake, "target": target_water, "progress": min(100, water_progress)}
                if avg_water_intake < target_water:
                    daily_tip = "Remember to drink more water throughout the day to stay hydrated!"
            
            if target_sleep > 0:
                sleep_progress = (avg_sleep_hours / target_sleep) * 100
                goal_progress["sleep"] = {"current": avg_sleep_hours, "target": target_sleep, "progress": min(100, sleep_progress)}
                if avg_sleep_hours < target_sleep:
                    daily_tip = "Aim for consistent sleep to support your overall health and energy levels."

            if target_steps > 0:
                steps_progress = (total_steps / target_steps) * 100
                goal_progress["steps"] = {"current": total_steps, "target": target_steps, "progress": min(100, steps_progress)}
                if total_steps < target_steps:
                    daily_tip = "Try to incorporate more movement into your day to reach your step goal!"

    return {
        "status": "success",
        "date": end_date.strftime("%Y-%m-%d"),
        "metrics": {
            "total_steps": total_steps,
            "avg_sleep_hours": round(avg_sleep_hours, 1),
            "avg_water_intake": round(avg_water_intake, 1),
            "total_calories_consumed": total_calories_consumed
        },
        "goal_progress": goal_progress,
        "daily_tip": daily_tip
    }