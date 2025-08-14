from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "results.db"

# ---------- DB Helpers ----------
def init_db():
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL UNIQUE,
                m1 REAL NOT NULL,
                m2 REAL NOT NULL,
                m3 REAL NOT NULL,
                total REAL NOT NULL,
                percent REAL NOT NULL,
                grade TEXT NOT NULL,
                result TEXT NOT NULL
            )
        """)
        con.commit()

def calc(total_marks, subjects=3):
    percent = total_marks / (subjects * 100) * 100
    # Grade logic (customize if you like)
    if percent >= 90: grade = "A+"
    elif percent >= 80: grade = "A"
    elif percent >= 70: grade = "B+"
    elif percent >= 60: grade = "B"
    elif percent >= 50: grade = "C"
    elif percent >= 40: grade = "D"
    else: grade = "F"
    result = "PASS" if percent >= 40 else "FAIL"
    return round(percent, 2), grade, result

def add_student(name, roll, m1, m2, m3):
    total = m1 + m2 + m3
    percent, grade, result = calc(total)
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO students (name, roll, m1, m2, m3, total, percent, grade, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, roll, m1, m2, m3, total, percent, grade, result))
        con.commit()

def delete_student(student_id):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
        con.commit()

def fetch_students(filters):
    query = "SELECT * FROM students WHERE 1=1"
    params = []

    # Filters
    if filters.get("min_percent"):
        query += " AND percent >= ?"
        params.append(float(filters["min_percent"]))
    if filters.get("max_percent"):
        query += " AND percent <= ?"
        params.append(float(filters["max_percent"]))
    if filters.get("result") in ("PASS", "FAIL"):
        query += " AND result = ?"
        params.append(filters["result"])
    if filters.get("name"):
        query += " AND name LIKE ?"
        params.append(f"%{filters['name']}%")

    # Sorting
    sort = filters.get("sort", "")
    if sort == "percent_asc":
        query += " ORDER BY percent ASC"
    elif sort == "percent_desc":
        query += " ORDER BY percent DESC"
    elif sort == "name_asc":
        query += " ORDER BY name ASC"
    elif sort == "name_desc":
        query += " ORDER BY name DESC"
    else:
        query += " ORDER BY id DESC"

    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return rows

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    # Handle add form
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        roll = request.form.get("roll", "").strip()
        try:
            m1 = float(request.form.get("m1", 0))
            m2 = float(request.form.get("m2", 0))
            m3 = float(request.form.get("m3", 0))
        except ValueError:
            return redirect(url_for("index"))

        if name and roll:
            try:
                add_student(name, roll, m1, m2, m3)
            except Exception:
                # e.g., duplicate roll
                pass
        return redirect(url_for("index"))

    # Filters from query string
    filters = {
        "name": request.args.get("name", "").strip(),
        "min_percent": request.args.get("min_percent", "").strip(),
        "max_percent": request.args.get("max_percent", "").strip(),
        "result": request.args.get("result", "").strip(),
        "sort": request.args.get("sort", "").strip(),
    }

    rows = fetch_students(filters)

    # Quick stats for current filtered view
    total_students = len(rows)
    if total_students:
        avg_percent = round(sum(r["percent"] for r in rows) / total_students, 2)
    else:
        avg_percent = 0.0

    return render_template(
        "index.html",
        students=rows,
        total_students=total_students,
        avg_percent=avg_percent,
        filters=filters
    )

@app.route("/delete/<int:student_id>")
def delete(student_id):
    delete_student(student_id)
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
