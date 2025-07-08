from flask import Flask, jsonify, request
from google import genai
from heyoo import WhatsApp
import os
import ssl
import requests
from woocommerce import API

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key="AIzaSyAKJHDBN8cXHtFKc0rzX9oGMsOTXvK1BgI")

# Token de WhatsApp y ID de número de teléfono
WHATSAPP_TOKEN = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
WHATSAPP_NUMBER_ID = '730238483499494'

# Configuración de WooCommerce
wcapi = API(
    url="https://c2840384.ferozo.com/",
    consumer_key="ck_ce17ce5bf4c982b01b3a1aaffec210878e0cb8dc",
    consumer_secret="cs_9b51876fdd8daeb3d179f1d6d545840e2a9f2c32",
    version="wc/v3"
)

# Número estático para notificaciones de la tienda
NUMERO_TIENDA = "+584241220797"

preguntas_frecuentes = {
    "formas de pago minorista": {
        "pregunta": "¿Cuáles son las formas de pagos en la venta por menor?",
        "respuesta": "- Efectivo billete en nuestro local\n- Transferencia bancaria\n- Tarjetas de crédito y débito a través de Mercado Pago",
        "palabras_clave": ["pago", "minorista", "menor", "tarjeta", "mercado pago", "transferencia", "efectivo"]
    },
    "forma de pago mayorista": {
        "pregunta": "¿Cuál es la forma de pago en venta por mayor?",
        "respuesta": "- Únicamente contado efectivo billete en el local\n- Transferencia bancaria",
        "palabras_clave": ["mayorista", "mayor", "contado", "pago mayorista"]
    },
    "direccion y horario": {
        "pregunta": "¿En qué dirección y horario puedo retirar mi pedido?",
        "respuesta": "📍 Dirección: Alsina 455, San Miguel de Tucumán\n⏰ Horario: \n   - Mañana: 09:00 a 13:00\n   - Tarde: 17:00 a 21:00\n\nTambién realizamos envíos a todo el país a través de Correo Argentino.",
        "palabras_clave": ["dirección", "horario", "retirar", "local", "ubicación", "hora", "cuándo", "dónde"]
    },
    "envios tucuman": {
        "pregunta": "¿Realizan envíos dentro de la provincia de Tucumán?",
        "respuesta": "Únicamente si el cliente nos envía el cadete o comisionista con el dinero para abonar la compra.",
        "palabras_clave": ["envío", "tucumán", "provincia", "cadete", "comisionista"]
    },
    "tiempo entrega": {
        "pregunta": "¿Cuánto tarda en llegar mi pedido por correo argentino?",
        "respuesta": "El tiempo estimado de entrega es de 5 a 7 días hábiles.",
        "palabras_clave": ["tarda", "entrega", "correo", "días", "cuándo llega", "demora", "hora llegada"]
    },
    "horario atencion": {
        "pregunta": "¿Cuál es el horario de atención?",
        "respuesta": "Horario de atención:\nLunes a Sábados\n- Mañana: 09:00 a 13:00\n- Tarde: 17:00 a 21:00",
        "palabras_clave": ["horario", "atención", "abierto", "cierran", "hora", "atendiendo"]
    },
    "quienes somos": {
        "pregunta": "¿Quiénes son LD Make Up?",
        "respuesta": """Somos una empresa con experiencia en el mercado desde 2015, fundada por Luciana Díaz, maquilladora egresada del Teatro Colón y capacitada internacionalmente en Brasil con las últimas tendencias en Make Up.

Nuestros clientes nos destacan por:
- Excelente atención y asesoramiento
- Equipo altamente capacitado
- Amplia variedad de productos en:
  • Maquillaje
  • Insumos para uñas
  • Insumos para pestañas

¡Todo en un solo lugar!""",
        "palabras_clave": ["quienes", "somos", "historia", "empresa", "luciana", "díaz"]
    },
    "productos": {
        "pregunta": "¿Qué productos ofrecen?",
        "respuesta": "Ofrecemos una amplia variedad de productos:\n- Maquillaje profesional\n- Insumos para uñas\n- Insumos para pestañas\n\n¡Todo lo que necesitas en un solo lugar!",
        "palabras_clave": ["productos", "ofrecen", "venden", "maquillaje", "uñas", "pestañas"]
    },
    "tienda fisica": {
        "pregunta": "¿Tienen tienda física?",
        "respuesta": "Sí, nuestro local está ubicado en:\n📍 Alsina 455, San Miguel de Tucumán\n⏰ Horario:\n- Mañana: 09:00 a 13:00\n- Tarde: 17:00 a 21:00",
        "palabras_clave": ["tienda", "física", "local", "visitar", "presencial"]
    }
}

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

