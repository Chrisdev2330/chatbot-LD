# Welcome and goodbye templates
PLANTILLA_BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de LD Make Up.

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

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

# Flow templates
PLANTILLA_CONFIRMAR_PEDIDO = """📝 *Confirmación de Pedido* 📝

Por favor ingresa el ID de tu pedido (es el número que recibiste al hacer tu compra).

Si deseas salir de este proceso, escribe *salir*."""

PLANTILLA_CONFIRMAR_OPCIONES = """¿Confirmamos tu pedido con ID *{}*? 

Escribe:
- *si* para confirmar ✅
- *no* para cancelar ❌
- *salir* para salir del proceso 🚪"""

PLANTILLA_PEDIDO_CONFIRMADO = """¡Listo! ✅ 
Tu pedido con ID *{}* ha sido confirmado exitosamente.

Ahora puedes enviar tu comprobante de pago escribiendo *mipago*.

¡Gracias por elegir LD Make Up! 💖"""

PLANTILLA_PEDIDO_CANCELADO = """Entendido ❌
Hemos cancelado tu pedido con ID *{}*.

Si cambias de opinión, puedes iniciar el proceso nuevamente escribiendo *confirmar*.

¡Estamos para ayudarte! 💄"""

PLANTILLA_MIPAGO = """💳 *Envío de Comprobante* 💳

Para completar tu pago, por favor envía tu comprobante al siguiente número:
📱 +584241220797

Incluye en el mensaje:
1. ID de tu pedido: *{}*
2. Tu nombre completo

Nuestro equipo validará tu pago y te notificará los próximos pasos.

¡Gracias por tu compra! 💖"""

MENSAJE_INSTRUCCIONES = """ℹ️ *Instrucciones importantes:*
- Escribe *confirmar* para confirmar tu pedido
- Escribe *mipago* para enviar comprobante
- Escribe *salir* para salir de cualquier proceso

Todas las notificaciones sobre tu pedido llegarán a este chat. 📦🔔"""

MENSAJE_FUERA_CONTEXTO = """Disculpa, solo puedo ayudarte con información sobre LD Make Up. 💄

¿Tienes alguna pregunta sobre nuestros productos o servicios?"""

MENSAJE_SIGUE_INSTRUCCIONES = "Por favor sigue las instrucciones para continuar. Si deseas salir, escribe *salir*."