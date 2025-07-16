from openai import OpenAI
from config import GEMINI_API_KEY

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=GEMINI_API_KEY
)

class GeminiAI:
    @staticmethod
    def generate_response(prompt, user_message):
        try:
            completion = client.chat.completions.create(
                model="google/gemini-2.0-flash-exp:free",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "Disculpa, hubo un error al procesar tu mensaje. Por favor intenta nuevamente."