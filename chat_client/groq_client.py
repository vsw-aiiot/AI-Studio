import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# GROQ_API_KEY = "gsk_test_..."  # replace with your key
GROQ_API_KEY = os.getenv("groq-api")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def chat_with_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(GROQ_URL, headers=headers, json=data)

    try:
        response.raise_for_status()
        result = response.json()
        print(f'result=>\t{result["choices"][0]["message"]["content"]}')
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("ERROR:", response.status_code, response.text)
        return f"Failed to fetch response: {e}"
    

def chat_with_groq_new(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(GROQ_URL, headers=headers, json=data)
    try:
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("ERROR:", response.status_code, response.text)
        return f"Error: {e}"
