from pathlib import Path

from .runner import run_preflight_001c


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "artifacts" / "gate1_replay_consolidation_001c_executable_preflight"
    run_preflight_001c(repo_root=repo_root, output_dir=output_dir)
