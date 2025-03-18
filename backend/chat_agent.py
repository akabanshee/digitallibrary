# chat_agent.py

import os
import json
import traceback
from openai import AzureOpenAI
from dotenv import load_dotenv

# Manager'i import ediyoruz
from manager import Manager

# Çevre değişkenlerini yükleme (örneğin AZURE_OPENAI_API_KEY, vb. .env'den)
load_dotenv()

# Azure OpenAI istemcisini yapılandırma
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),        # .env'de tanımlı API Key
    api_version="2024-07-01-preview",                 # Azure OpenAI API sürümü
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") # Azure endpoint
)

# Kullanıcıların konuşmalarını saklayacak bir sözlük
# Her kullanıcı için bir 'chat_history' listesi tutuyoruz
chat_sessions = {}

def _base_chat_llm(user_input, user_id="default_user"):
    """
    Bu 'iç' fonksiyon, OpenAI ile sohbet (chat) çağrısını yapar.
    - Daha önce 'chat_with_user' fonksiyonunun içinde SQL sorgusu da tetikleniyordu,
      ancak artık Manager'e taşıdığımız için burada function_call dönerse
      sadece function_call bilgisini verip geri çekiliyoruz.

    Parametreler:
      - user_input: Kullanıcıdan gelen sorgu veya mesaj
      - user_id: Oturum kimliği (varsayılan "default_user")

    Dönüş:
      - Bir sözlük: 
        {
          "status": "success" or "error",
          "type": "Chat",
          "data": "...",                # LLM'den gelen metinsel cevap
          "function_call": {...} or None
        }
    """
    try:
        # 1) Mevcut oturum var mı, yoksa yeni oluştur
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []

        # Kullanıcıya ait konuşma geçmişini al
        chat_history = chat_sessions[user_id]

        # 2) System mesajı: ChatGPT'ye rol ve içerik veriyoruz
        system_message = {
            "role": "system",
            "content": (
                "You are a friendly and engaging AI assistant. "
                "When responding, use a natural, conversational tone. "
                "If the user's question requires an SQL lookup, generate an SQL query and return a well-formatted response. "
            )
        }

        # 3) Mümkün olabilecek fonksiyon çağrılarını tanımlıyoruz
        #    (burada sadece 'execute_sql_query' var)
        function_definitions = [
            {
                "name": "execute_sql_query",
                "description": "Executes an SQL query and returns structured results.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "The SQL query to execute, such as 'SELECT COUNT(*) FROM books'."
                        }
                    },
                    "required": ["sql_query"]
                }
            }
        ]

        # 4) Mesaj listesi oluştur (system mesaj + geçmiş + yeni user mesajı)
        messages = [system_message] + chat_history + [
            {"role": "user", "content": user_input}
        ]

        # 5) OpenAI ChatCompletion isteğini yap
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),   # Model adı .env'den
            messages=messages,                           # Mesajlar
            functions=function_definitions,              # Tanımlı fonksiyonlar
            function_call="auto",                        # Otomatik function call
            max_tokens=500
        )

        # 6) Dönen cevaptan 'function_call' olup olmadığını okuyalım
        response_message = response.choices[0].message
        function_call = response_message.function_call

        if function_call:
            # 7) Eğer function_call varsa, SQL sorgusunu direkt tetiklemek yerine
            #    sadece function_call bilgisini geriye döndürürüz.
            #    Manager bu bilgiyi alıp SQL sorgusunu çalıştıracak.

            # İsteğe bağlı olarak, geçmişe "function_call" bilgisini not düşebiliriz:
            chat_history.append({
                "role": "assistant",
                "content": f"Function call: {function_call}"
            })
            chat_sessions[user_id] = chat_history

            return {
                "status": "success",
                "type": "Chat",
                "data": "",  # Metin cevabı şimdilik yok, function_call var
                "function_call": {
                    "name": function_call.name,
                    "arguments": json.loads(function_call.arguments)
                }
            }
        else:
            # 8) Hiç function_call yoksa bu bir normal metin cevabıdır
            #    ChatGPT cevabını 'content' içinde gönderir
            chat_history.append({"role": "assistant", "content": response_message.content})
            chat_sessions[user_id] = chat_history

            return {
                "status": "success",
                "type": "Chat",
                "data": response_message.content,
                "function_call": None
            }

    except Exception as e:
        # 9) Eğer herhangi bir aşamada hata olursa, geriye hata mesajı döndürüyoruz
        error_details = traceback.format_exc()
        print(f"❌ Error in _base_chat_llm:\n{error_details}")
        return {
            "status": "error",
            "message": "Oops! Something went wrong on our side. Please try again later."
        }


# Manager örneğini oluşturuyoruz (tek bir yerde)
manager = Manager()

def chat_with_user(user_input, user_id="default_user"):
    """
    'main.py' veya diğer dosyalardan import edilen, 'dışa açık' fonksiyon.

    - Arka planda, Manager'in handle_chat_message metodunu kullanıyoruz.
    - Manager'e '_base_chat_llm' fonksiyonunu iletiyoruz ki
      function_call varsa SQL sorgusunu Manager tetiklesin.

    Dönüş:
      - Manager'ın döndürdüğü sözlük (status, type, data vs.)
    """
    return manager.handle_chat_message(_base_chat_llm, user_input, user_id)
