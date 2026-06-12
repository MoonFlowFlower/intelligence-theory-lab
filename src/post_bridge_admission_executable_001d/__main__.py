from pathlib import Path

from .core import pretty_json
from .runner import run_admission_001d


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    print(pretty_json(run_admission_001d(repo_root=repo_root)))

if __name__ == "__main__":
    main()
