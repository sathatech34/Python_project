from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        num1 = float(request.form.get("num1"))
        num2 = float(request.form.get("num2"))
        operation = request.form.get("operation")

        if operation == "add":
            result = num1 + num2
        elif operation == "subtract":
            result = num1 - num2
        elif operation == "multiply":
            result = num1 * num2
        elif operation == "divide":
            result = num1 / num2 if num2 != 0 else "Error (Divide by 0)"
        else:
            result = "Invalid Operation"
    except ValueError:
        result = "Invalid Input"

    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
