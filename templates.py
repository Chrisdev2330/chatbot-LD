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
- Para enviar comprobante de pago escribe *MIPAGO*
- Escribe *SALIR* para cerrar la sesión

Todas las notificaciones sobre el estado de tu pedido llegarán a este mismo chat. 📦🔔

¿En qué puedo ayudarte hoy?""",

    "GOODBYE": """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨""",

    "NOTIFICATIONS": """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔""",

    "CONFIRM_PROMPT": """Por favor escribe el *ID de tu pedido* para confirmar:""",

    "PAYMENT_PROMPT": """Por favor enviar el comprobante de pago con ID del pedido a este número: 
👉 https://wa.me/584241220797 👈""",

    "CONFIRM_ADMIN_NOTIFICATION": """El cliente con número *{user_phone}* ha confirmado el pedido con ID: *{order_id}* ✅""",

    "NEED_CONFIRM_FIRST": """⚠️ Para realizar el pago primero debes confirmar tu pedido. 
Escribe *CONFIRMAR* para iniciar el proceso.""",

    "UNRELATED_QUERY": """Parece que tu consulta no está relacionada con LD Make Up. 
Por favor escribe algo relacionado con nuestros productos o servicios. 💄""",

    "HUMAN_SUPPORT": """Para consultas muy específicas, por favor escribe al número: 
👉 https://wa.me/584241220797 👈 
Un asistente de la tienda responderá tus inquietudes. 📩"""
}