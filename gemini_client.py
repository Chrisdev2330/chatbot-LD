from openai import OpenAI
import os

class GeminiClient:
    def __init__(self, api_key):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    
    def generate_response(self, user_message, session):
        # Read prompt from file
        with open('prompt.txt', 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        full_prompt = f"""
        {prompt}
        
        Contexto de la conversación:
        - Usuario: {session.get('user_name', 'No proporcionado')}
        - Pedido actual: {session.get('order_id', 'Ninguno')}
        
        Mensaje del usuario: {user_message}
        """
        
        response = self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://ldmakeup.com",
                "X-Title": "LD Make Up Bot"
            },
            model="google/gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente virtual de LD Make Up."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content