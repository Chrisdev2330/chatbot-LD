import time
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 86400  # 24 horas en segundos

    def get_session(self, user_id):
        """Obtiene o crea una sesión para el usuario"""
        now = datetime.now()
        if user_id not in self.sessions or (now - self.sessions[user_id]['last_activity']) > timedelta(seconds=self.session_timeout):
            self.sessions[user_id] = {
                'state': 'main',
                'data': {},
                'last_activity': now,
                'confirmed_order': False,
                'attempts': 0
            }
        else:
            self.sessions[user_id]['last_activity'] = now
        return self.sessions[user_id]

    def update_session_state(self, user_id, state, data=None):
        """Actualiza el estado de la sesión"""
        session = self.get_session(user_id)
        session['state'] = state
        if data:
            session['data'].update(data)
        session['last_activity'] = datetime.now()
        return session

    def reset_session(self, user_id):
        """Reinicia la sesión del usuario"""
        self.sessions[user_id] = {
            'state': 'main',
            'data': {},
            'last_activity': datetime.now(),
            'confirmed_order': False,
            'attempts': 0
        }
        return self.sessions[user_id]

    def increment_attempts(self, user_id):
        """Incrementa el contador de intentos fuera de contexto"""
        session = self.get_session(user_id)
        session['attempts'] += 1
        return session['attempts']

    def reset_attempts(self, user_id):
        """Reinicia el contador de intentos"""
        session = self.get_session(user_id)
        session['attempts'] = 0

    def confirm_order(self, user_id, order_id):
        """Marca un pedido como confirmado"""
        session = self.get_session(user_id)
        session['confirmed_order'] = True
        session['order_id'] = order_id
        return session

    def cancel_order(self, user_id):
        """Cancela el pedido actual"""
        session = self.get_session(user_id)
        session['confirmed_order'] = False
        if 'order_id' in session:
            order_id = session['order_id']
            del session['order_id']
            return order_id
        return None

# Instancia global del administrador de sesiones
session_manager = SessionManager()