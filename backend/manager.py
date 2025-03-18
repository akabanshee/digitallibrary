# manager.py
import traceback
import json
from sql_agent import execute_sql_query, correct_column_names

class Manager:
    """
    Bu sınıf, chat_agent ve sql_agent arasındaki orkestrasyonu üstlenir.
    """
    def __init__(self):
        pass

    def handle_chat_message(self, llm_chat_fn, user_input, user_id="default_user"):
        """
        1) 'llm_chat_fn', OpenAI ile konuşan fonksiyon (yani "eski" chat agent fonksiyonu).
        2) user_input: Kullanıcının mesajı.
        3) user_id: Oturum yönetimi için kullanıcı ID'si.

        Adımlar:
        - OpenAI'ye soralım. "function_call" var mı diye bakarız.
        - Varsa, sql_agent ile sorgu çalıştırırız.
        - Sonucu tekrar formatlatırız.
        - Manager final yanıtı döndürür.
        """
        try:
            # 1) İlk LLM çağrısı (chat_agent fonksiyonunu) yap
            chat_response = llm_chat_fn(user_input, user_id)

            # Eğer hata varsa direkt dön
            if chat_response.get("status") == "error":
                return chat_response

            # 2) function_call var mı?
            function_call = chat_response.get("function_call")
            if function_call and function_call.get("name") == "execute_sql_query":
                # SQL sorgusunu al
                sql_args = function_call.get("arguments", {})
                sql_query = sql_args.get("sql_query", "").strip()
                if not sql_query:
                    return {
                        "status": "error",
                        "message": "Generated SQL query is empty"
                    }

                # Sütun adı düzeltme
                corrected_sql = correct_column_names(sql_query)
                sql_result = execute_sql_query(corrected_sql)

                if isinstance(sql_result, dict) and sql_result.get("status") == "error":
                    return {
                        "status": "error",
                        "message": (
                            "Oops! Something went wrong while searching for books. "
                            "Try asking in a different way."
                        )
                    }

                # 3) SQL sonucunu user-friendly formata çevirtmek için
                #    chat_agent fonksiyonuna tekrar "Format this result..." diyelim
                format_request = (
                    f"Format this SQL result into a user-friendly response:\n\n{sql_result}"
                )
                format_response = llm_chat_fn(format_request, user_id)

                if format_response.get("status") == "error":
                    return format_response

                # Nihai cevabı (metinsel) dönüyoruz
                return {
                    "status": "success",
                    "type": "Chat",
                    "data": format_response.get("data", "")
                }

            else:
                # Hiç function_call yoksa normal metin cevabı
                return chat_response

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"❌ Manager Error:\n{error_details}")
            return {
                "status": "error",
                "message": "Manager encountered an unexpected error. Please try again later."
            }
