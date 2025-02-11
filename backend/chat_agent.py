import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
from sql_agent import generate_sql_query, execute_sql_query
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
    Processes user input and routes it accordingly.
    """
    try:
        classification_response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are an AI assistant. Classify the user's query as either 'SQL' or 'Chat'. "
                 "If the question requires retrieving data (like counting books, listing books, etc.), classify it as 'SQL'. "
                 "Otherwise, classify it as 'Chat'. Only reply with 'SQL' or 'Chat'."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=10
        )

        classification = classification_response.choices[0].message.content.strip()
        print(f"Classification: {classification}")

        if classification == "SQL":
            sql_query = generate_sql_query(user_input)
            print(f"Generated SQL Query: {sql_query}")

            sql_result = execute_sql_query(sql_query)
            print(f"SQL Execution Result: {sql_result}")

            return {
                "status": "success",
                "type": "SQL",
                "data": sql_result
            }

        elif classification == "Chat":
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Always reply in English."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=300
            )
            structured_response = response.choices[0].message.content.strip()
            print(f"Chat Response: {structured_response}")

            return {
                "status": "success",
                "type": "Chat",
                "data": structured_response
            }

        else:
            return {
                "status": "error",
                "message": "Query classification failed."
            }

    except Exception as e:
        print(f"Error in chat_with_user: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
