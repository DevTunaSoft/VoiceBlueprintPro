"""Catch missing backend startup modules without importing heavy inference runtimes."""
from __future__ import annotations

import ast
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1] / "backend"


def test_backend_main_imports_reference_existing_local_modules() -> None:
    tree = ast.parse((BACKEND / "main.py").read_text(encoding="utf-8"))
    required: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "api.routers":
                required.update(f"api.routers.{alias.name}" for alias in node.names)
            elif node.module.startswith(("api.routers.", "services.")):
                required.add(node.module)
        elif isinstance(node, ast.Import):
            required.update(
                alias.name for alias in node.names
                if alias.name.startswith(("api.routers.", "services."))
            )
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "importlib"
            and node.func.attr == "import_module"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            name = node.args[0].value
            if name.startswith(("api.routers.", "services.")):
                required.add(name)

    def exists(module: str) -> bool:
        path = BACKEND.joinpath(*module.split("."))
        return path.with_suffix(".py").is_file() or (path / "__init__.py").is_file()

    missing = sorted(module for module in required if not exists(module))
    assert not missing, f"backend/main.py imports unshipped modules: {missing}"
