"""
practice_lab.py — touches most of the Python concepts from this handbook,
using a small, familiar example: employee records.
"""

import json
from pathlib import Path


def log_call(func):
    """A simple decorator (Section 11), just to see it in action."""
    def wrapper(*args, **kwargs):
        print(f"[log] Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


class Employee:
    """A simple class (Section 8)."""
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def describe(self) -> str:
        return f"{self.name} works as a {self.role}"


@log_call
def load_employees(path: str) -> list[dict]:
    """Type hints (Section 15) + context manager (Section 14) + error handling (Section 10)."""
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"No such file: {path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    data_file = "employees.json"

    # Create some sample data first, so the lab runs standalone.
    sample_data = [
        {"name": "Priya Nair", "role": "Backend Engineer"},
        {"name": "Marcus Webb", "role": "Sales Manager"},
    ]
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    try:
        records = load_employees(data_file)
    except FileNotFoundError as ex:
        print(f"Could not load data: {ex}")
        return

    # List comprehension (Section 7)
    employees = [Employee(r["name"], r["role"]) for r in records]

    # For loop (Section 5)
    for e in employees:
        print(e.describe())


if __name__ == "__main__":
    main()