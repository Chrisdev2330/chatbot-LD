import requests
import os

class WhatsAppAPI:
    def __init__(self, token, phone_id):
        self.token = token
        self.phone_id = phone_id
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_id}/messages"
    
    def send_message(self, recipient, message):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return None
    
    def send_admin_notification(self, admin_number, message):
        return self.send_message(admin_number, message)