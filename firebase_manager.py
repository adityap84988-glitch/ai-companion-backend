import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
import os
import json

class FirebaseManager:
    def __init__(self):
        try:
            # Check if running on cloud (Render.com)
            if os.getenv('FIREBASE_CREDENTIALS'):
                firebase_creds = json.loads(os.getenv('FIREBASE_CREDENTIALS'))
                cred = credentials.Certificate(firebase_creds)
            else:
                # Local development
                cred = credentials.Certificate('firebase-credentials.json')
            
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("✅ Firebase initialized successfully!")
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            self.db = None
    
    def save_message(self, user_id, message, sender, ai_gender):
        """Save chat message to Firestore"""
        try:
            self.db.collection('users').document(user_id).collection('chats').add({
                'message': message,
                'sender': sender,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'ai_gender': ai_gender
            })
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def get_chat_history(self, user_id, limit=10):
        """Get recent chat history"""
        try:
            messages = self.db.collection('users').document(user_id)\
                .collection('chats')\
                .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .stream()
            
            chat_history = []
            for msg in messages:
                data = msg.to_dict()
                role = "user" if data['sender'] == 'user' else "assistant"
                chat_history.append({
                    "role": role,
                    "content": data['message']
                })
            
            return list(reversed(chat_history))
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
    
    def save_user_profile(self, user_id, name, gender, ai_gender):
        """Save user profile"""
        try:
            self.db.collection('users').document(user_id).set({
                'name': name,
                'gender': gender,
                'ai_gender': ai_gender,
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_active': firestore.SERVER_TIMESTAMP
            }, merge=True)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def get_user_profile(self, user_id):
        """Get user profile"""
        try:
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def update_last_active(self, user_id):
        """Update user's last active time"""
        try:
            self.db.collection('users').document(user_id).update({
                'last_active': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            print(f"Error updating last active: {e}")
            return False
    
    def get_inactive_users(self, hours=3):
        """Get users inactive for X hours"""
        try:
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            users = self.db.collection('users')\
                .where('last_active', '<', cutoff_time)\
                .stream()
            
            inactive_users = []
            for user in users:
                data = user.to_dict()
                data['user_id'] = user.id
                inactive_users.append(data)
            
            return inactive_users
        except Exception as e:
            print(f"Error getting inactive users: {e}")
            return []