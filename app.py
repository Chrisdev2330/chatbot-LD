from flask import Flask, jsonify, request
from heyoo import WhatsApp
import os
import requests
import re
import time
from threading import Thread

app = Flask(__name__)

# ==============================================
# CONFIGURACIÓN INICIAL
# ==============================================

WHATSAPP_TOKEN = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
WHATSAPP_NUMBER_ID = '730238483499494'
NUMERO_ESTATICO = "584241220797"

# ==============================================
# BASE DE CONOCIMIENTO
# ==============================================

preguntas_frecuentes = {
    "1": {
        "pregunta": "1- Sobre Nosotros",
        "respuesta": """Somos una empresa con experiencia en el mercado desde 2015, fundada por Luciana Díaz, maquilladora egresada del Teatro Colón y capacitada internacionalmente en Brasil con las últimas tendencias en Make Up.

Nuestros clientes nos destacan por:
- Excelente atención y asesoramiento
- Equipo altamente capacitado
- Amplia variedad de productos en:
  • Maquillaje
  • Insumos para uñas
  • Insumos para pestañas

¡Todo en un solo lugar!"""
    },
    "2": {
        "pregunta": "2- Forma de pago mayorista",
        "respuesta": "- Únicamente contado efectivo billete en el local\n- Transferencia bancaria"
    },
    "3": {
        "pregunta": "3- Dirección y horario",
        "respuesta": "📍 Dirección: Alsina 455, San Miguel de Tucumán\n⏰ Horario: \n   - Mañana: 09:00 a 13:00\n   - Tarde: 17:00 a 21:00\n\nTambién realizamos envíos a todo el país a través de Correo Argentino."
    },
    "4": {
        "pregunta": "4- Envíos en Tucumán",
        "respuesta": "Únicamente si el cliente nos envía el cadete o comisionista con el dinero para abonar la compra."
    },
    "5": {
        "pregunta": "5- Tiempo de entrega",
        "respuesta": "El tiempo estimado de entrega es de 5 a 7 días hábiles."
    },
    "6": {
        "pregunta": "6- Horario de atención",
        "respuesta": "Horario de atención:\nLunes a Sábados\n- Mañana: 09:00 a 13:00\n- Tarde: 17:00 a 21:00"
    }
}

# ==============================================
# PLANTILLAS DE MENSAJES
# ==============================================

PLANTILLA_BIENVENIDA = """¡Hola! 💄 Soy tu asistente virtual de *LD Make Up*.

*Importante:* Todas las notificaciones de tus pedidos con su identificador llegarán a este medio."""

PLANTILLA_MENU = """📌 *Menú Principal*

Escribe el número correspondiente:
1- Sobre Nosotros
2- Forma de pago mayorista
3- Dirección y horario
4- Envíos en Tucumán
5- Tiempo de entrega
6- Horario de atención
7- Gestionar pedido
8- Procesar pago
9- Salir"""

PLANTILLA_GESTION_PEDIDO = """📦 *Gestión de Pedido*

Escribe el *ID de tu pedido* (recibido en la notificación) o *menu* para volver:"""

PLANTILLA_PROCESAR_PAGO = """💳 *Procesar Pago*

Envía:
- *Imagen* del comprobante (transferencia)
- *efectivo* (pago en efectivo)
- *Enlace de Google Drive* con el comprobante
- *menu* (volver al menú)"""

PLANTILLA_CONFIRMACION_ENVIADA = """✅ Confirmación enviada para el pedido *{}*"""

PLANTILLA_PAGO_ENVIADO = """✅ Pago recibido. Validación en proceso."""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

PLANTILLA_OPCION_INVALIDA = """⚠️ *Opción no válida*

Por favor selecciona una opción del menú (1-9) o escribe 'menu' para ver las opciones"""

# ==============================================
# FUNCIONES AUXILIARES
# ==============================================

def es_enlace_drive(url):
    patrones = [
        r'https?://drive\.google\.com/.+',
        r'https?://docs\.google\.com/.+'
    ]
    return any(re.match(patron, url) for patron in patrones)

