import os
import pyodbc  # Azure SQL bağlantısı için
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI istemcisi
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-05-13",
    azure_endpoint=os.getenv("OPENAI_API_ENDPOINT"),
)

# Azure SQL Veritabanı bağlantısı
DATABASE_URL = os.getenv("DATABASE_URL")

def generate_sql_query(user_input):
    """
    Kullanıcının girdisine göre SQL sorgusu oluşturur.
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "You are an AI that generates SQL queries based on user requests."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

def execute_sql_query(sql_query):
    """
    Azure SQL Veritabanında bir sorgu çalıştırır.
    """
    try:
        conn = pyodbc.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result if result else "No results found."
    except Exception as e:
        return f"SQL Execution Error: {str(e)}"
