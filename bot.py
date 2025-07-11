from google import genai
import time
import sys
from threading import Thread, Event

# Configuración API (la misma que usabas)
cliente = genai.Client(api_key="AIzaSyAKJHDBN8cXHtFKc0rzX9oGMsOTXvK1BgI")

# FAQs de PHP (solo 5 como pediste)
faqs_php = {
    "faqs": [
        {"question": "¿Qué es PHP?", "answer": "PHP es un lenguaje de scripting para desarrollo web, open source y muy popular."},
        {"question": "¿Cómo se instala PHP?", "answer": "Descárgalo desde php.net o usa XAMPP/WAMP para un stack completo."},
        {"question": "¿Qué significa PHP?", "answer": "Significa 'PHP: Hypertext Preprocessor' (es recursivo)."},
        {"question": "¿Cómo declaro una variable?", "answer": "Usa el símbolo $. Ejemplo: $edad = 25;"},
        {"question": "¿Qué frameworks hay?", "answer": "Los más usados: Laravel, Symfony, CodeIgniter y CakePHP."}
    ]
}

# --- Configuración de tiempo de inactividad (1 minuto) ---
inactividad_timeout = 60
ultima_interaccion = time.time()
salir_event = Event()

def temporizador_inactividad():
    while not salir_event.is_set():
        if time.time() - ultima_interaccion > inactividad_timeout:
            print("\n⏳ **Sesión cerrada por inactividad.**\n")
            sys.exit(0)
        time.sleep(5)

Thread(target=temporizador_inactividad, daemon=True).start()

# --- Generador de respuestas inteligentes ---
def generar_respuesta(pregunta):
    global ultima_interaccion
    ultima_interaccion = time.time()  # Reinicia temporizador

    # 1. Comando para salir
    if pregunta.lower() == "salir":
        print("\n✅ **Chat finalizado.** ¡Hasta pronto!\n")
        sys.exit(0)

    # 2. Buscar en FAQs de PHP
    for faq in faqs_php["faqs"]:
        if faq["question"].lower() in pregunta.lower():
            return faq["answer"]

    # 3. Si no es de PHP pero es técnico, usar la API
    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Eres un asistente experto en tecnología y programación. Responde de forma concisa.
            Pregunta: {pregunta}
            """
        )
        return respuesta.text

    except Exception as e:
        return f"🔴 Error: {str(e)}"

# --- Interfaz del Chat ---
print("""
****************************************************
           🤖 **Asistente de Tecnología**            
                                                        
  ▸ Pregunta sobre PHP (tengo FAQs rápidas).        
  ▸ También respondo dudas de programación, IT       
    y temas técnicos en general.                     
  ▸ Escribe 'salir' para cerrar el chat.            
****************************************************
""")

while True:
    try:
        user_input = input("\n👤 **Tú:** ")
        if user_input.strip():
            respuesta = generar_respuesta(user_input)
            print(f"\n🤖 **Bot:** {respuesta}")

    except KeyboardInterrupt:
        print("\n🚪 **Saliendo por comando...**")
        sys.exit(0)