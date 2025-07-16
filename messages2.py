# Plantillas de mensajes
BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de LD Make Up.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

Importante:
- Escribe confirmar para confirmar tu pedido, este es el primer paso si has solicitado un pedido.
- Escribe mipago para enviar comprobante, este es el segundo paso si has solicitado un pedido.
- Escribe salir para cerrar la sesión

Todas las notificaciones sobre tu pedido llegarán aquí. 📦🔔

¿En qué puedo ayudarte hoy?""" 

DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

CONFIRMAR_PEDIDO = """Para confirmar tu pedido:
1. Envía un mensaje al +584241220797
2. Incluye el ID de pedido y tu nombre y apellido 
3. Indica que deseas confirmar el pedido

¡Así de fácil! El equipo validará tu pedido y te permitirá continuar con los próximos pasos"""

PEDIR_COMPROBANTE = """📤 Para enviar tu comprobante:
1. Envía un mensaje al +584241220797
2. Adjunta el comprobante 
3. Incluye el ID de pedido, tu nombre y apellido

¡Así de fácil! El equipo validará tu pago pronto y te permitirá continuar con los próximos pasos."""

# Flujos de conversación
FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos", "salir"],
    "saludo": ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas noches"]
}