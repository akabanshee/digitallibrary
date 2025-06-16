# manager.py

import traceback
import json
from sql_agent import execute_sql_query, correct_column_names, generate_sql_query

# Translation dictionary for Turkish book categories
TURKISH_TO_ENGLISH_CATEGORY = {
    "Roman": "Novel",
    "Siir": "Poem",
    "Drama": "Drama",
    "Biyografi": "Biography",
    "Otobiyografi": "Autobiography",
    "Bilim Kurgu": "Science Fiction"
}



class Manager:
    """
    This class orchestrates the interaction between the Chat Agent and the SQL Agent.
    It sends the user's request to the Chat Agent, checks if there's a function call for SQL,
    executes the query via the SQL Agent, and finally formats the result for the user.
    
    ---------------------------------------------------------------------------------------
    [English Explanation of Manager's Role]
    
    Currently, the Manager in this file primarily acts as an orchestrator:
    1) It takes the user_input and passes it to the Chat Agent (via _base_chat_llm).
    2) If the LLM response contains a function_call (indicating an SQL query request),
       the Manager invokes the SQL Agent (execute_sql_query) to run the query.
    3) Once the SQL result is obtained, the Manager sends it back to _base_chat_llm
       to be converted into a user-friendly text response.
    4) The final answer is returned to the caller.
    
    In this sense, the Manager functions more like a "bridge" or "coordinator" between
    the Chat Agent and the SQL Agent, rather than acting as a standalone "AI agent"
    that reasons or generates queries on its own. It primarily takes the function_call
    produced by the LLM, executes the query, and then passes the result back to the LLM.
    ---------------------------------------------------------------------------------------
    """

    def __init__(self):
        # No special configuration here. The Manager just coordinates the functions.
        pass

    def decide_function_call(self, llm_chat_fn, user_input, function_call, user_id="default_user"):
        """
        Uses an LLM-based decision mechanism to determine whether the proposed function_call
        should be executed.
        
        The Manager sends a decision prompt to the LLM with its own system prompt,
        asking whether, given the user input and the proposed function call, it is appropriate
        to proceed with the execution.

        The LLM should return a JSON with the key 'decision' set to 'proceed' or 'reject'.
        
        This method adds a layer of reasoning to the Manager, allowing it to decide if executing
        the function call (e.g., an SQL query) is appropriate based on the context.
        """
        try:
            # Construct a decision prompt message for the Manager.
            # This prompt instructs the LLM to decide if the function call should be executed.
            decision_prompt = (
                "You are an orchestration agent responsible for determining whether a proposed "
                "function call is appropriate. Based on the following information, decide if the "
                "function call should be executed. Return your answer as a JSON object with a key "
                "'decision' that has a value of either 'proceed' or 'reject'. "
                "If rejecting, include a brief explanation.\n\n"
                f"User input: {user_input}\n"
                f"Proposed function call: {json.dumps(function_call)}"
            )
            
            # Call the LLM using the provided chat function with the decision prompt.
            # Here we assume that llm_chat_fn can handle the decision prompt.
            decision_response = llm_chat_fn(decision_prompt, user_id)
            
            # Expect the LLM to return JSON text in the 'data' field.
            decision_data = decision_response.get("data", "{}").strip()
            if not decision_data.startswith("{"):
                print("⚠️ Invalid decision response from LLM, defaulting to proceed.")
                return "proceed"
            decision_result = json.loads(decision_data)

            decision = decision_result.get("decision", "proceed")
            
            # Return the decision: 'proceed' to execute the function call, or 'reject' to abort.
            return decision
        except Exception as e:
            print(f"❌ Decision making error: {e}")
            # In case of an error, default to 'proceed' to avoid blocking execution.
            return "proceed"

    def handle_chat_message(self, llm_chat_fn, user_input, user_id="default_user"):
        """
        Orchestrates the flow between the user, Chat Agent, and SQL Agent:
         1) Sends the user's input to the Chat Agent.
         2) Checks if the response includes an 'execute_sql_query' function call.
         3) If it does, the Manager may ask its own LLM-based decision mechanism whether
            executing this function call is appropriate.
         4) If approved, the Manager uses the SQL Agent to run the query.
         5) The query result is formatted by the Chat Agent.
         6) Returns the final response.
         
         This method is the main entry point for handling a user's input. It integrates the
         LLM's initial response with additional decision-making steps before executing any SQL queries.
        """
        try:
            # 1) Send the user's input to the Chat Agent via the llm_chat_fn.
            chat_response = llm_chat_fn(user_input, user_id)
            
            # If an error occurred in the Chat Agent, return the error immediately.
            if chat_response.get("status") == "error":
                return chat_response

            # 2) Check if the Chat Agent's response includes a function_call for executing an SQL query.
            function_call = chat_response.get("function_call")
            if function_call and function_call.get("name") == "execute_sql_query":
                # --- Manager's Decision Step ---
                # Ask the LLM whether this function call should be executed.
                decision = self.decide_function_call(llm_chat_fn, user_input, function_call, user_id)
                if decision != "proceed":
                    # If the decision is not to proceed, return an error message.
                    return {
                        "status": "error",
                        "message": "The function call was rejected by the Manager based on its decision."
                    }
                # -------------------------------

                # 3) Extract the SQL query from the function call arguments.
                # LLM'den gelen sql_query yerine, kendi SQL oluşturucunu kullan
                normalized = generate_sql_query(user_input)
                if isinstance(normalized, dict) and normalized.get("status") == "error":
                    # fallback: function_call içinden gelen sql_query'yi kullan
                    sql_args = function_call.get("arguments", {})
                    sql_query = sql_args.get("sql_query", "").strip()
                else:
                    sql_query = normalized  # ✅ temiz ve kurallı SQL çıktısı

                if not sql_query:
                    return {
                        "status": "error",
                        "message": "Generated SQL query is empty"
                    }


                # 4) Correct column names if necessary using the SQL Agent's helper function.
                corrected_sql = correct_column_names(sql_query)

                # 5) Execute the SQL query using the SQL Agent.
                sql_result = execute_sql_query(corrected_sql)

                # Eğer hiç veri yoksa (yani boş liste) özel yanıt dön
                # Eğer sorgu semantik bir hataysa (örneğin olmayan kolon)
                # Eğer sorgu semantik bir hataysa (örneğin olmayan kolon)
                if isinstance(sql_result, dict) and sql_result.get("status") == "semantic_error":
                    return {
                        "status": "success",
                        "type": "Chat",
                        "data": (
                            "🚫 Sorry, I couldn't process your request because the information you're asking for "
                            "does not exist in the database schema. Try rephrasing your question or ask something else."
                        )
                    }

                # Eğer hiç veri yoksa (yani boş liste) veya diğer hata durumları
                if isinstance(sql_result, dict) and sql_result.get("status") == "error":
                    if sql_result.get("message", "").lower().startswith("no matching data"):
                        return {
                            "status": "success",
                            "type": "Chat",
                            "data": (
                                "🔍 I couldn’t find any matching books for your request. "
                                "There may not be any books in the database that meet that criteria."
                            )
                        }
                    else:
                        return {
                            "status": "success",
                            "type": "Chat",
                            "data": (
                                "⚠️ Something went wrong while processing your request. "
                                "Please try again later or contact support."
                            )
                        }

                # 6) Send the SQL result back to the Chat Agent to be formatted into a user-friendly response.
                # Optional: Translate Turkish category to English before sending to LLM
                if isinstance(sql_result, list):
                    for row in sql_result:
                        category = row.get("category")
                        if category in TURKISH_TO_ENGLISH_CATEGORY:
                            row["category"] = TURKISH_TO_ENGLISH_CATEGORY[category]

                format_request = f"Format this SQL result into a user-friendly response:\n\n{sql_result}"
                format_response = llm_chat_fn(format_request, user_id)
                if format_response.get("status") == "error":
                    return format_response

                # 7) Return the final formatted response.
                return {
                    "status": "success",
                    "type": "Chat",
                    "data": format_response.get("data", "")
                }
            else:
                # If there is no function call, simply return the Chat Agent's response.
                return chat_response

        except Exception as e:
            # If any unexpected error occurs, log the traceback and return an error message.
            error_details = traceback.format_exc()
            print(f"❌ Manager Error:\n{error_details}")
            return {
                "status": "error",
                "message": "Manager encountered an unexpected error. Please try again later."
            }
