from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
import os
import requests
from config import CONFIG
from templates import TEMPLATES
from session_manager import SessionManager
import re

app = Flask(__name__)

# Configuración inicial
cliente = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])
mensajeWa = WhatsApp(CONFIG["WHATSAPP_TOKEN"], CONFIG["WHATSAPP_PHONE_NUMBER_ID"])
session_manager = SessionManager()

# Cargar prompt
with open('prompt.txt', 'r', encoding='utf-8') as file:
    PROMPT_BASE = file.read()

def enviar(telefonoRecibe, respuesta):
    """Envía un mensaje a través de WhatsApp"""
    mensajeWa.send_message(respuesta, telefonoRecibe)

def enviar_a_admin(mensaje, order_id=None, client_number=None):
    """Envía un mensaje a los números administradores"""
    for admin_num in CONFIG["ADMIN_NUMBERS"]:
        try:
            if order_id and client_number:
                mensaje = mensaje.format(order_id=order_id, client_number=client_number)
            elif admin_num in mensaje:
                mensaje = mensaje.format(admin_number=admin_num)
            
            url = f"https://graph.facebook.com/v18.0/{CONFIG['WHATSAPP_PHONE_NUMBER_ID']}/messages"
            headers = {
                'Authorization': f'Bearer {CONFIG["WHATSAPP_TOKEN"]}',
                'Content-Type': 'application/json'
            }
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": admin_num,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": mensaje
                }
            }
            requests.post(url, headers=headers, json=data)
        except Exception as e:
            print(f"Error enviando a admin {admin_num}: {e}")

def procesar_ia(mensaje_usuario, telefono_cliente):
    """Procesa el mensaje con la IA de Gemini"""
    try:
        # Reiniciar contador si la consulta es relacionada
        session_manager.reset_unrelated_queries(telefono_cliente)
        
        prompt = f"""
        Eres un asistente virtual profesional de LD Make Up. 
        Basa tus respuestas únicamente en esta información:
        
        {PROMPT_BASE}
        
        Instrucciones:
        - Responde de manera amable, profesional y con emojis moderados
        - Si la pregunta no está relacionada con la tienda, indica cortésmente que solo puedes ayudar con temas de LD Make Up
        - Para consultas muy específicas o personales, sugiere contactar al {CONFIG['STORE_PHONE']}
        - Mantén un tono cercano pero profesional
        - Si el cliente expresa emociones positivas (ej: "me encanta"), responde con gratitud y ofrece ayuda
        
        Pregunta del cliente: {mensaje_usuario}
        """
        
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return respuesta.text
    except Exception as e:
        print(f"Error en IA: {e}")
        return "Disculpa, hubo un error al procesar tu solicitud. Por favor intenta nuevamente."

def manejar_flujo_confirmacion(telefono_cliente, mensaje_usuario, session):
    """Maneja el flujo de confirmación de pedido"""
    if mensaje_usuario.upper() == "NO":
        enviar(telefono_cliente, TEMPLATES["ORDER_NOT_CONFIRMED"])
        if session['order_id']:
            enviar_a_admin(TEMPLATES["ORDER_NOT_CONFIRMED_ADMIN"], 
                          session['order_id'], telefono_cliente)
        session_manager.update_session_state(telefono_cliente, "IDLE")
        return True
    
    elif mensaje_usuario.upper() == "SALIR":
        enviar(telefono_cliente, "Has salido del proceso de confirmación.")
        session_manager.update_session_state(telefono_cliente, "IDLE")
        return True
    
    elif re.match(r'^#\w+', mensaje_usuario):
        order_id = mensaje_usuario[1:].strip()
        session_manager.confirm_order(telefono_cliente, order_id)
        enviar(telefono_cliente, TEMPLATES["ORDER_CONFIRMED"])
        enviar_a_admin(TEMPLATES["ORDER_CONFIRMED_ADMIN"], order_id, telefono_cliente)
        return True
    
    elif session['state'] == 'CONFIRMING':
        enviar(telefono_cliente, TEMPLATES["CONFIRM_PROMPT"])
        return True
    
    return False

