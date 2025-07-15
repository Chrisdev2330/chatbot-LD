from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
import os
import time
from config import CONFIG
from templates import TEMPLATES
from session_manager import get_session, close_session, reset_unrelated_queries
from static_flows import handle_confirm_flow, handle_payment_flow
import requests

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])

# Cargar prompt
with open('prompts/prompt.txt', 'r', encoding='utf-8') as f:
    PROMPT_BASE = f.read()

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        if request.args.get('hub.verify_token') == CONFIG["VERIFY_TOKEN"]:
            return request.args.get('hub.challenge')
        return "Error de autentificación."
    
    # RECIBIMOS TODOS LOS DATOS ENVIADOS VIA JSON
    data = request.get_json()
    
    # Verificar si es una notificación de cambio de estado
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}, 200)
    except:
        return jsonify({"status": "error"}, 400)
    
    # EXTRAEMOS EL NUMERO DE TELEFONO Y EL MENSAJE
    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].lower()
    
    # Obtener sesión del usuario
    session = get_session(telefonoCliente)
    
    # Verificar si es el primer mensaje para enviar bienvenida
    if any(palabra in mensaje for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, TEMPLATES["WELCOME"])
        reset_unrelated_queries(telefonoCliente)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un mensaje de despedida
    if any(palabra in mensaje for palabra in ["adiós", "chao", "bye", "hasta luego", "nos vemos", "salir"]):
        if "salir" in mensaje:
            close_session(telefonoCliente)
        enviar(telefonoCliente, TEMPLATES["GOODBYE"])
        return jsonify({"status": "success"}, 200)
    
    # Manejar flujos estáticos
    if "confirmar" in mensaje:
        handle_confirm_flow(telefonoCliente, mensaje, session)
        return jsonify({"status": "success"}, 200)
    
    if "mipago" in mensaje:
        handle_payment_flow(telefonoCliente, session)
        return jsonify({"status": "success"}, 200)
    
    # Si está esperando ID de pedido
    if session.get('state') == 'awaiting_order_id':
        handle_confirm_flow(telefonoCliente, mensaje, session)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un agradecimiento
    if any(palabra in mensaje for palabra in ["gracias", "muchas gracias", "thanks", "thank you"]):
        enviar(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        reset_unrelated_queries(telefonoCliente)
        return jsonify({"status": "success"}, 200)
    
    # Verificar preguntas sobre notificaciones
    if any(palabra in mensaje for palabra in ["notificaciones", "estado de pedido", "seguimiento", "tracking"]):
        enviar(telefonoCliente, TEMPLATES["NOTIFICATIONS"])
        reset_unrelated_queries(telefonoCliente)
        return jsonify({"status": "success"}, 200)
    
    # Usar IA para responder
    try:
        # Construir prompt contextual
        prompt = f"{PROMPT_BASE}\n\nContexto:\n- Estado sesión: {session['state']}\n- Pedido confirmado: {session.get('confirmed_order', False)}\n\nPregunta: {mensaje}"
        
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        respuesta_texto = respuesta.text
        
        # Verificar si la respuesta es relevante
        if "no está relacionada" in respuesta_texto.lower() or "no tengo información" in respuesta_texto.lower():
            session['unrelated_queries'] += 1
            
            if session['unrelated_queries'] >= 3:
                enviar(telefonoCliente, TEMPLATES["HUMAN_SUPPORT"])
                session['unrelated_queries'] = 0
            else:
                enviar(telefonoCliente, TEMPLATES["UNRELATED_QUERY"])
        else:
            enviar(telefonoCliente, respuesta_texto)
            reset_unrelated_queries(telefonoCliente)
            
    except Exception as e:
        print(f"Error con Gemini: {e}")
        enviar(telefonoCliente, "Disculpa, hubo un error. Por favor intenta nuevamente o contacta al +54 9 3813 02-1066 para asistencia.")

    return jsonify({"status": "success"}, 200)

def enviar(telefonoRecibe, respuesta):
    mensajeWa = WhatsApp(CONFIG["WHATSAPP_TOKEN"], CONFIG["PHONE_NUMBER_ID"])
    mensajeWa.send_message(respuesta, telefonoRecibe)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)