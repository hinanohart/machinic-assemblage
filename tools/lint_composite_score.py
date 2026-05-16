"""Static lint: reject any function in src/ whose return annotation collapses
ThreeEcologiesKPI to a single float.

SPEC §2.6 — composite score is intentionally absent and a static check enforces it.
"""

from __future__ import annotations

import ast
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[1] / "src" / "machinic_assemblage"


def _is_float(annotation: ast.expr | None) -> bool:
    if annotation is None:
        return False
    if isinstance(annotation, ast.Name) and annotation.id == "float":
        return True
    if isinstance(annotation, ast.Attribute) and annotation.attr == "float":
        return True
    return False


def _takes_three_ecologies(args: ast.arguments) -> bool:
    for arg in (*args.args, *args.kwonlyargs):
        if arg.annotation is None:
            continue
        if isinstance(arg.annotation, ast.Name) and arg.annotation.id == "ThreeEcologiesKPI":
            return True
        if isinstance(arg.annotation, ast.Attribute) and arg.annotation.attr == "ThreeEcologiesKPI":
            return True
    return False


def find_violations(root: pathlib.Path) -> list[tuple[pathlib.Path, int, str]]:
    out: list[tuple[pathlib.Path, int, str]] = []
    for py in root.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if _takes_three_ecologies(node.args) and _is_float(node.returns):
                    out.append((py, node.lineno, node.name))
    return out


def main() -> int:
    violations = find_violations(SRC)
    if not violations:
        print("lint_composite_score: OK (no violation)")
        return 0
    print("lint_composite_score: VIOLATIONS")
    for path, lineno, name in violations:
        print(f"  {path}:{lineno}  {name}(ThreeEcologiesKPI) -> float")
    print(
        "\nSPEC §2.6 — composite/aggregate of ThreeEcologiesKPI is intentionally "
        "absent. Refactor to return ThreeEcologiesKPI, a tuple, or per-axis values."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
