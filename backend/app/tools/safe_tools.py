import ast
import operator
import os
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(os.getenv("AGENTIA_WORKSPACE_ROOT", ".")).resolve()
MAX_FILE_BYTES = 1_000_000


def _authorized_path(relative_path: str) -> Path:
    target = (WORKSPACE_ROOT / relative_path).resolve(strict=False)
    if not target.is_relative_to(WORKSPACE_ROOT):
        raise PermissionError("Le chemin demandé sort du dossier autorisé")
    if not target.exists():
        raise FileNotFoundError("Le chemin demandé est introuvable")
    return target


def read_file(inputs: dict[str, Any]) -> dict[str, Any]:
    target = _authorized_path(str(inputs["path"]))
    if not target.is_file() or target.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Le fichier est absent, trop volumineux ou non régulier")
    return {
        "path": str(target.relative_to(WORKSPACE_ROOT)),
        "content": target.read_text(encoding="utf-8"),
    }


def list_directory(inputs: dict[str, Any]) -> dict[str, Any]:
    target = _authorized_path(str(inputs.get("path", ".")))
    if not target.is_dir():
        raise ValueError("Le chemin demandé n'est pas un dossier")
    entries = sorted(target.iterdir(), key=lambda item: item.name)[:200]
    return {
        "path": str(target.relative_to(WORKSPACE_ROOT)),
        "entries": [{"name": item.name, "directory": item.is_dir()} for item in entries],
    }


def search_text(inputs: dict[str, Any]) -> dict[str, Any]:
    query = str(inputs["query"])
    base = _authorized_path(str(inputs.get("path", ".")))
    candidates = [base] if base.is_file() else list(base.rglob("*"))[:2000]
    matches = []
    for candidate in candidates:
        try:
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(WORKSPACE_ROOT) or not resolved.is_file():
                continue
            if resolved.stat().st_size > MAX_FILE_BYTES:
                continue
            lines = resolved.read_text(encoding="utf-8").splitlines()
            for line_number, line in enumerate(lines, 1):
                if query.casefold() in line.casefold():
                    matches.append(
                        {"path": str(resolved.relative_to(WORKSPACE_ROOT)), "line": line_number}
                    )
                    if len(matches) >= 100:
                        return {"matches": matches}
        except (OSError, UnicodeError):
            continue
    return {"matches": matches}


def calculate(inputs: dict[str, Any]) -> dict[str, float]:
    expression = str(inputs["expression"])
    tree = ast.parse(expression, mode="eval")
    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exposant trop grand")
            result = operations[type(node.op)](left, right)
            if not isinstance(result, (int, float)) or abs(result) > 1e100:
                raise ValueError("Résultat hors limites")
            return float(result)
        raise ValueError("Expression arithmétique non autorisée")

    return {"result": evaluate(tree)}


def paper_trade(inputs: dict[str, Any]) -> dict[str, Any]:
    return {"mode": "PAPER_ONLY", "accepted": True, "order": inputs}


TOOL_RUNNERS = {
    "file.read": read_file,
    "filesystem.list": list_directory,
    "text.search": search_text,
    "calculator": calculate,
    "quant.paper_trade": paper_trade,
}