def enviar(telefono, mensaje):
    try:
        mensajeWa = WhatsApp(WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID)
        mensajeWa.send_message(mensaje, telefono)
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

def enviar_con_delay(telefono, mensajes, delay=2):
    def enviar_mensajes():
        for mensaje in mensajes:
            enviar(telefono, mensaje)
            time.sleep(delay)
    Thread(target=enviar_mensajes).start()

def enviar_a_numero_estatico(mensaje):
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": NUMERO_ESTATICO,
            "type": "text",
            "text": {"body": mensaje}
        }
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error al enviar a admin: {e}")

def enviar_imagen_a_numero_estatico(image_url, caption):
    try:
        url = f"https://graph.facebook.com/v18.0/{WHATSAPP_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": NUMERO_ESTATICO,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error al enviar imagen: {e}")

def obtener_url_imagen(image_id):
    try:
        url = f"https://graph.facebook.com/v18.0/{image_id}/"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        response = requests.get(url, headers=headers)
        return response.json().get('url')
    except Exception as e:
        print(f"Error al obtener imagen: {e}")
        return None

def procesar_pago(telefono_cliente, contenido, id_pedido):
    try:
        mensaje_admin = f"🔄 Comprobante recibido para pedido: {id_pedido}\n"
        
        if contenido.startswith(('http://', 'https://')):
            if es_enlace_drive(contenido):
                mensaje_admin += f"📎 Enlace Drive: {contenido}"
            else:
                mensaje_admin += f"🔗 Enlace: {contenido}"
        elif contenido == "efectivo":
            mensaje_admin += "💵 Pago en efectivo"
        
        enviar_a_numero_estatico(mensaje_admin)
        
        enviar_con_delay(telefono_cliente, [
            PLANTILLA_PAGO_ENVIADO,
            PLANTILLA_MENU
        ])
        
        return True
    except Exception as e:
        print(f"Error en procesar_pago: {e}")
        return False

# ==============================================
# MANEJO DE ESTADOS
# ==============================================

estados_chats = {}

def actualizar_estado(telefono, clave, valor):
    if telefono not in estados_chats:
        estados_chats[telefono] = {}
    estados_chats[telefono][clave] = valor

def obtener_estado(telefono, clave, default=None):
    return estados_chats.get(telefono, {}).get(clave, default)

