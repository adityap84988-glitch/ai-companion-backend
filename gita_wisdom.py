import json

class GitaWisdom:
    def __init__(self):
        # Load Gita database
        try:
            with open('gita_database.json', 'r', encoding='utf-8') as f:
                self.gita_data = json.load(f)
        except FileNotFoundError:
            print("ERROR: gita_database.json not found!")
            self.gita_data = []
    
    def detect_emotion(self, user_message):
        """Detect if user needs Gita wisdom"""
        user_message_lower = user_message.lower()
        
        # Emotion keywords
        emotion_keywords = {
            'sad': ['sad', 'dukhi', 'upset', 'depression', 'depressed', 'hopeless', 'failure', 'fail', 'haar', 'nahi ho raha'],
            'angry': ['angry', 'gussa', 'frustrate', 'irritate', 'chid'],
            'confused': ['confuse', 'doubt', 'samajh nahi', 'kya karu', 'lost', 'uncertain'],
            'anxiety': ['tension', 'worry', 'anxiety', 'stress', 'dar'],
            'heartbreak': ['heartbreak', 'breakup', 'betrayal', 'cheat', 'dhoka', 'lonely', 'akela']
        }
        
        # Check for emotion
        for emotion_type, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in user_message_lower:
                    for shloka in self.gita_data:
                        if emotion_type in [e.lower() for e in shloka['emotion']]:
                            return shloka
        return None
    
    def format_gita_response(self, shloka, user_gender):
        """Format Gita wisdom response"""
        response = f"{shloka['modern_advice']}\n\n"
        response += f"Suna hai kabhi ye shloka?\n"
        response += f"'{shloka['shloka_sanskrit']}'\n\n"
        response += f"{shloka['meaning_hinglish']}\n\n"
        response += f"Samjha? Bas yahi karna hai abhi. I believe in you! 💪"
        return response