import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from sql_agent import generate_sql_query, execute_sql_query, correct_column_names  # ✅ Buraya ekledik!
from web_search import search_web  

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
                "You are an AI assistant that determines whether a user's query needs an SQL database lookup. "
                "If the query requires an SQL operation (like counting books, listing books, or filtering books), "
                "call the 'execute_sql_query' function with the necessary SQL statement. "
                "IMPORTANT: The 'books' table DOES NOT have a column named 'genre'. "
                "Always use 'category' for filtering books by genre."
            )
        }

        function_definitions = [
            {
                "name": "execute_sql_query",
                "description": "Executes an SQL query on the books database and returns the result.",
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

            if not sql_query:  # Eğer SQL boşsa, hata döndür
                return {"status": "error", "message": "Generated SQL query is empty"}

            corrected_sql = correct_column_names(sql_query)

            if not corrected_sql:  # Eğer düzeltilmiş SQL boşsa, hata döndür
                return {"status": "error", "message": "Final SQL query is empty after correction"}

            sql_result = execute_sql_query(corrected_sql)
            return {"status": "success", "type": "SQL", "data": sql_result}

        else:
            return {"status": "success", "type": "Chat", "data": response_message.content}

    except Exception as e:
        print(f"❌ Error in chat_with_user: {e}")
        return {"status": "error", "message": str(e)}
