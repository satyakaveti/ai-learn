"""
generate_employee_content.py — reads employee records from a JSON file
and uses a free, local LLM (via Ollama) to generate a short newsletter
"spotlight" blurb for each employee, grounded in their real data.
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:2b"


def generate(prompt: str, temperature: float = 0.7) -> str:
    """Send a prompt to the local LLM and return the generated text."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "options": {"temperature": temperature},
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"]


def load_employees(path: str = "employees.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(employee: dict) -> str:
    """Ground the prompt in the employee's real data, so the model
    describes this specific person instead of inventing details."""
    return (
        "Write a warm, 3-sentence 'Employee Spotlight' blurb for a company "
        "newsletter, using only the facts below. Do not invent any details "
        "that aren't provided.\n\n"
        f"Name: {employee['name']}\n"
        f"Role: {employee['role']}\n"
        f"Department: {employee['department']}\n"
        f"Tenure: {employee['tenure_years']} years\n"
        f"Achievement: {employee['achievement']}\n"
    )


if __name__ == "__main__":
    employees = load_employees()

    for employee in employees:
        prompt = build_prompt(employee)
        generatedMessage = generate(prompt)
        print(f"\n--- Spotlight Message For: {employee['name']} ---\n")
        print(generatedMessage)