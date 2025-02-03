import openai

openai.api_key = "your-openai-api-key"

def get_chat_response(user_input: str):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}]
    )
    return response["choices"][0]["message"]["content"]
