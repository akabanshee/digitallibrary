import os
import json
import pyodbc
import re
from openai import AzureOpenAI
from dotenv import load_dotenv

# .env içeriğini yükle (DATABASE_TYPE gibi ortam değişkenlerini de okuyabilir)
load_dotenv()

# Azure OpenAI istemcisi (SQL sorgusu oluştururken istersen kullanılabilir)
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

# Yanlış sütun adlarını düzeltmek için bir eşleme sözlüğü
# (Aşağıdaki dictionary, örneğin 'genre' yerine 'category' gibi düzeltmeler yapabilir.)
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
    Yanlış veya eksik sütun adlarını düzeltir, ayrıca
    veritabanı türüne göre SQL sözdizimini düzenler (örneğin 'LIMIT' yerine 'TOP').
    """
    # Bu dictionary'yi fonksiyon içinde tanımlıyoruz ki
    # ek düzeltmeler yapılabilsin:
    COLUMN_NAME_FIXES = {
        "price": "pricing",
        "author_id": "author",
        "first name": "first_name",
        "last name": "last_name",
        "date of birth": "date_of_birth",
        "nationality": "nationality",
        "genre": "category"
    }

    # 1) Yanlış sütun adlarını doğru sütun adlarıyla değiştir
    for wrong_name, correct_name in COLUMN_NAME_FIXES.items():
        sql_query = sql_query.replace(wrong_name, correct_name)

    # 2) Veritabanı türüne göre (SQL Server) 'LIMIT 1' -> 'TOP 1' dönüşümü yap
    db_type = os.getenv("DATABASE_TYPE", "").lower()
    if "sql server" in db_type:
        # LIMIT 1 ifadesini TOP 1 ile değiştirmek için regex kullanıyoruz.
        # (Not: Bu basit bir yaklaşımdır, bazen SELECT'e 'TOP 1' eklemeniz gerekir)
        sql_query = re.sub(r"LIMIT\s+1", "TOP 1", sql_query, flags=re.IGNORECASE)

    print(f"✅ Corrected SQL Query: {sql_query}")  
    return sql_query

def get_pyodbc_connection_string():
    """
    .env dosyasındaki bilgilere göre pyodbc bağlantı stringi oluşturur.
    (SQL Server'a bağlanmak için gerekli sürücü ve parametreler)
    """
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
    """
    Kullanıcıya veya OpenAI'ye ait fazladan ```
    gibi ifadeleri temizler, sadece gerçek SQL sorgusunu bırakır.
    """
    sql_query = sql_query.strip()
    sql_query = re.sub(r"^```sql\s*", "", sql_query)
    sql_query = re.sub(r"^```\s*", "", sql_query)
    return sql_query.strip()

def generate_sql_query(user_input):
    """
    Kullanıcının doğal dildeki isteğine karşılık bir SQL sorgusu üretir.
    OpenAI ChatCompletion'u kullanarak, prompt içindeki kurallara
    uygun biçimde JSON formatında yanıt bekler:
      { "query": "SQL_QUERY_HERE" }
    """
    try:
        # System mesajı: OpenAI'ye "Sen bir SQL üreten AI'sın" diyor
        # ve çeşitli kurallar anlatıyor.
        system_message = (
            "You are an AI that generates SQL queries in JSON format from natural language questions. "
            "Ensure that the response is a pure JSON object without markdown formatting. "
            "The database has a 'books' table with the following columns: 'id', 'title', 'author', 'year', 'category', 'pricing'. "
            "IMPORTANT RULES: "
            "1️⃣ The 'books' table **DOES NOT** have a column named 'genre'. Use 'category' instead. "
            "2️⃣ If searching for the cheapest or most expensive book, do NOT use MIN() or MAX() with SELECT title. "
            "   Instead, use ORDER BY pricing ASC or DESC with LIMIT 1 (MySQL) or TOP 1 (SQL Server). "
            "3️⃣ Do NOT use 'AS' with 'LIMIT 1' in SQL queries. Do not write 'LIMIT 1 AS lowest_price'. "
            "4️⃣ If using an aggregate function like MIN() or MAX(), ensure that all non-aggregated columns are included in a GROUP BY clause. "
            "5️⃣ If the user is asking for **book price**, make sure to return only the 'pricing' column, like this: "
            "   SELECT pricing FROM books WHERE title = '...' "
            "6️⃣ If the user is asking for **book count**, make sure to return only the COUNT(*), like this: "
            "   SELECT COUNT(*) FROM books "
            "7️⃣ If the user is asking for **book details**, make sure to return all columns using: "
            "   SELECT title, author, year, category, pricing FROM books "
            "⚠️ DO NOT return COUNT(*) for book price questions! ⚠️"
            "Output format: {\"query\": \"SQL_QUERY_HERE\"}"
        )

        # OpenAI ChatCompletion
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_DEPLOYMENT_NAME"),  # .env'den model adı
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=150
        )

        # 1) OpenAI'den gelen yanıtı okuyoruz
        raw_sql_query = response.choices[0].message.content.strip()
        print(f"Generated Raw SQL: {raw_sql_query}")

        # 2) Yanıt içindeki ```json ...``` gibi formatlamaları temizle
        cleaned_sql_query = re.sub(r"^```json\s*|\s*```$", "", raw_sql_query).strip()
        
        # 3) JSON olup olmadığını kontrol edip parse ediyoruz
        try:
            structured_query = json.loads(cleaned_sql_query)
            # "query" alanını alıp fazladan Markdown veya ``` işaretlerini temizliyoruz
            cleaned_query = clean_sql_query(structured_query.get("query", ""))
        except (json.JSONDecodeError, TypeError):
            print("❌ OpenAI response is not in JSON format or returned None!")
            return {"status": "error", "message": "Invalid JSON format from OpenAI response"}

        if not cleaned_query:
            return {"status": "error", "message": "Generated SQL query is empty"}

        # 4) Sütun adlarını vs. düzeltelim (price -> pricing, author -> author_id vb.)
        corrected_query = correct_column_names(cleaned_query)

        if not corrected_query:  
            return {"status": "error", "message": "Final SQL query is empty after correction"}

        print(f"Final SQL Query: {corrected_query}")
        return corrected_query

    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return {"status": "error", "message": str(e)}

def execute_sql_query(sql_query):
    """
    Verilen SQL sorgusunu pyodbc ile çalıştırır, sonucu JSON formatında döndürür:
      [ {column: value, ...}, ... ]

    Eğer hata oluşursa veya veri yoksa yine { "status": "error", "message": "..." } döner.
    """
    try:
        # 1) Sorgu uygun mu?
        if not isinstance(sql_query, str) or sql_query.strip() == "":
            print("❌ SQL Query string değil veya boş!")
            return {"status": "error", "message": "Invalid SQL query"}

        print(f"Executing SQL Query: {sql_query}")  # Log SQL Query

        # 2) Veritabanı bağlantı dizesi al
        conn_string = get_pyodbc_connection_string()
        # 3) Bağlan ve sorguyu çalıştır
        conn = pyodbc.connect(conn_string, timeout=60)
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # 4) Sonuç sütunlarını al, veriyi dictionary listesi şeklinde dön
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        print(f"SQL Results: {results}")  # Log the results

        # 5) Eğer sonuç yoksa hata mesajı dönüyoruz
        if not results:
            return {"status": "error", "message": "No matching data found."}
        return results

    except pyodbc.OperationalError as e:
        # Örn: Zaman aşımı, sunucuya ulaşamama vs.
        print(f"SQL Timeout Error: {e}")
        return {"status": "error", "message": "SQL Timeout Error: Server is unreachable or connection took too long."}
    except pyodbc.Error as e:
        # PyODBC kaynaklı diğer hatalar
        print(f"SQL Execution Error: {e}")
        return {"status": "error", "message": f"SQL Execution Error: {e}"}
    except Exception as e:
        # Beklenmeyen diğer hatalar
        print(f"Unexpected Error in execute_sql_query: {e}")
        return {"status": "error", "message": f"Unexpected Error: {e}"}
