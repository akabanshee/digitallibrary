import os
import pyodbc  # Azure SQL bağlantısı için
from openai import AzureOpenAI
from dotenv import load_dotenv
import re

# .env içeriğini yükle
load_dotenv()

# Azure OpenAI istemcisi
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# Eğer bir yerde kullanmıyorsanız tamamen silebilirsiniz
DATABASE_URL = os.getenv("DATABASE_URL")

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
    SQL sorgusunda yalnızca yanlış sütun adlarını doğru olanlarla değiştirir.
    """
    sql_query = sql_query.replace("`", "")  # Gereksiz karakterleri kaldır

    # Yanlış sütun adlarını düzelt
    for wrong_name, correct_name in COLUMN_NAME_FIXES.items():
        # Sadece sütun adlarını düzeltmek için tablo adlarını değiştirmemeyi sağla
        pattern = rf"\b{wrong_name}\b"
        sql_query = re.sub(pattern, correct_name, sql_query)
    
    return sql_query

def get_pyodbc_connection_string():
    """
    .env dosyasında tanımlı ortam değişkenlerinden pyodbc için bağlantı dizesi oluşturur.
    """
    server = os.getenv("DATABASE_SERVER")
    database = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PASSWORD")
    encrypt = os.getenv("DATABASE_ENCRYPT", "no")
    trust_cert = os.getenv("DATABASE_TRUST_SERVER_CERTIFICATE", "yes")
    timeout = os.getenv("DATABASE_TIMEOUT", "60")

    return (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server=tcp:{server},1433;"
        f"Database={database};"
        f"Uid={user};"
        f"Pwd={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust_cert};"
        f"Connection Timeout={timeout};"
    )

def test_database_connection():
    """
    Veritabanı bağlantısını test eder ve sonucu döner.
    """
    try:
        conn_string = get_pyodbc_connection_string()
        print(f"Testing connection with: {conn_string}")
        conn = pyodbc.connect(conn_string)
        print("Connection successful!")
        conn.close()
    except pyodbc.OperationalError as e:
        print(f"OperationalError: {e}")
    except pyodbc.Error as e:
        print(f"SQL Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

def clean_sql_query(sql_query):
    """
    OpenAI tarafından oluşturulan SQL sorgularındaki gereksiz işaretlemeleri temizler.
    """
    sql_query = sql_query.strip()

    # Eğer OpenAI'nin döndürdüğü SQL bloğu içinde ```sql veya ``` varsa temizle
    sql_query = re.sub(r"^```sql\s*", "", sql_query)  # "```sql" ile başlayan satırları temizle
    sql_query = re.sub(r"^```\s*", "", sql_query)     # "```" ile başlayan satırları temizle
    sql_query = sql_query.strip()
    
    return sql_query

def generate_sql_query(user_input):
    """
    Kullanıcının girdisine göre SQL sorgusu oluşturur ve loglar.
    """
    try:
        system_message = (
            "You are an AI assistant that generates SQL queries from natural language questions. "
            "The database contains two tables: 'books' and 'authors'. "
            "The 'books' table has the following columns: id (int), title (varchar), author_id (int), "
            "year (int), category (varchar), file_path (varchar), pricing (float). "
            "The 'authors' table has the following columns: id (int), first_name (varchar), last_name (varchar), "
            "date_of_birth (varchar), nationality (varchar). "
            "For example, if the question asks about a book's price, use 'pricing' as the column name. "
            "If the question is about authors, use the 'authors' table and its respective column names. "
            "Ensure the generated query is syntactically correct for SQL Server."
        )

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150,
        )
        
        raw_sql_query = response.choices[0].message.content.strip()
        print(f"Generated SQL Query (Raw): {raw_sql_query}")  # OpenAI'den gelen ham sorguyu göster

        # Temizlenmiş SQL sorgusunu al
        cleaned_query = clean_sql_query(raw_sql_query)
        print(f"Cleaned SQL Query: {cleaned_query}")  # Temizlenmiş SQL sorgusunu göster

        # Yanlış sütun adlarını düzelterek döndür
        corrected_query = correct_column_names(cleaned_query)
        print(f"Final SQL Query: {corrected_query}")  # Düzeltmeden sonra logla

        return corrected_query
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return f"OpenAI API Error: {str(e)}"

def execute_sql_query(sql_query):
    """
    SQL sorgusunu çalıştırır ve sonuçları döner.
    """
    try:
        print(f"Executing SQL Query: {sql_query}")  # Sorguyu çalıştırmadan önce logla

        conn_string = get_pyodbc_connection_string()
        conn = pyodbc.connect(conn_string, timeout=60)

        cursor = conn.cursor()
        cursor.execute(sql_query)  # Sorguyu çalıştır
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        print(f"Query Results: {results}")  # Sorgu sonuçlarını logla
        return results
    except pyodbc.OperationalError as e:
        print(f"SQL Timeout Error: {e}")
        return "SQL Timeout Error: Server is unreachable or connection took too long."
    except pyodbc.Error as e:
        print(f"SQL Execution Error: {e}")
        return f"SQL Execution Error: {e}"
    except Exception as e:
        print(f"Unexpected Error in execute_sql_query: {e}")
        return f"Unexpected Error: {e}"
