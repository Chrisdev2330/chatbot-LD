from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
import os
import requests
from config import CONFIG
from templates import *
from session_manager import SessionManager
import re

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

# Configuración de WhatsApp
mensajeWa = WhatsApp(CONFIG["WHATSAPP_TOKEN"], CONFIG["WHATSAPP_PHONE_ID"])

# Manejo de sesiones
session_manager = SessionManager(CONFIG["SESSION_TIMEOUT"])

# Cargar prompt de la IA
with open('prompt.txt', 'r', encoding='utf-8') as f:
    PROMPT_IA = f.read()

def enviar(telefonoRecibe, respuesta):
    mensajeWa.send_message(respuesta, telefonoRecibe)

def enviar_a_admin(mensaje, pedido_id=None):
    for admin_number in CONFIG["ADMIN_NUMBERS"]:
        url = f"https://graph.facebook.com/v18.0/{CONFIG['WHATSAPP_PHONE_ID']}/messages"
        headers = {
            'Authorization': f'Bearer {CONFIG["WHATSAPP_TOKEN"]}',
            'Content-Type': 'application/json'
        }
        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": admin_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": f"Notificación de LD Make Up Bot:\n{mensaje}\n{'ID Pedido: ' + pedido_id if pedido_id else ''}"
            }
        }
        requests.post(url, headers=headers, json=body)

def es_fuera_de_contexto(mensaje):
    palabras_clave = ["maquillaje", "makeup", "uñas", "pestañas", "ld", "luciana", "díaz", 
                     "precio", "producto", "compra", "pedido", "envío", "local", "horario",
                     "pago", "transferencia", "efectivo", "mercadopago", "mayorista", "minorista"]
    
    mensaje_lower = mensaje.lower()
    return not any(palabra in mensaje_lower for palabra in palabras_clave)

def necesita_soporte_humano(mensaje):
    palabras_soporte = ["soporte", "humano", "representante", "asesor", "hablar con alguien",
                       "problema", "error", "reclamo", "queja", "no funciona", "incorrecto",
                       "equivocado", "no es lo que pedí"]
    
    mensaje_lower = mensaje.lower()
    return any(palabra in mensaje_lower for palabra in palabras_soporte)

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == CONFIG["VERIFY_TOKEN"]:
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
    idWA = data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    timestamp = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    
    # Obtener sesión del usuario
    session = session_manager.get_session(telefonoCliente)
    session_manager.add_to_history(telefonoCliente, mensaje)
    
    # Verificar si es el primer mensaje para enviar bienvenida
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, PLANTILLA_BIENVENIDA)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un mensaje de despedida
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["despedida"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        session_manager.close_session(telefonoCliente)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es para salir/cerrar sesión
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["salir"]):
        enviar(telefonoCliente, "✅ Sesión cerrada. ¡Esperamos verte pronto de nuevo en LD Make Up! 💖")
        session_manager.close_session(telefonoCliente)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un agradecimiento
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        enviar(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        return jsonify({"status": "success"}, 200)
    
    # Verificar preguntas sobre notificaciones
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["notificaciones"]):
        enviar(telefonoCliente, MENSAJE_NOTIFICACIONES)
        return jsonify({"status": "success"}, 200)
    
    # Flujo para confirmar pedido
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["confirmar"]):
        # Extraer ID del pedido si está en el mensaje
        pedido_id = re.search(r'confirmar\s+(.+)', mensaje.lower())
        if pedido_id:
            pedido_id = pedido_id.group(1).strip().upper()
            session_manager.update_session(telefonoCliente, {
                'pedido_confirmado': True,
                'pedido_id': pedido_id
            })
            enviar(telefonoCliente, PLANTILLA_PEDIDO_CONFIRMADO.format(pedido_id=pedido_id))
            enviar_a_admin(f"El cliente {telefonoCliente} ha confirmado el pedido", pedido_id)
        else:
            enviar(telefonoCliente, PLANTILLA_CONFIRMAR_PEDIDO)
        return jsonify({"status": "success"}, 200)
    
    # Flujo para enviar comprobante de pago
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["mipago"]):
        if session['data']['pedido_confirmado'] and session['data']['pedido_id']:
            admin_number = CONFIG["ADMIN_NUMBERS"][0]  # Primer número admin
            enviar(telefonoCliente, PLANTILLA_ENVIAR_COMPROBANTE.format(admin_number=admin_number))
            enviar_a_admin(f"El cliente {telefonoCliente} solicita enviar comprobante para el pedido {session['data']['pedido_id']}")
        else:
            enviar(telefonoCliente, PLANTILLA_CONFIRMAR_PRIMERO)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si el mensaje está fuera de contexto
    if es_fuera_de_contexto(mensaje):
        admin_number = CONFIG["ADMIN_NUMBERS"][0]
        enviar(telefonoCliente, PLANTILLA_FUERA_CONTEXTO.format(admin_number=admin_number))
        return jsonify({"status": "success"}, 200)
    
    # Verificar si necesita soporte humano
    if necesita_soporte_humano(mensaje):
        admin_number = CONFIG["ADMIN_NUMBERS"][0]
        enviar(telefonoCliente, PLANTILLA_CONTACTO_SOPORTE.format(admin_number=admin_number))
        return jsonify({"status": "success"}, 200)
    
    # Si no es ninguno de los casos anteriores, usar IA
    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""{PROMPT_IA}
            
            Historial reciente del cliente:
            {session['data']['historial'][-3:] if session['data']['historial'] else 'No hay historial reciente'}
            
            Pregunta actual: {mensaje}
            """
        )
        enviar(telefonoCliente, respuesta.text)
    except Exception as e:
        enviar(telefonoCliente, "Disculpas, hubo un error. Por favor contacta al +54 9 3813 02-1066 para asistencia.")

    return jsonify({"status": "success"}, 200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)