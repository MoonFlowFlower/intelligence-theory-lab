# Final Hostile Re-Audit — Route C Candidate Harness 001A (B4 Source-Pin Repair)

**Audit ID:** CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-HARNESS-001A-FINAL-NEGATIVE-EVIDENCE-REAUDIT-001A
**Date:** 2026-06-16 · **Role:** ITL Same-Agent Bridge Audit Role 001 (independent red-team)
**Branch:** `codex/meta-theory-scaffold` · **HEAD:** `b45598b1c56080f2f850ae088f42cf585950483e`
**Authoritative runner.py:** sha `7adf7167…`, 81765 bytes / 2017 lines (mount served a truncated 55976-byte prefix; verified via file-API)

## Verdict

**`accepted_computed_negative_evidence_close_or_downgrade`**

The repaired local harness produced **admissible computed negative evidence** that the current Route C candidate surface is **saturated by the strongest fair baseline (`exhaustive_legal_query`)** and should be **closed/downgraded**. B4 — the prior re-audit's single remaining blocker — is now substantively repaired; B1/B2/B3 and N2 remain repaired with no regression; the negative signal is independently reproduced; no new computed-evidence-path blocker and no forbidden-scope change were introduced.

Admission does **not** authorize candidate repair-to-beat-baseline, Gate execution, mainline integration, runtime/live path, or commit/push/tag/remote-anchor.

## Lineage

The prior REPAIRED re-audit (`…REPAIRED-EXECUTION-TIME-REAUDIT-001A`) returned `requires_harness_repair_before_negative_evidence_admission` with **B4 as the only blocker** (B1/B2/B3/N2 already FIXED) and listed three required fixes. This bundle implements all three. Runner grew `44b88044`/72187B → `7adf7167`/81765B — a targeted ~9.5 KB B4 repair.

## B4 — substantively repaired (the decisive question)

1. **Real independent second signal.** `read_file_bytes_via_comparison_process` (L1055-1103) runs a separate reader process — PowerShell `[System.IO.File]::ReadAllBytes` on Windows (used here: artifact `comparison_reader = powershell_system_io_readallbytes` on all 4 pins), with a python-subprocess fallback.
2. **Self-comparison rejected.** `build_source_pin_readback_report` calls `read_file_pin` with `require_comparison_signal=True` (L1240); with no second signal the pin yields `conflict_status = missing_independent_comparison_signal` → fail closed. Verified by verbatim probe.
3. **`prefix_truncation_detected` is computed**, from `len(shell) < len(first)` + prefix test (L1149-1155) — not a forced `false`.
4. **Truncated-prefix positive control through the REAL gate, end-to-end.** `build_source_pin_truncation_positive_control` (L1486-1566) injects a 35-byte prefix (exactly the first line `from __future__ import annotations\n`) via `comparison_read_overrides` into the **same** `build_source_pin_readback_report` → `conflict_status = bounded_prefix_truncation_detected` → `source_pin_readback_conflict_fail_closed` → the **same** `derive_verdict_from_gates` → `verdict = invalid`, `terminal_reason = source_pin_readback_conflict`. Artifact: `prefix_truncation_detected = true`, `source_pin_gate_fail_closed = true`. This is injection-through-the-real-callable, **not separate theater**.

Verbatim `read_file_pin` probes: truncation → `bounded_prefix_truncation_detected`; self-only+require → `missing_independent_comparison_signal`; clean second-signal → `no_conflict`; divergent non-prefix → `unresolved_readback_conflict`.

## B1/B2/B3 — no regression

- **B1 verdict derivation:** `result.verdict`/`terminal_reason`/`stop_conditions` assigned from `derive_verdict_from_gates` (L1904/1905/1954); recompute+assert (L1980-1986) before write. Verbatim execution flips `close_or_downgrade ↔ candidate_margin_cleared`.
- **B2 access parity:** 11 trace-derived dimensions; negative control perturbs `query_budget` (39 vs 40) → `access_parity_failed`; consumed by saturation gate and verdict.
- **B3 saturation control:** dual-branch (`saturated_case` → close_or_downgrade, `not_saturated_case` → not_saturated) through the same `saturation_gate`; consumes `access_parity_report.json` (verdict + file sha256).

