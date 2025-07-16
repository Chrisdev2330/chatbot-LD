from openai import OpenAI

class GeminiClient:
    def __init__(self, api_key):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
    def generate_response(self, user_message):
        try:
            # Read the prompt from file
            with open('prompt.txt', 'r', encoding='utf-8') as f:
                system_prompt = f.read()
                
            completion = self.client.chat.completions.create(
                model="google/gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "Disculpas, hubo un error. Por favor contacta al +54 9 3813 02-1066 para asistencia."