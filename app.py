from flask import Flask, jsonify, request
from openai import OpenAI
from heyoo import WhatsApp
import os
import requests
from datetime import datetime, timedelta
from session_manager import SessionManager
from templates import *
import config

app = Flask(__name__)

# Configuración de DeepSeek
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config.DEEPSEEK_API_KEY,
)

# Configuración de WhatsApp
mensajeWa = WhatsApp(config.WHATSAPP_TOKEN, config.WHATSAPP_PHONE_ID)

# Manejo de sesiones
session_manager = SessionManager()

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
    except:
        return jsonify({"status": "error"}, 400)
    
    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    
    # Obtener o crear sesión
    session = session_manager.get_session(telefonoCliente)
    
    # Manejar flujos especiales
    if handle_special_flows(telefonoCliente, mensaje, session):
        return jsonify({"status": "success"}, 200)
    
    # Manejar mensajes normales
    handle_normal_message(telefonoCliente, mensaje, session)
    
    return jsonify({"status": "success"}, 200)

def handle_special_flows(telefonoCliente, mensaje, session):
    mensaje = mensaje.lower().strip()
    
    # Saludo inicial
    if any(palabra in mensaje for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, PLANTILLA_BIENVENIDA)
        return True
    
    # Despedida
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["despedida"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        session_manager.clear_session(telefonoCliente)
        return True
    
    # Agradecimiento
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        enviar(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        return True
    
    # Notificaciones
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["notificaciones"]):
        enviar(telefonoCliente, MENSAJE_NOTIFICACIONES)
        return True
    
    # Flujo confirmar pedido
    if mensaje == "confirmar":
        session['current_flow'] = 'confirmar'
        enviar(telefonoCliente, PLANTILLA_CONFIRMAR_PEDIDO)
        return True
    
    # Flujo mi pago
    if mensaje == "mipago":
        if 'confirmed_order' not in session:
            enviar(telefonoCliente, PLANTILLA_CONFIRMAR_PRIMERO)
            return True
        session['current_flow'] = 'mipago'
        enviar(telefonoCliente, PLANTILLA_ENVIAR_COMPROBANTE)
        return True
    
    # Manejar respuestas dentro de flujos
    if 'current_flow' in session:
        return handle_flow_response(telefonoCliente, mensaje, session)
    
    return False

def handle_flow_response(telefonoCliente, mensaje, session):
    current_flow = session['current_flow']
    
    if current_flow == 'confirmar':
        if mensaje.lower() == 'regresar':
            session.pop('current_flow', None)
            enviar(telefonoCliente, "Has salido del flujo de confirmación. ¿En qué más puedo ayudarte?")
            return True
        
        if mensaje.lower() == 'cancelar':
            session.pop('current_flow', None)
            enviar(telefonoCliente, PLANTILLA_CANCELAR_PEDIDO_CLIENTE)
            enviar_admin(PLANTILLA_CANCELAR_PEDIDO_ADMIN.format(order_id=session.get('order_id', 'N/A')))
            session_manager.clear_session(telefonoCliente)
            return True
        
        if mensaje.startswith('#') or mensaje.startswith('-'):
            order_id = mensaje[1:].strip()
            session['confirmed_order'] = True
            session['order_id'] = order_id
            session.pop('current_flow', None)
            enviar(telefonoCliente, PLANTILLA_PEDIDO_CONFIRMADO_CLIENTE.format(order_id=order_id))
            enviar_admin(PLANTILLA_PEDIDO_CONFIRMADO_ADMIN.format(order_id=order_id))
            return True
        else:
            enviar(telefonoCliente, PLANTILLA_FORMATO_INCORRECTO)
            return True
    
    elif current_flow == 'mipago':
        if mensaje.lower() == 'cancelar':
            session.pop('current_flow', None)
            enviar(telefonoCliente, PLANTILLA_CANCELAR_PAGO_CLIENTE)
            enviar_admin(PLANTILLA_CANCELAR_PAGO_ADMIN.format(order_id=session.get('order_id', 'N/A')))
            session_manager.clear_session(telefonoCliente)
            return True
        
        if mensaje.startswith('#') or mensaje.startswith('-'):
            order_id = mensaje[1:].strip()
            session.pop('current_flow', None)
            enviar(telefonoCliente, PLANTILLA_COMPROBANTE_RECIBIDO_CLIENTE.format(order_id=order_id))
            enviar_admin(PLANTILLA_COMPROBANTE_RECIBIDO_ADMIN.format(order_id=order_id))
            session_manager.clear_session(telefonoCliente)
            return True
        else:
            enviar(telefonoCliente, PLANTILLA_FORMATO_INCORRECTO)
            return True
    
    return False

def handle_normal_message(telefonoCliente, mensaje, session):
    # Contador de mensajes no relacionados
    if 'unrelated_count' not in session:
        session['unrelated_count'] = 0
    
    # Obtener respuesta de la IA
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
        respuesta = completion.choices[0].message.content
        
        # Verificar si la respuesta es relevante
        if "no está relacionada" in respuesta or "no tengo información" in respuesta:
            session['unrelated_count'] += 1
        else:
            session['unrelated_count'] = 0
        
        # Manejar múltiples mensajes no relacionados
        if session['unrelated_count'] >= 3:
            enviar(telefonoCliente, PLANTILLA_CONTACTO_HUMANO)
            session['unrelated_count'] = 0
        else:
            enviar(telefonoCliente, respuesta)
            
    except Exception as e:
        print(f"Error al obtener respuesta de IA: {e}")
        enviar(telefonoCliente, "Disculpas, hubo un error. Por favor intenta nuevamente.")

def enviar(telefonoRecibe, respuesta):
    mensajeWa.send_message(respuesta, telefonoRecibe)

def enviar_admin(mensaje):
    for admin in config.ADMIN_NUMBERS:
        mensajeWa.send_message(mensaje, admin)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)