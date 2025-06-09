from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.data.db import get_db
from backend.services import db_service
from backend.services.goal_analysis import analyze_goal, calculate_bmi, calculate_bmr
from backend.dependencies import get_current_user
from models.db_models import User
from backend.schemas import GoalSet

router = APIRouter()

# @router.post("/goal/set", status_code=status.HTTP_201_CREATED)
# async def set_goal(goal: GoalSet, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     existing_goal = db_service.get_goal_by_user_id(db, current_user.id)
#     if existing_goal:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has an active goal. Please update the existing goal.")
    
#     # Calculate BMI and BMR if sufficient data is provided
#     bmi = None
#     bmr = None
#     if goal.current_weight and goal.height and goal.age and goal.gender:
#         try:
#             bmi = calculate_bmi(goal.current_weight, goal.height)
#             bmr = calculate_bmr(goal.current_weight, goal.height, goal.age, goal.gender)
#         except Exception as e:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating BMI/BMR: {e}")

#     # Create a goal description from the new fields
#     goal_description = f"Goal Type: {goal.goal_type}"
#     goal_description += f", Target Weight: {goal.target_weight}kg"
#     goal_description += f", Timeframe: {goal.timeframe}"
#     goal_description += f", Activity Level: {goal.activity_level}"
#     if goal.dietary_preferences: goal_description += f", Dietary Preferences: {goal.dietary_preferences}"
#     if goal.allergies: goal_description += f", Allergies: {goal.allergies}"
#     goal_description += f", Current Weight: {goal.current_weight}kg"
#     goal_description += f", Height: {goal.height}cm"
#     goal_description += f", Age: {goal.age}"
#     goal_description += f", Gender: {goal.gender}"

#     # Analyze the combined goal description
#     analysis_result = await analyze_goal(goal_description)
#     if analysis_result.get("clarification_needed"):
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=analysis_result.get("message"))

#     new_goal = db_service.add_goal(
#         db,
#         user_id=current_user.id,
#         goal_text=goal_description, # Use goal_text for the combined description
#         goal_type=goal.goal_type,
#         target_weight=goal.target_weight,
#         timeframe=goal.timeframe,
#         activity_level=goal.activity_level,
#         preferences=goal.dietary_preferences, # Map to preferences
#         allergies=goal.allergies,
#         analysis_result=analysis_result, # Store the analysis result
#         current_weight=goal.current_weight,
#         height=goal.height,
#         age=goal.age,
#         gender=goal.gender,
#         calculated_bmi=bmi,
#         calculated_bmr=bmr
#     )
#     return {"status": "success", "message": "Goal set successfully", "goal_id": new_goal.id}
@router.post("/goal/set", status_code=status.HTTP_201_CREATED)
async def set_goal(goal: GoalSet, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        print("Incoming goal:", goal)
        print("Current user:", current_user)

        existing_goal = db_service.get_goal_by_user_id(db, current_user.id)
        if existing_goal:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has an active goal.")

        # BMI / BMR
        bmi = bmr = None
        if goal.current_weight and goal.height and goal.age and goal.gender:
            bmi = calculate_bmi(goal.current_weight, goal.height)
            bmr = calculate_bmr(goal.current_weight, goal.height, goal.age, goal.gender)

        goal_description = f"Goal Type: {goal.goal_type}, Target Weight: {goal.target_weight}kg, ..."
        print("Goal description:", goal_description)

        analysis_result = await analyze_goal(goal_description)
        print("Analysis:", analysis_result)

        new_goal = db_service.add_goal(
            db, user_id=current_user.id,
            goal_text=goal_description,
            goal_type=goal.goal_type,
            target_weight=goal.target_weight,
            timeframe=goal.timeframe,
            activity_level=goal.activity_level,
            preferences=goal.dietary_preferences,
            allergies=goal.allergies,
            analysis_result=analysis_result,
            current_weight=goal.current_weight,
            height=goal.height,
            age=goal.age,
            gender=goal.gender,
            calculated_bmi=bmi,
            calculated_bmr=bmr
        )

        return {"status": "success", "message": "Goal set successfully", "goal_id": new_goal.id}
    
    except Exception as e:
        print(f"❌ Goal set error: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong")

@router.get("/goal/get")
async def get_goal(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db_service.get_goal_by_user_id(db, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No goal found for this user.")
    return goal.to_dict()

@router.put("/goal/update")
async def update_goal(goal: GoalSet, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_goal = db_service.get_goal_by_user_id(db, current_user.id)
    if not existing_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No goal found for this user to update.")
    
    # Calculate BMI and BMR if sufficient data is provided
    bmi = None
    bmr = None
    if goal.current_weight and goal.height and goal.age and goal.gender:
        try:
            bmi = calculate_bmi(goal.current_weight, goal.height)
            bmr = calculate_bmr(goal.current_weight, goal.height, goal.age, goal.gender)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error calculating BMI/BMR: {e}")

    # Create a goal description from the new fields
    goal_description = f"Goal Type: {goal.goal_type}"
    goal_description += f", Target Weight: {goal.target_weight}kg"
    goal_description += f", Timeframe: {goal.timeframe}"
    goal_description += f", Activity Level: {goal.activity_level}"
    if goal.dietary_preferences: goal_description += f", Dietary Preferences: {goal.dietary_preferences}"
    if goal.allergies: goal_description += f", Allergies: {goal.allergies}"
    goal_description += f", Current Weight: {goal.current_weight}kg"
    goal_description += f", Height: {goal.height}cm"
    goal_description += f", Age: {goal.age}"
    goal_description += f", Gender: {goal.gender}"

    # Analyze the combined goal description
    analysis_result = await analyze_goal(goal_description)
    if analysis_result.get("clarification_needed"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=analysis_result.get("message"))

    updated_goal = db_service.update_goal(
        db,
        goal_id=existing_goal.id,
        goal_text=goal_description, # Use goal_text for the combined description
        goal_type=goal.goal_type,
        target_weight=goal.target_weight,
        timeframe=goal.timeframe,
        activity_level=goal.activity_level,
        preferences=goal.dietary_preferences, # Map to preferences
        allergies=goal.allergies,
        analysis_result=analysis_result, # Store the analysis result
        current_weight=goal.current_weight,
        height=goal.height,
        age=goal.age,
        gender=goal.gender,
        calculated_bmi=bmi,
        calculated_bmr=bmr
    )
    return {"status": "success", "message": "Goal updated successfully", "goal_id": updated_goal.id}