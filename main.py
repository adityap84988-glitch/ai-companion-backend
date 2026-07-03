from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_engine import AICompanion
from firebase_manager import FirebaseManager
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Companion API")

# ✅ ADD THIS - Enable CORS for ALL origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains (or add specific ones)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize Firebase (optional)
try:
    firebase = FirebaseManager()
    print("✅ Firebase loaded!")
except Exception as e:
    print(f"⚠️ Firebase skipped: {e}")
    firebase = None

# Initialize AI
try:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in environment!")
    
    ai = AICompanion(
        api_key=groq_key,
        provider="groq",
        model="llama-3.1-8b-instant"
    )
    print("✅ AI Engine loaded with GROQ!")
except Exception as e:
    print(f"❌ Error loading AI: {e}")
    ai = None

class ChatRequest(BaseModel):
    user_id: str
    user_message: str
    user_gender: str
    user_name: str
    ai_gender: str
    mood_state: str = "normal"

@app.get("/")
def home():
    return {
        "status": "AI Companion Backend Running! 🚀",
        "ai_provider": "Groq (Llama-3.1-8B)",
        "version": "2.0"
    }

@app.post("/chat")
def chat(request: ChatRequest):
    if ai is None:
        raise HTTPException(status_code=500, detail="AI not initialized")
    
    try:
        # Get chat history (skip if Firebase not available)
        if firebase:
            chat_history = firebase.get_chat_history(request.user_id, limit=6)
        else:
            chat_history = []
        
        # Get AI response
        response = ai.get_response(
            user_message=request.user_message,
            user_gender=request.ai_gender,
            user_name=request.user_name,
            conversation_history=chat_history,
            mood_state=request.mood_state
        )
        
        # Save messages to Firebase (if available)
        if firebase:
            firebase.save_message(request.user_id, request.user_message, "user", request.ai_gender)
            firebase.save_message(request.user_id, response, "ai", request.ai_gender)
        
        return {
            "success": True,
            "ai_response": response,
            "provider": "groq"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "ai": "groq"}