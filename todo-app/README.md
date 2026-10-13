# To-Do List (Python + SQLite)

A command-line task manager written in Python. Tasks are stored in a SQLite database, so they are kept between runs.

## Features
- Add tasks with a priority (High, Medium, Low)
- View all tasks or only pending ones, sorted by priority
- Mark tasks as done and delete tasks
- Progress summary (total, done, pending, percentage)

## Run it
Requires Python 3.8 or newer. SQLite is built into Python, so nothing else needs to be installed.

```bash
python todo.py
```

## What I practised
- Working with a SQL database from Python (`sqlite3`)
- `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE` and `DELETE` queries
- Parameterised queries (`?`) to avoid SQL injection
- Sorting and filtering data with SQL (`ORDER BY`, `WHERE`)
- Input validation and clean, reusable functions
