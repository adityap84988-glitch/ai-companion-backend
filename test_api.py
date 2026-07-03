import requests
import json

# Test 1: Homepage
print("🧪 Test 1: Homepage")
response = requests.get("http://127.0.0.1:8000")
print(response.json())
print("\n" + "="*50 + "\n")

# Test 2: Normal chat
print("🧪 Test 2: Normal Chat")
response = requests.post("http://127.0.0.1:8000/chat", json={
    "user_message": "Hey! Kya kar rahi ho?",
    "user_gender": "female",
    "user_name": "Priya",
    "conversation_history": [],
    "mood_state": "normal"
})
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print("\n" + "="*50 + "\n")

# Test 3: Sad message (Gita wisdom trigger)
print("🧪 Test 3: Sad Message (Should trigger Gita)")
response = requests.post("http://127.0.0.1:8000/chat", json={
    "user_message": "Bahut sad feel ho raha hai yaar, kuch achieve nahi ho raha life mein",
    "user_gender": "female",
    "user_name": "Priya",
    "conversation_history": [],
    "mood_state": "normal"
})
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print("\n" + "="*50 + "\n")

# Test 4: Angry mood
print("🧪 Test 4: AI in Angry Mood")
response = requests.post("http://127.0.0.1:8000/chat", json={
    "user_message": "Sorry yaar, busy tha",
    "user_gender": "male",
    "user_name": "Raj",
    "conversation_history": [],
    "mood_state": "angry"
})
print(json.dumps(response.json(), indent=2, ensure_ascii=False))