#!/usr/bin/env python3
"""Dependency-free checks for the Knowledge-Engineering research archive.

Four gates, all of which can fail:

1. Every relative Markdown link or image target resolves to a tracked path
   inside the repository.
2. Every tracked Python file compiles under the running Python.
3. Every tracked notebook is valid JSON and carries no committed cell outputs,
   matching the repository rule that notebook outputs stay out of git.
4. No Jupyter checkpoint file is tracked.

External URLs are not fetched, so the verdict does not depend on third-party
availability.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
CHECKPOINT = re.compile(r"(^|/)\.ipynb_checkpoints/")


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [ROOT / name for name in result.stdout.decode("utf-8").split("\0") if name]


def link_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    parts = target.split()
    return parts[0] if parts else ""


def check_links(files: list[Path]) -> list[str]:
    errors: list[str] = []
    resolved_root = ROOT.resolve()
    for path in files:
        if path.suffix.lower() not in {".md", ".markdown"}:
            continue
        text = path.read_text(encoding="utf-8")
        targets = INLINE_LINK.findall(text) + REFERENCE_LINK.findall(text)
        for raw in targets:
            target = unquote(link_target(raw))
            if not target or target.startswith("#") or SCHEME.match(target):
                continue
            base = target.split("#", 1)[0]
            if not base:
                continue
            resolved = (path.parent / base).resolve()
            try:
                resolved.relative_to(resolved_root)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link target: {raw}")
    return errors


def check_python(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path.suffix != ".py":
            continue
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}: Python syntax error: {exc}")
    return errors


def check_notebooks(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path.suffix != ".ipynb":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid notebook JSON: {exc}")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("cells"), list):
            errors.append(f"{path.relative_to(ROOT)}: notebook has no cells list")
            continue
        for index, cell in enumerate(data["cells"]):
            if isinstance(cell, dict) and cell.get("outputs"):
                errors.append(
                    f"{path.relative_to(ROOT)}: cell {index} carries committed outputs"
                )
    return errors


def check_checkpoints(files: list[Path]) -> list[str]:
    return [
        f"{path.relative_to(ROOT)}: Jupyter checkpoint file is tracked"
        for path in files
        if CHECKPOINT.search(path.as_posix())
    ]


def main() -> int:
    files = tracked_files()
    errors = (
        check_links(files)
        + check_python(files)
        + check_notebooks(files)
        + check_checkpoints(files)
    )
    if errors:
        print(f"{len(errors)} archive check(s) failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"checked {len(files)} tracked files: links resolve; Python compiles; "
        "notebooks are output-free JSON; no checkpoints"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
