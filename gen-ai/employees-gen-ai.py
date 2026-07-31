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

    print("\n \n 1.ungrounded\n --------------------\n")
    # Ungrounded: the model has to guess or invent details
    ungrounded = "Write a 3-sentence employee spotlight for Priya Nair."
    print(generate(ungrounded))



    print("\n \n 2.Grounded\n --------------------\n")
    for employee in employees:
        # Grounded: the model uses only the real facts you gave it
        prompt = build_prompt(employee)
        generatedMessage = generate(prompt)
        print(f"\n--- Grounded Message For: {employee['name']} ---\n")
        print(generatedMessage)



    print("\n \n 3.Try zero-shot vs. few-shot for tone consistency \n --------------------\n")
    for employee in employees:
        few_shot_prefix = """Example spotlight:
        Name: Jordan Lee, Role: Data Analyst, Achievement: automated the weekly reporting process
        -> "Jordan Lee has been a quiet powerhouse on our Data team, automating a
        weekly reporting process that used to take hours. Their work now saves the
        whole team valuable time every single week."

        Now write one in the same style for:
        """
        prompt = few_shot_prefix + build_prompt(employees[1])
        print(generate(prompt))

    print("\n \n 4. Try temperature settings  \n --------------------\n")
    print("0.2 --> "+generate(build_prompt(employees[0]), temperature=0.2))
    print("6.0 --> "+generate(build_prompt(employees[0]), temperature=6.0))