# ==============================================
# WEBHOOK PRINCIPAL
# ==============================================

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

        telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        
        if 'text' in data['entry'][0]['changes'][0]['value']['messages'][0]:
            mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].lower()
            
            # Manejo de saludos
            if any(palabra in mensaje for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
                enviar_con_delay(telefonoCliente, [PLANTILLA_BIENVENIDA, PLANTILLA_MENU])
                return jsonify({"status": "success"}, 200)
            
            # Manejo de menú
            if mensaje == "menu":
                enviar(telefonoCliente, PLANTILLA_MENU)
                actualizar_estado(telefonoCliente, "esperando_id_pedido", False)
                actualizar_estado(telefonoCliente, "esperando_comprobante", False)
                return jsonify({"status": "success"}, 200)
            
            # Opción 7 - Gestionar pedido
            if obtener_estado(telefonoCliente, "esperando_id_pedido"):
                actualizar_estado(telefonoCliente, "id_pedido_actual", mensaje)
                actualizar_estado(telefonoCliente, "esperando_id_pedido", False)
                
                enviar_a_numero_estatico(f"Pedido confirmado - ID: {mensaje}")
                enviar_con_delay(telefonoCliente, [
                    PLANTILLA_CONFIRMACION_ENVIADA.format(mensaje),
                    PLANTILLA_MENU
                ])
                return jsonify({"status": "success"}, 200)
            
            # Opción 8 - Procesar pago
            if obtener_estado(telefonoCliente, "esperando_comprobante"):
                id_pedido = obtener_estado(telefonoCliente, "id_pedido_actual")
                
                if id_pedido:
                    if mensaje == "efectivo":
                        procesar_pago(telefonoCliente, mensaje, id_pedido)
                    elif mensaje.startswith(('http://', 'https://')):
                        if es_enlace_drive(mensaje):
                            procesar_pago(telefonoCliente, mensaje, id_pedido)
                        else:
                            enviar(telefonoCliente, "⚠️ El enlace no es de Google Drive. Por favor usa un enlace válido.")
                    elif mensaje == "menu":
                        enviar(telefonoCliente, PLANTILLA_MENU)
                    else:
                        enviar(telefonoCliente, PLANTILLA_PROCESAR_PAGO)
                    
                    actualizar_estado(telefonoCliente, "esperando_comprobante", False)
                    actualizar_estado(telefonoCliente, "id_pedido_actual", None)
                else:
                    enviar_con_delay(telefonoCliente, [
                        "⚠️ No se encontró número de pedido",
                        PLANTILLA_MENU
                    ])
                
                return jsonify({"status": "success"}, 200)
            
            # Manejo de opciones del menú
            if mensaje.isdigit():
                opcion = mensaje
                
                if opcion in preguntas_frecuentes:
                    enviar_con_delay(telefonoCliente, [
                        preguntas_frecuentes[opcion]["respuesta"],
                        PLANTILLA_MENU
                    ])
                elif opcion == "7":
                    enviar(telefonoCliente, PLANTILLA_GESTION_PEDIDO)
                    actualizar_estado(telefonoCliente, "esperando_id_pedido", True)
                elif opcion == "8":
                    if obtener_estado(telefonoCliente, "id_pedido_actual"):
                        enviar(telefonoCliente, PLANTILLA_PROCESAR_PAGO)
                        actualizar_estado(telefonoCliente, "esperando_comprobante", True)
                    else:
                        enviar_con_delay(telefonoCliente, [
                            "⚠️ Primero debes confirmar un pedido (opción 7)",
                            PLANTILLA_MENU
                        ])
                elif opcion == "9":
                    enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
                else:
                    enviar(telefonoCliente, PLANTILLA_OPCION_INVALIDA)
                    enviar(telefonoCliente, PLANTILLA_MENU)
                
                return jsonify({"status": "success"}, 200)
            else:
                enviar(telefonoCliente, PLANTILLA_OPCION_INVALIDA)
                enviar(telefonoCliente, PLANTILLA_MENU)
                return jsonify({"status": "success"}, 200)
            
        elif 'image' in data['entry'][0]['changes'][0]['value']['messages'][0]:
            if obtener_estado(telefonoCliente, "esperando_comprobante"):
                image_id = data['entry'][0]['changes'][0]['value']['messages'][0]['image']['id']
                id_pedido = obtener_estado(telefonoCliente, "id_pedido_actual")
                
                if id_pedido:
                    image_url = obtener_url_imagen(image_id)
                    if image_url:
                        enviar_a_numero_estatico(f"📸 Comprobante en imagen para pedido: {id_pedido}")
                        enviar_imagen_a_numero_estatico(image_url, f"ID Pedido: {id_pedido}")
                        enviar_con_delay(telefonoCliente, [
                            PLANTILLA_PAGO_ENVIADO,
                            PLANTILLA_MENU
                        ])
                    else:
                        enviar(telefonoCliente, "⚠️ Error al procesar la imagen")
                else:
                    enviar(telefonoCliente, "⚠️ No se encontró número de pedido")
                
                actualizar_estado(telefonoCliente, "esperando_comprobante", False)
                actualizar_estado(telefonoCliente, "id_pedido_actual", None)
                return jsonify({"status": "success"}, 200)
            else:
                enviar_con_delay(telefonoCliente, [
                    "Por favor selecciona la opción 8 del menú para enviar comprobantes",
                    PLANTILLA_MENU
                ])
                return jsonify({"status": "success"}, 200)
        
        else:
            enviar(telefonoCliente, "⚠️ Solo se aceptan mensajes de texto o imágenes")
            enviar(telefonoCliente, PLANTILLA_MENU)
            return jsonify({"status": "success"}, 200)
            
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"status": "error"}, 500)

# ==============================================
# INICIO DE LA APLICACIÓN
# ==============================================

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)