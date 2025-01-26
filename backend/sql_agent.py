from azure_openai import generate_response

def generate_sql_query(user_input):
    prompt = f"Generate an SQL query for the following request: {user_input}"
    response = generate_response(prompt)
    return response
