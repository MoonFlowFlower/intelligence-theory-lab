from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import yaml


TASK_ID = "PRESERVE-ONE-GATE-HARNESS-NEGATIVE-AUDIT-LEDGER-SYNC-001A"
BASE_COMMIT = "cb95bbdb06c9fadbbbf7765ae61acc46609ed994"
START_HEAD = "c27d4ffcc855876c26211407f5a9152dd0aa405f"
BRANCH = "codex/meta-theory-scaffold"
LEDGER_MD = Path("docs/NEGATIVE_EVIDENCE_LEDGER.md")
FAILED_CLAIMS = Path("theories/failed_claims.yaml")
OUTPUT = Path("artifacts/one_gate_harness_negative_audit_ledger_sync_001a/validation_result.json")

ALLOWED_CHANGED = {
    "docs/NEGATIVE_EVIDENCE_LEDGER.md",
    "theories/failed_claims.yaml",
    "docs/codex/tasks/PRESERVE-ONE-GATE-HARNESS-NEGATIVE-AUDIT-LEDGER-SYNC-001A.md",
    "artifacts/one_gate_harness_negative_audit_ledger_sync_001a/validate_ledger_sync.py",
    "artifacts/one_gate_harness_negative_audit_ledger_sync_001a/validation_result.json",
}

FORBIDDEN_PREFIXES = (
    "src/one_gate_future_only_non_circular_harness_001a/",
    "src/evidence_admission_verifier_001a/",
    "src/same_agent_bridge_001a/",
    "tests/",
)

FORBIDDEN_POSITIVE_CLAIMS = (
    "Gate validity",
    "mechanism validity",
    "mainline effect",
    "agency evidence",
    "consciousness evidence",
    "autonomy evidence",
    "EGO readiness is authorized",
    "runtime readiness is authorized",
    "companion readiness",
)


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8").rstrip("\n")


def run_git_value(args: list[str]) -> str:
    return run_git(args).strip()


