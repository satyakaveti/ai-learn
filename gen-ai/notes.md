
## 13. Hands-On Lab: Generate Employee Content from Real Data

This is a complete, working example — a Python script that reads a small set of **fictional employee records**, and uses a **free, local LLM** (via Ollama — the same free tool used in the MCP Handbook's lab), to generate personalised text for each one, like an internal newsletter "employee spotlight," or a welcome message. No API keys, no cost, no real personal data involved.

### What you will build

- `employees.json` — a small file of fictional employee records (name, role, department, tenure, achievement)
- `generate_employee_content.py` — a script that reads each record, builds a grounded prompt from it, and generates text
- **Ollama**, running a free open-source model (e.g., `llama3.1`) entirely on your own machine

**Why this is a good exercise:** it is a small, realistic taste of the same pattern real companies use — grounding generated text in actual structured data, instead of letting the model guess, which directly reinforces the RAG idea from Section 8.

### Step 1 — Install prerequisites

```bash
# Ollama (free, local LLM runner)
brew install ollama
ollama pull llama3.1        # or any other available model

# Python HTTP library
pip install requests
```

Ollama runs a local server at `http://localhost:11434`, once installed — this is the "free LLM" this lab calls, entirely on your own machine, with no internet request, and no API key.

### Step 2 — Create the employee data (`employees.json`)

```json
[
  {
    "name": "Priya Nair",
    "role": "Senior Backend Engineer",
    "department": "Engineering",
    "tenure_years": 4,
    "achievement": "led the migration to a new payments system with zero downtime"
  },
  {
    "name": "Marcus Webb",
    "role": "Sales Manager",
    "department": "Sales",
    "tenure_years": 2,
    "achievement": "grew the regional accounts team's revenue by 30% this year"
  },
  {
    "name": "Aiko Tanaka",
    "role": "UX Designer",
    "department": "Product",
    "tenure_years": 1,
    "achievement": "redesigned the onboarding flow, cutting signup drop-off in half"
  }
]
```

Save this as `employees.json`, in the same folder as the script below. (These are fictional names and details for practice — swap in real data only with proper care and consent, in an actual workplace.)

### Step 3 — The generation script (`generate_employee_content.py`)

```python
"""
generate_employee_content.py — reads employee records from a JSON file
and uses a free, local LLM (via Ollama) to generate a short newsletter
"spotlight" blurb for each employee, grounded in their real data.
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"


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


def build_spotlight_prompt(employee: dict) -> str:
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
        prompt = build_spotlight_prompt(employee)
        spotlight = generate(prompt)
        print(f"\n--- Spotlight: {employee['name']} ---\n")
        print(spotlight)
```

### Step 4 — Run it

```bash
python3 generate_employee_content.py
```

This prints a generated spotlight blurb for each of the three employees, each grounded in their own real record — Priya's mentions her payments migration, Marcus's mentions his revenue growth, and so on, rather than just generic filler text.

### Step 5 — Experiment with the concepts from this handbook

**See grounding (RAG, Section 8) prevent hallucination — try it both ways:**
```python
# Ungrounded: the model has to guess or invent details
ungrounded = "Write a 3-sentence employee spotlight for Priya Nair."
print(generate(ungrounded))

# Grounded: the model uses only the real facts you gave it
employees = load_employees()
grounded = build_spotlight_prompt(employees[0])
print(generate(grounded))
```
Compare the two outputs — the ungrounded version will likely invent a role, department, or achievement, while the grounded version sticks to the real facts.

**Try zero-shot vs. few-shot for tone consistency (Section 6):**
```python
few_shot_prefix = """Example spotlight:
Name: Jordan Lee, Role: Data Analyst, Achievement: automated the weekly reporting process
-> "Jordan Lee has been a quiet powerhouse on our Data team, automating a
weekly reporting process that used to take hours. Their work now saves the
whole team valuable time every single week."

Now write one in the same style for:
"""
prompt = few_shot_prefix + build_spotlight_prompt(employees[1])
print(generate(prompt))
```

**Try temperature settings (Section 5):**
```python
print(generate(build_spotlight_prompt(employees[2]), temperature=0.2))
print(generate(build_spotlight_prompt(employees[2]), temperature=1.0))
```
Run this a few times at each temperature — low temperature should stay close to a safe, predictable tone; high temperature will vary more, in wording and style, each time you run it.

**Try a different generation task, on the same data — a personalised welcome email:**
```python
def build_welcome_prompt(employee: dict) -> str:
    return (
        "Write a short, friendly welcome-to-the-team email for a new hire, "
        "using only the facts below.\n\n"
        f"Name: {employee['name']}\nRole: {employee['role']}\n"
        f"Department: {employee['department']}\n"
    )

print(generate(build_welcome_prompt(employees[0])))
```

### What's happening under the hood (mapped to earlier sections)

| Piece | Concept | Section |
|---|---|---|
| `employees.json` | The "external knowledge" a RAG-style prompt is grounded in | Section 8 |
| `build_spotlight_prompt()` inserting real fields into the prompt | Augmenting the prompt with retrieved context | Section 8 |
| "Do not invent any details that aren't provided" | A direct defence against hallucination | Section 11, 12 |
| `temperature` option | Controls randomness/creativity | Section 5 |
| the few-shot example before the real request | Few-shot prompting for consistent tone | Section 6 |
| `MODEL = "llama3.1"` | Which pretrained LLM is doing the generating | Section 5 |

### Notes and troubleshooting

- If responses feel slow, try a smaller model — check Ollama's model library for lightweight options.
- If you get a connection error, make sure Ollama is running (`ollama serve` — it usually starts automatically after install).
- If the model still invents details, despite the grounding instruction, try being even more explicit ("only use the facts listed below, do not add a last name, location, or any detail not given") — smaller local models sometimes need firmer constraints than larger hosted ones like ChatGPT or Claude.
- This script uses Ollama's `/api/generate` endpoint (a single prompt in, text out) rather than the `/api/chat` endpoint used in the MCP Handbook's lab (which supports multi-turn conversation and tool calls) — both are valid, simplified starting points.
- Exact Ollama API details may evolve — check `ollama.com`'s documentation, if a call errors.
- **A note on real workplace use:** if you ever adapt this pattern for actual employee data, treat it like any other sensitive HR data — get proper consent, follow your organisation's data policies, and have a human review generated text, before it gets published anywhere.
