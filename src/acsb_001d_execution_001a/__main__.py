from pathlib import Path

from .runner import execute_challenge


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    execute_challenge(repo_root, persist_artifacts=True)


if __name__ == "__main__":
    main()
