import time
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, session_timeout=86400):  # 24 horas por defecto
        self.sessions = {}
        self.session_timeout = session_timeout
    
    def get_session(self, user_id):
        self.clean_sessions()
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'data': {
                    'pedido_confirmado': False,
                    'pedido_id': None,
                    'historial': []
                }
            }
        else:
            self.sessions[user_id]['last_activity'] = datetime.now()
        return self.sessions[user_id]
    
    def update_session(self, user_id, data):
        session = self.get_session(user_id)
        session['data'].update(data)
        session['last_activity'] = datetime.now()
    
    def clean_sessions(self):
        now = datetime.now()
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if (now - session['last_activity']) > timedelta(seconds=self.session_timeout)
        ]
        for user_id in expired_users:
            del self.sessions[user_id]
    
    def close_session(self, user_id):
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def add_to_history(self, user_id, message):
        session = self.get_session(user_id)
        session['data']['historial'].append({
            'timestamp': datetime.now(),
            'message': message
        })
        # Mantener solo los últimos 10 mensajes en el historial
        session['data']['historial'] = session['data']['historial'][-10:]