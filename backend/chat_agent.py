from azure_openai import generate_response

def chat_with_user(user_input):
    prompt = f"You are a helpful librarian. Answer the following: {user_input}"
    response = generate_response(prompt)
    return response
