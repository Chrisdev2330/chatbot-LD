from flask import jsonify
from config import CONFIG
from templates import *
from session_manager import session_manager
from heyoo import WhatsApp

whatsapp = WhatsApp(CONFIG["WHATSAPP_TOKEN"], CONFIG["WHATSAPP_NUMBER_ID"])

def handle_flows(user_id, message):
    session = session_manager.get_session(user_id)
    
    # Comandos principales que inician flujos
    if any(word in message.lower() for word in FLUJO_CONVERSACION["confirmar"]):
        session_manager.update_session_state(user_id, "confirmar")
        whatsapp.send_message(FLUJO_CONFIRMAR, user_id)
        return jsonify({"status": "success"}), 200
    
    elif any(word in message.lower() for word in FLUJO_CONVERSACION["mipago"]):
        if session.get('confirmed_order'):
            session_manager.update_session_state(user_id, "mipago")
            whatsapp.send_message(FLUJO_MIPAGO, user_id)
        else:
            whatsapp.send_message(PLANTILLA_NO_CONFIRMADO, user_id)
        return jsonify({"status": "success"}), 200
    
    elif any(word in message.lower() for word in FLUJO_CONVERSACION["salir"]):
        session_manager.reset_session(user_id)
        whatsapp.send_message(PLANTILLA_DESPEDIDA, user_id)
        return jsonify({"status": "success"}), 200
    
    elif any(word in message.lower() for word in FLUJO_CONVERSACION["cancelar"]):
        order_id = session_manager.cancel_order(user_id)
        if order_id and session['state'] in ['confirmar', 'mipago']:
            whatsapp.send_message(PLANTILLA_CANCELACION_CLIENTE, user_id)
            whatsapp.send_message(PLANTILLA_CANCELACION_ADMIN(order_id), CONFIG["ADMIN_NUMBERS"][0])
        session_manager.reset_session(user_id)
        return jsonify({"status": "success"}), 200
    
    # Manejo de estados dentro de los flujos
    if session['state'] == "confirmar":
        return handle_confirm_flow(user_id, message)
    elif session['state'] == "mipago":
        return handle_mipago_flow(user_id, message)
    
    return None

def handle_confirm_flow(user_id, message):
    if any(word in message.lower() for word in FLUJO_CONVERSACION["regresar"]):
        session_manager.reset_session(user_id)
        whatsapp.send_message(PLANTILLA_BIENVENIDA, user_id)
        return jsonify({"status": "success"}), 200
    
    # Validar formato del ID (debe empezar con #)
    if message.startswith('#') and len(message) > 1:
        order_id = message[1:].strip()
        session_manager.confirm_order(user_id, order_id)
        
        # Enviar confirmación al cliente
        whatsapp.send_message(PLANTILLA_CONFIRMACION_CLIENTE(order_id), user_id)
        
        # Notificar al administrador
        whatsapp.send_message(PLANTILLA_CONFIRMACION_ADMIN(order_id), CONFIG["ADMIN_NUMBERS"][0])
        
        # Volver al estado principal
        session_manager.update_session_state(user_id, "main")
    else:
        whatsapp.send_message(PLANTILLA_FORMATO_INCORRECTO, user_id)
    
    return jsonify({"status": "success"}), 200

def handle_mipago_flow(user_id, message):
    if any(word in message.lower() for word in FLUJO_CONVERSACION["regresar"]):
        session_manager.update_session_state(user_id, "main")
        whatsapp.send_message("Has vuelto al menú principal. ¿En qué más puedo ayudarte?", user_id)
        return jsonify({"status": "success"}), 200
    
    session = session_manager.get_session(user_id)
    order_id = session.get('order_id', 'ID no proporcionado')
    
    # Aquí podrías validar el comprobante si lo deseas
    whatsapp.send_message(f"Gracias por enviar tu comprobante para el pedido {order_id}. Lo hemos recibido y lo estamos procesando.", user_id)
    
    # Notificar al administrador
    whatsapp.send_message(f"El cliente ha enviado un comprobante para el pedido {order_id}", CONFIG["ADMIN_NUMBERS"][0])
    
    # Volver al estado principal
    session_manager.update_session_state(user_id, "main")
    return jsonify({"status": "success"}), 200