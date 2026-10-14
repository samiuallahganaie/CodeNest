
import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "jobs.db"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                location TEXT DEFAULT '',
                job_type TEXT DEFAULT 'Full-time',
                salary TEXT DEFAULT '',
                job_url TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Applied',
                applied_date TEXT NOT NULL,
                interview_date TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    query = "SELECT * FROM applications WHERE 1=1"
    params = []

    if search:
        query += """
            AND (
                company LIKE ?
                OR role LIKE ?
                OR location LIKE ?
            )
        """
        term = f"%{search}%"
        params.extend([term, term, term])

    valid_statuses = [
        "Applied", "Interview", "Offer", "Rejected", "Withdrawn"
    ]

    if status in valid_statuses:
        query += " AND status = ?"
        params.append(status)

    query += """
        ORDER BY
            CASE status
                WHEN 'Interview' THEN 1
                WHEN 'Applied' THEN 2
                WHEN 'Offer' THEN 3
                WHEN 'Rejected' THEN 4
                ELSE 5
            END,
            applied_date DESC,
            id DESC
    """

    with get_db() as db:
        applications = db.execute(query, params).fetchall()

        stats = db.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'Applied' THEN 1 ELSE 0 END)
                    AS applied,
                SUM(CASE WHEN status = 'Interview' THEN 1 ELSE 0 END)
                    AS interviews,
                SUM(CASE WHEN status = 'Offer' THEN 1 ELSE 0 END)
                    AS offers,
                SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END)
                    AS rejected
            FROM applications
        """).fetchone()

    return render_template(
        "index.html",
        applications=applications,
        stats=stats,
        search=search,
        selected_status=status,
        today=date.today().isoformat(),
    )


@app.route("/add", methods=["POST"])
def add_application():
    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()

    if not company or not role:
        flash("Company name and job title are required.", "error")
        return redirect(url_for("index"))

    job_type = request.form.get("job_type", "Full-time")
    valid_types = [
        "Full-time", "Part-time", "Internship", "Contract", "Remote"
    ]
    if job_type not in valid_types:
        job_type = "Full-time"

    status = request.form.get("status", "Applied")
    valid_statuses = [
        "Applied", "Interview", "Offer", "Rejected", "Withdrawn"
    ]
    if status not in valid_statuses:
        status = "Applied"

    applied_date = request.form.get("applied_date", date.today().isoformat())
    try:
        date.fromisoformat(applied_date)
    except ValueError:
        applied_date = date.today().isoformat()

    interview_date = request.form.get("interview_date", "").strip()
    if interview_date:
        try:
            date.fromisoformat(interview_date)
        except ValueError:
            interview_date = ""

    with get_db() as db:
        db.execute("""
            INSERT INTO applications (
                company, role, location, job_type, salary, job_url,
                status, applied_date, interview_date, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company,
            role,
            request.form.get("location", "").strip(),
            job_type,
            request.form.get("salary", "").strip(),
            request.form.get("job_url", "").strip(),
            status,
            applied_date,
            interview_date,
            request.form.get("notes", "").strip(),
        ))

    flash("Job application added successfully!", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:application_id>", methods=["POST"])
def edit_application(application_id):
    company = request.form.get("company", "").strip()
    role = request.form.get("role", "").strip()

    if not company or not role:
        flash("Company name and job title are required.", "error")
        return redirect(url_for("index"))

    status = request.form.get("status", "Applied")
    valid_statuses = [
        "Applied", "Interview", "Offer", "Rejected", "Withdrawn"
    ]
    if status not in valid_statuses:
        status = "Applied"

    applied_date = request.form.get("applied_date", date.today().isoformat())
    try:
        date.fromisoformat(applied_date)
    except ValueError:
        applied_date = date.today().isoformat()

    interview_date = request.form.get("interview_date", "").strip()
    if interview_date:
        try:
            date.fromisoformat(interview_date)
        except ValueError:
            interview_date = ""

    with get_db() as db:
        result = db.execute("""
            UPDATE applications
            SET company = ?, role = ?, location = ?, job_type = ?,
                salary = ?, job_url = ?, status = ?, applied_date = ?,
                interview_date = ?, notes = ?
            WHERE id = ?
        """, (
            company,
            role,
            request.form.get("location", "").strip(),
            request.form.get("job_type", "Full-time"),
            request.form.get("salary", "").strip(),
            request.form.get("job_url", "").strip(),
            status,
            applied_date,
            interview_date,
            request.form.get("notes", "").strip(),
            application_id,
        ))

    if result.rowcount:
        flash("Application updated successfully!", "success")
    else:
        flash("Application not found.", "error")

    return redirect(url_for("index"))


@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    with get_db() as db:
        result = db.execute(
            "DELETE FROM applications WHERE id = ?",
            (application_id,),
        )

    if result.rowcount:
        flash("Application deleted.", "success")
    else:
        flash("Application not found.", "error")

    return redirect(url_for("index"))


initialize_database()

if __name__ == "__main__":
    app.run(debug=False)
