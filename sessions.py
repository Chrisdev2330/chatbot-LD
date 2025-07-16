import time
from config import SESSION_TIMEOUT

class SessionManager:
    def __init__(self):
        self.sessions = {}
        
    def get_session(self, user_id):
        """Get or create a session for user"""
        now = time.time()
        
        # Clean up expired sessions
        expired = [k for k, v in self.sessions.items() if now - v['last_activity'] > SESSION_TIMEOUT]
        for k in expired:
            del self.sessions[k]
            
        # Create new session if needed
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'created_at': now,
                'last_activity': now,
                'flow': None,  # 'confirmar', 'mipago', or None
                'flow_data': {},  # Stores data like pedido_id
                'history': []
            }
        else:
            self.sessions[user_id]['last_activity'] = now
            
        return self.sessions[user_id]
        
    def update_flow(self, user_id, flow, data=None):
        """Update user's current flow"""
        session = self.get_session(user_id)
        session['flow'] = flow
        if data:
            session['flow_data'].update(data)
            
    def clear_flow(self, user_id):
        """Clear user's current flow"""
        session = self.get_session(user_id)
        session['flow'] = None
        session['flow_data'] = {}
        
    def log_message(self, user_id, message, from_user=True):
        """Log message to session history"""
        session = self.get_session(user_id)
        session['history'].append({
            'timestamp': time.time(),
            'from_user': from_user,
            'message': message
        })

# Global session manager instance
session_manager = SessionManager()