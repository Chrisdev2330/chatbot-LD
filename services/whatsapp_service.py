from heyoo import WhatsApp
from config import Config

class WhatsAppService:
    def __init__(self):
        self.token = Config.WHATSAPP_TOKEN
        self.phone_id = Config.WHATSAPP_PHONE_ID
        self.client = WhatsApp(self.token, self.phone_id)
    
    def send_message(self, to: str, message: str):
        try:
            # Reemplazar "521" por "58" si es necesario (para números venezolanos)
            # to = to.replace("521", "58")
            self.client.send_message(message, to)
        except Exception as e:
            print(f"Error al enviar mensaje a {to}: {str(e)}")
            # Podrías implementar un reintento aquí si lo deseas

# Instancia global del servicio de WhatsApp
whatsapp_service = WhatsAppService()