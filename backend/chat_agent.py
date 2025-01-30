import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Çevre değişkenlerini yükleme
load_dotenv()

# Azure OpenAI istemcisini yapılandırma
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  # Azure API Anahtarı
    api_version="2024-07-01-preview",          # API sürümü
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")  # Azure Endpoint URL
)

def chat_with_user(user_input):
    """
    Kullanıcıdan gelen girdiye Azure OpenAI ile yanıt döndürür.
    """
    try:
        # Chat completions API çağrısı
        response = client.chat.completions.create(
            model="gpt-4o",  # Azure'daki deployment name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100  # Yanıtın maksimum uzunluğu
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
