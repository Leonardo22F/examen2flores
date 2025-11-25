from __future__ import annotations

import ast
import operator
import re
from typing import Callable, Optional

from flask import Flask, jsonify, request

app = Flask(__name__)


# --- Calculator core ---------------------------------------------------------

ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

ALLOWED_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_ast(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_ast(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BIN_OPS:
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        return ALLOWED_BIN_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_UNARY_OPS:
        return ALLOWED_UNARY_OPS[type(node.op)](_eval_ast(node.operand))
    raise ValueError("Unsupported expression")


def safe_eval_expression(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Constant,
                ast.Load,
                ast.Pow,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Mod,
                ast.UAdd,
                ast.USub,
            ),
        ):
            continue
        raise ValueError("Unsupported token")
    return _eval_ast(tree)


def ai_guess_operation(text: str) -> Optional[Callable[[float, float], float]]:
    cleaned = text.lower()
    if any(word in cleaned for word in ["sum", "suma", "add", "mas"]):
        return operator.add
    if any(word in cleaned for word in ["resta", "sub", "menos"]):
        return operator.sub
    if any(word in cleaned for word in ["multiplica", "multiplicacion", "por", "producto", "x"]):
        return operator.mul
    if any(word in cleaned for word in ["divide", "division", "entre", "sobre", "dividir"]):
        return operator.truediv
    return None


def ai_resolve(text: str) -> float:
    numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text)]
    operation = ai_guess_operation(text)
    if operation and len(numbers) >= 2:
        return operation(numbers[0], numbers[1])

    return safe_eval_expression(text)


# --- HTTP interface ----------------------------------------------------------

@app.route("/", methods=["GET"])
def root():
    return jsonify(
        {
            "message": "Calculadora Flask con interprete basico de lenguaje natural.",
            "usage": "POST /api/calc con JSON {'input': 'suma 5 y 3'} o {'input': '2+2*2'}",
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/calc", methods=["POST"])
def calculate():
    payload = request.get_json(silent=True) or {}
    user_input = payload.get("input")
    if not user_input or not isinstance(user_input, str):
        return (
            jsonify({"error": "Se requiere el campo 'input' con una expresion o pregunta."}),
            400,
        )

    try:
        result = ai_resolve(user_input)
    except Exception:
        return (
            jsonify({"error": "No pude interpretar la operacion. Intenta con otra frase o expresion."}),
            400,
        )

    mode = "nlp" if ai_guess_operation(user_input) else "expression"
    return jsonify({"input": user_input, "mode": mode, "result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
