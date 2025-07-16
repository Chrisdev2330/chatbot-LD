from flask import Flask, jsonify, request
from config import Config
from services.ai_service import ai_service
from services.whatsapp_service import whatsapp_service
import asyncio
from functools import wraps

app = Flask(__name__)

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@app.route("/webhook/", methods=["POST", "GET"])
@async_route
async def webhook_whatsapp():
    # Verificación del token (GET)
    if request.method == "GET":
        if request.args.get('hub.verify_token') == Config.VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Error de autentificación", 403
    
    # Procesamiento de mensajes (POST)
    try:
        data = request.get_json()
        
        # Extraer información del mensaje
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        
        # Verificar si hay mensajes
        if 'messages' not in value:
            return jsonify({"status": "success"}), 200
            
        message = value['messages'][0]
        telefono_cliente = message['from']
        mensaje = message['text']['body'].lower() if 'text' in message else ''
        
        # Manejar mensajes especiales
        if not mensaje:
            return jsonify({"status": "success"}), 200
            
        # Comandos especiales
        if mensaje == 'confirmar':
            whatsapp_service.send_message(telefono_cliente, Config.CONFIRMAR_PEDIDO)
            return jsonify({"status": "success"}), 200
            
        if mensaje == 'mipago':
            whatsapp_service.send_message(telefono_cliente, Config.PEDIR_COMPROBANTE)
            return jsonify({"status": "success"}), 200
            
        if mensaje == 'salir':
            whatsapp_service.send_message(telefono_cliente, Config.DESPEDIDA)
            return jsonify({"status": "success"}), 200
            
        # Mensaje de bienvenida para saludos iniciales
        saludos = ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches"]
        if any(saludo in mensaje for saludo in saludos):
            whatsapp_service.send_message(telefono_cliente, Config.BIENVENIDA)
            return jsonify({"status": "success"}), 200
            
        # Mensajes de despedida
        despedidas = ["adiós", "chao", "bye", "hasta luego", "nos vemos"]
        if any(despedida in mensaje for despedida in despedidas):
            whatsapp_service.send_message(telefono_cliente, Config.DESPEDIDA)
            return jsonify({"status": "success"}), 200
            
        # Agradecimientos
        agradecimientos = ["gracias", "muchas gracias", "thanks", "thank you"]
        if any(agradecimiento in mensaje for agradecimiento in agradecimientos):
            whatsapp_service.send_message(telefono_cliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
            return jsonify({"status": "success"}), 200
            
        # Procesar con IA para otros mensajes
        respuesta_ia = await ai_service.generate_response(mensaje)
        whatsapp_service.send_message(telefono_cliente, respuesta_ia)
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error en webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)