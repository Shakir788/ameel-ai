import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def llm_chat(prompt, language='ar'):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4.1-mini",  # tu chahe to claude-3.5-sonnet ya koi bhi free/cheap model use kar
        "messages": [
            {"role": "system", "content": f"You are AMEEL, an Arabic assistant for accounting and e-commerce."},
            {"role": "user", "content": prompt}
        ]
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error: {resp.text}"
