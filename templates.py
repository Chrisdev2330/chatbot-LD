# Plantillas de mensajes para el bot
from config import CONFIG

ADMIN_NUMBER = CONFIG["ADMIN_NUMBERS"][0]

PLANTILLA_BIENVENIDA = f"""¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:* Todas las notificaciones sobre el estado de tu pedido llegarán a este mismo chat. 📦🔔

*Para confirmar un pedido* escribe *CONFIRMAR*
*Para enviar comprobante de pago* escribe *MIPAGO*
*Para salir* escribe *SALIR*

¿En qué puedo ayudarte hoy?"""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

MENSAJE_NOTIFICACIONES = """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔"""

FLUJO_CONFIRMAR = """📝 *Confirmación de Pedido*
Por favor, escribe el ID de tu pedido en el siguiente formato:
#ID (ejemplo: #12345abc)

Escribe *CANCELAR* para cancelar el proceso
Escribe *REGRESAR* para volver al menú principal"""

FLUJO_MIPAGO = f"""💳 *Envío de Comprobante*
Por favor, envía tu comprobante de pago al número:
{ADMIN_NUMBER}

Incluye el ID de tu pedido en el mensaje.

Escribe *CANCELAR* para cancelar el proceso
Escribe *REGRESAR* para volver al menú principal"""

PLANTILLA_CONFIRMACION_ADMIN = lambda id_pedido: f"""📦 *Nueva Confirmación de Pedido*
El cliente ha confirmado el pedido con ID: {id_pedido}"""

PLANTILLA_CONFIRMACION_CLIENTE = lambda id_pedido: f"""✅ *Pedido Confirmado*
Hemos recibido la confirmación de tu pedido con ID: {id_pedido}

Ahora puedes enviar tu comprobante de pago escribiendo *MIPAGO*"""

PLANTILLA_CANCELACION_ADMIN = lambda id_pedido: f"""❌ *Pedido Cancelado*
El cliente ha cancelado el pedido con ID: {id_pedido}"""

PLANTILLA_CANCELACION_CLIENTE = """🚫 *Proceso Cancelado*
Has cancelado la operación actual. ¿En qué más puedo ayudarte?"""

PLANTILLA_FORMATO_INCORRECTO = """⚠️ *Formato Incorrecto*
Por favor, asegúrate de escribir el ID en el formato solicitado.

Ejemplo válido: #12345abc"""

PLANTILLA_NO_CONFIRMADO = """🔴 *Acción no disponible*
Primero debes confirmar tu pedido escribiendo *CONFIRMAR*"""

PLANTILLA_FUERA_CONTEXTO = """Parece que tu consulta no está relacionada con LD Make Up. ¿En qué puedo ayudarte sobre maquillaje o productos de belleza? 💄"""

PLANTILLA_CONTACTO_HUMANO = f"""📩 *Asistencia Personalizada*
Para consultas muy específicas, escribe a {ADMIN_NUMBER}. Un asistente te ayudará personalmente."""

FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you", "agradecido", "agradecida"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos", "hasta pronto"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking", "rastreo"],
    "confirmar": ["confirmar", "confirmacion", "confirmación", "confirmar pedido"],
    "mipago": ["mipago", "pago", "comprobante", "voucher", "transferencia"],
    "salir": ["salir", "cerrar sesion", "cerrar sesión", "logout"],
    "cancelar": ["cancelar", "cancelar pedido", "anular"]
}