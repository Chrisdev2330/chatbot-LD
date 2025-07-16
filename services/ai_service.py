from openai import OpenAI
from config import Config
import os
import asyncio

class AIService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY,
        )
        
        # Cargar el prompt de la tienda
        with open('templates/prompts/prompt.txt', 'r', encoding='utf-8') as file:
            self.tienda_prompt = file.read()

    async def generate_response(self, user_message: str) -> str:
        try:
            # Construir el mensaje completo con el prompt de la tienda
            full_prompt = f"{self.tienda_prompt}\n\nUsuario: {user_message}\nAsistente:"
            
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": self.tienda_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Disculpa, estoy teniendo problemas para procesar tu solicitud. Por favor intenta nuevamente más tarde. 💖 Error: {str(e)}"

# Instancia global del servicio de IA
ai_service = AIService()