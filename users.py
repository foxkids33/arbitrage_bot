# users.py
import json
import os
from typing import Set

class UserManager:
    def __init__(self, filename='users.json'):
        self.filename = filename
        self.users: Set[str] = self.load_users()

    def load_users(self) -> Set[str]:
        """Load users from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    return set(data['users'])
        except Exception as e:
            print(f"Error loading users: {e}")
        return set()

    def save_users(self):
        """Save users to file"""
        try:
            data = {'users': list(self.users)}
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")

    def add_user(self, chat_id: str):
        """Add new user"""
        self.users.add(chat_id)
        self.save_users()

    def get_all_users(self) -> Set[str]:
        """Get all users"""
        return self.users

# Create global user manager instance
user_manager = UserManager()