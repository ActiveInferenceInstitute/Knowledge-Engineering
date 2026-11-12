#!/usr/bin/env python3
"""Dependency-free archive checks for the Knowledge-Engineering research archive.

Four checks, each of which can fail:

1. ``links``: every relative Markdown link or image target resolves to a path
   inside the repository.
2. ``python``: every tracked Python file compiles under the running Python.
3. ``notebooks``: every tracked notebook is valid JSON and carries no committed
   cell outputs, matching the repository rule that notebook outputs stay out of
   git.
4. ``checkpoints``: no Jupyter checkpoint file is tracked.

External URLs are not fetched, so the verdict does not depend on third-party
availability. This module holds the checks; `gate.py` is the command-line entry
point that runs them individually or together.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from subprocess import run as run_process
from urllib.parse import unquote

INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
EXTERNAL_TARGET = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
CHECKPOINT = re.compile(r"(^|/)\.ipynb_checkpoints/")


def tracked_files(root: Path) -> list[Path]:
    """Return every tracked path, resolved against ``root``."""
    result = run_process(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [root / name for name in result.stdout.decode("utf-8").split("\0") if name]


def link_target(raw: str) -> str:
    """Extract the destination from a Markdown link target, dropping any title."""
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    parts = target.split()
    return parts[0] if parts else ""


def _relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def check_links(files: list[Path], root: Path) -> list[str]:
    """Flag relative link or image targets that do not resolve inside ``root``."""
    errors: list[str] = []
    resolved_root = root.resolve()
    for path in files:
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue
        text = path.read_text(encoding="utf-8")
        targets = INLINE_LINK.findall(text) + REFERENCE_LINK.findall(text)
        for raw in targets:
            target = unquote(link_target(raw))
            if not target or target.startswith("#") or EXTERNAL_TARGET.match(target):
                continue
            base = target.split("#", 1)[0]
            if not base:
                continue
            resolved = (path.parent / base).resolve()
            try:
                resolved.relative_to(resolved_root)
            except ValueError:
                errors.append(f"{_relative(path, root)}: link escapes repository: {raw}")
                continue
            if not resolved.exists():
                errors.append(f"{_relative(path, root)}: missing link target: {raw}")
    return errors


def check_python(files: list[Path], root: Path) -> list[str]:
    """Flag tracked Python files that do not compile."""
    errors: list[str] = []
    for path in files:
        if path.suffix != ".py":
            continue
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"{_relative(path, root)}: Python syntax error: {exc}")
    return errors


def check_notebooks(files: list[Path], root: Path) -> list[str]:
    """Flag notebooks that are not valid JSON or carry committed cell outputs."""
    errors: list[str] = []
    for path in files:
        if path.suffix != ".ipynb":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{_relative(path, root)}: invalid notebook JSON: {exc}")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("cells"), list):
            errors.append(f"{_relative(path, root)}: notebook has no cells list")
            continue
        for index, cell in enumerate(data["cells"]):
            if isinstance(cell, dict) and cell.get("outputs"):
                errors.append(
                    f"{_relative(path, root)}: cell {index} carries committed outputs"
                )
    return errors


def check_checkpoints(files: list[Path], root: Path) -> list[str]:
    """Flag tracked Jupyter checkpoint files."""
    return [
        f"{_relative(path, root)}: Jupyter checkpoint file is tracked"
        for path in files
        if CHECKPOINT.search(path.as_posix())
    ]


CHECKS = {
    "links": check_links,
    "python": check_python,
    "notebooks": check_notebooks,
    "checkpoints": check_checkpoints,
}


def run(names: tuple[str, ...], root: Path) -> tuple[int, list[str]]:
    """Run the named checks over one ``git ls-files`` read.

    Returns the number of tracked files inspected and the collected errors, so
    callers can report a single consistent summary.
    """
    files = tracked_files(root)
    errors: list[str] = []
    for name in names:
        errors.extend(CHECKS[name](files, root))
    return len(files), errors
