from flask import Flask, jsonify, request
from config import Config
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from  messages2 import (
    BIENVENIDA, DESPEDIDA, CONFIRMAR_PEDIDO, PEDIR_COMPROBANTE, FLUJO_CONVERSACION
)
import asyncio
from functools import wraps

app = Flask(__name__)
ai_service = AIService()
whatsapp_service = WhatsAppService()

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.route("/webhook/", methods=["POST", "GET"])
@async_route
async def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == Config.WEBHOOK_VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Error de autentificación", 403
    
    try:
        data = request.get_json()
        entry = data['entry'][0]['changes'][0]['value']
        
        if 'messages' not in entry:
            return jsonify({"status": "success"}), 200
            
        message_data = entry['messages'][0]
        phone = message_data['from']
        message = message_data['text']['body'].lower() if 'text' in message_data else ""
        
        # Manejo de mensajes
        if any(palabra in message for palabra in FLUJO_CONVERSACION["saludo"]):
            await whatsapp_service.send_message(phone, BIENVENIDA)
        elif any(palabra in message for palabra in FLUJO_CONVERSACION["despedida"]):
            await whatsapp_service.send_message(phone, DESPEDIDA)
        elif "confirmar" in message:
            await whatsapp_service.send_message(phone, CONFIRMAR_PEDIDO)
        elif "mipago" in message:
            await whatsapp_service.send_message(phone, PEDIR_COMPROBANTE)
        else:
            # Consultar a la IA para otras preguntas
            ai_response = await ai_service.generate_response(message)
            await whatsapp_service.send_message(phone, ai_response)
            
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)