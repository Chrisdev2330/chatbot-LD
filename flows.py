from templates import Templates
from utils import send_message, send_admin_notification
from session_manager import session_manager

class Flows:
    @staticmethod
    def handle_confirm(user_id, user_number, message):
        session = session_manager.get_session(user_id)
        
        if message.lower() == 'cancelar':
            session_manager.clear_current_flow(user_id)
            send_message(user_number, Templates.cancel_action("confirmación"))
            send_admin_notification(Templates.cancel_admin_notification(
                session.get('confirmed_order', 'N/A'), 
                user_number, 
                "confirmación"
            ))
            return True
        
        if not message.startswith('#'):
            send_message(user_number, Templates.invalid_format())
            return False
        
        order_id = message[1:].strip()
        if not order_id:
            send_message(user_number, Templates.invalid_format())
            return False
        
        # Confirmación exitosa
        session_manager.set_confirmed_order(user_id, order_id)
        session_manager.clear_current_flow(user_id)
        
        send_message(user_number, Templates.confirm_success(order_id))
        send_admin_notification(Templates.confirm_admin_notification(
            order_id, 
            user_number
        ))
        return True

    @staticmethod
    def handle_payment(user_id, user_number, message):
        session = session_manager.get_session(user_id)
        
        if message.lower() == 'cancelar':
            session_manager.clear_current_flow(user_id)
            send_message(user_number, Templates.cancel_action("envío de comprobante"))
            send_admin_notification(Templates.cancel_admin_notification(
                session.get('confirmed_order', 'N/A'), 
                user_number, 
                "envío de comprobante"
            ))
            return True
        
        if not message.startswith('-'):
            send_message(user_number, Templates.invalid_format())
            return False
        
        order_id = message[1:].strip()
        if not order_id:
            send_message(user_number, Templates.invalid_format())
            return False
        
        # Pago procesado
        session_manager.clear_current_flow(user_id)
        
        send_message(user_number, Templates.payment_success(order_id))
        send_admin_notification(Templates.payment_admin_notification(
            order_id, 
            user_number
        ))
        return True