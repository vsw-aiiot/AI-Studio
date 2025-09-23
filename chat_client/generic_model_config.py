from importlib import import_module
import os
import json
import requests
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

TOGETHER_API_KEY = os.getenv("TOGETHER_API")
TOGETHER_BASE_URL = os.getenv("TOGETHER_URL")

print(f'TOGETHER_API_KEY=>\t{TOGETHER_API_KEY}\nTOGETHER_BASE_URL=>\t{TOGETHER_BASE_URL}')


def read_model_config():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, "../models_registry.json"), "r") as f:
        MODEL_REGISTRY = json.load(f)
        return MODEL_REGISTRY
    
MODEL_REGISTRY = read_model_config()

def get_model_handler(model_key):
    model_config = MODEL_REGISTRY.get(model_key)

    if not model_config:
        raise ValueError("Invalid model key.")

    def handler(prompt: str):
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_config["id"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
        }

        response = requests.post(TOGETHER_BASE_URL, json=payload, headers=headers)
        result = response.json()

        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            return "⚠️ No response received from the model."

    return handler



