from __future__ import annotations

from pathlib import Path

from .runner import run_preflight_001b
from .core import pretty_json


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    print(pretty_json(run_preflight_001b(repo_root=repo_root)))


if __name__ == "__main__":
    main()
