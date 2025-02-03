import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from sql_agent import generate_sql_query, execute_sql_query

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
    Kullanıcıdan gelen girdiyi analiz eder ve gerekirse SQL Agent'a yönlendirir.
    """
    try:
        # AI'ya sorunun SQL gerektirip gerektirmediğini soralım
        classification_response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are an AI assistant. Your task is to classify whether the user's query requires an SQL database lookup or not. Answer only with 'SQL' or 'Chat'."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=10
        )
        
        classification = classification_response.choices[0].message.content.strip()
        print(f"Classification: {classification}")  # Loglama

        # Eğer SQL sorgusu gerektiriyorsa, SQL Agent'a yönlendir
        if classification == "SQL":
            sql_query = generate_sql_query(user_input)  # SQL sorgusu oluştur
            print(f"Generated SQL Query: {sql_query}")  # SQL sorgusunu logla
            sql_result = execute_sql_query(sql_query)  # Sorguyu çalıştır
            return sql_result if sql_result else "No matching data found in the database."
        
        # Eğer sadece chat yanıtı gerekliyse, normal cevap ver
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error in chat_with_user: {e}")
        return f"Error: {str(e)}"
