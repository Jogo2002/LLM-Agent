"""Math evaluation tool for the chat program.

This module evaluates simple Python expressions and returns JSON-formatted results.
"""

import json


def calculate(expression):
    """Evaluate a mathematical expression and return a JSON result.

    >>> calculate("2 + 2")
    '{"result": 4}'
    >>> calculate("10 / 4")
    '{"result": 2.5}'
    >>> calculate("invalid")
    '{"error": "Invalid expression"}'
    >>> calculate("__import__('os').system('echo hi')")
    '{"error": "Invalid expression"}'
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"result": result})
    except Exception:
        return json.dumps({"error": "Invalid expression"})


calculate_schema = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Use this for mathematical expressions and arithmetic. Evaluate a mathematical expression and return the result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
}