def git_blob(commit: str, path: Path) -> str:
    return subprocess.check_output(["git", "show", f"{commit}:{path.as_posix()}"], text=True, encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def changed_paths() -> list[str]:
    status = run_git(["status", "--porcelain=v1", "-uall"])
    paths: list[str] = []
    for line in status.splitlines():
        if not line:
            continue
        paths.append(line[3:])
    return sorted(paths)


def main() -> None:
    base_md = git_blob(BASE_COMMIT, LEDGER_MD)
    current_md = LEDGER_MD.read_text(encoding="utf-8")

    base_yaml_text = git_blob(BASE_COMMIT, FAILED_CLAIMS)
    current_yaml_text = FAILED_CLAIMS.read_text(encoding="utf-8")
    base_yaml = yaml.safe_load(base_yaml_text)
    current_yaml = yaml.safe_load(current_yaml_text)

    base_claims = base_yaml.get("failed_claims", [])
    current_claims = current_yaml.get("failed_claims", [])
    base_by_id = {item.get("claim_id"): item for item in base_claims}
    current_by_id = {item.get("claim_id"): item for item in current_claims}
    removed_ids = sorted(set(base_by_id) - set(current_by_id))
    mutated_ids = sorted(
        claim_id for claim_id, claim in base_by_id.items() if current_by_id.get(claim_id) != claim
    )
    new_ids = sorted(set(current_by_id) - set(base_by_id))
    new_entry = current_by_id.get("future_only_evidence_harness_noncircularity_001a", {})

    diff_numstat = run_git(["diff", "--numstat", BASE_COMMIT, "--", LEDGER_MD.as_posix(), FAILED_CLAIMS.as_posix()])
    diff_name_status = run_git(["diff", "--name-status", BASE_COMMIT, "--", LEDGER_MD.as_posix(), FAILED_CLAIMS.as_posix()])
    diff_check = subprocess.run(
        ["git", "diff", "--check", "--", LEDGER_MD.as_posix(), FAILED_CLAIMS.as_posix()],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )

    status_paths = changed_paths()
    forbidden_changed = [
        path for path in status_paths if path.startswith(FORBIDDEN_PREFIXES) or path not in ALLOWED_CHANGED
    ]

    combined_new_text = "\n".join(
        [
            current_md[len(base_md) :] if current_md.startswith(base_md) else current_md,
            current_yaml_text,
        ]
    )
    forbidden_claim_hits = [
        phrase for phrase in FORBIDDEN_POSITIVE_CLAIMS if phrase.lower() in combined_new_text.lower()
    ]

    result = {
        "task_id": TASK_ID,
        "claim_ceiling": "negative-audit ledger sync and remote-anchor hygiene only",
        "start_head_expected": START_HEAD,
        "current_head": run_git_value(["rev-parse", "HEAD"]),
        "branch": run_git_value(["branch", "--show-current"]),
        "remote_branch_head": run_git_value(["ls-remote", "origin", f"refs/heads/{BRANCH}"]).split()[0],
        "comparison_base": BASE_COMMIT,
        "dirty_file_list": status_paths,
        "diff_name_status": diff_name_status.splitlines(),
        "diff_numstat": diff_numstat.splitlines(),
        "diff_check_exit_code": diff_check.returncode,
        "diff_check_stdout": diff_check.stdout.splitlines(),
        "diff_check_stderr": diff_check.stderr.splitlines(),
        "markdown_ledger": {
            "base_sha256": sha256_text(base_md),
            "current_sha256": sha256_text(current_md),
            "base_length": len(base_md),
            "current_length": len(current_md),
            "base_prefix_preserved": current_md.startswith(base_md),
        },
        "failed_claims_yaml": {
            "parse_ok": True,
            "base_sha256": sha256_text(base_yaml_text),
            "current_sha256": sha256_text(current_yaml_text),
            "base_claim_count": len(base_claims),
            "current_claim_count": len(current_claims),
            "removed_existing_claim_ids": removed_ids,
            "mutated_existing_claim_ids": mutated_ids,
            "new_claim_ids": new_ids,
            "overwrite_allowed_current": current_yaml.get("negative_evidence_policy", {}).get("overwrite_allowed"),
            "new_entry_status": new_entry.get("status"),
            "new_entry_failure_type": new_entry.get("failure_type"),
            "new_entry_claim_ceiling": new_entry.get("claim_ceiling"),
        },
        "claim_inflation_scan": {
            "forbidden_positive_claim_hits": forbidden_claim_hits,
            "bounded_no_claim_text_present": "no Gate, mechanism, autonomy, agency, consciousness, or EGO/runtime claim"
            in str(new_entry.get("claim_ceiling", "")),
        },
        "scope_check": {
            "allowed_changed_paths": sorted(path for path in status_paths if path in ALLOWED_CHANGED),
            "forbidden_or_unexpected_changed_paths": forbidden_changed,
        },
        "append_only_verification": {
            "markdown_base_prefix_preserved": current_md.startswith(base_md),
            "yaml_removed_existing_claim_ids_empty": not removed_ids,
            "yaml_mutated_existing_claim_ids_empty": not mutated_ids,
            "diff_numstat_has_zero_deletions": all(
                line.split("\t")[1] == "0" for line in diff_numstat.splitlines() if line
            ),
        },
        "preservation_decision": "preserve",
        "revert_would_lose": [
            "canonical negative-evidence ledger reference",
            "structured failed-claim record",
            "global successor constraint requiring candidate-inaccessible ground truth",
        ],
        "acceptance_snapshot": {
            "yaml_parse_ok": True,
            "overwrite_allowed_remains_false": current_yaml.get("negative_evidence_policy", {}).get("overwrite_allowed")
            is False,
            "prior_claims_preserved": not removed_ids and not mutated_ids,
            "only_allowed_paths_dirty": not forbidden_changed,
            "c27d4ffc_is_current_head": run_git_value(["rev-parse", "HEAD"]) == START_HEAD,
        },
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "integrated admission readiness",
            "mainline effect",
            "agency",
            "consciousness",
            "autonomy",
            "runtime readiness",
            "bridge readiness",
            "EGO readiness",
        ],
    }

    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
