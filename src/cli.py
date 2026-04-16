from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence


def build_command(name: str, args: Sequence[str]) -> list[str]:
    command_map = {
        "app": ["streamlit", "run", "src/app.py"],
        "hooks": ["pre-commit", "run", "--all-files"],
        "lint": ["ruff", "check", "."],
        "format": ["ruff", "format", "."],
        "paper": ["latexmk", "-pdf", "report.tex"],
        "paper-watch": ["latexmk", "-pvc", "-pdf", "report.tex"],
        "test": ["pytest"],
        "typecheck": ["ty", "check", "--extra-search-path", "src"],
    }
    try:
        base = command_map[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported command: {name}") from exc
    return [*base, *args]


def build_pipeline(name: str, args: Sequence[str]) -> list[list[str]]:
    if name != "check":
        raise ValueError(f"Unsupported pipeline: {name}")
    if args:
        raise ValueError("The check pipeline does not accept additional arguments.")
    return [
        build_command("lint", []),
        build_command("typecheck", []),
        build_command("test", []),
    ]


def _run(command: Sequence[str]) -> None:
    subprocess.run(command, check=True)


def _run_entry(name: str) -> int:
    _run(build_command(name, sys.argv[1:]))
    return 0


def app() -> int:
    return _run_entry("app")


def hooks() -> int:
    return _run_entry("hooks")


def lint() -> int:
    return _run_entry("lint")


def format_cmd() -> int:
    return _run_entry("format")


def paper() -> int:
    return _run_entry("paper")


def paper_watch() -> int:
    return _run_entry("paper-watch")


def test() -> int:
    return _run_entry("test")


def typecheck() -> int:
    return _run_entry("typecheck")


def fix() -> int:
    _run(["ruff", "check", ".", "--fix"])
    _run(["ruff", "format", "."])
    return 0


def check() -> int:
    for command in build_pipeline("check", sys.argv[1:]):
        _run(command)
    return 0
