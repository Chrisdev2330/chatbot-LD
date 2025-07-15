import time

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def get_session(self, user_id):
        # Limpiar sesiones antiguas
        self.clean_expired_sessions()
        
        # Crear nueva sesión si no existe
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'created_at': time.time(),
                'data': {}
            }
        
        # Resetear tiempo de creación si se accede
        self.sessions[user_id]['created_at'] = time.time()
        return self.sessions[user_id]['data']
    
    def clean_expired_sessions(self, max_age_hours=24):
        current_time = time.time()
        expired = [user_id for user_id, session in self.sessions.items() 
                  if current_time - session['created_at'] > max_age_hours * 3600]
        
        for user_id in expired:
            del self.sessions[user_id]