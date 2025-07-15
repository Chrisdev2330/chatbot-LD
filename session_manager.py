import time
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(hours=24)  # Sesiones expiran después de 24 horas

    def get_session(self, phone_number):
        """Obtiene o crea una sesión para el número de teléfono"""
        now = datetime.now()
        
        # Limpiar sesiones expiradas
        expired = [k for k, v in self.sessions.items() if now - v['last_activity'] > self.session_timeout]
        for key in expired:
            del self.sessions[key]
        
        # Crear nueva sesión si no existe o está expirada
        if phone_number not in self.sessions:
            self.sessions[phone_number] = {
                'state': 'IDLE',  # Estados: IDLE, CONFIRMING, PAYING
                'order_id': None,
                'last_activity': now,
                'unrelated_queries': 0,
                'confirmed': False
            }
        else:
            self.sessions[phone_number]['last_activity'] = now
        
        return self.sessions[phone_number]

    def update_session_state(self, phone_number, state, order_id=None):
        """Actualiza el estado de la sesión"""
        session = self.get_session(phone_number)
        session['state'] = state
        session['last_activity'] = datetime.now()
        if order_id:
            session['order_id'] = order_id
        return session

    def reset_unrelated_queries(self, phone_number):
        """Reinicia el contador de consultas no relacionadas"""
        session = self.get_session(phone_number)
        session['unrelated_queries'] = 0

    def increment_unrelated_queries(self, phone_number):
        """Incrementa el contador de consultas no relacionadas"""
        session = self.get_session(phone_number)
        session['unrelated_queries'] = session.get('unrelated_queries', 0) + 1
        return session['unrelated_queries']

    def close_session(self, phone_number):
        """Cierra una sesión específica"""
        if phone_number in self.sessions:
            del self.sessions[phone_number]

    def confirm_order(self, phone_number, order_id):
        """Marca un pedido como confirmado"""
        session = self.get_session(phone_number)
        session['confirmed'] = True
        session['order_id'] = order_id
        session['state'] = 'IDLE'
        return session