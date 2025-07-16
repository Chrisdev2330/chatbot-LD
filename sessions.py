from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(hours=24)
    
    def get_session(self, user_id):
        if user_id not in self.sessions or self._is_expired(user_id):
            self._create_session(user_id)
        return self.sessions[user_id]
    
    def _create_session(self, user_id):
        self.sessions[user_id] = {
            'created_at': datetime.now(),
            'flow': None,
            'data': {},
            'last_interaction': datetime.now()
        }
    
    def _is_expired(self, user_id):
        return datetime.now() - self.sessions[user_id]['created_at'] > self.session_timeout
    
    def update_last_interaction(self, user_id):
        self.get_session(user_id)['last_interaction'] = datetime.now()
    
    def set_flow(self, user_id, flow):
        self.get_session(user_id)['flow'] = flow
        self.update_last_interaction(user_id)
    
    def get_flow(self, user_id):
        return self.get_session(user_id)['flow']
    
    def set_data(self, user_id, key, value):
        self.get_session(user_id)['data'][key] = value
        self.update_last_interaction(user_id)
    
    def get_data(self, user_id, key):
        return self.get_session(user_id)['data'].get(key)
    
    def clear_flow(self, user_id):
        self.get_session(user_id)['flow'] = None
        self.update_last_interaction(user_id)