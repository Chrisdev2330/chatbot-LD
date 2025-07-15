import requests
from config import CONFIG

def send_whatsapp_message(phone, message):
    url = f"https://graph.facebook.com/v18.0/{CONFIG['WHATSAPP_PHONE_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {CONFIG['WHATSAPP_TOKEN']}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def send_admin_notification(message):
    for admin_number in CONFIG['ADMIN_NUMBERS']:
        send_whatsapp_message(admin_number, message)