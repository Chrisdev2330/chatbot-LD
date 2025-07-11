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

WHATSAPP_TOKEN = 'EAAOxgq6y2fwBPE7uSprf6b8R9o11T4OaRQVFgEmxFeZA6S797ZBqx4364yZCXhq8jwqArtK9ZCreyO6KZAgcx1R04CcMjjZCKxYhjl4adNBHneTwz6SPj18nBWbhv7u2GanUn0OpdNWdFWQmjHqOdKTJmiadeu3oOudzmfKW9jU7fIK26eeff3BCSklGKyjev5xQZDZD'
WHATSAPP_NUMBER_ID = '730238483499494'
NUMERO_ESTATICO = "584241220797"

# ==============================================
# BASE DE CONOCIMIENTO
# ==============================================

preguntas_frecuentes = {
    "1": {
        "pregunta": "1- Sobre Nosotros",
        "respuesta": """Somos una empresa con experiencia en el mercado desde 2015, fundada por Luciana Díaz..."""
    },
    "2": {
        "pregunta": "2- Forma de pago mayorista",
        "respuesta": "- Únicamente contado efectivo billete en el local\n- Transferencia bancaria"
    },
    "3": {
        "pregunta": "3- Dirección y horario",
        "respuesta": "📍 Dirección: Alsina 455, San Miguel de Tucumán\n⏰ Horario: \n   - Mañana: 09:00 a 13:00\n   - Tarde: 17:00 a 21:00"
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
1- ¿Quiénes son LD Make Up?
2- ¿Cuál es la forma de pago en venta por mayor?
3- ¿En qué dirección y horario puedo retirar mi pedido?
4- ¿Realizan envíos dentro de la provincia de Tucumán?
5- ¿Cuánto tarda en llegar mi pedido por correo argentino?
6- ¿Cuál es el horario de atención?
7- Gestionar pedido
8- Procesar pago
9- Salir"""

PLANTILLA_GESTION_PEDIDO = """📦 *Gestión de Pedido*

Escribe el *ID de tu pedido* (recibido en la notificación) o *menu* para volver:"""

PLANTILLA_PROCESAR_PAGO = """💳 *Procesar Pago*

Envía:
- *efectivo* (para pago en efectivo)
- *Enlace de Google Drive* con el comprobante
- *menu* (para volver al menú)"""

PLANTILLA_CONFIRMACION_ENVIADA = """✅ Confirmación enviada para el pedido *{}*"""

PLANTILLA_PAGO_ENVIADO = """✅ Pago recibido. Validación en proceso."""

PLANTILLA_DESPEDIDA = """¡Gracias por contactar a LD Make Up! 💖

Para cualquier otra consulta, ¡no dudes en escribirnos!"""

PLANTILLA_OPCION_INVALIDA = """⚠️ Por favor escribe:
- 'efectivo' (pago en efectivo)
- Un enlace de Google Drive
- 'menu' (volver al menú)"""

# ==============================================
# FUNCIONES PRINCIPALES
# ==============================================

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
        telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        
        if 'text' in data['entry'][0]['changes'][0]['value']['messages'][0]:
            mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'].lower()
            
            # Manejo de saludos
            if any(palabra in mensaje for palabra in ["hola", "hi", "hello"]):
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
                        enviar_a_numero_estatico(f"Pago en efectivo confirmado - ID Pedido: {id_pedido}")
                        enviar_con_delay(telefonoCliente, [
                            PLANTILLA_PAGO_ENVIADO,
                            PLANTILLA_MENU
                        ])
                    elif mensaje.startswith(('http://', 'https://')):
                        enviar_a_numero_estatico(f"Comprobante Drive recibido - ID: {id_pedido}\nEnlace: {mensaje}")
                        enviar_con_delay(telefonoCliente, [
                            PLANTILLA_PAGO_ENVIADO,
                            PLANTILLA_MENU
                        ])
                    elif mensaje == "menu":
                        enviar(telefonoCliente, PLANTILLA_MENU)
                    else:
                        enviar(telefonoCliente, PLANTILLA_OPCION_INVALIDA)
                        enviar(telefonoCliente, PLANTILLA_PROCESAR_PAGO)
                        return jsonify({"status": "success"}, 200)
                    
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
            
        else:
            # Si no es texto (ej. imagen, audio, etc.)
            enviar(telefonoCliente, "⚠️ Por favor envía solo texto según las opciones del menú")
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