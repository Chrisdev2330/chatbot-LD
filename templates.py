def welcome_template():
    return """¡Hola! 💄 Soy tu asistente virtual de LD Make Up.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

Importante:
- Escribe *confirmar* para confirmar tu pedido
- Escribe *mipago* para enviar comprobante
- Escribe *salir* para cerrar la sesión

Todas las notificaciones sobre tu pedido llegarán aquí. 📦🔔

¿En qué puedo ayudarte hoy?"""

def goodbye_template():
    return """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

# Flujo Confirmar
def confirmar_start_template():
    return """Para confirmar su pedido por favor ingrese el ID del pedido.

Escriba *salir* si desea salir de la confirmación."""

def confirmar_id_received_template(pedido_id):
    return f"""ID recibido: {pedido_id}

Por favor indique:
- *si* para confirmar el pedido
- *no* para cancelar pedido
- *salir* para salir del flujo"""

def confirmar_success_template(pedido_id):
    return f"""✅ Su pedido con ID {pedido_id} se ha confirmado exitosamente. 
Por favor continúe con el paso *mipago* para enviar su comprobante."""

def confirmar_cancel_template(pedido_id):
    return f"""❌ Su pedido con ID {pedido_id} fue cancelado exitosamente."""

def confirmar_exit_template():
    return "Usted ha salido del proceso de confirmación del pedido."

# Flujo Mipago
def mipago_instructions_template():
    return """Para enviar el comprobante de pago:
1. Escriba a este número: +584241220797
2. Envíe el comprobante junto con:
   - ID del pedido
   - Su nombre completo

Nuestro personal validará su pago y le notificará los próximos pasos.

Si desea cancelar el pago, por favor notifíquelo a ese mismo número."""

def mipago_not_ready_template():
    return """⚠️ Para enviar comprobante de pago primero debe confirmar su pedido.
Escriba *confirmar* para iniciar el proceso de confirmación."""

# Admin notifications
def admin_confirm_notification(pedido_id):
    return f"📌 El pedido con ID {pedido_id} fue confirmado exitosamente."

def admin_cancel_notification(pedido_id):
    return f"📌 El pedido con ID {pedido_id} fue cancelado por parte del cliente."