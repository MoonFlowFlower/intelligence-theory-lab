from pathlib import Path

from .runner import ARTIFACT_DIR_REL, run_reconciliation


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / ARTIFACT_DIR_REL
    run_reconciliation(repo_root=repo_root, output_dir=output_dir)
