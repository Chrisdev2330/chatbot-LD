from flask import Flask, jsonify, request
from heyoo import WhatsApp
import os
import requests
import time
from threading import Thread

app = Flask(__name__)

# ==============================================
# CONFIGURACIÓN INICIAL
# ==============================================

# Token de WhatsApp y ID de número de teléfono
WHATSAPP_TOKEN = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
WHATSAPP_NUMBER_ID = '730238483499494'
NUMERO_ESTATICO = "584241220797"  # Número al que se enviarán las confirmaciones

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

*Importante:* Todas las notificaciones de tus pedidos con su identificador llegarán a este medio. Si has creado un pedido, elige el punto 7 (Gestionar pedido) en el menú."""

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

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Recuerda que estamos en:
📍 Alsina 455, San Miguel de Tucumán
⏰ Lunes a Sábados: 09:00-13:00 y 17:00-21:00

Para cualquier otra consulta, ¡no dudes en escribirnos!

¡Que tengas un día hermoso! ✨"""

PLANTILLA_GESTION_PEDIDO = """📦 *Gestión de Pedido*

Si has creado un pedido, recibirás una notificación con su ID.

Escribe:
- El *ID de tu pedido* (el que recibiste en la notificación) si deseas confirmarlo
- *menu* si deseas volver al menú principal"""

PLANTILLA_PROCESAR_PAGO = """💳 *Procesar Pago*

Por favor:
- Envía una *imagen* con el comprobante de pago si fue por transferencia
- O escribe *efectivo* si fue por pago en efectivo
- O escribe *menu* para volver al menú principal

*Importante:* Solo usar esta opción si has confirmado el pedido (paso 7) y recibiste notificación de 'Esperando pago'"""

PLANTILLA_CONFIRMACION_ENVIADA = """✅ *Confirmación enviada*

El pedido con ID *{}* ha sido confirmado para su proceso de pago.

Pronto recibirás una notificación con los siguientes pasos."""

PLANTILLA_PAGO_ENVIADO = """✅ *Pago recibido*

El pago de tu pedido se está validando. Si todo está correcto, recibirás una notificación con el estado correspondiente en breves momentos."""

PLANTILLA_OPCION_INVALIDA = """⚠️ *Opción no válida*

Por favor:
- Envía una imagen del comprobante
- O escribe *efectivo* para pago en efectivo
- O escribe *menu* para volver al menú principal"""

# ==============================================
# FUNCIONES AUXILIARES
# ==============================================

def enviar_con_delay(telefono, mensajes, delay=2):
    """Envía múltiples mensajes con un delay entre ellos"""
    def enviar_mensajes():
        for mensaje in mensajes:
            enviar(telefono, mensaje)
            time.sleep(delay)
    
    Thread(target=enviar_mensajes).start()

# ==============================================
# MANEJO DE ESTADOS Y CONTEXTO
# ==============================================

estados_chats = {}

def actualizar_estado(telefono, clave, valor):
    """Actualiza el estado de la conversación para un número de teléfono específico"""
    if telefono not in estados_chats:
        estados_chats[telefono] = {}
    estados_chats[telefono][clave] = valor

def obtener_estado(telefono, clave, default=None):
    """Obtiene el estado actual de la conversación"""
    return estados_chats.get(telefono, {}).get(clave, default)

# ==============================================
# FUNCIONES DE ENVÍO DE MENSAJES
# ==============================================

def enviar(telefono, mensaje):
    """Envía un mensaje de texto a través de WhatsApp"""
    mensajeWa = WhatsApp(WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID)
    mensajeWa.send_message(mensaje, telefono)

def enviar_a_numero_estatico(mensaje):
    """Envía un mensaje al número estático de administración (+584241220797)"""
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
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def enviar_imagen_a_numero_estatico(image_url, caption=None):
    """Envía una imagen al número estático de administración (+584241220797)"""
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
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ==============================================
# MANEJO DE OPCIONES DEL MENÚ
# ==============================================

def manejar_opcion_menu(telefono, opcion):
    """Maneja la selección de opciones del menú principal"""
    if opcion in preguntas_frecuentes:
        # Opciones del 1 al 6
        enviar_con_delay(telefono, [
            preguntas_frecuentes[opcion]["respuesta"],
            PLANTILLA_MENU
        ])
        
    elif opcion == "7":
        # Gestionar pedido
        enviar(telefono, PLANTILLA_GESTION_PEDIDO)
        actualizar_estado(telefono, "esperando_id_pedido", True)
        
    elif opcion == "8":
        # Procesar pago - Verificar si tiene un ID de pedido
        id_pedido = obtener_estado(telefono, "id_pedido_actual")
        if id_pedido:
            enviar(telefono, PLANTILLA_PROCESAR_PAGO)
            actualizar_estado(telefono, "esperando_comprobante_pago", True)
        else:
            enviar_con_delay(telefono, [
                "⚠️ Primero debes confirmar un pedido (opción 7) antes de procesar el pago.",
                PLANTILLA_MENU
            ])
        
    elif opcion == "9":
        # Salir
        enviar(telefono, PLANTILLA_DESPEDIDA)
        
    else:
        enviar(telefono, "⚠️ Opción no válida. Por favor, escribe un número del 1 al 9.")
        enviar(telefono, PLANTILLA_MENU)

