from flask import Flask, render_template, request, redirect
import csv
import os
from datetime import datetime

app = Flask(__name__)

CSV_FILE = "expenses.csv"

# Create CSV file if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Description", "Amount"])

def read_expenses():
    expenses = []
    with open(CSV_FILE, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            expenses.append(row)
    return expenses

def write_expense(date, desc, amount):
    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([date, desc, amount])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST" and "description" in request.form:
        desc = request.form.get("description")
        amount = request.form.get("amount")
        date = datetime.now().strftime("%Y-%m-%d")
        if desc and amount:
            write_expense(date, desc, amount)
        return redirect("/")

    expenses = read_expenses()

    # Get filter values from query params
    sort_order = request.args.get("sort", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    # Filter by date range
    if start_date and end_date:
        expenses = [
            exp for exp in expenses
            if start_date <= exp["Date"] <= end_date
        ]

    # Sort by amount
    if sort_order == "low":
        expenses.sort(key=lambda x: float(x["Amount"]))
    elif sort_order == "high":
        expenses.sort(key=lambda x: float(x["Amount"]), reverse=True)

    # Calculate total for filtered results
    total = sum(float(exp["Amount"]) for exp in expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        sort_order=sort_order,
        start_date=start_date,
        end_date=end_date
    )

if __name__ == "__main__":
    app.run(debug=True)
