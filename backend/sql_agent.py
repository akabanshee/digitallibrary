import os
import json
import pyodbc
import re
from openai import AzureOpenAI
from dotenv import load_dotenv

# .env içeriğini yükle
load_dotenv()

# Azure OpenAI istemcisi
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# Yanlış sütun adlarını düzeltmek için bir eşleme sözlüğü
COLUMN_NAME_FIXES = {
    "price": "pricing",
    "author": "author_id",
    "first name": "first_name",
    "last name": "last_name",
    "date of birth": "date_of_birth",
    "nationality": "nationality",
}

def correct_column_names(sql_query):
    """
    Corrects incorrect column names in SQL queries.
    """
    COLUMN_NAME_FIXES = {
        "price": "pricing",
        "author_id": "author",
        "first name": "first_name",
        "last name": "last_name",
        "date of birth": "date_of_birth",
        "nationality": "nationality",
        "genre": "category",
        "author": "authors"  # ✅ Books yerine 'authors' tablosunu kullan
    }

    # Eğer SQL sorgusunda nationality eksikse düzelt
    if "WHERE author LIKE '%Turkish%'" in sql_query:
        sql_query = sql_query.replace("WHERE author LIKE '%Turkish%'", "WHERE nationality = 'Turkish'")

    print(f"🔄 Corrected SQL Query: {sql_query}")  
    return sql_query


def get_pyodbc_connection_string():
    return (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server=tcp:{os.getenv('DATABASE_SERVER')},1433;"
        f"Database={os.getenv('DATABASE_NAME')};"
        f"Uid={os.getenv('DATABASE_USER')};"
        f"Pwd={os.getenv('DATABASE_PASSWORD')};"
        f"Encrypt={os.getenv('DATABASE_ENCRYPT', 'no')};"
        f"TrustServerCertificate={os.getenv('DATABASE_TRUST_SERVER_CERTIFICATE', 'yes')};"
        f"Connection Timeout={os.getenv('DATABASE_TIMEOUT', '60')};"
    )

def clean_sql_query(sql_query):
    sql_query = sql_query.strip()
    sql_query = re.sub(r"^```sql\s*", "", sql_query)
    sql_query = re.sub(r"^```\s*", "", sql_query)
    return sql_query.strip()

def generate_sql_query(user_input):
    """
    Generates an SQL query based on the user's input.
    """
    try:
        system_message = (
            "You are an AI that generates SQL queries in JSON format from natural language questions. "
            "Ensure that the response is a pure JSON object without markdown formatting. "
            "The database has two tables: 'books' and 'authors'. "
            "If the question asks about the number of books, use COUNT(*) from 'books'. "
            "If the question asks about the number of authors, use COUNT(*) from 'authors'. "
            "If filtering by nationality (e.g., 'Turkish authors'), use 'authors' table and WHERE nationality='Turkish'. "
            "If filtering by category (e.g., 'Drama books'), use 'books' table and WHERE category='Drama'. "
            "Output format: {\"query\": \"SQL_QUERY_HERE\"}"
        )

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150
        )

        raw_sql_query = response.choices[0].message.content.strip()
        print(f"Generated Raw SQL: {raw_sql_query}")

        cleaned_sql_query = re.sub(r"^```json\s*|\s*```$", "", raw_sql_query).strip()
        
        try:
            structured_query = json.loads(cleaned_sql_query)
            cleaned_query = clean_sql_query(structured_query.get("query", ""))
        except json.JSONDecodeError:
            print("❌ OpenAI response is not in JSON format!")
            return {"status": "error", "message": "Invalid JSON format from OpenAI response"}

        if not cleaned_query:
            return {"status": "error", "message": "Generated SQL query is empty"}

        corrected_query = correct_column_names(cleaned_query)
        print(f"Final SQL Query: {corrected_query}")

        return corrected_query

    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return {"status": "error", "message": str(e)}




def execute_sql_query(sql_query):
    """
    SQL sorgusunu çalıştırır ve sonuçları JSON formatında döner.
    """
    try:
        if not isinstance(sql_query, str) or sql_query.strip() == "":
            print("❌ SQL Query string değil veya boş!")
            return {"status": "error", "message": "Invalid SQL query"}

        print(f"Executing SQL Query: {sql_query}")  # Log SQL Query
        conn_string = get_pyodbc_connection_string()
        conn = pyodbc.connect(conn_string, timeout=60)
        cursor = conn.cursor()
        cursor.execute(sql_query)

        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        print(f"SQL Results: {results}")  # Log the results

        if not results:
            return {"status": "error", "message": "No matching data found."}
        return results

    except pyodbc.OperationalError as e:
        print(f"SQL Timeout Error: {e}")
        return {"status": "error", "message": "SQL Timeout Error: Server is unreachable or connection took too long."}
    except pyodbc.Error as e:
        print(f"SQL Execution Error: {e}")
        return {"status": "error", "message": f"SQL Execution Error: {e}"}
    except Exception as e:
        print(f"Unexpected Error in execute_sql_query: {e}")
        return {"status": "error", "message": f"Unexpected Error: {e}"}