# ==============================================
# ENDPOINT PRINCIPAL
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
    except:
        return jsonify({"status": "error"}, 400)

    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    
    # Manejar diferentes tipos de mensajes (texto, imagen, etc.)
    if 'text' in data['entry'][0]['changes'][0]['value']['messages'][0]:
        mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].lower()
    elif 'image' in data['entry'][0]['changes'][0]['value']['messages'][0]:
        # Si es una imagen, manejarla para el proceso de pago
        if obtener_estado(telefonoCliente, "esperando_comprobante_pago"):
            image_id = data['entry'][0]['changes'][0]['value']['messages'][0]['image']['id']
            image_url = f"https://graph.facebook.com/v18.0/{image_id}/"
            
            # Obtener la URL de la imagen
            headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
            image_data = requests.get(image_url, headers=headers).json()
            image_download_url = image_data.get('url', '')
            
            if image_download_url:
                # Enviar la imagen al número estático
                enviar_imagen_a_numero_estatico(
                    image_download_url,
                    caption=f"Comprobante de pago para el pedido con ID: {obtener_estado(telefonoCliente, 'id_pedido_actual')}"
                )
                
                # Confirmar al usuario
                enviar_con_delay(telefonoCliente, [
                    PLANTILLA_PAGO_ENVIADO,
                    PLANTILLA_MENU
                ])
                
                # Resetear estados
                actualizar_estado(telefonoCliente, "esperando_comprobante_pago", False)
                actualizar_estado(telefonoCliente, "id_pedido_actual", None)
            
            return jsonify({"status": "success"}, 200)
        else:
            enviar_con_delay(telefonoCliente, [
                "Por favor, selecciona una opción del menú primero.",
                PLANTILLA_MENU
            ])
            return jsonify({"status": "success"}, 200)
    else:
        # Otros tipos de mensajes no soportados
        enviar_con_delay(telefonoCliente, [
            "Solo puedo procesar texto o imágenes. Por favor, selecciona una opción del menú.",
            PLANTILLA_MENU
        ])
        return jsonify({"status": "success"}, 200)

    # ==============================================
    # MANEJO DE FLUJOS CONVERSACIONALES
    # ==============================================
    
    # Saludos iniciales
    if any(palabra in mensaje for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar_con_delay(telefonoCliente, [
            PLANTILLA_BIENVENIDA,
            PLANTILLA_MENU
        ])
        return jsonify({"status": "success"}, 200)
    
    # Despedidas
    if any(palabra in mensaje for palabra in ["adiós", "chao", "bye", "hasta luego", "nos vemos", "hasta pronto", "salir"]):
        enviar(telefonoCliente, PLANTILLA_DESPEDIDA)
        return jsonify({"status": "success"}, 200)
    
    # Volver al menú
    if mensaje == "menu":
        enviar(telefonoCliente, PLANTILLA_MENU)
        # Resetear todos los estados
        actualizar_estado(telefonoCliente, "esperando_id_pedido", False)
        actualizar_estado(telefonoCliente, "esperando_comprobante_pago", False)
        actualizar_estado(telefonoCliente, "id_pedido_actual", None)
        return jsonify({"status": "success"}, 200)
    
    # Manejar confirmación de pedido (opción 7)
    if obtener_estado(telefonoCliente, "esperando_id_pedido"):
        # Guardar el ID del pedido
        actualizar_estado(telefonoCliente, "id_pedido_actual", mensaje)
        actualizar_estado(telefonoCliente, "esperando_id_pedido", False)
        
        # Enviar confirmación al número estático (+584241220797)
        mensaje_confirmacion = f"El pedido con ID {mensaje} fue confirmado para su proceso de pago."
        enviar_a_numero_estatico(mensaje_confirmacion)
        
        # Confirmar al usuario
        enviar_con_delay(telefonoCliente, [
            PLANTILLA_CONFIRMACION_ENVIADA.format(mensaje),
            PLANTILLA_MENU
        ])
        return jsonify({"status": "success"}, 200)
    
    # Manejar comprobante de pago (opción 8)
    if obtener_estado(telefonoCliente, "esperando_comprobante_pago"):
        id_pedido = obtener_estado(telefonoCliente, "id_pedido_actual")
        
        if mensaje == "efectivo":
            # Enviar confirmación de pago en efectivo al número estático (+584241220797)
            mensaje_pago = f"Se ha recibido pago en efectivo para el pedido con ID: {id_pedido}"
            enviar_a_numero_estatico(mensaje_pago)
            
            # Confirmar al usuario
            enviar_con_delay(telefonoCliente, [
                PLANTILLA_PAGO_ENVIADO,
                PLANTILLA_MENU
            ])
            
            # Resetear estados
            actualizar_estado(telefonoCliente, "esperando_comprobante_pago", False)
            actualizar_estado(telefonoCliente, "id_pedido_actual", None)
        elif mensaje == "menu":
            # Volver al menú si el usuario lo solicita
            enviar(telefonoCliente, PLANTILLA_MENU)
            actualizar_estado(telefonoCliente, "esperando_comprobante_pago", False)
        else:
            # Opción no válida
            enviar(telefonoCliente, PLANTILLA_OPCION_INVALIDA)
        
        return jsonify({"status": "success"}, 200)
    
    # Manejar opciones del menú principal (1-9)
    if mensaje.isdigit() and 1 <= int(mensaje) <= 9:
        manejar_opcion_menu(telefonoCliente, mensaje)
    else:
        enviar_con_delay(telefonoCliente, [
            "⚠️ Por favor, selecciona una opción válida del menú (1-9) o escribe 'menu' para ver las opciones.",
            PLANTILLA_MENU
        ])

    return jsonify({"status": "success"}, 200)

# ==============================================
# INICIO DE LA APLICACIÓN
# ==============================================

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)