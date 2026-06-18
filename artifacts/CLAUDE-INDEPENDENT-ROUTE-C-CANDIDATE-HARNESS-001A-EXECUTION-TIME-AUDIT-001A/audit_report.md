# Independent Hostile Execution-Time Audit — Route C Candidate Harness 001A

**Audit ID:** CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-HARNESS-001A-EXECUTION-TIME-AUDIT-001A
**Date:** 2026-06-16
**Role:** independent auditor / red-team (Same-Agent Bridge Audit Role 001)
**Target:** `src/route_c_candidate_harness_001a/runner.py` (sha256 `e07980a4…`), `tests/test_route_c_candidate_harness_001a.py`, `artifacts/route_c_candidate_harness_001a/`

---

## Verdict

**`requires_harness_repair_before_negative_evidence_admission`**

**Implementation may proceed:** No.

The underlying computed negative *signal* is genuine, reproducible, and fail-able: the candidate ties the strongest fair interventional baseline (delta = 0.0), and the computed comparison gates respond correctly to inputs. **But the *reported* `close_or_downgrade` is packaged with a hardcoded `result.json` headline verdict, a self-reported access-parity gate sitting on the declared causal path, and several non-fail-able / hand-filled controls.** Those defects do not make the negative finding false — they prevent the *bundle* from being admitted as clean computed negative evidence. All defects are repairable, so this is not an unrepairable rejection.

## Research layer

Engineering implementation + mechanism-hypothesis (negative). Audit only — no implementation performed, repo not modified.

---

## Core finding (what is actually true)

`candidate_policy` and `fair_interventional_baseline.exhaustive_legal_query` **both call `query_all_policy(episode)` with the default order**, and the query budget equals the item count (8 = all items). Both therefore query the entire legal action space and recover the exact hidden set → Jaccard score 1.0. **The candidate is code-identical to the strongest fair baseline; `delta = 0.0` is structural, not coincidental.** This is honest baseline equivalence for *this* candidate implementation, and it is exactly what the lab's baseline rule says to report.

This is corroborated three independent ways, all computed:
- The parity-independent **margin gate** returns `close_or_downgrade` because advantage 0.0 < 0.05.
- The **`replace_candidate_policy_with_strongest_fair_baseline_policy` ablation** scores 1.0 = candidate score.
- The scorer is **discriminative** — passive/observation-only baselines genuinely score 0.16–0.40; ablations 0.20–1.00 — so the 1.0 values are earned, not pinned.

## Decisive execution-time probe (fail-ability)

Monkeypatching every baseline to score 0.0 while the candidate stays 1.0 (delta = 1.0):

| Artifact / field | Result |
|---|---|
| `baseline_comparison.margin_decision.verdict` | **flipped → `candidate_margin_cleared`** |
| `baseline_comparison.saturation_decision.verdict` | **flipped → `not_saturated`** |
| `failure_manifest.stop_conditions_triggered` | **flipped → `[]`** |
| `result.json["verdict"]` | **stayed `close_or_downgrade` (literal)** |
| `result.json["terminal_reason"]` | **stayed `strongest_fair_baseline_saturated_candidate` (literal)** |

Conclusion: the computed gates **are** fail-able (good — the negative finding is meaningful), while the `result.json` headline verdict is a **hardcoded constant** disconnected from them (bad — the reported verdict is not computed).

---

## Check-by-check

| # | Check | Result |
|---|---|---|
| 1 | CLI recomputes candidate/baselines/controls/replay/ablation/leakage/provenance | **PASS** — exit 0; pytest 4 passed; byte-identical to committed after CRLF→LF normalization |
| 2 | `exhaustive_legal_query` is a fair baseline under access parity | **PASS (substance)** — code-identical to candidate → provably equal access |
| 3 | Access parity is computed, not self-reported | **FAIL** — static all-true dict; consumes no access traces |
| 4 | Saturation control consumes `access_parity_report.json` and returns `close_or_downgrade` | **FAIL** — consumption asserted via literal field; hardcoded inputs; never exhibits `not_saturated` |
| 5 | Margin failing control fails closed | **PASS** — adv 0.01 → `close_or_downgrade` via real `margin_gate` |
| 6 | Replay recomputes from serialized state + legal history, not stored hashes | **PASS w/ caveat** — main recomputation real; sub-controls hardcoded |
| 7 | Ablations rerun under real intervention | **PASS** — real episode reruns; varying scores |
| 8 | Leakage positive controls actually detected | **PASS w/ caveat** — detected, but detector-matched & no real-artifact scan / clean-negative |
| 9 | Source-pin readback not reliant only on FUSE/mount (truncation/stale) | **FAIL** — hardcodes `prefix_truncation_detected=false`; no independent-reader check |
| 10 | Provenance rows callable-produced & complete | **PASS** — 115 rows, 0 missing fields, 8 roles, real code hash |
| 11 | No literal/static/hand-filled/result-patching path creates the verdict | **FAIL** — `result.json` verdict + terminal_reason are literals (proven by probe) |
| 12 | No forbidden scope changes (Gate runner/mainline/runtime/bridge/scheduler/product/admission; commit/push/tag/anchor) | **PASS** — writes only output_dir; read-only git; outputs untracked |