MENSAJE_FUERA_CONTEXTO = """🔍 *Parece que tu consulta no está relacionada con LD Make Up*

Te invito a preguntarme sobre:
• Maquillaje profesional 💄
• Insumos para uñas/pestañas 💅
• Métodos de pago y envíos 🚚
• Horarios de atención 🕘
• Dirección de nuestro local 📍

Si necesitas otro tipo de asistencia, contáctanos directamente:
📞 +54 9 3813 02-1066"""

MENSAJE_CONTACTO_HUMANO = """👩‍💼 *Asistencia Humana*
Parece que no he podido resolver tu consulta satisfactoriamente. 

Por favor, contacta a nuestro equipo de atención al cliente:
📞 Teléfono: +54 9 3813 02-1066
⏰ Horario: Lunes a Sábados 9-13hs y 17-21hs

¡Estaremos encantados de ayudarte!"""

PLANTILLA_NUEVO_PEDIDO_CLIENTE = """📦 *¡Tu pedido en LD Make Up ha sido creado!*

ID del pedido: #{order_id}
Fecha: {order_date}
Total: ${order_total}

📝 *Detalles del pedido:*
{order_items}

📍 *Dirección de envío:*
{shipping_address}

¡Estaremos procesando tu pedido pronto! Te notificaremos cuando sea enviado."""

PLANTILLA_NUEVO_PEDIDO_TIENDA = """🛒 *¡Nuevo pedido recibido!*

Cliente: {customer_name}
Teléfono: {customer_phone}
ID Pedido: #{order_id}
Total: ${order_total}

📝 *Productos:*
{order_items}

📍 *Dirección:*
{shipping_address}

💬 *Notas del cliente:*
{customer_note}"""

PLANTILLA_ACTUALIZACION_ESTADO_CLIENTE = """🔄 *Actualización de tu pedido #{order_id}*

El estado de tu pedido ha cambiado:
🏷️ *De:* {old_status}
🏷️ *A:* {new_status}

📦 *Detalles del pedido:*
{order_items}

Si tienes alguna pregunta, no dudes en contactarnos."""

PLANTILLA_ACTUALIZACION_ESTADO_TIENDA = """📊 *Estado de pedido actualizado*

Has cambiado el estado del pedido #{order_id}

👤 Cliente: {customer_name}
📞 Teléfono: {customer_phone}

🔄 Cambio de estado:
🏷️ *De:* {old_status}
🏷️ *A:* {new_status}

📝 *Notas internas:*
{order_note}"""

FLUJO_CONVERSACION = {
    "agradecimiento": ["gracias", "muchas gracias", "thanks", "thank you", "agradecido", "agradecida"],
    "despedida": ["adiós", "chao", "bye", "hasta luego", "nos vemos", "hasta pronto"],
    "notificaciones": ["notificaciones", "estado de pedido", "seguimiento", "tracking", "donde está", "cuando llega"],
    "contacto_humano": ["humano", "persona", "asesor", "representante", "operador", "hablar con alguien"]
}

estados_chats = {}

def actualizar_estado(telefono, clave, valor):
    if telefono not in estados_chats:
        estados_chats[telefono] = {}
    estados_chats[telefono][clave] = valor

