from flask import Flask, request, jsonify
from session_manager import SessionManager
from gemini_client import GeminiClient
from whatsapp_api import WhatsAppAPI
from message_templates import *

app = Flask(__name__)

# Configuration
WHATSAPP_TOKEN = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
WHATSAPP_NUMBER_ID = '730238483499494'
ADMIN_NUMBER = '584241220797'
GEMINI_API_KEY = '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'

# Initialize components
session_manager = SessionManager()
gemini_client = GeminiClient(GEMINI_API_KEY)
whatsapp_api = WhatsAppAPI(WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID)

@app.route("/webhook/", methods=["GET", "POST"])
def webhook_whatsapp():
    # Verify webhook
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        return "Error de autentificación", 403
    
    # Process incoming message
    data = request.get_json()
    
    try:
        # Skip non-message events
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}), 200
            
        # Extract message info
        message_data = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_id = message_data['from']
        message = message_data['text']['body']
        
        # Get user session
        session = session_manager.get_session(user_id)
        session_manager.log_message(user_id, message)
        
        # Check if user is in a flow
        current_flow = session['flow']
        
        # Handle confirmation flow
        if current_flow == 'confirmar':
            return handle_confirm_flow(user_id, message)
            
        # Handle payment flow
        if message.lower() == 'mipago':
            return handle_payment_flow(user_id)
            
        # Handle confirmation command
        if message.lower() == 'confirmar':
            session_manager.update_flow(user_id, 'confirmar')
            whatsapp_api.send_message(user_id, get_confirm_start_template())
            return jsonify({"status": "success"}), 200
            
        # Handle greetings
        greetings = ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches"]
        if any(greeting in message.lower() for greeting in greetings):
            whatsapp_api.send_message(user_id, WELCOME_TEMPLATE)
            return jsonify({"status": "success"}), 200
            
        # Handle goodbyes
        goodbyes = ["adiós", "chao", "bye", "hasta luego", "nos vemos"]
        if any(goodbye in message.lower() for goodbye in goodbyes):
            whatsapp_api.send_message(user_id, GOODBYE_TEMPLATE)
            return jsonify({"status": "success"}), 200
            
        # Default: Use AI to respond
        ai_response = gemini_client.generate_response(message)
        whatsapp_api.send_message(user_id, ai_response)
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error processing message: {e}")
        whatsapp_api.send_message(user_id, "Disculpas, hubo un error procesando tu mensaje. Por favor intenta nuevamente.")
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_confirm_flow(user_id, message):
    """Handle the confirmation flow steps"""
    session = session_manager.get_session(user_id)
    flow_data = session['flow_data']
    
    # Step 1: Starting confirmation - get order ID
    if 'pedido_id' not in flow_data:
        if message.lower() == 'salir':
            session_manager.clear_flow(user_id)
            whatsapp_api.send_message(user_id, get_confirm_exit_template())
            return jsonify({"status": "success"}), 200
            
        flow_data['pedido_id'] = message
        whatsapp_api.send_message(user_id, get_confirm_id_received_template(message))
        return jsonify({"status": "success"}), 200
    
    # Step 2: Confirmation choice
    if message.lower() == 'si':
        # Send success messages
        pedido_id = flow_data['pedido_id']
        whatsapp_api.send_message(user_id, get_confirm_success_template(pedido_id))
        whatsapp_api.send_admin_notification(ADMIN_NUMBER, get_admin_confirm_notification(pedido_id))
        session_manager.clear_flow(user_id)
        return jsonify({"status": "success"}), 200
        
    elif message.lower() == 'no':
        # Send cancel messages
        pedido_id = flow_data['pedido_id']
        whatsapp_api.send_message(user_id, get_confirm_cancel_template(pedido_id))
        whatsapp_api.send_admin_notification(ADMIN_NUMBER, get_admin_cancel_notification(pedido_id))
        session_manager.clear_flow(user_id)
        return jsonify({"status": "success"}), 200
        
    elif message.lower() == 'salir':
        session_manager.clear_flow(user_id)
        whatsapp_api.send_message(user_id, get_confirm_exit_template())
        return jsonify({"status": "success"}), 200
        
    else:
        whatsapp_api.send_message(user_id, "Por favor responda con *si*, *no* o *salir*.")
        return jsonify({"status": "success"}), 200

def handle_payment_flow(user_id):
    """Handle the payment flow"""
    session = session_manager.get_session(user_id)
    
    # Check if user completed confirmation flow
    if 'pedido_id' not in session['flow_data']:
        whatsapp_api.send_message(user_id, get_payment_not_ready_template())
        return jsonify({"status": "success"}), 200
        
    # Send instructions and exit flow
    whatsapp_api.send_message(user_id, get_payment_instructions_template())
    session_manager.clear_flow(user_id)
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)