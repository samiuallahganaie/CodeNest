"""Expense Tracker: a small command-line app to record and review spending.

Data is saved in expenses.json next to this file, so it is kept between runs.
"""

import json
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).with_name("expenses.json")


def load_expenses():
    """Read saved expenses, or return an empty list if there are none yet."""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("Warning: expenses.json is damaged. Starting with an empty list.")
        return []


def save_expenses(expenses):
    DATA_FILE.write_text(json.dumps(expenses, indent=2), encoding="utf-8")


def ask_amount():
    """Keep asking until the user enters a positive number."""
    while True:
        try:
            amount = float(input("Amount: "))
            if amount > 0:
                return round(amount, 2)
            print("Amount must be greater than 0.")
        except ValueError:
            print("Please enter a valid number.")


def add_expense(expenses):
    title = input("What did you spend on? ").strip()
    if not title:
        print("Title cannot be empty.")
        return
    category = input("Category (e.g. Food, Travel, Books): ").strip().title() or "Other"
    amount = ask_amount()

    expenses.append({
        "title": title,
        "category": category,
        "amount": amount,
        "date": date.today().isoformat(),
    })
    save_expenses(expenses)
    print(f"Added: {title} - {amount:.2f} ({category})")


def view_expenses(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return
    print(f"\n{'#':<4}{'Date':<12}{'Category':<12}{'Title':<20}{'Amount':>10}")
    print("-" * 58)
    for number, item in enumerate(expenses, start=1):
        print(f"{number:<4}{item['date']:<12}{item['category']:<12}"
              f"{item['title'][:18]:<20}{item['amount']:>10.2f}")


def show_summary(expenses):
    if not expenses:
        print("No expenses recorded yet.")
        return
    totals = {}
    for item in expenses:
        totals[item["category"]] = totals.get(item["category"], 0) + item["amount"]

    print("\nSpending by category")
    print("-" * 28)
    for category, total in sorted(totals.items(), key=lambda pair: pair[1], reverse=True):
        print(f"{category:<16}{total:>10.2f}")
    print("-" * 28)
    print(f"{'Total':<16}{sum(totals.values()):>10.2f}")


def delete_expense(expenses):
    view_expenses(expenses)
    if not expenses:
        return
    try:
        number = int(input("Number to delete: "))
        removed = expenses.pop(number - 1)
    except (ValueError, IndexError):
        print("That number is not in the list.")
        return
    save_expenses(expenses)
    print(f"Deleted: {removed['title']}")


def main():
    expenses = load_expenses()
    actions = {
        "1": ("Add expense", add_expense),
        "2": ("View expenses", view_expenses),
        "3": ("Spending summary", show_summary),
        "4": ("Delete expense", delete_expense),
    }

    while True:
        print("\n=== Expense Tracker ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print("5. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "5":
            print("Goodbye!")
            break
        if choice in actions:
            actions[choice][1](expenses)
        else:
            print("Please choose a number from 1 to 5.")


if __name__ == "__main__":
    main()
