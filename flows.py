class FlowManager:
    def __init__(self, whatsapp_api, session_manager):
        self.whatsapp = whatsapp_api
        self.sessions = session_manager
        self.admin_number = "584241220797"  # Static admin number
    
    def handle_flow(self, user_id, message, session):
        # Check if trying to access payment flow without confirmation
        if message == 'mipago' and not session.get('flow_data', {}).get('order_confirmed'):
            self.whatsapp.send_message(user_id, 
                "⚠️ No puedes ingresar a esta opción de pagos sin antes confirmar tu pedido. "
                "Por favor escribe *confirmar* para confirmar tu pedido primero."
            )
            return
        
        # Start confirmation flow
        if message == 'confirmar' and not session.get('current_flow'):
            session['current_flow'] = 'confirmar'
            session['flow_data'] = {}
            self.sessions.save_session(user_id, session)
            self.whatsapp.send_message(user_id,
                "💄 *Confirmación de Pedido* 💄\n\n"
                "Por favor ingresa el *ID de tu pedido* (el número que recibiste al hacer tu compra).\n\n"
                "Escribe *salir* en cualquier momento para cancelar este proceso."
            )
            return
        
        # Handle confirmation flow steps
        if session.get('current_flow') == 'confirmar':
            self._handle_confirmation_flow(user_id, message, session)
            return
        
        # Handle payment flow
        if message == 'mipago' and session.get('flow_data', {}).get('order_confirmed'):
            self._handle_payment_flow(user_id, session)
            return
    
    def _handle_confirmation_flow(self, user_id, message, session):
        flow_data = session.get('flow_data', {})
        
        # Exit flow
        if message == 'salir':
            self.whatsapp.send_message(user_id,
                "Has salido del proceso de confirmación de pedido. "
                "Puedes continuar con otras consultas."
            )
            self.sessions.end_flow(user_id)
            return
        
        # Step 1: Get order ID
        if 'order_id' not in flow_data:
            flow_data['order_id'] = message
            session['flow_data'] = flow_data
            self.sessions.save_session(user_id, session)
            
            self.whatsapp.send_message(user_id,
                f"🔍 ID del pedido recibido: *{message}*\n\n"
                "Por favor escribe:\n"
                "- *si* para confirmar este pedido\n"
                "- *no* para cancelarlo\n"
                "- *salir* para salir sin cambios"
            )
            return
        
        # Step 2: Confirm or cancel order
        if message in ['si', 'no']:
            order_id = flow_data['order_id']
            
            if message == 'si':
                # Confirm order
                flow_data['order_confirmed'] = True
                session['flow_data'] = flow_data
                self.sessions.save_session(user_id, session)
                
                # Notify user
                self.whatsapp.send_message(user_id,
                    f"✅ ¡Pedido confirmado exitosamente!\n\n"
                    f"ID del pedido: *{order_id}*\n\n"
                    "Ahora puedes proceder con el pago escribiendo *mipago*."
                )
                
                # Notify admin
                self.whatsapp.send_admin_notification(self.admin_number,
                    f"📦 Nuevo pedido confirmado\n\n"
                    f"ID: {order_id}\n"
                    f"Cliente: {user_id}\n"
                    f"Estado: CONFIRMADO"
                )
            else:
                # Cancel order
                self.whatsapp.send_message(user_id,
                    f"❌ Pedido cancelado exitosamente\n\n"
                    f"ID del pedido: *{order_id}*"
                )
                
                # Notify admin
                self.whatsapp.send_admin_notification(self.admin_number,
                    f"📦 Pedido cancelado\n\n"
                    f"ID: {order_id}\n"
                    f"Cliente: {user_id}\n"
                    f"Estado: CANCELADO POR CLIENTE"
                )
            
            self.sessions.end_flow(user_id)
    
    def _handle_payment_flow(self, user_id, session):
        order_id = session['flow_data']['order_id']
        
        self.whatsapp.send_message(user_id,
            "💳 *Proceso de Pago* 💳\n\n"
            "Para enviar tu comprobante de pago:\n"
            "1. Envía un mensaje al número *+584241220797*\n"
            "2. Adjunta el comprobante de pago\n"
            "3. Incluye esta información:\n"
            f"   - ID del pedido: *{order_id}*\n"
            "   - Tu nombre completo\n\n"
            "Nuestro equipo validará tu pago y te notificará los próximos pasos.\n\n"
            "Si deseas cancelar el pago, por favor notifícalo al mismo número."
        )
        
        self.sessions.end_flow(user_id)