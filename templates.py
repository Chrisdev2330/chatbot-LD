# Plantillas de mensajes
TEMPLATES = {
    "WELCOME": """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:*
- Para confirmar tu pedido escribe *CONFIRMAR*
- Para enviar comprobante escribe *MIPAGO*
- Escribe *SALIR* para cerrar la sesión

Todas las notificaciones sobre el estado de tu pedido llegarán a este mismo chat. 📦🔔

¿En qué puedo ayudarte hoy?""",

    "GOODBYE": """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
{store_address}
{store_hours}

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨""",

    "NOTIFICATIONS": """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔""",

    "CONFIRM_PROMPT": """Por favor escribe el ID de tu pedido para confirmar en formato:
#numerodepedido

Opciones:
- Escribe *NO* si no quieres confirmar tu pedido
- Escribe *SALIR* para salir de la confirmación""",

    "PAYMENT_PROMPT": """Por favor envía el comprobante de pago con el ID del pedido a este número: {admin_number}

Opciones:
- Escribe *CANCELAR* si deseas cancelar tu pedido
- Escribe *SALIR* para salir del proceso de pago""",

    "NEED_CONFIRM_FIRST": """⚠️ Para realizar el pago, primero debes confirmar tu pedido.

Por favor escribe *CONFIRMAR* para iniciar el proceso.""",

    "ORDER_CONFIRMED_ADMIN": """📦 *Nueva confirmación de pedido* ✅
ID del pedido: {order_id}
Cliente: {client_number}""",

    "ORDER_NOT_CONFIRMED_ADMIN": """📦 *Pedido no confirmado* ❌
ID del pedido: {order_id}
Cliente: {client_number}""",

    "PAYMENT_CANCELLED_ADMIN": """💸 *Pago cancelado* 🚫
ID del pedido: {order_id}
Cliente: {client_number}""",

    "UNRELATED_QUERY": """Parece que tu consulta no está relacionada con LD Make Up. 

¿En qué puedo ayudarte sobre maquillaje o productos de belleza? 💄""",

    "CONTACT_HUMAN": """Para consultas muy específicas, escribe a {store_phone}. Un asistente te ayudará personalmente. 📩""",

    "SESSION_CLOSED": """Tu sesión ha sido cerrada. Si necesitas más ayuda, escribe *HOLA* para comenzar de nuevo.""",

    "ORDER_CONFIRMED": """✅ Tu pedido ha sido confirmado con éxito. Ahora puedes proceder con el pago escribiendo *MIPAGO*.""",

    "ORDER_NOT_CONFIRMED": """⚠️ No se ha confirmado tu pedido. Si cambias de opinión, escribe *CONFIRMAR* más tarde.""",

    "PAYMENT_INSTRUCTIONS": """📝 Por favor envía el comprobante de pago al número proporcionado. 

Recuerda incluir el ID de tu pedido: {order_id}""",

    "ORDER_CANCELLED": """❌ Has cancelado tu pedido. Si fue un error, puedes iniciar de nuevo escribiendo *HOLA*.""",

    "DEFAULT_RESPONSE": """¡Gracias por tu mensaje! 😊 ¿En qué más puedo ayudarte?"""
}