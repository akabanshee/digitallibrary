import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from sql_agent import generate_sql_query, execute_sql_query, correct_column_names  # ✅ Buraya ekledik!
from web_search import search_web  
import random

# Çevre değişkenlerini yükleme
load_dotenv()

# Azure OpenAI istemcisini yapılandırma
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)


import random

import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from sql_agent import generate_sql_query, execute_sql_query, correct_column_names  # ✅ SQL Agent
from web_search import search_web  # ✅ Web Arama Fonksiyonu
import random

# Çevre değişkenlerini yükleme
load_dotenv()

# Azure OpenAI istemcisini yapılandırma
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

def chat_with_user(user_input):
    """
    Uses OpenAI's function calling feature to determine if an SQL query is needed.
    """
    try:
        system_message = {
            "role": "system",
            "content": (
                "You are a friendly and engaging AI assistant. "
                "When responding, use a natural, conversational tone. "
                "If the user's question requires an SQL lookup, generate an SQL query and return a well-formatted response. "
                "Start responses dynamically based on the context. "
                "For example: "
                "If it's about book count: 'There are a total of X books in the collection. 📚' "
                "If it's about book details: 'Here’s the book you’re looking for!' "
                "If it’s a general search: 'I found some great options for you. Let’s take a look!' "
                "DO NOT start every response with the same phrase like 'Here’s what I found for you!'. "
                "Always end responses with a polite follow-up like 'Let me know if you need anything else! 😊' or 'How else can I assist you today? 🤖'."
            )
        }

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

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                system_message,
                {"role": "user", "content": user_input}
            ],
            functions=function_definitions,
            function_call="auto",
            max_tokens=300
        )

        response_message = response.choices[0].message
        function_call = response_message.function_call  

        if function_call and function_call.name == "execute_sql_query":
            sql_query = json.loads(function_call.arguments)["sql_query"]

            if not sql_query:
                return {"status": "error", "message": "Generated SQL query is empty"}

            corrected_sql = correct_column_names(sql_query)

            if not corrected_sql:
                return {"status": "error", "message": "Final SQL query is empty after correction"}

            sql_result = execute_sql_query(corrected_sql)

            if isinstance(sql_result, dict) and sql_result.get("status") == "error":
                return {"status": "error", "message": "Oops! Something went wrong while searching for books. Try asking in a different way."}

            # 📌 **GPT’yi Kullanarak Sonucu Doğru Formatlama (Tool Calling ile)**
            formatted_response = client.chat.completions.create(
                model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    system_message,
                    {"role": "user", "content": f"Format this SQL result into a user-friendly response:\n\n{sql_result}"}
                ],
                max_tokens=500
            )

            return {
                "status": "success",
                "type": "Chat",
                "data": formatted_response.choices[0].message.content
            }

        else:
            return {"status": "success", "type": "Chat", "data": response_message.content}

    except Exception as e:
        print(f"❌ Error in chat_with_user: {e}")
        return {"status": "error", "message": "Oops! Something went wrong on our side. Please try again later."}
