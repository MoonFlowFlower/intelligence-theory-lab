"""Artifact generation (task card section 16) and the final bounded report."""

import json
import os
import re
import shutil

from . import config as cfg
from .attestation import (NETWORK_POLICY, STORAGE_POLICY, NETWORK_POLICY_HASH,
                          STORAGE_POLICY_HASH)
from .gates import SuiteEvidence, evaluate, CORE_RUNS
from .validator import split_records

_STDLIB_ALLOWED = {
    "math", "json", "hashlib", "os", "sys", "time", "uuid", "random",
    "collections", "datetime", "argparse", "subprocess", "shutil", "re",
}


def _scan_imports(pkg_dir):
    found, offending = set(), []
    pat = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_.]*)")
    for root, _d, files in os.walk(pkg_dir):
        if "__pycache__" in root:
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            with open(os.path.join(root, fn), encoding="utf-8") as f:
                for line in f:
                    m = pat.match(line)
                    if m:
                        top = m.group(1).split(".")[0]
                        if top == "" or m.group(1).startswith("."):
                            continue
                        found.add(top)
                        if top not in _STDLIB_ALLOWED and top != cfg.TASK_ID:
                            offending.append({"file": fn, "import": m.group(1)})
    return {"imports_found": sorted(found), "non_stdlib_non_package": offending,
            "isolated": not offending}


def _strip_series(m):
    return {k: v for k, v in m.items() if k != "series"}


