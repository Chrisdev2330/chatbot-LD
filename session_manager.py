from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, user_id):
        # Limpiar sesiones expiradas
        self.clean_expired_sessions()
        
        # Crear nueva sesión si no existe o está expirada
        if user_id not in self.sessions or self.sessions[user_id]['expires_at'] < datetime.now():
            self.sessions[user_id] = {
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=24),
                'data': {}
            }
        
        return self.sessions[user_id]['data']
    
    def clear_session(self, user_id):
        if user_id in self.sessions:
            del self.sessions[user_id]
    
    def clean_expired_sessions(self):
        current_time = datetime.now()
        expired_users = [user_id for user_id, session in self.sessions.items() 
                        if session['expires_at'] < current_time]
        
        for user_id in expired_users:
            del self.sessions[user_id]
    
    def get_all_sessions(self):
        return self.sessions