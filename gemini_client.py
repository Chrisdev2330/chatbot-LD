from openai import OpenAI
from config import GEMINI_API_KEY, GEMINI_BASE_URL, GEMINI_MODEL

class GeminiClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=GEMINI_BASE_URL,
            api_key=GEMINI_API_KEY
        )
        
    def generate_response(self, prompt, user_message):
        try:
            with open('prompt.txt', 'r') as f:
                system_prompt = f.read()
                
            completion = self.client.chat.completions.create(
                model=GEMINI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Disculpas, hubo un error procesando tu solicitud. Por favor intenta nuevamente."

# Global Gemini client instance
gemini_client = GeminiClient()