from flask import Flask, request, jsonify
from sessions import session_manager
from flows import handle_confirmar_flow, handle_mipago_flow
from templates import welcome_template, goodbye_template
from gemini_client import gemini_client
from whatsapp import send_message
import time

app = Flask(__name__)

@app.route("/webhook/", methods=["GET", "POST"])
def webhook():
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
        
        # Handle flows
        if message.lower() == 'confirmar':
            session_manager.update_flow(user_id, 'confirmar')
            return jsonify({"status": "success"}), 200
            
        elif message.lower() == 'mipago':
            session_manager.update_flow(user_id, 'mipago')
            return jsonify({"status": "success"}), 200
            
        elif current_flow == 'confirmar':
            response = handle_confirmar_flow(user_id, message)
            send_message(user_id, response)
            return jsonify({"status": "success"}), 200
            
        elif current_flow == 'mipago':
            response = handle_mipago_flow(user_id)
            send_message(user_id, response)
            return jsonify({"status": "success"}), 200
            
        # Handle greetings
        greetings = ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches"]
        if any(greeting in message.lower() for greeting in greetings):
            send_message(user_id, welcome_template())
            return jsonify({"status": "success"}), 200
            
        # Handle goodbyes
        goodbyes = ["adiós", "chao", "bye", "hasta luego", "nos vemos"]
        if any(goodbye in message.lower() for goodbye in goodbyes):
            send_message(user_id, goodbye_template())
            return jsonify({"status": "success"}), 200
            
        # Default: Use AI to respond
        ai_response = gemini_client.generate_response(message)
        send_message(user_id, ai_response)
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error processing message: {e}")
        send_message(user_id, "Disculpas, hubo un error procesando tu mensaje. Por favor intenta nuevamente.")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)