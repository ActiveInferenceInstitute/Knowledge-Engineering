"""Bind independently approved GNN bytes before any target-package import.

The vendored bootstrap and manifest are exact producer artifacts, not a local
bootstrap fork or an inventory generated from the target installation. Each
verdict needs a fresh process; installed refusal never selects source mode.
"""

from __future__ import annotations

import hashlib
import sys
import types
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parents[1] / "gnn"
BOOTSTRAP_PATH = ARTIFACTS / "gnn_bootstrap.py"
MANIFEST_PATH = ARTIFACTS / "v5.0.3-source-manifest.json"
BOOTSTRAP_SHA256 = "f638d4c01fe7de31e43d793e59bf382d0c3d1a82f365c59238334a2b40adfb37"
MANIFEST_SHA256 = "17a35bb2114e76a38119128d290d12377cb641652d70788000482366dca0a14a"
REPOSITORY = "ActiveInferenceInstitute/Generalized_Notation_Notation"
TAG = "v5.0.3"
REVISION = "8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1"
PIN_PATH = Path(".github") / "gnn-pin.json"
_BOOTSTRAP_NAME = "_knowledge_engineering_checked_gnn_bootstrap"
_MISSING = object()


@contextmanager
def checked_bootstrap() -> Iterator[tuple[types.ModuleType, bytes]]:
    """Check both frozen inputs, then execute exactly the checked source bytes."""
    bootstrap_bytes = BOOTSTRAP_PATH.read_bytes()
    if hashlib.sha256(bootstrap_bytes).hexdigest() != BOOTSTRAP_SHA256:
        raise ValueError("bootstrap-digest-mismatch: approved GNN bootstrap required")
    manifest_bytes = MANIFEST_PATH.read_bytes()
    if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
        raise ValueError("manifest-digest-mismatch: approved v5.0.3 manifest required")

    module = types.ModuleType(_BOOTSTRAP_NAME)
    module.__file__ = str(BOOTSTRAP_PATH)
    module.__package__ = ""
    previous = sys.modules.get(_BOOTSTRAP_NAME, _MISSING)
    sys.modules[_BOOTSTRAP_NAME] = module
    try:
        # Do not use an import loader: it could reread the file or accept a pyc.
        exec(
            compile(bootstrap_bytes, str(BOOTSTRAP_PATH), "exec", dont_inherit=True),
            module.__dict__,
        )
        yield module, manifest_bytes
    finally:
        if previous is _MISSING:
            sys.modules.pop(_BOOTSTRAP_NAME, None)
        else:
            sys.modules[_BOOTSTRAP_NAME] = previous


@contextmanager
def qualified_parser(
    root: Path,
    pin: dict,
    *,
    source_root: Path | None = None,
    installer: Callable[[dict], None] | None = None,
) -> Iterator[dict]:
    """Enclose imports, execution, and final rechecks in the producer's guard.

    An explicit source root selects the package directory (``src/gnn``), not a
    distribution or an automatic fallback. Installed mode leaves resolution
    alone and requires the real PEP610 origin plus complete frozen content.
    """
    if source_root is not None and installer is not None:
        raise ValueError("explicit source mode cannot install a distribution")

    with checked_bootstrap() as (bootstrap, manifest):
        bound_pin = bootstrap.read_pin(root / PIN_PATH)
        if bound_pin.raw != pin:
            raise ValueError("GNN pin changed before source admission")
        if (
            pin.get("repository") != REPOSITORY
            or pin.get("tag") != TAG
            or pin.get("revision") != REVISION
        ):
            raise ValueError("GNN pin has no independently approved source manifest")
        if any(name == "gnn" or name.startswith("gnn.") for name in sys.modules):
            raise ValueError("source-module-cached: use a fresh GNN verdict process")
        if installer is not None:
            # Frozen authority and pin identity precede any installation effect.
            installer(pin)

        if source_root is None:
            with bootstrap.qualified_source(
                bound_pin,
                manifest=manifest,
                manifest_sha256=MANIFEST_SHA256,
                origin_mode="installed",
            ) as qualification:
                yield qualification
        else:
            selected = source_root.resolve(strict=True)
            previous_path = sys.path[:]
            try:
                sys.path.insert(0, str(selected.parent))
                with bootstrap.qualified_source(
                    bound_pin,
                    manifest=manifest,
                    manifest_sha256=MANIFEST_SHA256,
                    package_root=selected,
                    origin_mode="source",
                ) as qualification:
                    yield qualification
            finally:
                sys.path[:] = previous_path
