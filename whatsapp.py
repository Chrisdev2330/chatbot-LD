import requests
from config import WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID, ADMIN_NUMBERS

def send_message(phone_number, message):
    """Send WhatsApp message to user"""
    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
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
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def send_admin_notification(message):
    """Send notification to all admin numbers"""
    for admin_number in ADMIN_NUMBERS:
        send_message(admin_number, message)