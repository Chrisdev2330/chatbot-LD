from flask import Flask, jsonify, request
from openai import OpenAI
from datetime import datetime, timedelta
import os
from sessions import SessionManager
from flows import FlowManager
from templates import (
    PLANTILLA_BIENVENIDA,
    PLANTILLA_DESPEDIDA,
    MENSAJE_INSTRUCCIONES,
    MENSAJE_FUERA_CONTEXTO
)
from whatsapp_api import WhatsAppAPI

app = Flask(__name__)

# Configuración
WHATSAPP_TOKEN = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
WHATSAPP_PHONE_ID = '730238483499494'
ADMIN_NUMBER = '584241220797'  # Número de administrador actual

# Inicializar servicios
whatsapp = WhatsAppAPI(WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, ADMIN_NUMBER)
session_manager = SessionManager()
flow_manager = FlowManager(whatsapp, session_manager, ADMIN_NUMBER)

# Inicializar cliente de Gemini
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def load_prompt():
    with open('prompt.txt', 'r', encoding='utf-8') as file:
        return file.read()

PROMPT_BASE = load_prompt()

def generate_ai_response(message, session_id):
    history = session_manager.get_conversation_history(session_id)
    
    messages = [{"role": "system", "content": PROMPT_BASE}]
    messages.extend(history[-4:])
    messages.append({"role": "user", "content": message})
    
    try:
        completion = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Disculpas, hubo un error al procesar tu mensaje. Por favor intenta nuevamente."

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        return "Error de autentificacion."
    
    data = request.get_json()
    
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error"}), 400
    
    # Extraer datos del mensaje
    message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
    telefono_cliente = message_data['from']
    mensaje = message_data['text']['body'].strip()  # Limpiar espacios
    message_id = message_data['id']
    timestamp = message_data['timestamp']

    # Obtener sesión
    session = session_manager.get_session(telefono_cliente)
    
    # Verificar si está en un flujo activo
    if session.current_flow:
        flow_manager.handle_flow(session, mensaje)
        return jsonify({"status": "success"}), 200
    
    # Manejar comandos especiales (confirmar/mipago)
    if mensaje.lower() == "confirmar":
        flow_manager.start_flow(telefono_cliente, "confirmar")
        return jsonify({"status": "success"}), 200
    
    if mensaje.lower() == "mipago":
        if not session.confirmed_order_id:
            whatsapp.send_message(
                telefono_cliente,
                "⚠️ No puedes ingresar a esta opción de pagos si antes no confirmas tu pedido.\n\n" +
                "Por favor escribe 'confirmar' para confirmar tu pedido."
            )
        else:
            flow_manager.start_flow(telefono_cliente, "mipago")
        return jsonify({"status": "success"}), 200
    
    # Mensaje inicial de bienvenida
    if session.is_new_session or any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        whatsapp.send_message(telefono_cliente, PLANTILLA_BIENVENIDA)
        session.is_new_session = False
        return jsonify({"status": "success"}), 200
    
    # Mensaje de despedida
    if any(palabra in mensaje.lower() for palabra in ["adiós", "chao", "bye", "hasta luego", "nos vemos"]):
        whatsapp.send_message(telefono_cliente, PLANTILLA_DESPEDIDA)
        return jsonify({"status": "success"}), 200
    
    # Generar respuesta con IA
    ai_response = generate_ai_response(mensaje, telefono_cliente)
    whatsapp.send_message(telefono_cliente, ai_response)
    
    # Actualizar historial de conversación
    session_manager.add_message_to_history(telefono_cliente, "user", mensaje)
    session_manager.add_message_to_history(telefono_cliente, "assistant", ai_response)
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)