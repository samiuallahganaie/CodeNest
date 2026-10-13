"""To-Do List: a command-line task manager that stores tasks in a SQLite database.

Tasks are saved in todo.db next to this file, so they are kept between runs.
"""

import sqlite3
from datetime import date
from pathlib import Path

DB_FILE = Path(__file__).with_name("todo.db")
PRIORITIES = {"1": "High", "2": "Medium", "3": "Low"}


def connect():
    """Open the database and create the tasks table if it does not exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT    NOT NULL,
            priority  TEXT    NOT NULL,
            done      INTEGER NOT NULL DEFAULT 0,
            created   TEXT    NOT NULL
        )
        """
    )
    return conn


def add_task(conn):
    title = input("Task: ").strip()
    if not title:
        print("Task cannot be empty.")
        return
    print("Priority: 1) High  2) Medium  3) Low")
    priority = PRIORITIES.get(input("Choose 1-3 (default 2): ").strip(), "Medium")

    conn.execute(
        "INSERT INTO tasks (title, priority, created) VALUES (?, ?, ?)",
        (title, priority, date.today().isoformat()),
    )
    conn.commit()
    print(f"Added: {title} ({priority})")


def list_tasks(conn, show="all"):
    query = "SELECT id, title, priority, done, created FROM tasks"
    if show == "pending":
        query += " WHERE done = 0"
    elif show == "done":
        query += " WHERE done = 1"
    # High priority first, then oldest first
    query += (" ORDER BY done, CASE priority WHEN 'High' THEN 1 "
              "WHEN 'Medium' THEN 2 ELSE 3 END, id")
    rows = conn.execute(query).fetchall()

    if not rows:
        print("No tasks to show.")
        return False

    print(f"\n{'ID':<5}{'Status':<9}{'Priority':<10}{'Task':<30}{'Added'}")
    print("-" * 66)
    for task_id, title, priority, done, created in rows:
        status = "Done" if done else "Pending"
        print(f"{task_id:<5}{status:<9}{priority:<10}{title[:28]:<30}{created}")
    return True


def ask_id(action):
    try:
        return int(input(f"Task ID to {action}: "))
    except ValueError:
        print("Please enter a valid number.")
        return None


def complete_task(conn):
    if not list_tasks(conn, "pending"):
        return
    task_id = ask_id("mark as done")
    if task_id is None:
        return
    cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    print("Marked as done." if cursor.rowcount else "No task with that ID.")


def delete_task(conn):
    if not list_tasks(conn):
        return
    task_id = ask_id("delete")
    if task_id is None:
        return
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    print("Deleted." if cursor.rowcount else "No task with that ID.")


def show_stats(conn):
    total, done = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(done), 0) FROM tasks"
    ).fetchone()
    if total == 0:
        print("No tasks yet.")
        return
    print(f"\nTotal: {total} | Done: {done} | Pending: {total - done} "
          f"| Progress: {done / total * 100:.0f}%")


def main():
    conn = connect()
    menu = {
        "1": ("Add task", add_task),
        "2": ("View all tasks", lambda c: list_tasks(c, "all")),
        "3": ("View pending tasks", lambda c: list_tasks(c, "pending")),
        "4": ("Mark task as done", complete_task),
        "5": ("Delete task", delete_task),
        "6": ("Progress summary", show_stats),
    }

    while True:
        print("\n=== To-Do List ===")
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")
        print("7. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "7":
            print("Goodbye!")
            break
        if choice in menu:
            menu[choice][1](conn)
        else:
            print("Please choose a number from 1 to 7.")

    conn.close()


if __name__ == "__main__":
    main()
