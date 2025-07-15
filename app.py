from flask import Flask, jsonify, request
from google import genai
from templates import Templates
from session_manager import session_manager
from flows import Flows
from utils import send_message, send_admin_notification, read_prompt
import time

app = Flask(__name__)

# Configuración de Gemini
cliente = genai.Client(api_key=CONFIG["GEMINI_API_KEY"])
prompt_base = read_prompt()

@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    # Verificación GET
    if request.method == "GET":
        if request.args.get('hub.verify_token') == CONFIG["VERIFY_TOKEN"]:
            return request.args.get('hub.challenge')
        return "Error de autentificación.", 403
    
    # Procesamiento POST
    data = request.get_json()
    
    # Ignorar notificaciones de estado
    try:
        if 'messages' not in data['entry'][0]['changes'][0]['value']:
            return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error"}), 400
    
    # Extraer datos del mensaje
    telefonoCliente = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    mensaje = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    idWA = data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    timestamp = data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    
    # Obtener sesión del usuario
    session = session_manager.get_session(telefonoCliente)
    
    # Manejar cierre de sesión
    if mensaje.lower() == 'salir':
        session_manager.clear_session(telefonoCliente)
        send_message(telefonoCliente, Templates.session_closed())
        return jsonify({"status": "success"}), 200
    
    # Verificar si está en un flujo
    if session['current_flow'] == 'confirmar':
        if Flows.handle_confirm(telefonoCliente, telefonoCliente, mensaje):
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "success"}), 200
    
    if session['current_flow'] == 'mipago':
        if Flows.handle_payment(telefonoCliente, telefonoCliente, mensaje):
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "success"}), 200
    
    # Manejar comandos especiales
    if mensaje.lower() == 'confirmar':
        session_manager.set_current_flow(telefonoCliente, 'confirmar')
        send_message(telefonoCliente, Templates.confirm_prompt())
        return jsonify({"status": "success"}), 200
    
    if mensaje.lower() == 'mipago':
        if session.get('confirmed_order'):
            session_manager.set_current_flow(telefonoCliente, 'mipago')
            send_message(telefonoCliente, Templates.payment_prompt())
        else:
            send_message(telefonoCliente, Templates.need_confirmation_first())
        return jsonify({"status": "success"}), 200
    
    # Manejar mensajes iniciales
    if any(palabra in mensaje.lower() for palabra in ["hola", "hi", "hello", "buenos días", "buenas tardes", "buenas"]):
        send_message(telefonoCliente, Templates.welcome())
        session_manager.reset_unrelated_attempts(telefonoCliente)
        return jsonify({"status": "success"}), 200
    
    # Manejar despedidas
    if any(palabra in mensaje.lower() for palabra in ["adiós", "chao", "bye", "hasta luego", "nos vemos"]):
        send_message(telefonoCliente, Templates.goodbye())
        return jsonify({"status": "success"}), 200
    
    # Manejar agradecimientos
    if any(palabra in mensaje.lower() for palabra in ["gracias", "muchas gracias", "thanks", "thank you"]):
        send_message(telefonoCliente, "¡Es un placer ayudarte! 😊 ¿Necesitas algo más?")
        return jsonify({"status": "success"}), 200
    
    # Consultar a Gemini
    try:
        # Verificar si la consulta es muy genérica
        if len(mensaje.strip()) < 3 or mensaje.lower() in ["hola", "hi", "hello"]:
            send_message(telefonoCliente, "¿En qué puedo ayudarte sobre nuestros productos o servicios? 💄")
            return jsonify({"status": "success"}), 200
            
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Eres un asistente virtual profesional de LD Make Up, una tienda de maquillaje y productos de belleza en Tucumán, Argentina. 
            Responde de forma amable, profesional y atractiva con información veraz basada en estos datos:
            
            {prompt_base}
            
            Instrucciones:
            1. Usa emojis moderados para hacer las respuestas más atractivas (máximo 3-4 por mensaje)
            2. Sé conciso pero completo en las respuestas
            3. Si la pregunta no está relacionada con los temas del prompt, indica cortésmente que no puedes ayudar
            4. Para consultas muy personales o complejas, sugiere contactar al número de atención
            
            Pregunta: {mensaje}
            """
        )
        
        # Verificar si la respuesta es relevante
        respuesta_texto = respuesta.text.strip()
        if not respuesta_texto or "no tengo información" in respuesta_texto.lower():
            attempts = session_manager.increment_unrelated_attempts(telefonoCliente)
            send_message(telefonoCliente, Templates.unrelated_query(attempts))
        else:
            session_manager.reset_unrelated_attempts(telefonoCliente)
            send_message(telefonoCliente, respuesta_texto)
            
    except Exception as e:
        print(f"Error consultando Gemini: {e}")
        send_message(telefonoCliente, "Disculpas, hubo un error. Por favor contacta al +54 9 3813 02-1066 para asistencia.")
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)