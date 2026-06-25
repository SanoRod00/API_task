"""
Calculations API
Run: python task.py
Test: http://127.0.0.1:5000/calculate
"""

import math
import os
from flask import Flask, request, jsonify

app = Flask(__name__)


def _validate_number(value, name):
    if isinstance(value, bool):
        raise TypeError(f"'{name}' must be a number, not a boolean.")
    if not isinstance(value, (int, float)):
        raise TypeError(f"'{name}' must be a number.")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"'{name}' must be a finite number.")


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


def power(a, b):
    if abs(b) > 1000:
        raise ValueError("Exponent out of safe range (max ±1000).")
    try:
        return a ** b
    except (ValueError, ZeroDivisionError) as e:
        raise ValueError(f"Cannot compute {a} ** {b}: {e}")


def square_root(a):
    if a < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    return math.sqrt(a)


def modulo(a, b):
    if b == 0:
        raise ValueError("Modulo by zero is not allowed.")
    return a % b


OPERATIONS = {
    "add":         add,
    "subtract":    subtract,
    "multiply":    multiply,
    "divide":      divide,
    "power":       power,
    "modulo":      modulo,
    "square_root": lambda a, _: square_root(a),
}

SINGLE_OPERAND_OPS = {"square_root"}


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Calculations API is running.",
        "endpoints": {
            "POST /calculate": "Perform a calculation",
            "GET  /operations": "List available operations",
        }
    })


@app.route("/operations", methods=["GET"])
def list_operations():
    return jsonify({
        "operations": list(OPERATIONS.keys()),
        "usage": {
            "two_operand":    {"a": "number", "b": "number", "operation": "add|subtract|multiply|divide|power|modulo"},
            "single_operand": {"a": "number", "operation": "square_root"},
        }
    })


@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    operation = data.get("operation")
    if not operation:
        return jsonify({"error": "Missing required field: 'operation'."}), 400

    if operation not in OPERATIONS:
        return jsonify({
            "error": f"Unknown operation '{operation}'.",
            "available": list(OPERATIONS.keys()),
        }), 400

    a = data.get("a")
    if a is None:
        return jsonify({"error": "Missing required field: 'a'."}), 400

    try:
        _validate_number(a, "a")
    except (TypeError, ValueError) as e:
        return jsonify({"error": str(e)}), 400

    b = data.get("b")
    if operation not in SINGLE_OPERAND_OPS:
        if b is None:
            return jsonify({"error": f"Operation '{operation}' requires field 'b'."}), 400
        try:
            _validate_number(b, "b")
        except (TypeError, ValueError) as e:
            return jsonify({"error": str(e)}), 400

    try:
        result = OPERATIONS[operation](a, b)
        response = {"operation": operation, "a": a, "result": result}
        if operation not in SINGLE_OPERAND_OPS:
            response["b"] = b
        return jsonify(response)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "detail": str(e)}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV") == "development"
    print("Starting Calculations API on http://127.0.0.1:5000")
    print("Available operations:", ", ".join(OPERATIONS.keys()))
    app.run(debug=debug)
