import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Test 1: Save profile
print("🧪 Test 1: Save User Profile")
response = requests.post(f"{BASE_URL}/profile/save", json={
    "user_id": "test_user_123",
    "name": "Priya",
    "gender": "female",
    "ai_gender": "female"
})
print(response.json())
print("\n" + "="*50 + "\n")

# Test 2: Get profile
print("🧪 Test 2: Get User Profile")
response = requests.get(f"{BASE_URL}/profile/test_user_123")
print(json.dumps(response.json(), indent=2))
print("\n" + "="*50 + "\n")

# Test 3: Chat with history
print("🧪 Test 3: Chat (will save to Firebase)")
response = requests.post(f"{BASE_URL}/chat", json={
    "user_id": "test_user_123",
    "user_message": "Hey! Kaise ho?",
    "user_gender": "male",
    "user_name": "Priya",
    "ai_gender": "female",
    "mood_state": "normal"
})
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print("\n" + "="*50 + "\n")

# Test 4: Get chat history
print("🧪 Test 4: Get Chat History")
response = requests.get(f"{BASE_URL}/chat/history/test_user_123")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))