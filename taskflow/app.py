
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DB_FILE = Path(__file__).with_name("todo.db")


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created TEXT NOT NULL
        )
    """)

    conn.commit()
    return conn


@app.route("/")
def index():
    status = request.args.get("status", "all")
    search = request.args.get("search", "").strip()

    if status not in ("all", "pending", "completed"):
        status = "all"

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status == "pending":
        query += " AND done = 0"
    elif status == "completed":
        query += " AND done = 1"

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    query += """
        ORDER BY done,
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            ELSE 3
        END,
        id
    """

    conn = connect()
    tasks = conn.execute(query, params).fetchall()

    total, done = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(done), 0) FROM tasks"
    ).fetchone()

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        done=done,
        status=status,
        search=search
    )


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Medium")

    if priority not in ("High", "Medium", "Low"):
        priority = "Medium"

    if title:
        conn = connect()
        conn.execute(
            """
            INSERT INTO tasks (title, priority, created)
            VALUES (?, ?, ?)
            """,
            (title, priority, date.today().isoformat())
        )
        conn.commit()
        conn.close()

    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete(task_id):
    conn = connect()
    conn.execute(
        "UPDATE tasks SET done = 1 - done WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    conn = connect()
    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["POST"])
def edit(task_id):
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "Medium")

    if priority not in ("High", "Medium", "Low"):
        priority = "Medium"

    if title:
        conn = connect()
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, priority = ?
            WHERE id = ?
            """,
            (title, priority, task_id)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False)
