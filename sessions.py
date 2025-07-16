import time

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, user_id):
        # Clear expired sessions first
        self._clean_expired_sessions()
        
        # Get or create session
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'created_at': time.time(),
                'initialized': False,
                'current_flow': None,
                'flow_data': {},
                'last_interaction': time.time()
            }
        else:
            self.sessions[user_id]['last_interaction'] = time.time()
        
        return self.sessions[user_id]
    
    def save_session(self, user_id, session_data):
        self.sessions[user_id] = session_data
        self.sessions[user_id]['last_interaction'] = time.time()
    
    def end_flow(self, user_id):
        if user_id in self.sessions:
            self.sessions[user_id]['current_flow'] = None
            self.sessions[user_id]['flow_data'] = {}
    
    def _clean_expired_sessions(self):
        current_time = time.time()
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if current_time - session['last_interaction'] > 86400  # 24 hours
        ]
        
        for user_id in expired_users:
            del self.sessions[user_id]