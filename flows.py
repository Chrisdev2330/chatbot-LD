from flask import jsonify
from config import CONFIG
from templates import TEMPLATES
from session_manager import session_manager
from whatsapp import send_whatsapp_message, send_admin_notification

def handle_confirm_flow(phone, message):
    flow = session_manager.get_current_flow(phone)
    
    # Check if flow timed out
    if not session_manager.is_flow_active(phone):
        session_manager.end_flow(phone)
        return jsonify({"status": "success"}), 200
    
    # Check if message starts with # (confirmation) or - (cancellation)
    if message.startswith('#'):
        order_id = message[1:].strip()
        if order_id:
            # Successful confirmation
            session_manager.set_confirmed_order(phone, order_id)
            send_whatsapp_message(phone, TEMPLATES['confirm_success'].format(order_id=order_id))
            
            # Notify admin
            admin_message = TEMPLATES['confirm_admin_notification'].format(
                client_number=phone,
                order_id=order_id
            )
            send_admin_notification(admin_message)
            
            session_manager.end_flow(phone)
            return jsonify({"status": "success"}), 200
        else:
            # Empty order ID
            send_whatsapp_message(phone, TEMPLATES['invalid_format'].format(
                format_instructions="`#ID_de_tu_pedido` (ejemplo: `#AB1234`)"
            ))
            return jsonify({"status": "success"}), 200
    
    elif message.startswith('-'):
        order_id = message[1:].strip()
        if order_id:
            # Cancellation
            send_whatsapp_message(phone, TEMPLATES['cancel_success'].format(order_id=order_id))
            
            # Notify admin
            admin_message = TEMPLATES['cancel_admin_notification'].format(
                client_number=phone,
                order_id=order_id
            )
            send_admin_notification(admin_message)
            
            session_manager.end_flow(phone)
            return jsonify({"status": "success"}), 200
        else:
            # Empty order ID
            send_whatsapp_message(phone, TEMPLATES['invalid_format'].format(
                format_instructions="`-ID_de_tu_pedido` (ejemplo: `-AB1234`)"
            ))
            return jsonify({"status": "success"}), 200
    
    else:
        # Invalid format
        send_whatsapp_message(phone, TEMPLATES['invalid_format'].format(
            format_instructions="Para confirmar: `#ID_de_tu_pedido`\nPara cancelar: `-ID_de_tu_pedido`"
        ))
        return jsonify({"status": "success"}), 200

def handle_payment_flow(phone, message):
    flow = session_manager.get_current_flow(phone)
    
    # Check if flow timed out
    if not session_manager.is_flow_active(phone):
        session_manager.end_flow(phone)
        send_whatsapp_message(phone, TEMPLATES['flow_timeout'])
        return jsonify({"status": "success"}), 200
    
    # Check if user wants to cancel
    if message.lower() == 'cancelar':
        order_id = session_manager.get_confirmed_order(phone)
        if order_id:
            send_whatsapp_message(phone, TEMPLATES['cancel_success'].format(order_id=order_id))
            
            # Notify admin
            admin_message = TEMPLATES['cancel_admin_notification'].format(
                client_number=phone,
                order_id=order_id
            )
            send_admin_notification(admin_message)
            
            session_manager.set_confirmed_order(phone, None)
        else:
            send_whatsapp_message(phone, "No hay pedido para cancelar.")
        
        session_manager.end_flow(phone)
        return jsonify({"status": "success"}), 200
    
    # For payment flow, any message is considered as acknowledgment
    order_id = session_manager.get_confirmed_order(phone)
    if order_id:
        send_whatsapp_message(phone, TEMPLATES['payment_success'].format(
            order_id=order_id,
            admin_number=CONFIG['ADMIN_NUMBERS'][0]
        ))
        
        # Notify admin
        admin_message = TEMPLATES['payment_admin_notification'].format(
            client_number=phone,
            order_id=order_id
        )
        send_admin_notification(admin_message)
    else:
        send_whatsapp_message(phone, TEMPLATES['missing_confirmation'])
    
    session_manager.end_flow(phone)
    return jsonify({"status": "success"}), 200