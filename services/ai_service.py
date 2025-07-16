from openai import OpenAI
from config import Config
import os
import asyncio

class AIService:
    def __init__(self):
        self.client = OpenAI(
            base_url=Config.AI_BASE_URL,
            api_key=Config.OPENROUTER_API_KEY,
        )
        self.prompt = self._load_prompt()
    
    def _load_prompt(self):
        try:
            with open(Config.PROMPT_FILE, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading prompt file: {e}")
            return ""
    
    async def generate_response(self, message: str, conversation_history: list = None) -> str:
        try:
            messages = [
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": message}
            ]
            
            if conversation_history:
                messages = [{"role": "system", "content": self.prompt}] + conversation_history + [{"role": "user", "content": message}]
            
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=Config.AI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                extra_headers={
                    "HTTP-Referer": "https://ldmakeup.com",
                    "X-Title": "LD Make Up Bot",
                }
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Voy a consultar eso para ti 💖"