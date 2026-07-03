from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_engine import AICompanion
from firebase_manager import FirebaseManager
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Companion API")

# Initialize Firebase
firebase = FirebaseManager()

# Initialize AI
try:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found!")
    
    ai = AICompanion(
        api_key=groq_key,
        provider="groq",
        model="llama-3.1-8b-instant"
    )
    print("✅ AI Engine loaded!")
except Exception as e:
    print(f"❌ Error: {e}")
    ai = None

# Request models
class ChatRequest(BaseModel):
    user_id: str
    user_message: str
    user_gender: str
    user_name: str
    ai_gender: str  # AI ka gender
    mood_state: str = "normal"

class UserProfile(BaseModel):
    user_id: str
    name: str
    gender: str
    ai_gender: str

@app.get("/")
def home():
    return {
        "status": "AI Companion Backend Running! 🚀",
        "ai_provider": "Groq (Llama-3.1-8B)",
        "database": "Firebase Firestore",
        "version": "2.0"
    }

@app.post("/chat")
def chat(request: ChatRequest):
    if ai is None:
        raise HTTPException(status_code=500, detail="AI not initialized")
    
    try:
        # Get chat history from Firebase
        chat_history = firebase.get_chat_history(request.user_id, limit=6)
        
        # Get AI response
        response = ai.get_response(
            user_message=request.user_message,
            user_gender=request.ai_gender,  # AI ka gender
            user_name=request.user_name,
            conversation_history=chat_history,
            mood_state=request.mood_state
        )
        
        # Save messages to Firebase
        firebase.save_message(request.user_id, request.user_message, "user", request.ai_gender)
        firebase.save_message(request.user_id, response, "ai", request.ai_gender)
        
        # Update last active
        firebase.update_last_active(request.user_id)
        
        return {
            "success": True,
            "ai_response": response,
            "provider": "groq"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/profile/save")
def save_profile(profile: UserProfile):
    """Save user profile"""
    success = firebase.save_user_profile(
        profile.user_id,
        profile.name,
        profile.gender,
        profile.ai_gender
    )
    
    if success:
        return {"success": True, "message": "Profile saved"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save profile")

@app.get("/profile/{user_id}")
def get_profile(user_id: str):
    """Get user profile"""
    profile = firebase.get_user_profile(user_id)
    
    if profile:
        return {"success": True, "profile": profile}
    else:
        raise HTTPException(status_code=404, detail="Profile not found")

@app.get("/chat/history/{user_id}")
def get_history(user_id: str, limit: int = 20):
    """Get chat history"""
    history = firebase.get_chat_history(user_id, limit)
    return {"success": True, "history": history}

@app.get("/health")
def health():
    return {"status": "healthy", "ai": "groq", "db": "firebase"}