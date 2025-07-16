from sessions import session_manager
from templates import *
from config import ADMIN_NUMBERS
from whatsapp import send_message, send_admin_notification

def handle_confirmar_flow(user_id, message):
    session = session_manager.get_session(user_id)
    flow_data = session['flow_data']
    
    # Step 1: Starting confirmation
    if 'pedido_id' not in flow_data:
        if message.lower() == 'salir':
            session_manager.clear_flow(user_id)
            return confirmar_exit_template()
            
        flow_data['pedido_id'] = message
        return confirmar_id_received_template(message)
    
    # Step 2: Confirmation choice
    if message.lower() == 'si':
        # Send success messages
        pedido_id = flow_data['pedido_id']
        send_admin_notification(admin_confirm_notification(pedido_id))
        session_manager.clear_flow(user_id)
        return confirmar_success_template(pedido_id)
        
    elif message.lower() == 'no':
        # Send cancel messages
        pedido_id = flow_data['pedido_id']
        send_admin_notification(admin_cancel_notification(pedido_id))
        session_manager.clear_flow(user_id)
        return confirmar_cancel_template(pedido_id)
        
    elif message.lower() == 'salir':
        session_manager.clear_flow(user_id)
        return confirmar_exit_template()
        
    else:
        return "Por favor responda con *si*, *no* o *salir*."

def handle_mipago_flow(user_id):
    session = session_manager.get_session(user_id)
    
    # Check if user completed confirmar flow
    if 'pedido_id' not in session['flow_data']:
        return mipago_not_ready_template()
        
    # Send instructions and exit flow
    session_manager.clear_flow(user_id)
    return mipago_instructions_template()