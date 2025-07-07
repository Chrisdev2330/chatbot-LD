from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
import os
import ssl
import requests

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key="AIzaSyAKJHDBN8cXHtFKc0rzX9oGMsOTXvK1BgI")

# Preguntas frecuentes sobre LD Make Up (TUS DATOS ORIGINALES)
preguntas_frecuentes = {
    "¿Cuáles son las formas de pagos en la venta por menor?": "- Efectivo billete en nuestro local\n- Transferencia bancaria\n- Tarjetas de crédito y débito a través de Mercado Pago",
    "¿Cuál es la forma de pago en venta por mayor?": "- Únicamente contado efectivo billete en el local\n- Transferencia bancaria",
    "¿En qué dirección y horario puedo retirar mi pedido?": "📍 Dirección: Alsina 455, San Miguel de Tucumán\n⏰ Horario: \n   - Mañana: 09:00 a 13:00\n   - Tarde: 17:00 a 21:00\n\nTambién realizamos envíos a todo el país a través de Correo Argentino.",
    "¿Realizan envíos dentro de la provincia de Tucumán?": "Únicamente si el cliente nos envía el cadete o comisionista con el dinero para abonar la compra.",
    "¿Cuánto tarda en llegar mi pedido por correo argentino?": "El tiempo estimado de entrega es de 5 a 7 días hábiles.",
    "¿Cuál es el horario de atención?": "Horario de atención:\nLunes a Sábados\n- Mañana: 09:00 a 13:00\n- Tarde: 17:00 a 21:00",
    "¿Quiénes son LD Make Up?": """Somos una empresa con experiencia en el mercado desde 2015, fundada por Luciana Díaz, maquilladora egresada del Teatro Colón y capacitada internacionalmente en Brasil con las últimas tendencias en Make Up.

Nuestros clientes nos destacan por:
- Excelente atención y asesoramiento
- Equipo altamente capacitado
- Amplia variedad de productos en:
  • Maquillaje
  • Insumos para uñas
  • Insumos para pestañas

¡Todo en un solo lugar!""",
    "¿Qué productos ofrecen?": "Ofrecemos una amplia variedad de productos:\n- Maquillaje profesional\n- Insumos para uñas\n- Insumos para pestañas\n\n¡Todo lo que necesitas en un solo lugar!",
    "¿Tienen tienda física?": "Sí, nuestro local está ubicado en:\n📍 Alsina 455, San Miguel de Tucumán\n⏰ Horario:\n- Mañana: 09:00 a 13:00\n- Tarde: 17:00 a 21:00"
}

# Plantillas de mensajes (TUS DATOS ORIGINALES + NUEVA PLANTILLA)
PLANTILLA_BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

Estoy aquí para ayudarte con:
- Consultas sobre productos y precios
- Métodos de pago y envíos
- Horarios y dirección de nuestro local
- Asesoramiento profesional

*Importante:* Todas las notificaciones sobre el estado de tu pedido llegarán a este mismo chat. 📦🔔

¿En qué puedo ayudarte hoy?"""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

MENSAJE_NOTIFICACIONES = """ℹ️ *Recordatorio importante:*
Todas las notificaciones sobre el estado de tu pedido (confirmación, envío, etc.) llegarán a este mismo chat. No es necesario que respondas a estos mensajes automáticos. 📦🔔"""

# NUEVA PLANTILLA AGREGADA
MENSAJE_FUERA_CONTEXTO = """🔍 *Parece que tu consulta no está relacionada con LD Make Up*

Te invito a preguntarme sobre:
• Maquillaje profesional 💄
• Insumos para uñas/pestañas 💅
• Métodos de pago y envíos 🚚
• Horarios de atención 🕘
• Dirección de nuestro local 📍

Si necesitas otro tipo de asistencia, contáctanos directamente:
📞 +54 9 3813 02-1066"""

FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking"]
}

# Variable para controlar el estado de la conversación
estados_chats = {}

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    global estados_chats

    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        return "Error de autentificacion."

    data = request.get_json()
    
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}, 200)
    except:
        return jsonify({"status": "error"}, 400)

    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']

    # Manejo mejorado de agradecimientos
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        estados_chats[telefonoCliente] = {"esperando_respuesta": True}
        enviar(telefonoCliente, "¡Con gusto! ¿En qué más puedo ayudarte? 😊")
        return jsonify({"status": "success"}, 200)

    # Resto de tu lógica original (SIN CAMBIOS)
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, PLANTILLA_BIENVENIDA)
        return jsonify({"status": "success"}, 200)
    
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["despedida"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        return jsonify({"status": "success"}, 200)
    
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["notificaciones"]):
        enviar(telefonoCliente, MENSAJE_NOTIFICACIONES)
        return jsonify({"status": "success"}, 200)

    # Búsqueda en preguntas frecuentes (SIN CAMBIOS)
    respuesta_faq = None
    for pregunta, respuesta in preguntas_frecuentes.items():
        if pregunta.lower() in mensaje.lower() or any(palabra in mensaje.lower() for palabra in pregunta.lower().split()[:3]):
            respuesta_faq = respuesta
            break

    if respuesta_faq:
        enviar(telefonoCliente, respuesta_faq)
    else:
        # Consulta a Gemini con manejo de contexto
        try:
            respuesta = cliente.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"""
                Eres un asistente de LD Make Up. Responde SOLO sobre:
                - Maquillaje y productos de belleza
                - Dirección: Alsina 455, San Miguel de Tucumán
                - Horarios: Lunes a Sábados 9-13hs y 17-21hs
                - Pagos: Efectivo/Transferencia/Tarjetas
                - Envíos por Correo Argentino

                Si la pregunta NO es sobre estos temas, responde EXACTAMENTE:
                "FUERA_DE_CONTEXTO"

                Datos para respuestas:
                {preguntas_frecuentes}

                Pregunta: {mensaje}
                """
            )
            
            if "FUERA_DE_CONTEXTO" in respuesta.text:
                enviar(telefonoCliente, MENSAJE_FUERA_CONTEXTO)
            else:
                enviar(telefonoCliente, respuesta.text)
                
        except Exception as e:
            enviar(telefonoCliente, "⚠️ Hubo un error. Por favor contáctanos al +54 9 3813 02-1066")

    return jsonify({"status": "success"}, 200)

# Función enviar() ORIGINAL SIN MODIFICACIONES
def enviar(telefonoRecibe, respuesta):
    token = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
    idNumeroTeléfono = '730238483499494'
    mensajeWa = WhatsApp(token, idNumeroTeléfono)
    mensajeWa.send_message(respuesta, telefonoRecibe)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)