## Negative signal — independently reproduced

| Quantity | Artifact | Independent clean-room |
|---|---|---|
| candidate per-seed | [1,1,1,1,1] = 1.0 | [1,1,1,1,1] = 1.0 |
| `exhaustive_legal_query` | [1,1,1,1,1] = 1.0 | [1,1,1,1,1] = 1.0 |
| candidate − strongest fair | **0.0** | **0.0** |
| `positional_first_k` | [0.5,0.5,0.5,0.0,0.5] = 0.4 | [0.5,0.5,0.5,0.0,0.5] = 0.4 |

The candidate is **code-identical** to `exhaustive_legal_query` (both call `query_all_policy` with budget = full legal action space). All 12 fair-interventional baselines — including all 6 graph-cache challengers (`graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`) — tie at 1.0; 8 passive baselines are discriminative (0.16-0.40); `replace_candidate_policy_with_strongest_fair_baseline` ablation == 1.0. Replay recomputed predictions match the independently computed hidden sets. The `close_or_downgrade` verdict is overdetermined and honest.

## Replay / ablation / leakage / provenance

Main replay recomputes predictions from `legal_history` (genuine). Ablations are real interventional reruns. Leakage scans 5 real artifacts + clean-negative control (all clean) with 11/11 positives detected. Provenance rows are callable-produced with all 13 required fields, single `code_path_hash 7adf7167`, roles candidate/passive/fair/control/gate/ablation/replay/leakage all present.

## Non-blocking issues (carried — do not gate admission)

- **N1:** replay sub-controls (`corrupted_state`/`missing_observation`/`forbidden_truth_field_read`) remain hardcoded `fail_closed` literals (L820-827); the main recomputation is genuine.
- **M1:** `result.verdict_consistency_check.matches_recomputed_verdict` is a hardcoded `True` (L1959); the real protection is the L1904 assignment + L1980-1986 assert.
- **P1 (provenance cleanliness):** the two positive-control files carry a later mtime (02:20) than the bundle (01:14). Content is fully consistent (same run_id, same runner sha, derived_verdict=invalid is a fail-CLOSED outcome that cannot patch failure into success, prefix == current first line); `result.json` @ 01:14 already encodes the fail-closed control and the PowerShell signal, so the whole bundle was produced by the B4-repaired code. Most plausibly a known-unreliable FUSE mtime artifact or a deterministic standalone regeneration. Recommend producing the control atomically in-run.
- **C1 (bounded scope):** the source-pin gate confirms in-process read == independent-process read of the same file; if a host truncated both readers identically it could read clean. The run is a Windows-local CLI (intact files) and the positive control proves the detector fires on divergent bytes — an honest bounded limitation.
- **E1 (environment):** the Linux FUSE mount serves a truncated, unrunnable `runner.py`; full in-sandbox re-execution was impossible. Source/artifacts were read via the authoritative file-API; the negative signal and all gate fail-abilities were verified by independent clean-room reimplementation and verbatim execution of the repaired pure functions.

## Routing (observation, not authorization)

Preserve this negative evidence and **close/downgrade** the current Route C candidate surface. Cause is **weak surface design**, not proof that Route C is impossible: the query budget equals the full legal action space, so exhaustive query recovers the hidden set with no room for any candidate mechanism. A non-trivial next surface needs **query budget < full legal action space** and must block `exhaustive_legal_query`, graph-cache, `lookup_imitation`, and `direct_objective_optimizer` from trivially recovering the hidden set. **Do not** repair the candidate to beat the baseline, weaken `exhaustive_legal_query`, remove graph-cache challengers, or change the metric.

## Scope compliance

No modification of source/tests/target-artifacts; no Gate/mainline/runtime change; no candidate/baseline/metric/threshold change; no commit/push/tag/remote-anchor; PAT in `.git/config` line 18 not read or exposed. The only repo write is this additive audit output directory.

## Claim ceiling

Final execution-time hostile re-audit of a repaired bounded local Route C candidate harness evidence bundle only. No Route C mechanism validity, no hidden-self-set inference, no self-boundary evidence, no candidate success, no Gate pass, no mainline/runtime/live effect, no agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
