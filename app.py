from flask import Flask, request, jsonify
from sessions import SessionManager
from whatsapp import WhatsAppAPI
from gemini import GeminiAI
from templates import *
import os

app = Flask(__name__)
sessions = SessionManager()
whatsapp = WhatsAppAPI()

# Cargar prompt
with open('prompt.txt', 'r', encoding='utf-8') as f:
    PROMPT = f.read()

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
    
    # Verificar si es notificación de estado
    if "messages" not in value:
        return jsonify({"status": "success"}), 200
    
    message = value["messages"][0]
    user_id = message["from"]
    user_message = message["text"]["body"].lower().strip()
    
    # Manejar flujos primero
    current_flow = sessions.get_flow(user_id)
    
    if current_flow == "confirmar":
        return handle_confirmar_flow(user_id, user_message)
    elif current_flow == "mipago":
        return handle_mipago_flow(user_id, user_message)
    elif user_message == "confirmar":
        return start_confirmar_flow(user_id)
    elif user_message == "mipago":
        return start_mipago_flow(user_id)
    else:
        return handle_normal_conversation(user_id, user_message)

def handle_confirmar_flow(user_id, user_message):
    if user_message == "salir":
        sessions.clear_flow(user_id)
        whatsapp.send_message(user_id, SALIR_CONFIRMAR)
        return jsonify({"status": "success"}), 200
    
    if not sessions.get_data(user_id, "pedido_id"):
        sessions.set_data(user_id, "pedido_id", user_message)
        whatsapp.send_message(user_id, CONFIRMAR_OPCION.format(user_message))
        return jsonify({"status": "success"}), 200
    
    if user_message == "si":
        pedido_id = sessions.get_data(user_id, "pedido_id")
        whatsapp.send_message(user_id, PEDIDO_CONFIRMADO.format(pedido_id))
        whatsapp.send_admin_notification(ADMIN_CONFIRMADO.format(pedido_id))
        sessions.clear_flow(user_id)
    elif user_message == "no":
        pedido_id = sessions.get_data(user_id, "pedido_id")
        whatsapp.send_message(user_id, PEDIDO_CANCELADO.format(pedido_id))
        whatsapp.send_admin_notification(ADMIN_CANCELADO.format(pedido_id))
        sessions.clear_flow(user_id)
    
    return jsonify({"status": "success"}), 200

def handle_mipago_flow(user_id, user_message):
    pedido_id = sessions.get_data(user_id, "pedido_id")
    whatsapp.send_message(user_id, PEDIR_COMPROBANTE.format(pedido_id))
    sessions.clear_flow(user_id)
    return jsonify({"status": "success"}), 200

def start_confirmar_flow(user_id):
    sessions.set_flow(user_id, "confirmar")
    whatsapp.send_message(user_id, PEDIR_ID)
    return jsonify({"status": "success"}), 200

def start_mipago_flow(user_id):
    if sessions.get_data(user_id, "pedido_id"):
        sessions.set_flow(user_id, "mipago")
        pedido_id = sessions.get_data(user_id, "pedido_id")
        whatsapp.send_message(user_id, PEDIR_COMPROBANTE.format(pedido_id))
        sessions.clear_flow(user_id)
    else:
        whatsapp.send_message(user_id, ERROR_MIPAGO)
    return jsonify({"status": "success"}), 200

def handle_normal_conversation(user_id, user_message):
    # Verificar si es primer mensaje
    if not sessions.get_session(user_id).get("has_welcome"):
        whatsapp.send_message(user_id, BIENVENIDA)
        sessions.get_session(user_id)["has_welcome"] = True
        return jsonify({"status": "success"}), 200
    
    # Generar respuesta con IA
    response = GeminiAI.generate_response(PROMPT, user_message)
    whatsapp.send_message(user_id, response)
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)