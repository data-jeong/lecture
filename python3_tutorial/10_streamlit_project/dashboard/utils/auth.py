"""Authentication utilities for the dashboard"""

import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    salt = "dashboard_salt_2024"  # In production, use unique salt per user
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def generate_token() -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(32)


def check_authentication() -> bool:
    """Check if user is authenticated (placeholder)"""
    # This is a simple placeholder
    # In production, implement proper session management
    import streamlit as st
    return st.session_state.get('authenticated', False)


class AuthManager:
    """Authentication manager"""
    
    def __init__(self):
        self.users = self._load_users()
        self.sessions = {}
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load user data (mock data for demo)"""
        return {
            "admin": {
                "password": hash_password("admin"),
                "role": "admin",
                "email": "admin@example.com",
                "full_name": "Administrator"
            },
            "user1": {
                "password": hash_password("user123"),
                "role": "user",
                "email": "user1@example.com",
                "full_name": "John Doe"
            },
            "demo": {
                "password": hash_password("demo"),
                "role": "viewer",
                "email": "demo@example.com",
                "full_name": "Demo User"
            }
        }
    
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if not verify_password(password, user["password"]):
            return None
        
        # Create session
        session_token = generate_token()
        session_data = {
            "username": username,
            "role": user["role"],
            "email": user["email"],
            "full_name": user["full_name"],
            "login_time": datetime.now(),
            "token": session_token
        }
        
        self.sessions[session_token] = session_data
        return session_data
    
    def logout(self, token: str) -> bool:
        """Logout user"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token"""
        if token not in self.sessions:
            return None
        
        session = self.sessions[token]
        
        # Check session timeout (30 minutes)
        if datetime.now() - session["login_time"] > timedelta(minutes=30):
            del self.sessions[token]
            return None
        
        return session
    
    def has_permission(self, token: str, permission: str) -> bool:
        """Check if user has permission"""
        session = self.validate_session(token)
        if not session:
            return False
        
        role = session.get("role", "viewer")
        
        permissions = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "viewer": ["read"]
        }
        
        return permission in permissions.get(role, [])