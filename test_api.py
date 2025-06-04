# import requests
# import json
# from datetime import datetime, timedelta

# BASE_URL = "http://localhost:8000/api/v1"

# def test_chat_endpoint():
#     print("\n--- Testing Chat Endpoint ---")
#     url = f"{BASE_URL}/chat"
#     payload = {"message": "Hello, how are you?", "session_id": "test_session_123"}
#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status() # Raise an exception for HTTP errors
#         data = response.json()
#         print(f"Chat Response: {data['response']}")
#         print(f"Session ID: {data['session_id']}")
#         print(f"Updated Chat History: {data['updated_chat_history']}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error testing chat endpoint: {e}")

# def test_create_goal_endpoint():
#     print("\n--- Testing Create Goal Endpoint ---")
#     url = f"{BASE_URL}/goal"
#     payload = {"goal_description": "Run a marathon in 6 months"}
#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         print(f"Create Goal Response: {data}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error testing create goal endpoint: {e}")

# def test_log_endpoint():
#     print("\n--- Testing Log Endpoint ---")
#     url = f"{BASE_URL}/log"
#     payload = {
#         "user_id": "user123",
#         "steps": 10000,
#         "sleep_hours": 7.5,
#         "water_intake": 2.0,
#         "calories": 2000
#     }
#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         print(f"Log Response: {data}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error testing log endpoint: {e}")

# def test_confirm_food_entry_endpoint():
#     print("\n--- Testing Confirm Food Entry Endpoint ---")
#     url = f"{BASE_URL}/ocr/confirm"
#     payload = {
#         "user_id": "user123",
#         "item_name": "Apple",
#         "calories": 95,
#         "confirmed": True
#     }
#     try:
#         response = requests.post(url, json=payload)
#         response.raise_for_status()
#         data = response.json()
#         print(f"Confirm Food Entry Response: {data}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error testing confirm food entry endpoint: {e}")

# def test_get_summary_endpoint():
#     print("\n--- Testing Get Summary Endpoint ---")
#     user_id = "user123"
#     url = f"{BASE_URL}/summary?user_id={user_id}"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         print(f"Summary Response: {data}")
#     except requests.exceptions.RequestException as e:
#         print(f"Error testing get summary endpoint: {e}")

# if __name__ == "__main__":
#     # Run the tests
#     test_chat_endpoint()
#     test_create_goal_endpoint()
#     test_log_endpoint()
#     test_confirm_food_entry_endpoint()
#     test_get_summary_endpoint()