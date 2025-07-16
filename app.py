from flask import Flask, jsonify, request
from whatsapp_api import WhatsAppAPI
from gemini_client import GeminiClient
from sessions import SessionManager
from flows import FlowManager
from templates import (
    WELCOME_TEMPLATE,
    GOODBYE_TEMPLATE,
    NOTIFICATIONS_INFO
)
import os
import time

app = Flask(__name__)

# Initialize components
whatsapp = WhatsAppAPI(
    token=os.getenv('WHATSAPP_TOKEN'),
    phone_id=os.getenv('WHATSAPP_PHONE_ID')
)
gemini = GeminiClient(api_key=os.getenv('GEMINI_API_KEY'))
sessions = SessionManager()
flows = FlowManager(whatsapp, sessions)

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # Verify webhook
    if request.method == "GET":
        if request.args.get('hub.verify_token') == os.getenv('VERIFY_TOKEN'):
            return request.args.get('hub.challenge')
        return "Authentication failed", 403
    
    # Process incoming message
    data = request.get_json()
    
    # Skip non-message events
    try:
        message_data = data['entry'][0]['changes'][0]['value']
        if 'messages' not in message_data:
            return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error"}), 400
    
    # Extract message info
    message = message_data['messages'][0]
    sender = message['from']
    text = message['text']['body'].lower().strip()
    timestamp = message['timestamp']
    
    # Get or create session
    session = sessions.get_session(sender)
    
    # Check if user is in a flow
    if session.get('current_flow'):
        flows.handle_flow(sender, text, session)
        return jsonify({"status": "success"}), 200
    
    # Handle first message
    if not session.get('initialized'):
        whatsapp.send_message(sender, WELCOME_TEMPLATE)
        session['initialized'] = True
        sessions.save_session(sender, session)
        return jsonify({"status": "success"}), 200
    
    # Handle special commands
    if text in ['confirmar', 'mipago']:
        flows.handle_flow(sender, text, session)
        return jsonify({"status": "success"}), 200
    
    # Handle goodbye messages
    if any(word in text for word in ['adiós', 'chao', 'bye', 'hasta luego', 'nos vemos']):
        whatsapp.send_message(sender, GOODBYE_TEMPLATE)
        return jsonify({"status": "success"}), 200
    
    # Handle notifications info
    if any(word in text for word in ['notificaciones', 'estado', 'seguimiento', 'tracking']):
        whatsapp.send_message(sender, NOTIFICATIONS_INFO)
        return jsonify({"status": "success"}), 200
    
    # Handle with Gemini AI
    try:
        response = gemini.generate_response(text, session)
        whatsapp.send_message(sender, response)
    except Exception as e:
        whatsapp.send_message(sender, "Disculpas, hubo un error. Por favor contacta al +54 9 3813 02-1066 para asistencia.")
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)