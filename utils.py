import requests
from config import CONFIG

def send_message(phone_number, message):
    """Envía un mensaje a través de WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{CONFIG['WHATSAPP_PHONE_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {CONFIG['WHATSAPP_TOKEN']}",
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
        return response.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def send_admin_notification(message):
    """Envía una notificación a los números administradores"""
    for admin_number in CONFIG["ADMIN_NUMBERS"]:
        send_message(admin_number, message)

def read_prompt():
    """Lee el contenido del archivo prompt.txt"""
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("Warning: prompt.txt not found, using empty prompt")
        return ""