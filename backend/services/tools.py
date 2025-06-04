from langchain.tools import BaseTool, Tool
from pydantic import BaseModel, Field
from typing import Type, Optional, List
import math

# Optional: Tavily Search Tool (requires TAVILY_API_KEY in .env)
from langchain_community.tools.tavily_search import TavilySearchResults
try:
    tavily_tool = TavilySearchResults(max_results=3)
except Exception:
    tavily_tool = None

class BMICalculatorInput(BaseModel):
    weight_kg: float = Field(description="User's weight in kilograms")
    height_m: float = Field(description="User's height in meters")

class BMICalculatorTool(BaseTool):
    name: str = "bmi_calculator"
    description: str = "Calculates Body Mass Index (BMI) using weight in kg and height in meters. BMI Categories: Underweight < 18.5, Normal weight = 18.5–24.9, Overweight = 25–29.9, Obesity >= 30."
    args_schema: Type[BaseModel] = BMICalculatorInput

    def _run(self, weight_kg: float, height_m: float) -> str:
        if height_m <= 0:
            return "Error: Height must be greater than 0."
        bmi = round(weight_kg / (height_m ** 2), 1)
        category = ""
        if bmi < 18.5:
            category = "Underweight"
        elif 18.5 <= bmi <= 24.9:
            category = "Normal weight"
        elif 25 <= bmi <= 29.9:
            category = "Overweight"
        else:
            category = "Obesity"
        return f"Your BMI is {bmi} ({category})."

    async def _arun(self, weight_kg: float, height_m: float) -> str:
        return self._run(weight_kg, height_m)

class BMRCalculatorInput(BaseModel):
    age_years: int = Field(description="User's age in years")
    gender: str = Field(description="User's gender, either 'male' or 'female'")
    weight_kg: float = Field(description="User's weight in kilograms")
    height_cm: float = Field(description="User's height in centimeters")

class BMRCalculatorTool(BaseTool):
    name: str = "bmr_calculator"
    description: str = "Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation. This is the number of calories your body burns at rest."
    args_schema: Type[BaseModel] = BMRCalculatorInput

    def _run(self, age_years: int, gender: str, weight_kg: float, height_cm: float) -> str:
        if gender.lower() not in ['male', 'female']:
            return "Error: Gender must be 'male' or 'female'."
        if weight_kg <= 0 or height_cm <= 0 or age_years <= 0:
            return "Error: Age, weight, and height must be positive values."

        if gender.lower() == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + 5
        else:  # female
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 161
        return f"Your estimated BMR is {round(bmr)} calories/day."

    async def _arun(self, age_years: int, gender: str, weight_kg: float, height_cm: float) -> str:
        return self._run(age_years, gender, weight_kg, height_cm)

class CalorieEstimatorInput(BaseModel):
    bmr: float = Field(description="User's Basal Metabolic Rate in calories/day")
    activity_level: str = Field(description="User's activity level: 'sedentary', 'light', 'moderate', 'active', 'very_active'")
    goal: str = Field(description="User's health goal: 'lose_weight', 'gain_weight', 'maintain_weight'")

class CalorieEstimatorTool(BaseTool):
    name: str = "calorie_estimator"
    description: str = "Estimates daily calorie needs based on BMR, activity level, and health goal (lose_weight, gain_weight, maintain_weight)."
    args_schema: Type[BaseModel] = CalorieEstimatorInput

    def _run(self, bmr: float, activity_level: str, goal: str) -> str:
        activity_multipliers = {
            'sedentary': 1.2,        # little or no exercise
            'light': 1.375,          # light exercise/sports 1-3 days/week
            'moderate': 1.55,        # moderate exercise/sports 3-5 days/week
            'active': 1.725,         # hard exercise/sports 6-7 days a week
            'very_active': 1.9       # very hard exercise/sports & physical job
        }
        activity_level_lower = activity_level.lower()
        if activity_level_lower not in activity_multipliers:
            return f"Error: Invalid activity level. Choose from: {', '.join(activity_multipliers.keys())}."

        maintenance_calories = bmr * activity_multipliers[activity_level_lower]

        if goal.lower() == 'lose_weight':
            target_calories = maintenance_calories - 500  # General deficit for ~1lb/week loss
            return f"To lose weight, aim for approximately {round(target_calories)} calories/day. This is based on a 500 calorie deficit from your maintenance of {round(maintenance_calories)} calories."
        elif goal.lower() == 'gain_weight':
            target_calories = maintenance_calories + 500  # General surplus for ~1lb/week gain
            return f"To gain weight, aim for approximately {round(target_calories)} calories/day. This is based on a 500 calorie surplus from your maintenance of {round(maintenance_calories)} calories."
        elif goal.lower() == 'maintain_weight':
            return f"To maintain your current weight, your estimated daily calorie need is {round(maintenance_calories)} calories/day."
        else:
            return "Error: Invalid goal. Choose from: 'lose_weight', 'gain_weight', 'maintain_weight'."

    async def _arun(self, bmr: float, activity_level: str, goal: str) -> str:
        return self._run(bmr, activity_level, goal)

