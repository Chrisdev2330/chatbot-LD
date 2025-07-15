# Mensajes estáticos
PLANTILLA_BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

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

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

📍 *Dirección:* Alsina 455, San Miguel de Tucumán
⏰ *Horario:* Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡escríbenos! ✨"""

# Flujo de confirmación
PLANTILLA_CONFIRMAR = """Por favor, escribe el ID de tu pedido en este formato:
#ID (ejemplo: #74834)

O escribe:
- Cancelar: Para cancelar el pedido
- Regresar: Para volver al menú principal"""

PLANTILLA_CONFIRMACION_EXITOSA = """✅ *Pedido Confirmado*
¡Gracias! Hemos confirmado tu pedido con ID: *{}*
Un asistente te contactará si es necesario."""

PLANTILLA_CANCELACION_EXITOSA = """❌ *Pedido Cancelado*
Hemos cancelado tu pedido con ID: *{}*
Si fue un error, contáctanos."""

# Flujo de pago
PLANTILLA_MIPAGO = """Por favor, envía tu comprobante de pago con el ID de pedido a este número: 
👉 {} 

*Importante:*
- El comprobante debe incluir el ID del pedido
- Escribe *cancelar* si deseas anular"""

PLANTILLA_PAGO_RECIBIDO = """💳 *Pago Registrado*
Hemos recibido tu comprobante para el pedido: *{}*
Estamos verificando y te notificaremos."""

# Mensajes de error
PLANTILLA_ID_INVALIDO = """⚠️ Formato incorrecto
Por favor, escribe el ID exactamente como se te indicó:
#ID (ejemplo: #74834)"""

PLANTILLA_FUERA_CONTEXTO = """Parece que tu consulta no está relacionada con LD Make Up. 
¿En qué puedo ayudarte sobre maquillaje o productos de belleza? 💄"""

PLANTILLA_CONTACTO_HUMANO = """Para consultas muy específicas, escribe a:
👉 {} 
Un asistente te ayudará personalmente. 📩"""

# Notificaciones para administradores
NOTIF_CONFIRMACION_ADMIN = """📦 *Nueva Confirmación de Pedido*
Cliente: {}
ID Pedido: {}
Fecha: {}"""

NOTIF_CANCELACION_ADMIN = """❌ *Pedido Cancelado*
Cliente: {}
ID Pedido: {}
Fecha: {}"""

NOTIF_PAGO_ADMIN = """💳 *Comprobante Recibido*
Cliente: {}
ID Pedido: {}
Fecha: {}"""