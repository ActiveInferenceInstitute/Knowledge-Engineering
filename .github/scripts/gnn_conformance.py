#!/usr/bin/env python3
"""Pinned Generalized Notation Notation (GNN) conformance for this archive.

The repository pins one upstream parser revision in ``.github/gnn-pin.json``
(schema ``gnn-importer-pin/v1``). This module validates that pin, installs the
pinned distribution when asked, and verifies that

* the installed parser reports the pinned version,
* every ``*.gnn.md`` sketch in the repository parses, passes the syntax
  validator, and passes the type checker, or
* when the repository carries no sketch, a pinned upstream exemplar does.

The GitHub Actions job ``gnn conformance (pinned)`` and the local gate arm
``gnn`` both call `gate.py`, which calls this module, so the job body exists
once. Fetching the parser and the exemplar needs the network; nothing here
touches the committed research artifacts.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

PIN_PATH = Path(".github") / "gnn-pin.json"
PIN_SCHEMA = "gnn-importer-pin/v1"
EXPECTED_REPOSITORY = "ActiveInferenceInstitute/Generalized_Notation_Notation"
EXEMPLAR_PATH = "input/gnn_files/basics/static_perception.md"
RUNTIME_DEPENDENCIES = ("defusedxml", "psutil", "pyyaml")
TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")
REVISION = re.compile(r"^[0-9a-f]{40}$")
RECORDED = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FETCH_TIMEOUT = 60


def load_pin(root: Path) -> dict:
    """Read the pin file, raising `ValueError` when it is not an object."""
    data = json.loads((root / PIN_PATH).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{PIN_PATH.as_posix()}: pin file is not a JSON object")
    return data


def validate_pin(pin: dict) -> list[str]:
    """Return every schema or identity problem with ``pin``."""
    errors: list[str] = []
    if pin.get("schema") != PIN_SCHEMA:
        errors.append(f"pin schema is {pin.get('schema')!r}, expected {PIN_SCHEMA!r}")
    if pin.get("repository") != EXPECTED_REPOSITORY:
        errors.append(
            f"pin repository is {pin.get('repository')!r}, "
            f"expected {EXPECTED_REPOSITORY!r}"
        )
    if not TAG.match(str(pin.get("tag", ""))):
        errors.append(f"pin tag {pin.get('tag')!r} is not vMAJOR.MINOR.PATCH")
    if not REVISION.match(str(pin.get("revision", ""))):
        errors.append(f"pin revision {pin.get('revision')!r} is not a 40-hex commit")
    if not RECORDED.match(str(pin.get("recorded", ""))):
        errors.append(f"pin recorded {pin.get('recorded')!r} is not YYYY-MM-DD")
    return errors


def install_spec(pin: dict) -> str:
    """Return the pip requirement for the pinned distribution."""
    return (
        "generalized-notation-notation @ "
        f"git+https://github.com/{pin['repository']}.git@{pin['revision']}"
    )


def install(pin: dict) -> None:
    """Install the parser's runtime dependencies and the pinned distribution."""
    pip = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    subprocess.check_call([*pip, *RUNTIME_DEPENDENCIES])
    subprocess.check_call([*pip, "--no-deps", install_spec(pin)])


def _exemplar_bytes(pin: dict) -> bytes:
    """Download the pinned upstream exemplar."""
    url = (
        "https://raw.githubusercontent.com/"
        f"{pin['repository']}/{pin['revision']}/{EXEMPLAR_PATH}"
    )
    with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT) as response:
        return response.read()


def _check_parses(sketch: Path) -> None:
    from gnn.parsers.basic import parse_gnn_formal, validate_gnn_syntax

    parsed = parse_gnn_formal(sketch)
    if parsed is None or getattr(parsed, "parse_errors", None):
        raise SystemExit(f"{sketch} did not parse cleanly")
    valid, errors = validate_gnn_syntax(sketch.read_text(encoding="utf-8"))
    if not valid:
        raise SystemExit(f"{sketch} syntax errors: {errors!r}")


def _check_types(sketches: list[Path]) -> None:
    from gnn.type_checker import GNNTypeChecker

    with tempfile.TemporaryDirectory(prefix="gnn-types-") as output_dir:
        model_dir = Path(output_dir) / "models"
        model_dir.mkdir()
        for index, sketch in enumerate(sketches):
            shutil.copy2(sketch, model_dir / f"{index:03d}_{sketch.name}")
        checked = GNNTypeChecker().validate_gnn_files(model_dir, Path(output_dir))
        # ``validate_gnn_files`` is tri-state, not boolean: ``True`` when every
        # file validated, ``2`` when one or more files were invalid *or* no GNN
        # file was found, ``False`` on a hard failure. ``2`` is truthy, so a
        # truthiness test passes an invalid model set; only ``True`` may pass.
        if checked is not True:
            raise SystemExit(
                "GNN type checker did not verify the checked sketches: "
                f"validate_gnn_files returned {checked!r} "
                "(True = every file validated, 2 = invalid files or none found, "
                "False = hard failure)"
            )


def verify(root: Path, pin: dict) -> dict:
    """Verify the installed parser and the checked sketches; return the receipt."""
    try:
        from gnn import __version__
    except ImportError as exc:
        raise SystemExit(
            "the pinned GNN parser is not installed for this interpreter; "
            "run `python .github/scripts/gate.py gnn --install`"
        ) from exc

    expected_version = str(pin["tag"]).removeprefix("v")
    if __version__ != expected_version:
        raise SystemExit(f"installed GNN {__version__!r} does not match {pin['tag']!r}")

    sketches = sorted(
        path
        for path in root.rglob("*.gnn.md")
        if ".git" not in path.relative_to(root).parts
    )

    with tempfile.TemporaryDirectory(prefix="gnn-conformance-") as workdir:
        if sketches:
            checked, source = sketches, "repository"
        else:
            exemplar = Path(workdir) / Path(EXEMPLAR_PATH).name
            exemplar.write_bytes(_exemplar_bytes(pin))
            checked, source = [exemplar], "pinned-exemplar"
        for sketch in checked:
            _check_parses(sketch)
        _check_types(checked)

    return {
        "gnn-version": __version__,
        "pin-revision": pin["revision"],
        "models": len(checked),
        "source": source,
        "result": "verified",
    }


def run(root: Path, *, install_first: bool = False) -> int:
    """Validate the pin, optionally install the parser, then verify."""
    try:
        pin = load_pin(root)
    except (OSError, ValueError) as exc:
        print(f"gnn conformance: {exc}", file=sys.stderr)
        return 1
    errors = validate_pin(pin)
    if errors:
        print("gnn conformance: pin does not satisfy the contract:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if install_first:
        install(pin)
    print(json.dumps(verify(root, pin), sort_keys=True))
    return 0
