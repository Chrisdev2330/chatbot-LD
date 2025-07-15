from flask import jsonify
from config import CONFIG
from templates import TEMPLATES
import requests

def send_to_admin(admin_number, message):
    """Envía un mensaje al número administrador"""
    url = f"https://graph.facebook.com/v18.0/{CONFIG['PHONE_NUMBER_ID']}/messages"
    headers = {
        'Authorization': f'Bearer {CONFIG["WHATSAPP_TOKEN"]}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": admin_number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending to admin: {e}")
        return False

def handle_confirm_flow(user_phone, user_message, session):
    """Maneja el flujo de confirmación de pedido"""
    from app import enviar  # Importación circular, pero necesaria
    
    if not session.get('order_id'):
        # Pedir ID del pedido
        enviar(user_phone, TEMPLATES["CONFIRM_PROMPT"])
        session['state'] = 'awaiting_order_id'
        return True
    else:
        # Confirmar pedido
        order_id = user_message.strip()
        session['order_id'] = order_id
        session['confirmed_order'] = True
        session['state'] = 'active'
        
        # Notificar al admin
        admin_message = TEMPLATES["CONFIRM_ADMIN_NOTIFICATION"].format(
            user_phone=user_phone,
            order_id=order_id
        )
        for admin in CONFIG["ADMIN_NUMBERS"]:
            send_to_admin(admin, admin_message)
        
        enviar(user_phone, "✅ Pedido confirmado con éxito! ¿Necesitas algo más?")
        return True

def handle_payment_flow(user_phone, session):
    """Maneja el flujo de envío de comprobante"""
    from app import enviar  # Importación circular, pero necesaria
    
    if not session.get('confirmed_order'):
        enviar(user_phone, TEMPLATES["NEED_CONFIRM_FIRST"])
        return False
    else:
        enviar(user_phone, TEMPLATES["PAYMENT_PROMPT"])
        return True