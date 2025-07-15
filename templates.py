PLANTILLA_BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:* Todas las notificaciones sobre el estado de tu pedido llegarán a este mismo chat. 📦🔔

¿En qué puedo ayudarte hoy?

Escribe:
- *confirmar* para confirmar un pedido
- *mipago* para enviar comprobante
- *salir* para cerrar la sesión"""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

PLANTILLA_CONFIRMAR_PEDIDO = """📝 *Confirmación de Pedido*

Por favor, escribe el ID de tu pedido en el siguiente formato:
#ID (ejemplo: #12345)

O si deseas cancelar:
-ID (ejemplo: -12345)"""

PLANTILLA_PEDIDO_CONFIRMADO_CLIENTE = """✅ *Pedido Confirmado*

¡Gracias! Hemos confirmado tu pedido con ID: *{}*

Recuerda que puedes:
- Enviar tu comprobante escribiendo *mipago*
- Consultar el estado de tu pedido en cualquier momento"""

PLANTILLA_PEDIDO_CONFIRMADO_ADMIN = """🔔 *Nueva Confirmación de Pedido*

El cliente ha confirmado el pedido con ID: *{}*

Por favor, procede con el procesamiento."""

PLANTILLA_PEDIDO_CANCELADO_CLIENTE = """❌ *Pedido Cancelado*

Hemos cancelado tu pedido con ID: *{}*

Si fue un error, puedes iniciar el proceso nuevamente."""

PLANTILLA_PEDIDO_CANCELADO_ADMIN = """⚠️ *Pedido Cancelado*

El cliente ha cancelado el pedido con ID: *{}*

Por favor, actualiza el sistema."""

PLANTILLA_ENVIAR_COMPROBANTE = """💳 *Enviar Comprobante*

Por favor, envía el comprobante de pago al siguiente número:
{}

Incluye el ID de tu pedido en el mensaje.

¡Gracias por tu compra! 💖"""

PLANTILLA_CONFIRMAR_PRIMERO = """⚠️ *Acción Requerida*

Para enviar tu comprobante, primero debes *confirmar* tu pedido.

Escribe *confirmar* y sigue las instrucciones."""

PLANTILLA_ID_INVALIDO = """❌ *Formato Incorrecto*

Por favor, escribe el ID en el formato correcto:
- Para confirmar: #ID (ejemplo: #12345)
- Para cancelar: -ID (ejemplo: -12345)"""

PLANTILLA_ERROR_IA = """⚠️ *Error de conexión*

Lo sentimos, estamos teniendo problemas técnicos. Por favor, intenta nuevamente más tarde o escribe al número +584241220797 para asistencia inmediata."""

MENSAJE_NOTIFICACIONES = """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔"""