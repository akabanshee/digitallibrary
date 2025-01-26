import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI yapılandırması
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-05-15"  # Azure OpenAI için doğru sürüm

deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

def generate_response(prompt, max_tokens=100):
    try:
        response = openai.Completion.create(
            engine=deployment_name,
            prompt=prompt,
            max_tokens=max_tokens
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"
