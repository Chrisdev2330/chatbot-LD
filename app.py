from flask import Flask, jsonify, request
from openai import OpenAI
from heyoo import WhatsApp
import os
import threading
from session_manager import SessionManager
from templates import *
from config import Config

app = Flask(__name__)
config = Config()
session_manager = SessionManager()

# Configuración de DeepSeek
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.DEEPSEEK_API_KEY,
)

# WhatsApp
mensaje_wa = WhatsApp(config.WHATSAPP_TOKEN, config.WHATSAPP_PHONE_ID)

def enviar(telefono, mensaje):
    try:
        mensaje_wa.send_message(mensaje, telefono)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

def procesar_mensaje_ia(telefono, mensaje):
    try:
        with open('prompt.txt', 'r') as file:
            prompt_base = file.read()
        
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {"role": "system", "content": prompt_base},
                {"role": "user", "content": mensaje}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error en IA: {e}")
        return PLANTILLA_ERROR_IA

def manejar_flujo_confirmar(telefono, mensaje, session):
    if not session.get('esperando_id'):
        enviar(telefono, PLANTILLA_CONFIRMAR_PEDIDO)
        session['esperando_id'] = True
        session['flujo_actual'] = 'confirmar'
        return True
    
    if mensaje.startswith('#') or mensaje.startswith('-'):
        order_id = mensaje[1:].strip()
        if order_id:
            session['order_id'] = order_id
            if mensaje.startswith('#'):
                enviar(telefono, PLANTILLA_PEDIDO_CONFIRMADO_CLIENTE.format(order_id=order_id))
                enviar(config.ADMIN_NUMBER, PLANTILLA_PEDIDO_CONFIRMADO_ADMIN.format(order_id=order_id))
            else:
                enviar(telefono, PLANTILLA_PEDIDO_CANCELADO_CLIENTE.format(order_id=order_id))
                enviar(config.ADMIN_NUMBER, PLANTILLA_PEDIDO_CANCELADO_ADMIN.format(order_id=order_id))
            session.clear()
            return True
        else:
            enviar(telefono, PLANTILLA_ID_INVALIDO)
            return True
    
    enviar(telefono, PLANTILLA_ID_INVALIDO)
    return True

def manejar_flujo_mipago(telefono, mensaje, session):
    if not session.get('order_id'):
        enviar(telefono, PLANTILLA_CONFIRMAR_PRIMERO)
        return True
    
    enviar(telefono, PLANTILLA_ENVIAR_COMPROBANTE.format(admin_number=config.ADMIN_NUMBER))
    session.clear()
    return True

def manejar_flujos_especiales(telefono, mensaje, session):
    mensaje = mensaje.lower().strip()
    
    if mensaje == 'confirmar':
        return manejar_flujo_confirmar(telefono, mensaje, session)
    elif mensaje == 'mipago':
        return manejar_flujo_mipago(telefono, mensaje, session)
    elif mensaje == 'salir':
        session.clear()
        enviar(telefono, PLANTILLA_DESPEDIDA)
        return True
    
    return False

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == config.VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Error de autentificacion."
    
    data = request.get_json()
    
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}, 200)
        
        telefono = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        
        session = session_manager.get_session(telefono)
        
        # Manejar mensajes especiales primero
        if manejar_flujos_especiales(telefono, mensaje, session):
            return jsonify({"status": "success"}, 200)
        
        # Procesar con IA
        threading.Thread(target=procesar_y_responder, args=(telefono, mensaje, session)).start()
        
        return jsonify({"status": "success"}, 200)
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"status": "error"}, 500)

def procesar_y_responder(telefono, mensaje, session):
    respuesta_ia = procesar_mensaje_ia(telefono, mensaje)
    enviar(telefono, respuesta_ia)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)