def _w(suite_dir, name, obj):
    with open(os.path.join(suite_dir, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True)


def finalize(suite_dir, tests_summary):
    ev = SuiteEvidence(suite_dir)
    res = evaluate(ev, tests_summary)
    verd = res["verdicts"]

    groups = {}
    for run_id in ev.metrics:
        meta = ev.meta(run_id)
        groups.setdefault(meta.get("group"), []).append(run_id)

    _w(suite_dir, "main_metrics.json", {
        "core_runs": {r: ev.metrics[r] for r in CORE_RUNS},
        "note": "canonical evidence is the raw per-step trace; these are derived summaries",
    })
    _w(suite_dir, "baseline_results.json", {
        "metrics": {r: _strip_series(ev.metrics[r]) for r in groups.get("baselines", [])},
        "gates": res["baseline_gates"],
        "coldstart_duplicate_comparison": res["duplicate_comparison"],
        "comparability_note": "baselines share each regime's seed; action/observation "
                              "streams are identical because the policy is external",
    })
    _w(suite_dir, "ablation_results.json", {
        "metrics": {r: _strip_series(ev.metrics[r])
                    for r in groups.get("ablations", []) + groups.get("protocol", [])},
        "validation": {r: {k: v for k, v in ev.validation[r].items() if k != "replay"}
                       for r in groups.get("protocol", [])},
        "gates": res["ablation_gates"],
    })
    _w(suite_dir, "perturbation_results.json", {
        "metrics": {r: _strip_series(ev.metrics[r]) for r in groups.get("perturbations", [])},
        "memdel_flush_comparison": res["memdel_flush_comparison"],
        "gates": res["perturbation_gates"],
    })

    sample_receipts = []
    pres = split_records(ev.records["core_as"])[1]
    for p in pres[:2] + pres[-1:]:
        sample_receipts.append(p.get("pre_commit_receipt"))
    _w(suite_dir, "commitment_report.json", {
        "commit_mode": cfg.COMMIT_MODE,
        "commit_sink_id": cfg.COMMIT_SINK_ID,
        "receipt_type": "local_mock",
        "receipt_verifier_key_id": "local_mock_unverifiable",
        "externally_verifiable": False,
        "evidence_status": "local mock only: implementation tests may pass, external "
                           "evidence claim is forbidden (task card 7.5)",
        "external_sink_unavailable_reason": "external timestamp/transparency services are "
                                            "external services, forbidden by the lab boundary",
        "sample_receipts": sample_receipts,
        "receipts_per_core_run": {r: len(split_records(ev.records[r])[1]) for r in CORE_RUNS},
        "chronology_validated": all(not ev.validation[r]["chronology_errors"] for r in CORE_RUNS),
    })

    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    import_scan = _scan_imports(pkg_dir)
    attest_runs = {}
    for run_id in ev.metrics:
        posts = split_records(ev.records[run_id])[2]
        meta = ev.meta(run_id)
        attest_runs[run_id] = {
            "declared_retrieval_enabled": meta.get("retrieval_enabled"),
            "declared_replay_enabled": meta.get("replay_enabled"),
            "measured_external_memory_access_total":
                sum(p.get("external_memory_access_count", 0) for p in posts),
            "retrieval_events_logged": sum(len(p.get("retrieval_event_log") or [])
                                           for p in posts),
            "replay_steps_in_trace": len(split_records(ev.records[run_id])[3]),
            "cold_start_marker": meta.get("cold_start_marker"),
            "cache_epoch_id": meta.get("cache_epoch_id"),
            "runtime_manifest_hash": meta.get("runtime_manifest_hash"),
        }
    _w(suite_dir, "attestation_report.json", {
        "storage_policy": STORAGE_POLICY, "storage_policy_hash": STORAGE_POLICY_HASH,
        "network_policy": NETWORK_POLICY, "network_policy_hash": NETWORK_POLICY_HASH,
        "import_isolation_scan": import_scan,
        "runs": attest_runs,
        "coldstart_duplicate_comparison": res["duplicate_comparison"],
        "limit_note": "audit-hook attestation is in-process instrumentation, not a "
                      "hardware/OS attestation; combined with replay and duplicates it "
                      "exceeds self-reported flags but is not externally verifiable",
    })

    _w(suite_dir, "replay_report.json", {
        r: ev.validation[r]["replay"] for r in ev.validation
        if ev.validation[r]["replay"].get("applicable")
    })
    _w(suite_dir, "stop_condition_report.json", {
        "stop_conditions": res["stop_conditions"],
        "triggered": verd["stop_conditions_triggered"],
        "gate_status": {
            "implementation": [(g["gate_id"], g["status"]) for g in res["implementation_gates"]],
            "evidence": [(g["gate_id"], g["status"]) for g in res["evidence_gates"]],
            "ablation": [(g["gate_id"], g["status"]) for g in res["ablation_gates"]],
            "perturbation": [(g["gate_id"], g["status"]) for g in res["perturbation_gates"]],
            "baseline": [(g["gate_id"], g["status"]) for g in res["baseline_gates"]],
        },
    })

    result = {
        "task_id": cfg.TASK_ID,
        "task_card": cfg.TASK_CARD,
        **verd,
        "belief_claim": res["belief_claim"],
        "theta_claim": res["theta_claim"],
        "tests": tests_summary,
        "artifact_index": sorted(os.listdir(suite_dir)),
    }
    _w(suite_dir, "result.json", result)

    failures = {
        "protocol_blockers": verd["protocol_blockers"],
        "failed_gates": verd["failed_gates"],
        "stop_conditions_triggered": verd["stop_conditions_triggered"],
        "note": "T1_external_commit_missing is an expected blocker under the lab "
                "boundary (no external services); it caps the evidence verdict and is "
                "preserved here, not patched around.",
    }
    _w(suite_dir, "failure_manifest.json", failures)

    shutil.copyfile(os.path.join(suite_dir, "runs", "core_as", "trace.jsonl"),
                    os.path.join(suite_dir, "trace.jsonl"))

    _write_final_report(suite_dir, res, tests_summary)
    return res


def _fmt_gates(gates):
    lines = []
    for g in gates:
        lines.append(f"- `{g['gate_id']}`: **{g['status']}**"
                     + (f" — measured: `{json.dumps(g['measured'], default=str)[:240]}`"
                        if g["measured"] is not None else ""))
    return "\n".join(lines)


def _write_final_report(suite_dir, res, tests_summary):
    v = res["verdicts"]
    body = f"""# FINAL REPORT — {cfg.TASK_CARD}

## Verdicts

- implementation_verdict: `{v['implementation_verdict']}`
- evidence_verdict: `{v['evidence_verdict']}` (class: `{v['evidence_verdict_class']}`)
- claim_mode: `{v['claim_mode']}`
- protocol_blockers: `{v['protocol_blockers']}`
- failed_gates: `{v['failed_gates']}`
- stop_conditions_triggered: `{v['stop_conditions_triggered']}`

## Claim mode sub-verdicts (judged separately, 12.2.13)

- belief-update claim: `{res['belief_claim']['verdict']}`
- theta-learning claim: `{res['theta_claim']['verdict']}`

## Tests

- exit_code: `{tests_summary.get('exit_code')}`
- summary: `{tests_summary.get('summary', '')[:400]}`

## Implementation gates (12.1)

{_fmt_gates(res['implementation_gates'])}

## Evidence gates (12.2)

{_fmt_gates(res['evidence_gates'])}

## Baseline gates (9.2)

{_fmt_gates(res['baseline_gates'])}

## Ablation gates (10.2)

{_fmt_gates(res['ablation_gates'])}

## Perturbation gates (11.2)

{_fmt_gates(res['perturbation_gates'])}

## Stop conditions triggered

{json.dumps(v['stop_conditions_triggered'])}

## Claim ceiling

{v['claim_ceiling']}

## Rollback recommendation

{"None required: implementation gates passed; evidence blocked only by the pre-declared external-commitment requirement (rollback path 14.2 applies only if external commitment is later authorized)." if v['implementation_verdict'] == 'bounded_contract_pass' else "Rollback to implementation repair (14.1)."}

## What this does not prove

This experiment produces bounded offline mechanism evidence only, for one frozen
finite-state contract in one small environment family. It does not prove and must
not be quoted as proving: consciousness, subjective experience, real emotion,
self-awareness, agency, functional-subject status, electronic life, companion
readiness, AGI, biological equivalence, stable user benefit, correctness of any
total theory (Bio-CMBC, CVPSM, VCCO, CMBC, R/G), superiority over transformers,
or finality of Bayesian filtering. Local-mock commitment means chronology
evidence is not externally verifiable. Results are specific to the declared
seeds, thresholds, and environment parameters.
"""
    with open(os.path.join(suite_dir, "FINAL_REPORT.md"), "w", encoding="utf-8") as f:
        f.write(body)


def write_readme(suite_dir):
    body = f"""# {cfg.TASK_CARD} — bounded experiment artifacts

## What was implemented

An isolated finite-state predictive-action learning experiment instantiating the
frozen skeleton (belief distribution, pseudo-count action-conditioned transition
model, pseudo-count observation model, all-action next-observation prediction,
pre-outcome NLL, entropy/calibration diagnostics, online belief + pseudo-count
updates, same-history all-action counterfactual logging), with 9 baselines,
10 ablations, 9 perturbations, an immutable hashed trace contract with
pre-outcome local-mock commitment, measured no-retrieval/no-replay attestation,
full-trace replay validation, cold-start duplicate runs, and gate/stop-condition
evaluation.

## How to run (from the repository root)

    python -m predictive_action_learning_contract_001 init --suite-dir <DIR>
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group core
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group baselines
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group ablations
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group protocol
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group perturbations
    python -m predictive_action_learning_contract_001 duplicates --suite-dir <DIR>
    python -m predictive_action_learning_contract_001 finalize --suite-dir <DIR> \\
        --tests-exit-code <N> --tests-summary "<pytest tail>"

Tests: `python -m pytest tests/test_predictive_action_learning_contract_001*.py -q`

## Explicitly out of scope

EGO mainline, companion behavior, LLM integration/inference, prompts,
personality, emotion, relationship learning, UI, product demo, replay /
consolidation, long-term memory, RAG inside the learner, vector databases, web
access, learner tool use, policy optimization, model-free RL, neural world
models, autonomous agents, and any consciousness / subjective experience /
agency / functional-subject / AGI / companion-readiness claim.

## Evidence status

Commitment sink is a LOCAL MOCK (external timestamp services are forbidden lab
boundary items). Per task card 7.5 the evidence verdict is therefore capped at
`protocol_blocked_by_T1_external_commit_missing` regardless of gate outcomes.
"""
    with open(os.path.join(suite_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(body)
