from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_engine import AICompanion
from firebase_manager import FirebaseManager
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Initialize FastAPI App
app = FastAPI(
    title="AI Companion Backend",
    description="Your Emotional Partner API",
    version="2.0"
)

# ✅ Enable CORS (Critical for web apps to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialization ---
firebase = None
try:
    # Load Firebase
    firebase = FirebaseManager()
    print("✅ Firebase initialized!")
except Exception as e:
    print(f"⚠️ Firebase skipped: {e}")

ai = None
try:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found!")
    
    ai = AICompanion(
        api_key=groq_key,
        provider="groq",
        model="llama-3.1-8b-instant"
    )
    print("✅ AI Engine Loaded!")
except Exception as e:
    print(f"❌ AI Failed: {e}")

# --- Models ---
class ChatRequest(BaseModel):
    user_id: str
    user_message: str
    user_gender: str
    user_name: str
    ai_gender: str
    mood_state: str = "normal"

# --- Endpoints ---

@app.get("/")
def home():
    """Root Endpoint - Test this first"""
    return {
        "status": "🚀 AI Companion Backend LIVE!",
        "message": "Welcome to your emotional partner!",
        "version": "2.0",
        "health": "healthy"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "ai": "groq", "db": "firebase"}

@app.post("/chat")
def chat(request: ChatRequest):
    """Main chat endpoint"""
    if ai is None:
        raise HTTPException(status_code=500, detail="AI not initialized")
    
    try:
        # 1. Get Chat History (Skip if Firebase failed)
        if firebase:
            chat_history = firebase.get_chat_history(request.user_id, limit=6)
        else:
            chat_history = []
        
        # 2. Generate Response
        response_text = ai.get_response(
            user_message=request.user_message,
            user_gender=request.ai_gender,
            user_name=request.user_name,
            conversation_history=chat_history,
            mood_state=request.mood_state
        )
        
        # 3. Save to Firebase (if enabled)
        if firebase:
            firebase.save_message(request.user_id, request.user_message, "user", request.ai_gender)
            firebase.save_message(request.user_id, response_text, "ai", request.ai_gender)
        
        return {
            "success": True,
            "ai_response": response_text
        }
        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))