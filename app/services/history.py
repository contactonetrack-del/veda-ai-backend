"""
Chat History Service
Stores recent conversation history for context-aware responses
Uses local JSON file storage for simplicity and speed
"""
import json
import os
from typing import List, Dict
from datetime import datetime

HISTORY_FILE = "chat_history.json"

class HistoryService:
    def __init__(self):
        self.file_path = HISTORY_FILE
        self._ensure_file()
    
    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)
    
    def _load_data(self) -> Dict:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except:
            return {}
            
    def _save_data(self, data: Dict):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)

    def add_message(self, user_id: str, role: str, content: str):
        """Add a message to user's history"""
        data = self._load_data()
        
        if user_id not in data:
            data[user_id] = []
            
        # Add new message
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        data[user_id].append(message)
        
        # Keep only last 20 messages per user to manage size
        if len(data[user_id]) > 20:
            data[user_id] = data[user_id][-20:]
            
        self._save_data(data)
        
    def get_recent_messages(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages for context"""
        data = self._load_data()
        history = data.get(user_id, [])
        return history[-limit:]
        
    def clear_history(self, user_id: str):
        """Clear user history"""
        data = self._load_data()
        if user_id in data:
            del data[user_id]
            self._save_data(data)

# Singleton
history_service = HistoryService()
