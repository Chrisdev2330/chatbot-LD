import time

# Diccionario para almacenar las sesiones
user_sessions = {}

def get_session(user_phone):
    """Obtiene o crea una sesión para el usuario"""
    now = time.time()
    
    if user_phone not in user_sessions or now - user_sessions[user_phone]['last_activity'] > 86400:
        user_sessions[user_phone] = {
            'state': 'active',
            'confirmed_order': False,
            'order_id': None,
            'unrelated_queries': 0,
            'last_activity': now
        }
    else:
        user_sessions[user_phone]['last_activity'] = now
    
    return user_sessions[user_phone]

def close_session(user_phone):
    """Cierra la sesión del usuario"""
    if user_phone in user_sessions:
        user_sessions[user_phone]['state'] = 'closed'
        return True
    return False

def reset_unrelated_queries(user_phone):
    """Reinicia el contador de consultas no relacionadas"""
    if user_phone in user_sessions:
        user_sessions[user_phone]['unrelated_queries'] = 0