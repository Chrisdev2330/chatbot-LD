BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de LD Make Up.

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

DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

# Flujo confirmar
PEDIR_ID = """Por favor ingresa el ID de tu pedido 📋
(Escribe *salir* para cancelar)"""

CONFIRMAR_OPCION = """¿Confirmar pedido con ID *{}*?
- Escribe *si* para confirmar ✅
- Escribe *no* para cancelar ❌
- Escribe *salir* para volver"""

PEDIDO_CONFIRMADO = """¡Listo! 🎉 Tu pedido *{}* está confirmado.
Ahora escribe *mipago* para enviar tu comprobante."""

PEDIDO_CANCELADO = """Pedido *{}* cancelado exitosamente. 
¿Necesitas algo más?"""

SALIR_CONFIRMAR = """Has salido del proceso de confirmación.
¿En qué más puedo ayudarte?"""

# Flujo mipago
PEDIR_COMPROBANTE = """📤 Para enviar tu comprobante:
1. Envía un mensaje al +584241220797
2. Adjunta el comprobante 
3. Incluye el ID de pedido *{}* y tu nombre

¡Así de fácil! El equipo validará tu pago pronto."""

ERROR_MIPAGO = """⚠️ Primero debes confirmar tu pedido.
Escribe *confirmar* para comenzar."""

# Mensajes admin
ADMIN_CONFIRMADO = "✅ Pedido {} confirmado por cliente"
ADMIN_CANCELADO = "❌ Pedido {} cancelado por cliente"