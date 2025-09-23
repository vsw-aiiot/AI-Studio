import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

TOGETHER_API_KEY = os.getenv("together-api")
TOGETHER_URL = os.getenv("together-url")

def chat_with_together(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama-3-70b-instruct",  # or try another from their supported list
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(TOGETHER_URL, headers=headers, json=data)

    # Debug output
    print("DEBUG:", response.status_code, response.text)

    response_json = response.json()
    if "choices" in response_json:
        return response_json["choices"][0]["message"]["content"]
    else:
        return f"Error: {response_json.get('error', 'Unknown error')}"


