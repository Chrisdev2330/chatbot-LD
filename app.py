from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
from config import CONFIG
from templates import *
from session_manager import session_manager
from flows import handle_flows
import os

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

# Cargar prompt
with open('prompt.txt', 'r', encoding='utf-8') as file:
    PROMPT_BASE = file.read()

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        if request.args.get('hub.verify_token') == CONFIG["VERIFY_TOKEN"]:
            return request.args.get('hub.challenge')
        else:
            return "Error de autentificacion."
    
    # RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data = request.get_json()
    
    # Verificar si es una notificación de cambio de estado (no mensaje de usuario)
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}, 200)
    except:
        return jsonify({"status": "error"}, 400)
    
    # EXTRAEMOS EL NUMERO DE TELEFONO Y EL MENSAJE
    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    
    # Manejar flujos estáticos primero
    flow_response = handle_flows(telefonoCliente, mensaje)
    if flow_response:
        return flow_response
    
    # Obtener sesión del usuario
    session = session_manager.get_session(telefonoCliente)
    
    # Verificar si es el primer mensaje para enviar bienvenida
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, PLANTILLA_BIENVENIDA)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un mensaje de despedida
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["despedida"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        session_manager.reset_session(telefonoCliente)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un agradecimiento
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        enviar(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        return jsonify({"status": "success"}, 200)
    
    # Verificar preguntas sobre notificaciones
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["notificaciones"]):
        enviar(telefonoCliente, MENSAJE_NOTIFICACIONES)
        return jsonify({"status": "success"}, 200)
    
    # Manejar consultas con IA
    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""{PROMPT_BASE}
            
            Contexto adicional:
            - Estado actual del cliente: {session['state']}
            - Pedido confirmado: {'Sí' if session.get('confirmed_order') else 'No'}
            
            Pregunta del cliente: {mensaje}
            
            Instrucciones:
            1. Responde de manera profesional pero cálida
            2. Usa emojis relevantes (máximo 2 por mensaje)
            3. Si la pregunta no está relacionada con LD Make Up, sugiere amablemente temas relacionados
            4. Para consultas muy personales o complejas, recomienda contactar al número de atención
            """
        )
        
        # Verificar si la respuesta está fuera de contexto
        if "no está relacionada" in respuesta.text.lower() or "no tengo información" in respuesta.text.lower():
            session_manager.increment_attempts(telefonoCliente)
            if session_manager.get_session(telefonoCliente)['attempts'] >= 3:
                enviar(telefonoCliente, PLANTILLA_CONTACTO_HUMANO)
                session_manager.reset_attempts(telefonoCliente)
            else:
                enviar(telefonoCliente, PLANTILLA_FUERA_CONTEXTO)
        else:
            session_manager.reset_attempts(telefonoCliente)
            enviar(telefonoCliente, respuesta.text)
    except Exception as e:
        print(f"Error con Gemini: {e}")
        enviar(telefonoCliente, "Disculpas, hubo un error procesando tu solicitud. Por favor intenta nuevamente.")
    
    return jsonify({"status": "success"}, 200)

def enviar(telefonoRecibe, respuesta):
    mensajeWa = WhatsApp(CONFIG["WHATSAPP_TOKEN"], CONFIG["WHATSAPP_NUMBER_ID"])
    mensajeWa.send_message(respuesta, telefonoRecibe)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)