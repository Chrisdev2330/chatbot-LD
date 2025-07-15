# Mensajes de flujo de conversación
FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos", "salir"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking"]
}

# Plantilla de bienvenida
PLANTILLA_BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:*
- Todas las notificaciones sobre tu pedido llegarán aquí 📦🔔
- Para *confirmar un pedido* escribe *CONFIRMAR*
- Para enviar comprobante escribe *MIPAGO*

📍 *Dirección:* Alsina 455, San Miguel de Tucumán
⏰ *Horario:* Lunes a Sábados 09:00-13:00 y 17:00-21:00

¿En qué puedo ayudarte hoy?"""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

MENSAJE_NOTIFICACIONES = """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔"""

# Plantillas para flujo de confirmación
PLANTILLA_CONFIRMAR_PEDIDO = """📝 *Confirmación de Pedido*

Por favor, escribe el ID de tu pedido en el siguiente formato:
#ID (ejemplo: #12345abc)

Opciones:
- *CANCELAR*: Para cancelar este proceso
- *REGRESAR*: Para volver al menú principal"""

PLANTILLA_PEDIDO_CONFIRMADO_CLIENTE = """✅ *¡Pedido Confirmado!*

Tu pedido con ID *#{}* ha sido confirmado con éxito. 

Ahora puedes enviar tu comprobante de pago escribiendo *MIPAGO*.

Gracias por tu compra en LD Make Up! 💄💖"""

PLANTILLA_PEDIDO_CONFIRMADO_ADMIN = """📢 *Nueva Confirmación de Pedido*

El cliente ha confirmado el pedido con ID: *#{}*

Por favor, procede con el procesamiento del mismo."""

PLANTILLA_CONFIRMAR_PRIMERO = """⚠️ *Primero debes confirmar tu pedido*

Para enviar tu comprobante de pago, primero debes confirmar tu pedido escribiendo *CONFIRMAR*.

Si necesitas ayuda, no dudes en preguntar."""

# Plantillas para flujo de pago
PLANTILLA_ENVIAR_COMPROBANTE = """💳 *Enviar Comprobante de Pago*

Por favor, escribe el ID de tu pedido en el siguiente formato:
#ID (ejemplo: #12345abc)

Luego envía tu comprobante de pago al número:
👉 +584241220797

Opciones:
- *CANCELAR*: Para cancelar este proceso"""

PLANTILLA_COMPROBANTE_RECIBIDO_CLIENTE = """✅ *¡Comprobante Recibido!*

Hemos registrado tu comprobante para el pedido *#{}*. 

Nuestro equipo verificará el pago y te notificará cuando tu pedido sea despachado.

¡Gracias por confiar en LD Make Up! 💖"""

PLANTILLA_COMPROBANTE_RECIBIDO_ADMIN = """📢 *Nuevo Comprobante Recibido*

El cliente ha enviado comprobante para el pedido con ID: *#{}*

Por favor, verifica el pago y procede con el despacho."""

# Plantillas para cancelación
PLANTILLA_CANCELAR_PEDIDO_CLIENTE = """❌ *Pedido Cancelado*

Has cancelado el proceso de confirmación de pedido. 

Si fue un error, puedes iniciar nuevamente escribiendo *CONFIRMAR*."""

PLANTILLA_CANCELAR_PEDIDO_ADMIN = """❌ *Pedido Cancelado*

El cliente ha cancelado el pedido con ID: *#{}*"""

PLANTILLA_CANCELAR_PAGO_CLIENTE = """❌ *Proceso de Pago Cancelado*

Has cancelado el envío del comprobante de pago. 

Si fue un error, puedes iniciar nuevamente escribiendo *MIPAGO*."""

PLANTILLA_CANCELAR_PAGO_ADMIN = """❌ *Pago Cancelado*

El cliente ha cancelado el envío de comprobante para el pedido con ID: *#{}*"""

# Plantilla para formato incorrecto
PLANTILLA_FORMATO_INCORRECTO = """⚠️ *Formato Incorrecto*

Por favor, escribe el ID de tu pedido comenzando con # o - seguido del número de ID (ejemplo: #12345abc o -12345abc)

O escribe *CANCELAR* para terminar este proceso."""

# Plantilla para contacto humano
PLANTILLA_CONTACTO_HUMANO = """👩💼 *Asistencia Personalizada*

Parece que necesitas ayuda más específica. Por favor, escribe directamente a nuestro asistente humano:

👉 +584241220797

Te atenderemos con gusto. 💖"""