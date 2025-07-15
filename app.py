from flask import Flask, jsonify, request
from openai import OpenAI
from heyoo import WhatsApp
from datetime import datetime
import threading
import time
from functools import lru_cache

# Importaciones locales
from config import WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID, VERIFY_TOKEN, ADMIN_NUMBERS, DEEPSEEK_API_KEY
from templates import *
from session_manager import session_manager

app = Flask(__name__)

# Configuración de DeepSeek
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=DEEPSEEK_API_KEY,
)

# Cliente WhatsApp
mensajeWa = WhatsApp(WHATSAPP_TOKEN, WHATSAPP_NUMBER_ID)

# Cache para respuestas de IA
@lru_cache(maxsize=100)
def get_ai_response(prompt_text):
    try:
        with open('prompt.txt', 'r') as file:
            prompt_base = file.read()
        
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {"role": "system", "content": prompt_base},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=300
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error en IA: {e}")
        return None

# Función para enviar mensajes
def enviar(telefono, mensaje):
    try:
        mensajeWa.send_message(mensaje, telefono)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

# Función para notificar a administradores
def notificar_admin(mensaje):
    for admin in ADMIN_NUMBERS:
        enviar(admin, mensaje)

# Procesamiento de mensajes en segundo plano
def process_message(telefono, mensaje):
    try:
        session = session_manager.get_session(telefono)
        
        # Manejo de flujos especiales
        current_flow = session_manager.get_current_flow(telefono)
        
        if mensaje.lower() == 'salir':
            session_manager.end_session(telefono)
            enviar(telefono, PLANTILLA_DESPEDIDA)
            return
        
        # Flujo de confirmación
        if mensaje.lower() == 'confirmar' or current_flow == 'confirmar':
            handle_confirm_flow(telefono, mensaje)
            return
        
        # Flujo de pago
        if mensaje.lower() == 'mipago' or current_flow == 'mipago':
            handle_payment_flow(telefono, mensaje)
            return
        
        # Mensaje normal
        handle_normal_message(telefono, mensaje, session)
        
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        enviar(telefono, "⚠️ Ocurrió un error. Por favor intenta nuevamente.")

def handle_confirm_flow(telefono, mensaje):
    if not session_manager.get_current_flow(telefono) and mensaje.lower() == 'confirmar':
        session_manager.set_flow(telefono, 'confirmar')
        enviar(telefono, PLANTILLA_CONFIRMAR)
        return
    
    if mensaje.lower() == 'cancelar':
        session_manager.exit_flow(telefono)
        enviar(telefono, "Has salido del proceso de confirmación.")
        return
    
    if mensaje.lower() == 'regresar':
        session_manager.exit_flow(telefono)
        enviar(telefono, "Volviendo al menú principal. ¿En qué más puedo ayudarte?")
        return
    
    # Validar formato del ID
    if mensaje.startswith('#') and len(mensaje) > 1:
        pedido_id = mensaje[1:]
        session_manager.set_flow_data(telefono, 'pedido_id', pedido_id)
        
        # Notificar al cliente
        enviar(telefono, PLANTILLA_CONFIRMACION_EXITOSA.format(pedido_id))
        
        # Notificar al admin
        notif_msg = NOTIF_CONFIRMACION_ADMIN.format(
            telefono,
            pedido_id,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        )
        notificar_admin(notif_msg)
        
        session_manager.exit_flow(telefono)
    
    elif mensaje.startswith('-') and len(mensaje) > 1:
        pedido_id = mensaje[1:]
        
        # Notificar cancelación
        enviar(telefono, PLANTILLA_CANCELACION_EXITOSA.format(pedido_id))
        
        # Notificar al admin
        notif_msg = NOTIF_CANCELACION_ADMIN.format(
            telefono,
            pedido_id,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        )
        notificar_admin(notif_msg)
        
        session_manager.exit_flow(telefono)
    else:
        enviar(telefono, PLANTILLA_ID_INVALIDO)

def handle_payment_flow(telefono, mensaje):
    if not session_manager.get_current_flow(telefono) and mensaje.lower() == 'mipago':
        # Verificar si ya confirmó pedido
        if not session_manager.get_flow_data(telefono, 'pedido_id'):
            enviar(telefono, "⚠️ Primero debes confirmar tu pedido. Escribe *confirmar*")
            return
        
        session_manager.set_flow(telefono, 'mipago')
        enviar(telefono, PLANTILLA_MIPAGO.format(ADMIN_NUMBERS[0]))
        return
    
    if mensaje.lower() == 'cancelar':
        session_manager.exit_flow(telefono)
        enviar(telefono, "Has salido del proceso de pago.")
        return
    
    # Aquí podrías procesar el comprobante si lo implementas
    session_manager.exit_flow(telefono)
    enviar(telefono, PLANTILLA_PAGO_RECIBIDO.format(
        session_manager.get_flow_data(telefono, 'pedido_id')
    ))

def handle_normal_message(telefono, mensaje, session):
    # Contador de mensajes fuera de contexto
    if 'out_of_context' not in session['data']:
        session['data']['out_of_context'] = 0
    
    # Respuestas automáticas para saludos
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        enviar(telefono, PLANTILLA_BIENVENIDA)
        return
    
    # Respuesta de IA
    respuesta_ia = get_ai_response(mensaje)
    
    if not respuesta_ia or "no está relacionada" in respuesta_ia:
        session['data']['out_of_context'] += 1
        
        if session['data']['out_of_context'] >= 3:
            enviar(telefono, PLANTILLA_CONTACTO_HUMANO.format(ADMIN_NUMBERS[0]))
            session['data']['out_of_context'] = 0
        else:
            enviar(telefono, PLANTILLA_FUERA_CONTEXTO)
    else:
        session['data']['out_of_context'] = 0
        enviar(telefono, respuesta_ia)

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    try:
        if request.method == "GET":
            if request.args.get('hub.verify_token') == VERIFY_TOKEN:
                return request.args.get('hub.challenge')
            return "Error de autentificación."
        
        data = request.get_json()
        
        # Ignorar actualizaciones que no son mensajes
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}), 200
        
        telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        
        # Procesar en segundo plano para evitar timeout
        threading.Thread(target=process_message, args=(telefonoCliente, mensaje)).start()
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error en webhook: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)