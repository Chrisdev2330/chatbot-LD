from heyoo import WhatsApp
from config import Config
import asyncio

class WhatsAppService:
    def __init__(self):
        self.token = Config.WHATSAPP_TOKEN
        self.phone_id = Config.WHATSAPP_PHONE_ID
        self.client = WhatsApp(self.token, self.phone_id)
    
    async def send_message(self, phone: str, message: str):
        try:
            # phone = phone.replace("521", "58")  # Descomenta si necesitas formatear el número
            await asyncio.to_thread(
                self.client.send_message,
                message=message,
                recipient_id=phone
            )
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False