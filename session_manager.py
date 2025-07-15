import time
from datetime import datetime

class SessionManager:
    def __init__(self, max_sessions=1000, session_timeout=86400):
        self.sessions = {}
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
    
    def get_session(self, user_id):
        self.clean_expired_sessions()
        
        if user_id not in self.sessions:
            if len(self.sessions) >= self.max_sessions:
                self.clear_oldest_sessions(100)
            
            self.sessions[user_id] = {
                'created': time.time(),
                'last_activity': time.time(),
                'data': {},
                'in_flow': None,
                'flow_data': None
            }
        
        self.sessions[user_id]['last_activity'] = time.time()
        return self.sessions[user_id]
    
    def clean_expired_sessions(self):
        current_time = time.time()
        expired = [user_id for user_id, session in self.sessions.items() 
                  if current_time - session['last_activity'] > self.session_timeout]
        
        for user_id in expired:
            del self.sessions[user_id]
    
    def clear_oldest_sessions(self, count):
        sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]['last_activity'])
        for user_id, _ in sorted_sessions[:count]:
            del self.sessions[user_id]
    
    def end_session(self, user_id):
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def set_flow(self, user_id, flow_name):
        session = self.get_session(user_id)
        session['in_flow'] = flow_name
        session['flow_data'] = {}
    
    def exit_flow(self, user_id):
        session = self.get_session(user_id)
        session['in_flow'] = None
        session['flow_data'] = None
    
    def get_current_flow(self, user_id):
        session = self.get_session(user_id)
        return session['in_flow']
    
    def set_flow_data(self, user_id, key, value):
        session = self.get_session(user_id)
        session['flow_data'][key] = value
    
    def get_flow_data(self, user_id, key):
        session = self.get_session(user_id)
        return session['flow_data'].get(key)

# Instancia global del gestor de sesiones
session_manager = SessionManager()