# Plantillas de mensajes para el bot

PLANTILLA_BIENVENIDA = """¡Hola! 💄✨ Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

📌 *Importante:*
- Todas las notificaciones sobre tu pedido llegarán aquí.
- Para confirmar tu pedido escribe *CONFIRMAR*
- Para enviar comprobante de pago escribe *MIPAGO*
- Escribe *SALIR* para cerrar la sesión

¿En qué puedo ayudarte hoy? 💖"""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💄💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

MENSAJE_NOTIFICACIONES = """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔"""

PLANTILLA_CONFIRMAR_PEDIDO = """Por favor escribe el *ID de tu pedido* para confirmarlo. 📝

Ejemplo: *CONFIRMAR PED-12345*"""

PLANTILLA_PEDIDO_CONFIRMADO = """✅ *Pedido confirmado con éxito!*

Tu pedido con ID *{pedido_id}* ha sido confirmado. 

Pronto recibirás actualizaciones sobre el estado de tu compra. ¡Gracias por confiar en LD Make Up! 💖"""

PLANTILLA_ENVIAR_COMPROBANTE = """💳 *Enviar comprobante de pago*

Por favor envía el comprobante de pago junto con el ID de tu pedido a este número: 
📲 {admin_number}

(Haz clic en el número para iniciar el chat)"""

PLANTILLA_CONFIRMAR_PRIMERO = """⚠️ *Primero debes confirmar tu pedido*

Para continuar con el pago, primero debes confirmar tu pedido escribiendo *CONFIRMAR*. 

Si ya lo hiciste y ves este mensaje, escribe *SALIR* y vuelve a iniciar el proceso. 💖"""

PLANTILLA_FUERA_CONTEXTO = """¡Hola! 👋 Parece que tu consulta no está relacionada con LD Make Up.

Por favor, escribe algo relacionado con nuestros productos o servicios de maquillaje para poder ayudarte mejor. 💄✨

Si necesitas ayuda con otra cosa, puedes contactar a nuestro equipo al {admin_number}."""

PLANTILLA_CONTACTO_SOPORTE = """👩‍💼 *Asistencia personalizada*

Para consultas muy específicas o asistencia personalizada, por favor contacta a nuestro equipo de soporte aquí:
📲 {admin_number}

(Haz clic en el número para iniciar el chat)"""

FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking"],
    "confirmar": ["confirmar"],
    "mipago": ["mipago", "mi pago", "comprobante", "pago"],
    "salir": ["salir", "cerrar", "terminar"]
}