def obtener_estado(telefono, clave, default=None):
    return estados_chats.get(telefono, {}).get(clave, default)

def buscar_en_preguntas_frecuentes(mensaje):
    mensaje = mensaje.lower()
    
    for faq in preguntas_frecuentes.values():
        if faq["pregunta"].lower() in mensaje:
            return True, faq["respuesta"]
    
    coincidencias = []
    for faq in preguntas_frecuentes.values():
        for palabra in faq["palabras_clave"]:
            if palabra.lower() in mensaje:
                coincidencias.append(faq)
                break
    
    if len(coincidencias) == 1:
        return True, coincidencias[0]["respuesta"]
    elif len(coincidencias) > 1:
        opciones = "\n".join([f"• {faq['pregunta']}" for faq in coincidencias])
        mensaje = f"🔍 Tengo varias opciones relacionadas con tu consulta:\n\n{opciones}\n\nPor favor, especifica cuál de estas preguntas es la que necesitas responder."
        return True, mensaje
    
    return False, None

def enviar(telefono, mensaje):
    mensajeWa = WhatsApp(WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID)
    mensajeWa.send_message(mensaje, telefono)

def manejar_respuesta_gemini(telefono, mensaje):
    intentos = obtener_estado(telefono, "intentos_fuera_contexto", 0)
    
    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Eres un asistente de LD Make Up. Responde profesionalmente sobre:
            - Maquillaje y productos de belleza
            - Dirección: Alsina 455, San Miguel de Tucumán
            - Horarios: Lunes a Sábados 9-13hs y 17-21hs
            - Pagos: Efectivo/Transferencia/Tarjetas
            - Envíos por Correo Argentino

            Usa este contexto para responder:
            {preguntas_frecuentes}

            Si la pregunta NO es sobre estos temas, responde EXACTAMENTE:
            "FUERA_DE_CONTEXTO"

            Pregunta: {mensaje}
            """
        )
        
        if "FUERA_DE_CONTEXTO" in respuesta.text:
            intentos += 1
            actualizar_estado(telefono, "intentos_fuera_contexto", intentos)
            
            if intentos >= 3:
                enviar(telefono, MENSAJE_CONTACTO_HUMANO)
                actualizar_estado(telefono, "intentos_fuera_contexto", 0)
            else:
                enviar(telefono, MENSAJE_FUERA_CONTEXTO)
        else:
            actualizar_estado(telefono, "intentos_fuera_contexto", 0)
            enviar(telefono, respuesta.text)
            
    except Exception as e:
        enviar(telefono, "⚠️ Hubo un error procesando tu solicitud. Por favor inténtalo nuevamente o contáctanos al +54 9 3813 02-1066")

def obtener_detalle_pedido(order_id):
    try:
        pedido = wcapi.get(f"orders/{order_id}").json()
        
        items = []
        for item in pedido['line_items']:
            items.append(f"- {item['quantity']}x {item['name']} (${item['price']} c/u)")
        
        shipping = pedido.get('shipping', {})
        shipping_address = "\n".join([
            f"{shipping.get('first_name', '')} {shipping.get('last_name', '')}",
            shipping.get('address_1', ''),
            shipping.get('address_2', ''),
            f"{shipping.get('city', '')}, {shipping.get('state', '')}",
            shipping.get('postcode', ''),
            shipping.get('country', '')
        ])
        
        return {
            'order_id': order_id,
            'order_date': pedido['date_created'].split('T')[0],
            'order_total': pedido['total'],
            'order_items': "\n".join(items),
            'shipping_address': shipping_address,
            'customer_name': f"{pedido['billing']['first_name']} {pedido['billing']['last_name']}",
            'customer_phone': pedido['billing']['phone'],
            'customer_note': pedido.get('customer_note', 'Ninguna'),
            'status': pedido['status']
        }
    except Exception as e:
        print(f"Error al obtener pedido {order_id}: {str(e)}")
        return None

def enviar_notificacion_pedido(order_id, tipo="creado"):
    detalle = obtener_detalle_pedido(order_id)
    if not detalle:
        return False
    
    if tipo == "creado":
        mensaje_cliente = PLANTILLA_NUEVO_PEDIDO_CLIENTE.format(**detalle)
    else:
        mensaje_cliente = PLANTILLA_ACTUALIZACION_ESTADO_CLIENTE.format(
            order_id=detalle['order_id'],
            old_status=detalle.get('old_status', 'creado').capitalize(),
            new_status=detalle['status'].capitalize(),
            order_items=detalle['order_items']
        )
    
    enviar(detalle['customer_phone'], mensaje_cliente)
    
    if tipo == "creado":
        mensaje_tienda = PLANTILLA_NUEVO_PEDIDO_TIENDA.format(**detalle)
    else:
        mensaje_tienda = PLANTILLA_ACTUALIZACION_ESTADO_TIENDA.format(
            order_id=detalle['order_id'],
            customer_name=detalle['customer_name'],
            customer_phone=detalle['customer_phone'],
            old_status=detalle.get('old_status', 'creado').capitalize(),
            new_status=detalle['status'].capitalize(),
            order_note=detalle.get('order_note', 'Ninguna')
        )
    
    enviar(NUMERO_TIENDA, mensaje_tienda)
    
    return True

@app.route('/webhook/woocommerce/order_created', methods=['POST'])
def webhook_order_created():
    try:
        data = request.get_json()
        order_id = data['id']
        enviar_notificacion_pedido(order_id, tipo="creado")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error en webhook order_created: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/webhook/woocommerce/order_updated', methods=['POST'])
def webhook_order_updated():
    try:
        data = request.get_json()
        order_id = data['id']
        
        old_status = data.get('old_status', 'creado')
        
        detalle = obtener_detalle_pedido(order_id)
        if detalle:
            detalle['old_status'] = old_status
            detalle['order_note'] = data.get('note', 'Ninguna')
            enviar_notificacion_pedido(order_id, tipo="actualizado")
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error en webhook order_updated: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    if request.method == "GET":
        if request.args.get('hub.verify_token') == "HolaNovato":
            return request.args.get('hub.challenge')
        return "Error de autentificación."

    data = request.get_json()
    
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}, 200)
    except:
        return jsonify({"status": "error"}, 400)

    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].lower()

    if any(palabra in mensaje for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefonoCliente, PLANTILLA_BIENVENIDA)
        return jsonify({"status": "success"}, 200)
    
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["agradecimiento"]):
        enviar(telefonoCliente, "¡Con gusto! ¿En qué más puedo ayudarte? 😊")
        return jsonify({"status": "success"}, 200)
    
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["despedida"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        return jsonify({"status": "success"}, 200)
    
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["notificaciones"]):
        enviar(telefonoCliente, MENSAJE_NOTIFICACIONES)
        return jsonify({"status": "success"}, 200)
    
    if any(palabra in mensaje for palabra in FLUJO_CONVERSACION["contacto_humano"]):
        intentos = obtener_estado(telefonoCliente, "intentos_fuera_contexto", 0)
        if intentos >= 2:
            enviar(telefonoCliente, MENSAJE_CONTACTO_HUMANO)
            actualizar_estado(telefonoCliente, "intentos_fuera_contexto", 0)
        else:
            enviar(telefonoCliente, "Por favor, indícame exactamente en qué necesitas ayuda para poder asistirte mejor. Si no logro resolver tu consulta, te proporcionaré nuestro contacto.")
        return jsonify({"status": "success"}, 200)

    encontrado, respuesta_faq = buscar_en_preguntas_frecuentes(mensaje)
    
    if encontrado:
        enviar(telefonoCliente, respuesta_faq)
    else:
        manejar_respuesta_gemini(telefonoCliente, mensaje)

    return jsonify({"status": "success"}, 200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)