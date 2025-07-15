from config import CONFIG

class Templates:
    @staticmethod
    def welcome():
        return """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:*
- Todas las notificaciones sobre tu pedido llegarán aquí 📦🔔
- Para confirmar un pedido escribe *confirmar*
- Para enviar comprobante escribe *mipago*
- Escribe *salir* para cerrar la sesión

¿En qué puedo ayudarte hoy?"""

    @staticmethod
    def goodbye():
        return """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

    @staticmethod
    def notifications():
        return """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔"""

    @staticmethod
    def confirm_prompt():
        return """📝 *Confirmación de Pedido*

Por favor, escribe el ID de tu pedido en el formato:
#ID (ejemplo: #12345abc)

Escribe *cancelar* para anular este proceso."""

    @staticmethod
    def payment_prompt():
        return """💳 *Envío de Comprobante*

Por favor, envía tu comprobante de pago junto con el ID de pedido a este número:
{}

Formato: 
-ID (ejemplo: -12345abc)

Escribe *cancelar* para anular este proceso.""".format(CONFIG["ADMIN_NUMBERS"][0])

    @staticmethod
    def confirm_success(pedido_id):
        return f"""✅ *Pedido Confirmado con Éxito*

Hemos registrado tu pedido con ID: {pedido_id}

Pronto recibirás actualizaciones sobre el estado de tu compra. ¡Gracias por confiar en LD Make Up! 💄💖"""

    @staticmethod
    def confirm_admin_notification(pedido_id, user_number):
        return f"""🔔 *Nuevo Pedido Confirmado*

El cliente {user_number} ha confirmado el pedido con ID: {pedido_id}

Por favor, procede con el procesamiento."""

    @staticmethod
    def payment_success(pedido_id):
        return f"""💰 *Comprobante Solicitado*

Hemos registrado tu solicitud para el pedido: {pedido_id}

Por favor, envía el comprobante al número indicado. ¡Gracias!"""

    @staticmethod
    def payment_admin_notification(pedido_id, user_number):
        return f"""📤 *Comprobante Solicitado*

El cliente {user_number} ha solicitado enviar comprobante para el pedido: {pedido_id}

Por favor, espera su documento."""

    @staticmethod
    def cancel_action(action):
        return f"""❌ *Proceso Cancelado*

Has cancelado el proceso de {action}.

¿En qué más puedo ayudarte?"""

    @staticmethod
    def cancel_admin_notification(pedido_id, user_number, action):
        return f"""⚠️ *Proceso Cancelado*

El cliente {user_number} ha cancelado el {action} para el pedido: {pedido_id}"""

    @staticmethod
    def invalid_format():
        return """⚠️ *Formato Incorrecto*

Por favor, usa el formato indicado:
- Para confirmar: #ID (ejemplo: #12345abc)
- Para pago: -ID (ejemplo: -12345abc)

Intenta nuevamente o escribe *cancelar* para salir."""

    @staticmethod
    def unrelated_query(attempt):
        if attempt < CONFIG["MAX_ATTEMPTS"]:
            return "Parece que tu consulta no está relacionada con LD Make Up. ¿En qué puedo ayudarte sobre maquillaje o productos de belleza? 💄"
        else:
            return f"Para consultas muy específicas, escribe a {CONFIG['ADMIN_NUMBERS'][0]}. Un asistente te ayudará. 📩"

    @staticmethod
    def need_confirmation_first():
        return """📌 *Primero Confirma tu Pedido*

Para enviar tu comprobante de pago, primero debes confirmar tu pedido.

Escribe *confirmar* para iniciar el proceso."""

    @staticmethod
    def session_closed():
        return "🔒 Tu sesión ha sido cerrada. Escribe cualquier mensaje para comenzar una nueva."