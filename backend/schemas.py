from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: Optional[int] = None
    name: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[int] = None

class GoalSet(BaseModel):
    goal_type: str
    target_weight: float
    timeframe: str
    activity_level: str
    dietary_preferences: Optional[str] = None
    allergies: Optional[str] = None
    current_weight: float
    height: float
    age: int
    gender: str