## Blocking issues

- **B1 (check 11):** `result.json` `verdict` + `terminal_reason` are non-computed literals (runner.py L1328–1329); the reported `close_or_downgrade` is not itself fail-able. Valid computed negative evidence lives only in `baseline_comparison.json` / `failure_manifest.stop_conditions`.
- **B2 (check 3):** access parity is a hand-filled all-true report consuming no access traces; the declared `terminal_reason` (saturation) conjoins this hardcoded-True parity.
- **B3 (check 4):** the saturation "failing negative control" does not read `access_parity_report.json` and never exhibits `not_saturated`; not fail-able in the discriminating direction.
- **B4 (check 9):** source-pin readback asserts no prefix truncation without any independent-reader / expected-size check.

## Non-blocking issues

- **N1 (check 6):** replay `controls` (corrupted_state/missing_observation/forbidden_truth) are hardcoded `fail_closed`, not executed.
- **N2 (check 8):** leakage scanner only confirms planted, detector-matched positives; never scans real artifacts; no clean-negative.
- **N3:** the test suite asserts literal outcomes (verdict, delta, parity) — a fixture, not a falsification test.
- **N4 (env):** Windows CRLF source_artifact makes source/predeclaration hashes line-ending-dependent across machines.
- **N5 (env):** in broken-git environments `forbidden_scope_status` is vacuously clean; independent filesystem check used here.

## Required fixes before admission

1. Derive `result.json` verdict/terminal_reason from the computed gates and assert `result.verdict == gate outcome`; fail on mismatch.
2. Compute access parity from recorded candidate/baseline access traces; make it fail on inequality; feed the computed parity into `saturation_gate`.
3. Replace hardcoded saturation/replay negative controls with controls that execute the failing **and** clearing inputs through the same callables (in-bundle fail-ability in both directions).
4. Run the leakage scanner over the real artifacts plus a clean-negative control.
5. Implement a real source-pin truncation check (independent reader / expected size / known-good hash).
6. Make tests assert fail-ability (a perturbed candidate must flip the gate verdict).

---

## Evidence summary

**Files changed:** none (audit only; repo not modified).
**Commands run:** fresh CLI rerun; `pytest` (4 passed); `sha256sum runner.py` (= committed code hash); CRLF-normalized diffs; fail-ability monkeypatch probe; provenance + scope scans.
**Tests run:** `tests/test_route_c_candidate_harness_001a.py` → 4 passed (note: asserts literals).
**Baseline results:** candidate 1.0; strongest fair `exhaustive_legal_query` 1.0; all 12 fair/graph-cache baselines 1.0; strongest passive `positional_first_k` 0.40; delta 0.0.
**Ablation results:** real reruns, scores 0.20–1.00; `replace_candidate_policy_with_strongest_fair_baseline_policy` = 1.0 (equivalence corroborated).
**Replay result:** genuine recomputation from legal history (5/5 match); sub-controls hardcoded.
**Stop conditions triggered (real run):** `strongest_fair_baseline_saturated_candidate` (also margin non-clearance). In probe: none — gates correctly emptied.
**Reproducibility:** `runner.py` sha256 = committed `code_path_hash` `e07980a4…`; `trace.jsonl` and `baseline_comparison.json` byte-identical to committed after CRLF→LF (only `predeclaration_hash` / `source_artifact_sha256` differ, both downstream of source CRLF).

## Claim ceiling

Execution-time audit of bounded local candidate-harness evidence only. No mechanism validity, candidate success, Gate pass, mainline/runtime effect, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## What this audit does not prove

- Not that Route C is impossible — only that **this** candidate implementation is baseline-equivalent.
- Not that the candidate has any mechanism, self-boundary, or hidden-self-set inference capability.
- Does not certify the harness integrity-control layer (several controls non-fail-able as written).
- Grants no Gate / mainline / runtime / anchor admission.

## Remaining unknowns

- Whether a *non-trivial* Route C candidate (one that does more than exhaustive legal querying) could beat the fair interventional + graph-cache panel — untested; current candidate cannot, by construction.
- Cross-machine hash stability once line endings are normalized.
