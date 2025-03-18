# chat_agent.py

import os
import json
import traceback
from openai import AzureOpenAI
from dotenv import load_dotenv

# Manager'i import ediyoruz
from manager import Manager

# Çevre değişkenlerini yükleme
load_dotenv()

# Azure OpenAI istemcisini yapılandırma
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# Kullanıcıların konuşmalarını saklayacak bir sözlük
chat_sessions = {}

def _base_chat_llm(user_input, user_id="default_user"):
    """
    Bu 'iç' fonksiyon, OpenAI ile sohbet çağrısını yapar.
    Eski 'chat_with_user' fonksiyonunun mantığı korunur,
    ancak function_call geldiğinde SQL sorgusu tetiklemek yerine
    sadece function_call bilgisini döndürür.
    """
    try:
        # Kullanıcının geçmiş konuşmalarını al
        if user_id not in chat_sessions:
            chat_sessions[user_id] = []

        chat_history = chat_sessions[user_id]

        # Sisteme ait mesaj (prompt ayarları)
        system_message = {
            "role": "system",
            "content": (
                "You are a friendly and engaging AI assistant. "
                "When responding, use a natural, conversational tone. "
                "If the user's question requires an SQL lookup, generate an SQL query and return a well-formatted response. "
            )
        }

        # SQL sorgusu gibi fonksiyon çağrılarını tanımlıyoruz
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

        # Mesaj dizisini oluştur
        messages = [system_message] + chat_history + [
            {"role": "user", "content": user_input}
        ]

        # OpenAI ChatCompletion isteğini yap
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=messages,
            functions=function_definitions,
            function_call="auto",
            max_tokens=500
        )

        response_message = response.choices[0].message
        function_call = response_message.function_call

        # Eğer bir function_call varsa, sorguyu burada çalıştırmak yerine
        # sadece 'function_call' verisini döndürüyoruz.
        if function_call:
            # Örnek: sohbet geçmişine not düşmek isteyebilirsiniz (isteğe bağlı)
            chat_history.append({
                "role": "assistant",
                "content": f"Function call: {function_call}"
            })
            chat_sessions[user_id] = chat_history

            return {
                "status": "success",
                "type": "Chat",
                "data": "",  # Şimdilik metin cevabı yok
                "function_call": {
                    "name": function_call.name,
                    "arguments": json.loads(function_call.arguments)
                }
            }
        else:
            # Hiç function_call yoksa, normal metin cevabı
            chat_history.append({"role": "assistant", "content": response_message.content})
            chat_sessions[user_id] = chat_history

            return {
                "status": "success",
                "type": "Chat",
                "data": response_message.content,
                "function_call": None
            }

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ Error in _base_chat_llm:\n{error_details}")
        return {
            "status": "error",
            "message": "Oops! Something went wrong on our side. Please try again later."
        }

# Manager örneğini oluşturuyoruz
manager = Manager()

def chat_with_user(user_input, user_id="default_user"):
    """
    'main.py' veya diğer dosyalardan import edilen, 'dışa açık' fonksiyon.
    Arka planda Manager'ı kullanarak _base_chat_llm'i çağırır.
    Böylece function_call varsa SQL sorgusunu Manager orkestre eder.
    """
    return manager.handle_chat_message(_base_chat_llm, user_input, user_id)
