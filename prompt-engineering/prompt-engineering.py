import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:2b"


def generate(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


review = "The food was cold and the service was slow."

zero_shot = f'Classify the sentiment of this review: "{review}"'

few_shot = f"""Review: "Amazing food, great service!" -> Positive
Review: "Terrible experience, never going back." -> Negative
Review: "{review}" ->"""

chain_of_thought = (
    f'Classify the sentiment of this review, thinking step by step about '
    f'the tone before giving a final one-word answer: "{review}"'
)

print("--- Zero-shot ---\n"+zero_shot)
print("Response: \n"+generate(zero_shot))

print("\n--- Few-shot ---\n"+few_shot)
print("Response: \n"+generate(few_shot))

print("\n--- Chain-of-thought\n"+chain_of_thought)
print("Response: \n"+generate(chain_of_thought))