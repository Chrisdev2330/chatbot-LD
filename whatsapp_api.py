import requests

class WhatsAppAPI:
    def __init__(self, token, phone_number_id):
        self.token = token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
        
    def send_message(self, phone_number, message):
        """Send WhatsApp message to user"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
            
    def send_admin_notification(self, admin_number, message):
        """Send notification to admin number"""
        return self.send_message(admin_number, message)