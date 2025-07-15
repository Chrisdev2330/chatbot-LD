# Message templates with emojis and professional styling
TEMPLATES = {
    "welcome": """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios 🛍️
- Métodos de pago y envíos 💳🚚
- Horarios y dirección de nuestro local 🏪
- Asesoramiento profesional 💅

*Flujos rápidos:*
- Escribe *confirmar* para validar tu pedido ✅
- Escribe *mipago* para enviar comprobante 📄
- Escribe *salir* para cerrar la sesión 🔚

*Importante:* Todas las notificaciones sobre el estado de tu pedido llegarán a este mismo chat. 📦🔔

¿En qué puedo ayudarte hoy?""",

    "goodbye": """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨""",

    "notifications": """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔""",

    "confirm_prompt": """📝 *Confirmación de Pedido*

Por favor, escribe el ID de tu pedido con el siguiente formato:
`#ID_de_tu_pedido`
Ejemplo: `#AB1234`

ℹ️ Para cancelar el pedido, escribe:
`-ID_de_tu_pedido`
Ejemplo: `-AB1234`""",

    "payment_prompt": """💳 *Envío de Comprobante*

Por favor envía tu comprobante de pago junto con el ID de pedido al siguiente número:
{admin_number}

ℹ️ Para cancelar el pedido, escribe:
`cancelar`""",

    "confirm_success": """✅ *Pedido Confirmado*

¡Gracias! Hemos recibido tu confirmación para el pedido:
ID: `{order_id}`

Un asistente revisará tu pedido y te notificará cualquier actualización. 📦""",

    "confirm_admin_notification": """📢 *Nueva Confirmación de Pedido*

El cliente {client_number} ha confirmado el pedido:
ID: `{order_id}`

Por favor proceder con el procesamiento.""",

    "payment_success": """📨 *Comprobante Solicitado*

Hemos registrado tu solicitud para el pedido:
ID: `{order_id}`

Por favor envía el comprobante de pago al número:
{admin_number}

¡Gracias por tu compra! 💖""",

    "payment_admin_notification": """💸 *Solicitud de Comprobante*

El cliente {client_number} ha solicitado enviar comprobante para el pedido:
ID: `{order_id}`

Por favor estar atento al envío del documento.""",

    "cancel_success": """❌ *Pedido Cancelado*

Hemos cancelado tu pedido:
ID: `{order_id}`

Si fue un error, por favor contáctanos nuevamente. 😊""",

    "cancel_admin_notification": """⚠️ *Pedido Cancelado*

El cliente {client_number} ha cancelado el pedido:
ID: `{order_id}`""",

    "invalid_format": """⚠️ *Formato Incorrecto*

Por favor usa el formato solicitado:
{format_instructions}

Inténtalo de nuevo o escribe *salir* para cancelar.""",

    "unrelated_message": """🤔 *Consulta no relacionada*

Parece que tu mensaje no está relacionado con LD Make Up. Por favor escribe algo sobre:

- Productos de maquillaje 💄
- Insumos para uñas o pestañas 💅
- Métodos de pago o envíos 🚚

¿En qué puedo ayudarte?""",

    "human_assistance": """👩💼 *Asistencia Personalizada*

Para consultas muy específicas, por favor escribe a:
{admin_number}

Un asistente humano te ayudará personalmente. 📩""",

    "flow_timeout": """⏱️ *Tiempo Agotado*

La operación anterior ha expirado. Por favor inicia nuevamente el proceso que necesites.

¿En qué más puedo ayudarte?""",

    "missing_confirmation": """⚠️ *Confirmación Requerida*

Para enviar tu comprobante, primero debes confirmar tu pedido.

Escribe *confirmar* para iniciar el proceso de confirmación.

¿Necesitas ayuda con algo más?"""
}