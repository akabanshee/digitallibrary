# manager.py
import traceback
import json
from sql_agent import execute_sql_query, correct_column_names

class Manager:
    """
    Bu sınıf, 'chat_agent' ve 'sql_agent' arasındaki orkestrasyonu üstlenir.
    Yani OpenAI'den gelen 'function_call' bilgisine göre SQL sorgusunu
    çalıştırır, ardından sonucu tekrar metin biçiminde formatlar.
    """
    def __init__(self):
        # Burada ek bir ayar yok. Manager sadece fonksiyonları koordine ediyor.
        pass

    def handle_chat_message(self, llm_chat_fn, user_input, user_id="default_user"):
        """
        Parametreler:
          - llm_chat_fn: OpenAI ile konuşmayı yapan fonksiyon (chat_agent içindeki '_base_chat_llm')
          - user_input: Kullanıcının metinsel girişi
          - user_id: Oturum yönetimi için kullanıcı (varsayılan "default_user")

        Çalışma Akışı:
          1) OpenAI'ye ilk sorgu gönderilip yanıt alınıyor. (llm_chat_fn çağrısı)
          2) Dönen yanıtta 'function_call' var mı diye kontrol ediliyor.
          3) Eğer 'execute_sql_query' function_call geldiyse, sql_agent kullanılarak sorgu çalıştırılıyor.
          4) Sorgu sonucunu tekrar OpenAI'ye göndererek 'kullanıcı dostu' bir metin haline getirmesini sağlıyoruz.
          5) Nihai yanıtı dönüyoruz.
        """
        try:
            # 1) İlk LLM çağrısı: Kullanıcı mesajını OpenAI'ye ilet
            chat_response = llm_chat_fn(user_input, user_id)

            # Hata dönmüşse, anında iletelim
            if chat_response.get("status") == "error":
                return chat_response

            # 2) Dönüşte function_call var mı? (örneğin 'execute_sql_query')
            function_call = chat_response.get("function_call")
            if function_call and function_call.get("name") == "execute_sql_query":
                # a) function_call varsa, içerisinden SQL sorgusunu alıyoruz
                sql_args = function_call.get("arguments", {})
                sql_query = sql_args.get("sql_query", "").strip()

                # b) Sorgu boş mu?
                if not sql_query:
                    return {
                        "status": "error",
                        "message": "Generated SQL query is empty"
                    }

                # c) Sorgu içinde sütun adı düzeltmeleri yapalım (price -> pricing vb.)
                corrected_sql = correct_column_names(sql_query)

                # d) sql_agent'tan sorguyu çalıştır
                sql_result = execute_sql_query(corrected_sql)

                # Eğer dönen sonuç bir hata mesajı içeriyorsa
                if isinstance(sql_result, dict) and sql_result.get("status") == "error":
                    return {
                        "status": "error",
                        "message": (
                            "Oops! Something went wrong while searching for books. "
                            "Try asking in a different way."
                        )
                    }

                # 3) SQL sonucunu kullanıcı dostu bir metinle dönmek için 
                #    aynı LLM fonksiyonuna, "Format this SQL result..." şeklinde tekrar soruyoruz
                format_request = f"Format this SQL result into a user-friendly response:\n\n{sql_result}"
                format_response = llm_chat_fn(format_request, user_id)

                # Formatlama adımında hata çıkarsa
                if format_response.get("status") == "error":
                    return format_response

                # 4) Nihai cevabı (metinsel) dönüyoruz
                return {
                    "status": "success",
                    "type": "Chat",
                    "data": format_response.get("data", "")
                }

            else:
                # function_call yoksa, demek ki normal bir metin cevabı dönmüş
                return chat_response

        except Exception as e:
            # Yakalanmayan bir hata olursa, traceback ile loglayalım
            error_details = traceback.format_exc()
            print(f"❌ Manager Error:\n{error_details}")
            return {
                "status": "error",
                "message": "Manager encountered an unexpected error. Please try again later."
            }
