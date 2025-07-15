from templates import (
    PLANTILLA_CONFIRMAR_PEDIDO,
    PLANTILLA_CONFIRMAR_OPCIONES,
    PLANTILLA_PEDIDO_CONFIRMADO,
    PLANTILLA_PEDIDO_CANCELADO,
    PLANTILLA_MIPAGO,
    MENSAJE_SIGUE_INSTRUCCIONES
)

class FlowManager:
    def __init__(self, whatsapp_api, session_manager, admin_number):
        self.whatsapp = whatsapp_api
        self.session_manager = session_manager
        self.admin_number = admin_number
    
    def start_flow(self, phone_number, flow_name):
        session = self.session_manager.get_session(phone_number)
        session.current_flow = flow_name
        
        if flow_name == "confirmar":
            self.whatsapp.send_message(phone_number, PLANTILLA_CONFIRMAR_PEDIDO)
        elif flow_name == "mipago":
            if session.confirmed_order_id:
                self.whatsapp.send_message(
                    phone_number, 
                    PLANTILLA_MIPAGO.format(session.confirmed_order_id)
                )
                self.session_manager.clear_current_flow(phone_number)
    
    def handle_flow(self, session, message):
        message = message.strip().lower()
        
        if session.current_flow == "confirmar":
            self._handle_confirm_flow(session, message)
        elif session.current_flow == "mipago":
            self._handle_payment_flow(session, message)
    
    def _handle_confirm_flow(self, session, message):
        phone_number = session.phone_number
        flow_data = self.session_manager.get_flow_data(phone_number)
        
        if 'order_id' not in flow_data:
            # Paso 1: Obtener ID del pedido
            if message == 'salir':
                self.whatsapp.send_message(phone_number, "Has salido del proceso de confirmación.")
                self.session_manager.clear_current_flow(phone_number)
            else:
                # Guardar cualquier valor como ID del pedido
                self.session_manager.set_flow_data(phone_number, 'order_id', message)
                self.whatsapp.send_message(
                    phone_number,
                    PLANTILLA_CONFIRMAR_OPCIONES.format(message)
                )
        else:
            # Paso 2: Confirmar o cancelar pedido
            order_id = flow_data['order_id']
            
            if message == 'si':
                # Confirmar pedido
                self.session_manager.set_order_id(phone_number, order_id)
                
                # Mensaje al cliente
                self.whatsapp.send_message(
                    phone_number,
                    PLANTILLA_PEDIDO_CONFIRMADO.format(order_id)
                )
                
                # Notificación al administrador
                self.whatsapp.send_message_to_admin(
                    f"✅ NUEVO PEDIDO CONFIRMADO\n\n"
                    f"ID: {order_id}\n"
                    f"Cliente: {phone_number}\n"
                    f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )
                
                self.session_manager.clear_current_flow(phone_number)
            
            elif message == 'no':
                # Cancelar pedido
                self.whatsapp.send_message(
                    phone_number,
                    PLANTILLA_PEDIDO_CANCELADO.format(order_id)
                )
                
                # Notificación al administrador
                self.whatsapp.send_message_to_admin(
                    f"❌ PEDIDO CANCELADO\n\n"
                    f"ID: {order_id}\n"
                    f"Cliente: {phone_number}\n"
                    f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                )
                
                self.session_manager.clear_current_flow(phone_number)
            
            elif message == 'salir':
                self.whatsapp.send_message(phone_number, "Has salido del proceso de confirmación.")
                self.session_manager.clear_current_flow(phone_number)
            
            else:
                self.whatsapp.send_message(phone_number, MENSAJE_SIGUE_INSTRUCCIONES)
    
    def _handle_payment_flow(self, session, message):
        # Este flujo es simple, solo muestra instrucciones y sale
        # No debería llegar aquí normalmente
        self.whatsapp.send_message(
            session.phone_number,
            "Por favor envía tu comprobante al número indicado con tu ID de pedido."
        )
        self.session_manager.clear_current_flow(session.phone_number)