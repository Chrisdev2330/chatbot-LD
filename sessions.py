from datetime import datetime, timedelta

class UserSession:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_new_session = True
        self.conversation_history = []
        self.current_flow = None
        self.confirmed_order_id = None
        self.flow_data = {}

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = timedelta(hours=24)
    
    def get_session(self, phone_number):
        self.cleanup_sessions()
        
        if phone_number not in self.sessions:
            self.sessions[phone_number] = UserSession(phone_number)
        else:
            self.sessions[phone_number].last_activity = datetime.now()
        
        return self.sessions[phone_number]
    
    def cleanup_sessions(self):
        now = datetime.now()
        expired_sessions = [
            phone for phone, session in self.sessions.items() 
            if now - session.last_activity > self.session_timeout
        ]
        
        for phone in expired_sessions:
            del self.sessions[phone]
    
    def add_message_to_history(self, phone_number, role, content):
        if phone_number in self.sessions:
            self.sessions[phone_number].conversation_history.append({
                "role": "user" if role == "user" else "assistant",
                "content": content
            })
    
    def get_conversation_history(self, phone_number):
        if phone_number in self.sessions:
            return self.sessions[phone_number].conversation_history
        return []
    
    def set_current_flow(self, phone_number, flow_name):
        if phone_number in self.sessions:
            self.sessions[phone_number].current_flow = flow_name
    
    def clear_current_flow(self, phone_number):
        if phone_number in self.sessions:
            self.sessions[phone_number].current_flow = None
            self.sessions[phone_number].flow_data = {}
    
    def set_order_id(self, phone_number, order_id):
        if phone_number in self.sessions:
            self.sessions[phone_number].confirmed_order_id = order_id
    
    def get_flow_data(self, phone_number):
        if phone_number in self.sessions:
            return self.sessions[phone_number].flow_data
        return {}
    
    def set_flow_data(self, phone_number, key, value):
        if phone_number in self.sessions:
            self.sessions[phone_number].flow_data[key] = value