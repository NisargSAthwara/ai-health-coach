from backend.data.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    goals = relationship("Goal", back_populates="owner")
    weight_logs = relationship("WeightLog", back_populates="owner")
    activity_logs = relationship("ActivityLog", back_populates="owner")
    food_logs = relationship("FoodEntry", back_populates="owner")
    ocr_logs = relationship("OCRLog", back_populates="owner")
    bmi_data = relationship("BMIData", back_populates="owner")
    bmr_data = relationship("BMRData", back_populates="owner")
    daily_logs = relationship("Log", back_populates="owner")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_type = Column(String(255))
    target_weight = Column(Float)
    timeframe = Column(String(255))
    activity_level = Column(String(255))
    preferences = Column(String(255))
    allergies = Column(String(255))
    current_weight = Column(Float)
    height = Column(Float)
    age = Column(Integer)
    gender = Column(String(50))
    calculated_bmi = Column(Float)
    calculated_bmr = Column(Float)
    goal_text = Column(String(2048), nullable=False)
    analysis_result = Column(String(2048), nullable=True) # Store structured data from goal analysis
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="goals")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "goal_type": self.goal_type,
            "target_weight": self.target_weight,
            "timeframe": self.timeframe,
            "activity_level": self.activity_level,
            "preferences": self.preferences,
            "allergies": self.allergies,
            "current_weight": self.current_weight,
            "height": self.height,
            "age": self.age,
            "gender": self.gender,
            "calculated_bmi": self.calculated_bmi,
            "calculated_bmr": self.calculated_bmr,
            "goal_text": self.goal_text,
            "analysis_result": self.analysis_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class WeightLog(Base):
    __tablename__ = "weight_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="weight_logs")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(255))
    value = Column(Float)
    date = Column(DateTime)

    owner = relationship("User", back_populates="activity_logs")

class FoodEntry(Base):
    __tablename__ = "food_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_name = Column(String(255), nullable=False)
    calories = Column(Integer, default=0)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="food_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "item_name": self.item_name,
            "calories": self.calories,
            "confirmed": self.confirmed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class OCRLog(Base):
    __tablename__ = "ocr_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_name = Column(String(255))
    extracted_text = Column(String(2048))
    confirmed = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="ocr_logs")

class BMIData(Base):
    __tablename__ = "bmi_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    height = Column(Float)
    weight = Column(Float)
    bmi = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="bmi_data")

class BMRData(Base):
    __tablename__ = "bmr_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    gender = Column(String(50))
    bmr = Column(Float)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="bmr_data")

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    steps = Column(Integer)
    sleep_hours = Column(Float)
    water_intake = Column(Float)
    calories = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="daily_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "steps": self.steps,
            "sleep_hours": self.sleep_hours,
            "water_intake": self.water_intake,
            "calories": self.calories,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }