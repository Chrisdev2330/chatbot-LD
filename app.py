from flask import Flask, request, jsonify
from sessions import SessionManager
from whasatpp import WhatsAppAPI
from gemini import GeminiAI
from templates import *
import time

app = Flask(__name__)
sessions = SessionManager()
whatsapp = WhatsAppAPI()

# Cargar prompt
with open('prompt.txt', 'r', encoding='utf-8') as f:
    PROMPT = f.read()

def handle_confirmar_flow(user_id, user_message):
    session = sessions.get_session(user_id)
    
    if user_message == "salir":
        sessions.clear_flow(user_id)
        whatsapp.send_message(user_id, SALIR_CONFIRMAR)
        return True
    
    if not session['data'].get('pedido_id'):
        sessions.set_data(user_id, 'pedido_id', user_message)
        whatsapp.send_message(user_id, CONFIRMAR_OPCION.format(user_message))
        return False
    
    if user_message == "si":
        pedido_id = session['data']['pedido_id']
        whatsapp.send_message(user_id, PEDIDO_CONFIRMADO.format(pedido_id))
        whatsapp.send_admin_notification(ADMIN_CONFIRMADO.format(pedido_id))
        sessions.clear_flow(user_id)
        return True
    elif user_message == "no":
        pedido_id = session['data']['pedido_id']
        whatsapp.send_message(user_id, PEDIDO_CANCELADO.format(pedido_id))
        whatsapp.send_admin_notification(ADMIN_CANCELADO.format(pedido_id))
        sessions.clear_flow(user_id)
        return True
    
    return False

def handle_mipago_flow(user_id):
    pedido_id = sessions.get_data(user_id, 'pedido_id')
    if pedido_id:
        whatsapp.send_message(user_id, PEDIR_COMPROBANTE.format(pedido_id))
        sessions.clear_flow(user_id)
        return True
    else:
        whatsapp.send_message(user_id, ERROR_MIPAGO)
        return False

@app.route("/webhook/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == "HolaNovato":
            return request.args.get("hub.challenge")
        return "Error de autenticación", 403

    data = request.get_json()
    entry = data.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    
    if "messages" not in value:
        return jsonify({"status": "success"}), 200
    
    message = value["messages"][0]
    user_id = message["from"]
    user_message = message["text"]["body"].lower().strip()
    
    # Manejar flujos primero
    current_flow = sessions.get_flow(user_id)
    
    if current_flow == "confirmar":
        flow_completed = handle_confirmar_flow(user_id, user_message)
        if flow_completed:
            return jsonify({"status": "success"}), 200
    elif user_message == "mipago":
        if sessions.get_data(user_id, 'pedido_id'):
            handle_mipago_flow(user_id)
            return jsonify({"status": "success"}), 200
        else:
            whatsapp.send_message(user_id, ERROR_MIPAGO)
            return jsonify({"status": "success"}), 200
    
    # Si no está en flujo o ya salió
    if not sessions.get_flow(user_id):
        if user_message == "confirmar":
            sessions.set_flow(user_id, "confirmar")
            whatsapp.send_message(user_id, PEDIR_ID)
            return jsonify({"status": "success"}), 200
        
        # Conversación normal con IA
        if not sessions.get_session(user_id).get("has_welcome"):
            whatsapp.send_message(user_id, BIENVENIDA)
            sessions.get_session(user_id)["has_welcome"] = True
        else:
            response = GeminiAI.generate_response(PROMPT, user_message)
            whatsapp.send_message(user_id, response)
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)