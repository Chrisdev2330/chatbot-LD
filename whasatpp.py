import requests
from config import WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID

class WhatsAppAPI:
    @staticmethod
    def send_message(to, message):
        url = f"https://graph.facebook.com/v19.0/{WHATSAPP_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    @staticmethod
    def send_admin_notification(message):
        return WhatsAppAPI.send_message(ADMIN_NUMBER, message)