def manejar_flujo_pago(telefono_cliente, mensaje_usuario, session):
    """Maneja el flujo de envío de comprobante de pago"""
    if not session.get('confirmed', False):
        enviar(telefono_cliente, TEMPLATES["NEED_CONFIRM_FIRST"])
        session_manager.update_session_state(telefono_cliente, "IDLE")
        return True
    
    if mensaje_usuario.upper() == "CANCELAR":
        enviar(telefono_cliente, TEMPLATES["ORDER_CANCELLED"])
        if session['order_id']:
            enviar_a_admin(TEMPLATES["PAYMENT_CANCELLED_ADMIN"], 
                          session['order_id'], telefono_cliente)
        session_manager.update_session_state(telefono_cliente, "IDLE")
        return True
    
    elif mensaje_usuario.upper() == "SALIR":
        enviar(telefono_cliente, "Has salido del proceso de pago.")
        session_manager.update_session_state(telefono_cliente, "IDLE")
        return True
    
    elif session['state'] == 'PAYING':
        enviar(telefono_cliente, TEMPLATES["PAYMENT_PROMPT"].format(
            admin_number=CONFIG["ADMIN_NUMBERS"][0]))
        if session['order_id']:
            enviar(telefono_cliente, TEMPLATES["PAYMENT_INSTRUCTIONS"].format(
                order_id=session['order_id']))
        return True
    
    return False

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        return "Error de autentificación."
    
    data = request.get_json()
    
    try:
        # Ignorar notificaciones de estado
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}), 200
        
        # Extraer datos del mensaje
        telefono_cliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        mensaje_usuario = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        timestamp = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
        
        # Obtener sesión del usuario
        session = session_manager.get_session(telefono_cliente)
        
        # Manejar saludo inicial
        if any(palabra in mensaje_usuario.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
            enviar(telefono_cliente, TEMPLATES["WELCOME"])
            return jsonify({"status": "success"}), 200
        
        # Manejar despedida
        if any(palabra in mensaje_usuario.lower() for palabra in ["adiós", "chao", "bye", "hasta luego", "nos vemos"]):
            enviar(telefono_cliente, TEMPLATES["GOODBYE"].format(
                store_address=CONFIG["STORE_ADDRESS"],
                store_hours=CONFIG["STORE_HOURS"]
            ))
            return jsonify({"status": "success"}), 200
        
        # Manejar salir (cerrar sesión)
        if mensaje_usuario.upper() == "SALIR":
            session_manager.close_session(telefono_cliente)
            enviar(telefono_cliente, TEMPLATES["SESSION_CLOSED"])
            return jsonify({"status": "success"}), 200
        
        # Manejar confirmación de pedido
        if mensaje_usuario.upper() == "CONFIRMAR":
            session_manager.update_session_state(telefono_cliente, "CONFIRMING")
            enviar(telefono_cliente, TEMPLATES["CONFIRM_PROMPT"])
            return jsonify({"status": "success"}), 200
        
        # Manejar envío de comprobante
        if mensaje_usuario.upper() == "MIPAGO":
            session_manager.update_session_state(telefono_cliente, "PAYING")
            enviar(telefono_cliente, TEMPLATES["PAYMENT_PROMPT"].format(
                admin_number=CONFIG["ADMIN_NUMBERS"][0]))
            if session.get('order_id'):
                enviar(telefono_cliente, TEMPLATES["PAYMENT_INSTRUCTIONS"].format(
                    order_id=session['order_id']))
            return jsonify({"status": "success"}), 200
        
        # Manejar flujos de confirmación y pago
        if manejar_flujo_confirmacion(telefono_cliente, mensaje_usuario, session):
            return jsonify({"status": "success"}), 200
        
        if manejar_flujo_pago(telefono_cliente, mensaje_usuario, session):
            return jsonify({"status": "success"}), 200
        
        # Manejar consultas no relacionadas
        unrelated_count = session_manager.increment_unrelated_queries(telefono_cliente)
        if unrelated_count >= 3:
            enviar(telefono_cliente, TEMPLATES["CONTACT_HUMAN"].format(
                store_phone=CONFIG["STORE_PHONE"]))
            return jsonify({"status": "success"}), 200
        elif unrelated_count > 1:
            enviar(telefono_cliente, TEMPLATES["UNRELATED_QUERY"])
            return jsonify({"status": "success"}), 200
        
        # Procesar con IA
        respuesta_ia = procesar_ia(mensaje_usuario, telefono_cliente)
        enviar(telefono_cliente, respuesta_ia)
        
        return jsonify({"status": "success"}), 200
    
    except Exception as e:
        print(f"Error general: {e}")
        return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)