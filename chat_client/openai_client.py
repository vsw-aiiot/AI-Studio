import os
import openai

# Set your API key here (or from environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY") or "sk-xxxx"

def ask_chat(prompt):       # OpenAI [Future purpose]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can use "gpt-4o" if you have access
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        reply = ask_chat(user_input)
        print("AI:", reply)
