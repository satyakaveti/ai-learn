"""
agentic_ai_goa_trip.py — agent that plans a 3-day Goa trip within a budget,
using real prices from SerpApi and a free local LLM (Ollama).

Setup: pip install requests | export SERPAPI_KEY="..." | ollama serve
"""
import json, os, re
from datetime import date, timedelta
import requests

# --- Config ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma2:2b"
SERPAPI_KEY = "KEY"
ORIGIN, DESTINATION = "HYD", "GOX,GOI"       # GOX = Mopa, GOI = Dabolim
NIGHTS, BUDGET = 3, 13000
CHECK_IN = (date.today() + timedelta(days=30)).isoformat()
CHECK_OUT = (date.today() + timedelta(days=30 + NIGHTS)).isoformat()


# --- Tools ---
def serp(params):
    data = requests.get("https://serpapi.com/search.json",
                        params={**params, "api_key": SERPAPI_KEY}, timeout=60).json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def search_flights(origin, destination, outbound_date, return_date, choice="best"):
    data = serp({"engine": "google_flights", "departure_id": origin, "arrival_id": destination,
                 "outbound_date": outbound_date, "return_date": return_date, "currency": "INR"})
    options = [o for o in data.get("best_flights", []) + data.get("other_flights", []) if "price" in o]
    if not options:
        return "No flights found."
    pick = min(options, key=lambda o: o["price"]) if choice == "cheapest" else options[0]
    leg = pick["flights"][0]
    return f"Flight ({choice}): {leg.get('airline')} {leg.get('flight_number', '')} - Rs {int(pick['price'])} round trip"


def search_hotels(city, check_in, check_out, choice="best"):
    nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
    data = serp({"engine": "google_hotels", "q": f"hotels in {city}", "check_in_date": check_in,
                 "check_out_date": check_out, "adults": 1, "currency": "INR"})
    found = []
    for p in data.get("properties", []):
        total = (p.get("total_rate") or {}).get("extracted_lowest")
        if total is None and (p.get("rate_per_night") or {}).get("extracted_lowest"):
            total = p["rate_per_night"]["extracted_lowest"] * nights
        if total:
            found.append((p.get("name", "?"), total))
    if not found:
        return "No hotels found."
    name, total = min(found, key=lambda h: h[1]) if choice == "cheapest" else found[0]
    return f"Hotel ({choice}): {name} - Rs {int(total)} for {nights} nights"


def check_budget(flight_price, hotel_total, budget):
    total = float(flight_price) + float(hotel_total)      # a tool does the maths, not the LLM
    if total <= float(budget):
        return f"Total Rs {total:.0f} - WITHIN budget (Rs {float(budget) - total:.0f} left)"
    return f"Total Rs {total:.0f} - OVER budget by Rs {total - float(budget):.0f}"


TOOLS = {"search_flights": search_flights, "search_hotels": search_hotels, "check_budget": check_budget}

SYSTEM = """You are a travel-planning agent. Call one tool at a time.

Tools:
- search_flights(origin, destination, outbound_date, return_date, choice)  choice: "best" or "cheapest"
- search_hotels(city, check_in, check_out, choice)                         choice: "best" or "cheapest"
- check_budget(flight_price, hotel_total, budget)

Plan:
1. search_flights (best)  2. search_hotels (best)  3. check_budget
4. If OVER budget: search_flights and search_hotels with "cheapest", then check_budget again.
5. Give the final answer.

Reply with ONLY one JSON object:
{"tool": "<name>", "args": {...}}   or   {"final_answer": "Flight: ... Hotel: ... Total: ..."}
"""


# --- LLM ---
def call_llm(prompt):
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt, "stream": False,
                                        "format": "json", "options": {"temperature": 0}}, timeout=180)
    r.raise_for_status()
    return r.json()["response"]


def parse(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


# --- Agent loop: think -> act -> observe ---
def run_agent(goal, max_steps=14):
    history = f"{SYSTEM}\nGoal: {goal}\n"
    done, price, over = set(), {}, False

    def pending():          # cheaper searches not tried yet
        return [t for t in ("search_flights", "search_hotels") if (t, "cheapest") not in done]

    for step in range(1, max_steps + 1):
        d = parse(call_llm(history))                                   # THINK

        if "final_answer" in d:
            if over and pending():                                     # guardrail: don't quit early
                print(f"  [guardrail] still over budget, {pending()[0]} (cheapest) not tried")
                history += f'\nSystem: Still over budget. Call {pending()[0]} with choice "cheapest" first.\n'
                continue
            print(f"\nFINAL ANSWER\n{d['final_answer']}")
            return d["final_answer"]

        if "tool" not in d or d["tool"] not in TOOLS:
            history += "\nSystem: Reply with ONE valid JSON object.\n"
            continue

        name, args = d["tool"], d.get("args") or {}
        if name == "check_budget":                                     # guardrail: use real latest prices
            args = {"flight_price": price.get("search_flights", 0),
                    "hotel_total": price.get("search_hotels", 0), "budget": BUDGET}
        try:
            result = TOOLS[name](**args)                               # ACT
        except Exception as e:
            result = f"Error: {e}"
        print(f"Step {step}: {name}({', '.join(f'{k}={v}' for k, v in args.items())})\n   -> {result}\n")  # OBSERVE

        if name != "check_budget":
            done.add((name, args.get("choice", "best")))
            m = re.search(r"Rs (\d+)", result)
            if m:
                price[name] = int(m.group(1))
        else:
            over = "OVER" in result
            if over and pending():
                history += f'\nSystem: Still over budget. Next call {pending()[0]} with choice "cheapest".\n'
        history += f"\nYou called: {json.dumps(d)}\nTool result: {result}\nNext step? JSON only.\n"

    print("Stopped: max_steps reached.")


if __name__ == "__main__":
    if not SERPAPI_KEY:
        raise SystemExit('Set your key first: export SERPAPI_KEY="your_key"')
    goal = (f"Plan a {NIGHTS}-day trip to Goa within Rs {BUDGET}. Fly {ORIGIN} to {DESTINATION} round trip "
            f"on {CHECK_IN}, returning {CHECK_OUT}. Hotel in Goa from {CHECK_IN} to {CHECK_OUT}.")
    print(f"GOAL: {goal}\n")
    run_agent(goal)