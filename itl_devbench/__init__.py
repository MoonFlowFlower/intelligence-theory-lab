"""Import shim for running the src-layout devbench package from repo root."""

from pathlib import Path

_SRC_PACKAGE = Path(__file__).resolve().parent.parent / "src" / "itl_devbench"
if _SRC_PACKAGE.exists():
    __path__.append(str(_SRC_PACKAGE))

