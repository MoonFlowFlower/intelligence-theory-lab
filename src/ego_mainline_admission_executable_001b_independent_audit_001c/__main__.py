from __future__ import annotations

from pathlib import Path

from .runner import run_audit


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "artifacts" / "ego_mainline_admission_executable_001b_independent_audit_001c"
    result = run_audit(repo_root=repo_root, output_dir=output_dir, verify_remote=True)
    print(result["verdict"])


if __name__ == "__main__":
    main()
