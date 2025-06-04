from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

Base = declarative_base()

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    goal_text = Column(String, nullable=False)
    analysis_result = Column(String, nullable=True) # Store structured data from goal analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    steps = Column(Integer, default=0)
    sleep_hours = Column(Float, default=0.0)
    water_intake = Column(Float, default=0.0)
    calories = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FoodEntry(Base):
    __tablename__ = "food_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    calories = Column(Integer, default=0)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())