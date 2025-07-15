from flask import Flask, jsonify, request
from google import genai
import os
import time
from config import CONFIG
from templates import TEMPLATES
from session_manager import SessionManager
from flows import handle_confirm_flow, handle_payment_flow
from whatsapp import send_whatsapp_message, send_admin_notification

app = Flask(__name__)

# Initialize services
session_manager = SessionManager()
cliente = genai.Client(api_key=CONFIG['GEMINI_API_KEY'])

# Load AI prompt
with open('prompt.txt', 'r', encoding='utf-8') as f:
    AI_PROMPT = f.read()

# Conversation flows
FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking"]
}

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # Handle verification
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        return "Error de autentificacion."
    
    # Handle incoming messages
    data = request.get_json()
    
    # Skip status notifications
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error"}, 400)
    
    # Extract message data
    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    
    # Get or create session
    session = session_manager.get_session(telefonoCliente)
    session_manager.update_session(telefonoCliente)
    
    # Check if in any flow
    current_flow = session_manager.get_current_flow(telefonoCliente)
    if current_flow:
        if current_flow['flow_type'] == 'confirmar':
            return handle_confirm_flow(telefonoCliente, mensaje)
        elif current_flow['flow_type'] == 'mipago':
            return handle_payment_flow(telefonoCliente, mensaje)
    
    # Handle static flows
    if mensaje.lower() == 'confirmar':
        session_manager.start_flow(telefonoCliente, 'confirmar')
        send_whatsapp_message(telefonoCliente, TEMPLATES['confirm_prompt'])
        return jsonify({"status": "success"}), 200
    
    elif mensaje.lower() == 'mipago':
        if session_manager.get_confirmed_order(telefonoCliente):
            session_manager.start_flow(telefonoCliente, 'mipago')
            send_whatsapp_message(telefonoCliente, TEMPLATES['payment_prompt'].format(
                admin_number=CONFIG['ADMIN_NUMBERS'][0]
            ))
        else:
            send_whatsapp_message(telefonoCliente, TEMPLATES['missing_confirmation'])
        return jsonify({"status": "success"}), 200
    
    elif mensaje.lower() == 'salir':
        confirmed_order = session_manager.clear_session(telefonoCliente)
        if confirmed_order:
            # Notify admin about session close with pending order
            admin_message = f"⚠️ El cliente {telefonoCliente} cerró sesión con pedido pendiente:\nID: {confirmed_order}"
            send_admin_notification(admin_message)
        send_whatsapp_message(telefonoCliente, TEMPLATES['goodbye'])
        return jsonify({"status": "success"}), 200
    
    # Handle greetings
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        send_whatsapp_message(telefonoCliente, TEMPLATES['welcome'])
        return jsonify({"status": "success"}), 200
    
    # Handle thanks
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        send_whatsapp_message(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        return jsonify({"status": "success"}), 200
    
    # Handle goodbye
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["despedida"]):
        send_whatsapp_message(telefonoCliente, TEMPLATES['goodbye'])
        return jsonify({"status": "success"}), 200
    
    # Handle notifications
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["notificaciones"]):
        send_whatsapp_message(telefonoCliente, TEMPLATES['notifications'])
        return jsonify({"status": "success"}), 200
    
    # Check for unrelated messages
    if session['unrelated_attempts'] >= CONFIG['MAX_UNRELATED_ATTEMPTS']:
        send_whatsapp_message(telefonoCliente, TEMPLATES['human_assistance'].format(
            admin_number=CONFIG['ADMIN_NUMBERS'][0]
        ))
        return jsonify({"status": "success"}), 200
    
    # Use AI for response
    try:
        # Check if message seems unrelated
        response = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Eres un asistente de LD Make Up. Analiza si esta pregunta está relacionada con maquillaje, belleza o la tienda:
            Pregunta: {mensaje}
            
            Responde SOLO con 'si' o 'no'. No agregues explicaciones.
            """
        )
        
        if response.text.lower().strip() == 'no':
            session_manager.increment_unrelated_attempts(telefonoCliente)
            if session['unrelated_attempts'] < CONFIG['MAX_UNRELATED_ATTEMPTS']:
                send_whatsapp_message(telefonoCliente, TEMPLATES['unrelated_message'])
            else:
                send_whatsapp_message(telefonoCliente, TEMPLATES['human_assistance'].format(
                    admin_number=CONFIG['ADMIN_NUMBERS'][0]
                ))
            return jsonify({"status": "success"}), 200
        
        # If related, generate full response
        response = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            {AI_PROMPT}
            
            Instrucciones:
            1. Responde de manera profesional pero amigable
            2. Usa emojis relevantes pero con moderación
            3. Si la pregunta no está en el prompt pero puedes inferirla, responde basado en la información disponible
            4. Mantén respuestas concisas pero completas
            
            Pregunta: {mensaje}
            """
        )
        send_whatsapp_message(telefonoCliente, response.text)
        session_manager.reset_unrelated_attempts(telefonoCliente)
        
    except Exception as e:
        send_whatsapp_message(telefonoCliente, "Disculpas, hubo un error. Por favor contacta al +54 9 3813 02-1066 para asistencia.")
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)