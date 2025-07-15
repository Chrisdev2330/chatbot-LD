from templates import (
    PLANTILLA_CONFIRMAR_PEDIDO,
    PLANTILLA_CONFIRMAR_OPCIONES,
    PLANTILLA_PEDIDO_CONFIRMADO,
    PLANTILLA_PEDIDO_CANCELADO,
    PLANTILLA_MIPAGO,
    MENSAJE_SIGUE_INSTRUCCIONES
)

class FlowManager:
    def __init__(self, whatsapp_api, admin_number):
        self.whatsapp = whatsapp_api
        self.admin_number = admin_number
    
    def start_flow(self, phone_number, flow_name):
        session = session_manager.get_session(phone_number)
        session.current_flow = flow_name
        
        if flow_name == "confirmar":
            self.whatsapp.send_message(phone_number, PLANTILLA_CONFIRMAR_PEDIDO)
        elif flow_name == "mipago":
            if session.confirmed_order_id:
                self.whatsapp.send_message(
                    phone_number, 
                    PLANTILLA_MIPAGO.format(session.confirmed_order_id)
                )
                session_manager.clear_current_flow(phone_number)
            else:
                self.whatsapp.send_message(
                    phone_number,
                    "⚠️ No puedes ingresar a esta opción de pagos si antes no confirmas tu pedido.\n\nPor favor escribe 'confirmar' para confirmar tu pedido."
                )
                session_manager.clear_current_flow(phone_number)
    
    def handle_flow(self, session, message):
        phone_number = session.phone_number
        flow_name = session.current_flow
        message = message.lower().strip()
        
        if flow_name == "confirmar":
            self._handle_confirm_flow(session, message)
        elif flow_name == "mipago":
            self._handle_payment_flow(session, message)
    
    def _handle_confirm_flow(self, session, message):
        phone_number = session.phone_number
        flow_data = session_manager.get_flow_data(phone_number)
        
        if 'order_id' not in flow_data:
            # First step: Get order ID
            if message.lower() == 'salir':
                self.whatsapp.send_message(phone_number, "Has salido del proceso de confirmación.")
                session_manager.clear_current_flow(phone_number)
            else:
                session_manager.set_flow_data(phone_number, 'order_id', message)
                self.whatsapp.send_message(
                    phone_number,
                    PLANTILLA_CONFIRMAR_OPCIONES.format(message)
                )
        else:
            # Second step: Confirm or cancel
            order_id = flow_data['order_id']
            
            if message == 'si':
                # Confirm order
                session_manager.set_order_id(phone_number, order_id)
                self.whatsapp.send_message(
                    phone_number,
                    PLANTILLA_PEDIDO_CONFIRMADO.format(order_id)
                )
                
                # Notify admin
                self.whatsapp.send_message(
                    self.admin_number,
                    f"✅ Nuevo pedido confirmado\nID: {order_id}\nCliente: {phone_number}"
                )
                
                session_manager.clear_current_flow(phone_number)
            elif message == 'no':
                # Cancel order
                self.whatsapp.send_message(
                    phone_number,
                    PLANTILLA_PEDIDO_CANCELADO.format(order_id)
                )
                
                # Notify admin
                self.whatsapp.send_message(
                    self.admin_number,
                    f"❌ Pedido cancelado\nID: {order_id}\nCliente: {phone_number}"
                )
                
                session_manager.clear_current_flow(phone_number)
            elif message == 'salir':
                self.whatsapp.send_message(phone_number, "Has salido del proceso de confirmación.")
                session_manager.clear_current_flow(phone_number)
            else:
                self.whatsapp.send_message(phone_number, MENSAJE_SIGUE_INSTRUCCIONES)
    
    def _handle_payment_flow(self, session, message):
        # The payment flow is simple - just show instructions and exit
        # This shouldn't normally be called since we exit after showing instructions
        self.whatsapp.send_message(
            session.phone_number,
            "Por favor envía tu comprobante al número indicado con tu ID de pedido."
        )
        session_manager.clear_current_flow(session.phone_number)