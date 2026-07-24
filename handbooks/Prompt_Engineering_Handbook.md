# Prompt Engineering Handbook
### A Short, Practical Guide to the Techniques You'll Actually Use

---

## Table of Contents

1. What is Prompt Engineering?
2. Anatomy of a Good Prompt
3. System Prompt vs. User Prompt
4. The Core Techniques
5. Structuring Prompts for Reliability
6. Common Pitfalls
7. Quick Hands-On Lab
8. Cheat Sheet / Where to Go Next

---

## 1. What is Prompt Engineering?

Prompt engineering is simply the practice of wording your input so a generative AI model gives you a better, more reliable answer — without changing the model itself.

**Same model, different results:**

| Prompt | Result quality |
|---|---|
| "Tell me about electric cars." | Vague, generic, unpredictable length |
| "List 3 pros and 3 cons of electric cars, in bullet points, under 100 words." | Specific, consistent, usable immediately |

Nothing about the model changed between those two — only the wording. That gap is what prompt engineering closes.

---

## 2. Anatomy of a Good Prompt

Most effective prompts are made of up to four parts. You don't always need all four, but knowing them helps you diagnose a weak prompt.

![Anatomy of a prompt](prompt_engineering_images/p1_anatomy.png)

| Part | What it does | Example |
|---|---|---|
| **Instruction** | What you want done | "Summarize the following text" |
| **Context** | Background that shapes the response | "You are writing for a 10-year-old" |
| **Input data** | The actual content to work on | The article, code, or data itself |
| **Output format** | How the answer should look | "In exactly 3 bullet points" |

**Combined example:**
```
You are writing for a 10-year-old. Summarize the following text in exactly
3 bullet points:

"[article text goes here]"
```

---

## 3. System Prompt vs. User Prompt

| Type | Purpose | Example |
|---|---|---|
| **System prompt** | Sets behavior for the whole conversation, usually set once by the developer | "You are a helpful support agent. Always be polite and concise." |
| **User prompt** | The specific question or request each time | "My order hasn't arrived yet, what do I do?" |

**Why it matters:** the system prompt is where you bake in consistent rules (tone, role, boundaries) so you don't have to repeat them in every user message.

---

## 4. The Core Techniques

These five cover the large majority of real-world prompting needs.

![Technique ladder](prompt_engineering_images/p2_technique_ladder.png)

### 4.1 Zero-shot prompting
Just ask directly, no examples given.
```
Classify the sentiment: "The food was cold and the service was slow."
```
Good for simple, common tasks the model already handles well.

### 4.2 Few-shot prompting
Show 2-3 examples of the pattern you want before the real request.
```
Review: "Amazing food, great service!" → Positive
Review: "Terrible experience, never going back." → Negative
Review: "The food was cold and the service was slow." →
```
Use this when you need a specific format or the task is a bit unusual.

### 4.3 Chain-of-thought prompting
Ask the model to reason step-by-step before giving a final answer — improves accuracy on anything multi-step.
```
A store had 120 apples. They sold 45 in the morning and 30 in the afternoon.
How many are left? Think step by step before giving the final answer.
```

### 4.4 Role / persona prompting
Assign the model a role to shape tone and depth.
```
You are an experienced financial advisor. Explain compound interest to a
16-year-old in simple terms.
```

### 4.5 Format, length, and tone constraints
Be explicit about what the output should look like.
```
Summarize this article in exactly 3 sentences, in a neutral tone, avoiding jargon.
```

**Rule of thumb:** start with zero-shot. If the output is inconsistent, add few-shot examples. If it's getting facts or logic wrong, add chain-of-thought. Always add format constraints if you need a predictable structure.

---

## 5. Structuring Prompts for Reliability

### Use delimiters to separate instructions from data
Without a clear separator, the model can confuse your instructions with the content you gave it — especially with longer inputs.
```
Summarize the text between the triple quotes in 2 sentences.

"""
[article text goes here]
"""
```
Triple quotes, markdown headers, or tags like `<text>...</text>` all work — pick one and use it consistently.

### Ask for structured output directly
```
Extract the name, date, and total from this receipt. Return it as JSON with
keys "name", "date", and "total".
```
This is far more reliable than asking for the same info "in a sentence" and then trying to parse it yourself.

### Use negative constraints
Sometimes it's easier to say what NOT to do.
```
Summarize this article. Do not include any opinions, only factual statements
from the text.
```

---

## 6. Common Pitfalls

| Pitfall | What goes wrong | Fix |
|---|---|---|
| **Vague instructions** | "Make this better" → model guesses what "better" means | Be specific: "make this more concise" or "make this more formal" |
| **Overloading one prompt** | Asking for a summary, translation, and sentiment analysis all in one go often degrades all three | Split into separate prompts, or clearly numbered steps |
| **Assuming memory** | Referring to "that document" without including it | Always include the actual content the model needs, every time |
| **Prompt injection** | If you insert untrusted text (like a scraped webpage) into a prompt, it may contain hidden instructions that hijack the model's behavior | Treat inserted external content as data, not instructions; keep instructions and untrusted content clearly separated with delimiters |

---

## 7. Quick Hands-On Lab

A short script comparing zero-shot, few-shot, and chain-of-thought side-by-side on the same task, using a free local LLM (Ollama — no API key, no cost).

**Setup:**
```bash
brew install ollama
ollama pull llama3.1
pip install requests
```

**The script:**
```python
"""
compare_prompts.py — runs the same underlying task through three
different prompting techniques and prints each result for comparison.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1"


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

print("--- Zero-shot ---")
print(generate(zero_shot))

print("\n--- Few-shot ---")
print(generate(few_shot))

print("\n--- Chain-of-thought ---")
print(generate(chain_of_thought))
```

Run it with `python3 compare_prompts.py` and compare the three outputs — notice how few-shot tends to return a clean single-word label, while chain-of-thought shows its reasoning first.

---

## 8. Cheat Sheet / Where to Go Next

| If you need... | Use... |
|---|---|
| A quick, simple answer | Zero-shot |
| Consistent formatting or an unusual pattern | Few-shot |
| Better accuracy on multi-step reasoning | Chain-of-thought |
| Consistent tone or depth of expertise | Role/persona prompting |
| A specific structure every time | Explicit output format instructions |
| To process long or untrusted text safely | Delimiters, separating instructions from data |

**Next steps:**
- Try the lab in Section 7 and swap in your own task.
- Read the Generative AI Fundamentals Handbook's section on RAG — grounding prompts in real data is the natural next step once these basics feel comfortable.
- If you start building multi-step or tool-using prompts regularly, that's the point where it's worth exploring agents (also covered in the Generative AI Fundamentals Handbook).

---

*End of Handbook*
