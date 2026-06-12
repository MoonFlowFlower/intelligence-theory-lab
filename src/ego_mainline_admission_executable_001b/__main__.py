from __future__ import annotations

from pathlib import Path

from .runner import run_admission_001b


if __name__ == "__main__":
    repo_root = Path.cwd()
    output_dir = repo_root / "artifacts" / "ego_mainline_admission_executable_001b"
    result = run_admission_001b(repo_root=repo_root, output_dir=output_dir)
    print(result["verdict"])
