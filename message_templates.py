# Welcome and goodbye templates
WELCOME_TEMPLATE = """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:*
- Escribe *confirmar* para confirmar tu pedido
- Escribe *mipago* para enviar comprobante
- Escribe *salir* para cerrar la sesión

Todas las notificaciones sobre tu pedido llegarán aquí. 📦🔔

¿En qué puedo ayudarte hoy?"""

GOODBYE_TEMPLATE = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

# Confirmation flow templates
def get_confirm_start_template():
    return """Para confirmar su pedido por favor ingrese el ID del pedido.

Escriba *salir* si desea salir de la confirmación."""

def get_confirm_id_received_template(pedido_id):
    return f"""ID recibido: {pedido_id}

Por favor indique:
- *si* para confirmar el pedido
- *no* para cancelar pedido
- *salir* para salir del flujo"""

def get_confirm_success_template(pedido_id):
    return f"""✅ Su pedido con ID {pedido_id} se ha confirmado exitosamente. 
Por favor continúe con el paso *mipago* para enviar su comprobante."""

def get_confirm_cancel_template(pedido_id):
    return f"""❌ Su pedido con ID {pedido_id} fue cancelado exitosamente."""

def get_confirm_exit_template():
    return "Usted ha salido del proceso de confirmación del pedido."

# Payment flow templates
def get_payment_instructions_template():
    return """Para enviar el comprobante de pago:
1. Escriba a este número: +584241220797
2. Envíe el comprobante junto con:
   - ID del pedido
   - Su nombre completo

Nuestro personal validará su pago y le notificará los próximos pasos.

Si desea cancelar el pago, por favor notifíquelo a ese mismo número."""

def get_payment_not_ready_template():
    return """⚠️ Para enviar comprobante de pago primero debe confirmar su pedido.
Escriba *confirmar* para iniciar el proceso de confirmación."""

# Admin notifications
def get_admin_confirm_notification(pedido_id):
    return f"📌 El pedido con ID {pedido_id} fue confirmado exitosamente."

def get_admin_cancel_notification(pedido_id):
    return f"📌 El pedido con ID {pedido_id} fue cancelado por parte del cliente."