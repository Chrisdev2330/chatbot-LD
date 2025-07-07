from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
import os
import ssl
import certifi
import requests

#os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
#ssl._create_default_https_context = ssl._create_unverified_context
#requests.utils.DEFAULT_CA_BUNDLE_PATH = certifi.where()

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key="AIzaSyAKJHDBN8cXHtFKc0rzX9oGMsOTXvK1BgI")

# Preguntas frecuentes sobre LD Make Up
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

# Plantillas de mensajes
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

FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking"]
}

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        else:
            return "Error de autentificacion."
    
    # RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data = request.get_json()
    
    # Verificar si es una notificación de cambio de estado (no mensaje de usuario)
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            # Es una notificación de estado, no manejamos estas respuestas
            return jsonify({"status": "success"}, 200)
    except:
        return jsonify({"status": "error"}, 400)
    
    # EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    idWA = data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    timestamp = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    
    # Verificar si es el primer mensaje para enviar bienvenida
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, PLANTILLA_BIENVENIDA)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un mensaje de despedida
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["despedida"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        return jsonify({"status": "success"}, 200)
    
    # Verificar si es un agradecimiento
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        enviar(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        return jsonify({"status": "success"}, 200)
    
    # Verificar preguntas sobre notificaciones
    if any(palabra in mensaje.lower() for palabra in FLUJO_CONVERSACION["notificaciones"]):
        enviar(telefonoCliente, MENSAJE_NOTIFICACIONES)
        return jsonify({"status": "success"}, 200)
    
    # Verificar preguntas frecuentes
    respuesta_faq = None
    for pregunta, respuesta in preguntas_frecuentes.items():
        if pregunta.lower() in mensaje.lower() or any(palabra in mensaje.lower() for palabra in pregunta.lower().split()[:3]):
            respuesta_faq = respuesta
            break
    
    if respuesta_faq:
        enviar(telefonoCliente, respuesta_faq)
    else:
        # Si no es pregunta frecuente, usar Gemini
        try:
            respuesta = cliente.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"""
                Eres un asistente virtual profesional de LD Make Up, una tienda de maquillaje y productos de belleza en Tucumán, Argentina. 
                Responde de forma amable y profesional con información veraz basada en estos datos:
                
                - Empresa fundada en 2015 por Luciana Díaz, maquilladora profesional
                - Especializados en maquillaje, insumos para uñas y pestañas
                - Local en Alsina 455, San Miguel de Tucumán
                - Horario: Lunes a Sábados 09:00-13:00 y 17:00-21:00
                - Venta minorista: Efectivo, transferencia, tarjetas vía Mercado Pago
                - Venta mayorista: Solo efectivo o transferencia
                - Envíos: A todo el país por Correo Argentino (5-7 días hábiles)
                - Envíos en Tucumán: Solo si el cliente envía cadete/comisionista
                
                Si la pregunta no está relacionada con estos temas o no tienes información suficiente, responde:
                "Por favor, comunícate con nosotros al +54 9 3813 02-1066 para asistencia personalizada."
                
                Pregunta: {mensaje}
                """
            )
            enviar(telefonoCliente, respuesta.text)
        except Exception as e:
            enviar(telefonoCliente, f"Disculpas, hubo un error. Por favor contacta al +54 9 3813 02-1066 para asistencia.")

    return jsonify({"status": "success"}, 200)

def enviar(telefonoRecibe, respuesta):
    # TOKEN DE ACCESO DE FACEBOOK
    token = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
    # IDENTIFICADOR DE NÚMERO DE TELÉFONO
    idNumeroTeléfono = '730238483499494'
    # INICIALIZAMOS ENVIO DE MENSAJES
    mensajeWa = WhatsApp(token, idNumeroTeléfono)
    # ENVIAMOS UN MENSAJE DE TEXTO
    mensajeWa.send_message(respuesta, telefonoRecibe)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)