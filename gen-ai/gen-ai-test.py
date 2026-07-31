import requests

prompt = input("Enter your prompt: ")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma2:2b",
        "prompt": prompt,
        "stream": False
    }
)

print(response.json()["response"])