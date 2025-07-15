import time
from config import CONFIG

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.flow_sessions = {}
    
    def get_session(self, phone):
        # Clean expired sessions
        self._clean_expired_sessions()
        
        # Create new session if doesn't exist or expired
        if phone not in self.sessions or self._is_session_expired(phone):
            self.sessions[phone] = {
                'created_at': time.time(),
                'unrelated_attempts': 0,
                'confirmed_order': None,
                'last_interaction': time.time()
            }
        return self.sessions[phone]
    
    def update_session(self, phone):
        if phone in self.sessions:
            self.sessions[phone]['last_interaction'] = time.time()
    
    def reset_unrelated_attempts(self, phone):
        if phone in self.sessions:
            self.sessions[phone]['unrelated_attempts'] = 0
    
    def increment_unrelated_attempts(self, phone):
        if phone in self.sessions:
            self.sessions[phone]['unrelated_attempts'] += 1
            return self.sessions[phone]['unrelated_attempts']
        return 0
    
    def set_confirmed_order(self, phone, order_id):
        if phone in self.sessions:
            self.sessions[phone]['confirmed_order'] = order_id
    
    def get_confirmed_order(self, phone):
        if phone in self.sessions:
            return self.sessions[phone]['confirmed_order']
        return None
    
    def clear_session(self, phone):
        if phone in self.sessions:
            confirmed_order = self.sessions[phone]['confirmed_order']
            del self.sessions[phone]
            return confirmed_order
        return None
    
    def start_flow(self, phone, flow_type):
        self.flow_sessions[phone] = {
            'flow_type': flow_type,
            'started_at': time.time()
        }
        return True
    
    def end_flow(self, phone):
        if phone in self.flow_sessions:
            del self.flow_sessions[phone]
            return True
        return False
    
    def get_current_flow(self, phone):
        return self.flow_sessions.get(phone, None)
    
    def is_flow_active(self, phone):
        if phone in self.flow_sessions:
            flow = self.flow_sessions[phone]
            return (time.time() - flow['started_at']) < CONFIG['FLOW_TIMEOUT']
        return False
    
    def _is_session_expired(self, phone):
        if phone in self.sessions:
            session = self.sessions[phone]
            return (time.time() - session['created_at']) > CONFIG['SESSION_TIMEOUT']
        return True
    
    def _clean_expired_sessions(self):
        current_time = time.time()
        expired_phones = [
            phone for phone, session in self.sessions.items()
            if (current_time - session['created_at']) > CONFIG['SESSION_TIMEOUT']
        ]
        for phone in expired_phones:
            del self.sessions[phone]