class UserLogSummaryInput(BaseModel):
    user_id: str = Field(description="The ID of the user whose logs are to be summarized")
    days: int = Field(default=7, description="Number of past days to summarize logs for, e.g., 3 or 7")

class UserLogSummaryTool(BaseTool):
    name: str = "user_log_summary_tool"
    description: str = "Analyzes and summarizes user's recent health logs (e.g., steps, water intake, sleep) from the past few days. Provides insights based on the log data."
    args_schema: Type[BaseModel] = UserLogSummaryInput

    def _run(self, user_id: str, days: int = 7) -> str:
        # Placeholder: In a real application, this would query a database or data store
        # For now, it returns a mock response.
        # Example: Fetch logs for user_id for the last 'days' days
        # Perform analysis (e.g., average sleep, water intake consistency, step goals)
        # Return a summary string.
        return f"Placeholder: Summarizing logs for user {user_id} for the past {days} days. Based on your (mock) recent activity, you seem to be drinking less water than needed. You’re getting enough steps but could improve sleep duration."

    async def _arun(self, user_id: str, days: int = 7) -> str:
        return self._run(user_id, days)


# List of all tools to be used by the agent
all_tools: List[BaseTool] = [
    BMICalculatorTool(),
    BMRCalculatorTool(),
    CalorieEstimatorTool(),
    UserLogSummaryTool(),
    # Add Tavily tool if available and configured
    # *( [tavily_tool] if tavily_tool else [] )
]

def get_tools() -> List[BaseTool]:
    """Returns the list of available tools."""
    # Here you could dynamically enable/disable tools based on config
    # For now, returns all defined tools.
    # If TAVILY_API_KEY is set, Tavily tool will be attempted to be included.
    current_tools = [
        BMICalculatorTool(),
        BMRCalculatorTool(),
        CalorieEstimatorTool(),
        UserLogSummaryTool(),
    ]
    # try:
    #     from langchain_community.tools.tavily_search import TavilySearchResults
    #     import os
    #     if os.getenv("TAVILY_API_KEY"):
    #         tavily_search = TavilySearchResults(max_results=3)
    #         current_tools.append(tavily_search)
    #     else:
    #         print("Tavily API key not found, Tavily Search tool will not be available.")
    # except ImportError:
    #     print("Tavily package not installed, Tavily Search tool will not be available.")
    
    return current_tools

# Example usage (for testing)
if __name__ == '__main__':
    bmi_tool = BMICalculatorTool()
    print(bmi_tool.run({"weight_kg": 70, "height_m": 1.75}))

    bmr_tool = BMRCalculatorTool()
    print(bmr_tool.run({"age_years": 30, "gender": "male", "weight_kg": 70, "height_cm": 175}))

    calorie_tool = CalorieEstimatorTool()
    # Assuming BMR is 1600 for this example
    print(calorie_tool.run({"bmr": 1600, "activity_level": "light", "goal": "lose_weight"}))

    log_summary_tool = UserLogSummaryTool()
    print(log_summary_tool.run({"user_id": "test_user_123"}))

    # available_tools = get_tools()
    # print(f"\nAvailable tools: {[tool.name for tool in available_tools]}")