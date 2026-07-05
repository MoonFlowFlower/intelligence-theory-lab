# TLGP-001B — Implementation + Non-Evidential Smoke + Handoff Report

## Verdict (of THIS task)
`HARNESS_IMPLEMENTED_AND_GUARDS_VALIDATED__OFFICIAL_RUN_HANDED_OFF`.
The full frozen-budget TLGP-001B run was **not executed in this sandbox** (measured infeasible).
No H0/H1/INVALID verdict is emitted here. The frozen prereg was not modified.

## Research layer
engineering_implementation + mechanism_hypothesis_preflight (candidate-free). No upgrade to
subjectivity / consciousness / agency / EGO claims.

## Frozen prereg
- canonical sha256 readback = `c9f4ba279b75cfc1753a6c6586f11708a9d561bbbff82e8db98859165c580d41`
  == authorized frozen sha (MATCH). raw-bytes sha256 = `35e7ade9...` (== SHA256SUMS.txt).

## Files changed (all within authorized scope; created, not modifying anything pre-existing)
src/tlgp_001b/__init__.py, preregistration.py, splits.py, lower_reference.py, meta_learners.py,
harness.py. Artifacts: artifacts/TLGP-001B/{SMOKE_NONPREREG/smoke_report.json,
SMOKE_NONPREREG/smoke_run_output.txt, HANDOFF/HANDOFF.md, HANDOFF/requirements.txt,
HANDOFF/source_manifest.json, failure_manifest.json, IMPLEMENTATION_REPORT.md}.

## Commands run
pip install scikit-learn (1.7.2), torch (2.12.1+cpu); FUSE-safe author->/tmp readback;
`PYTHONPATH=. python -m src.tlgp_001b.harness --smoke` (from a clean /tmp root); py_compile;
independent verdict-precedence check; git status / mtime forbidden-path readback. NO git write.

## Tests run (guards, validated NON-evidentially)
- frozen prereg canonical sha verify: MATCH (harness raises on mismatch).
- delivered==executed source hashes: 6/6 MATCH (mount == /tmp executed copy).
- split assertions: rule partition disjoint (500/125), train/val rules subset of TRAIN_RULES,
  test rules subset of TEST_RULES, train/test rule overlap empty, episode ids disjoint — all True.
- leakage controls (N=200): all_planted_caught=True, renamed_leak_caught=True,
  no_clean_false_flag=True, detector_valid=True, structural_boundary_ok=True.
- replay exact (smoke, 12 rows): True (ideal + meta recomputed from recorded preds, no retrain).
- tamper fail-ability (independent, exact enum): 8/8 — clean->H1; inflate-meta->H0;
  planted-leak-missed->INVALID; shuffle-not-collapsed->H0; replay-false->INVALID; capacity 8/10
  ->INVALID; context-not-collapsed->H0; INVALID precedence over H1 confirmed.

## Baseline results
NOT produced here (non-evidential smoke). The lower-reference panel (predict_all, no_adaptation,
lookup, knn1, logistic, mlp, random_forest, count_table witness) + ideal observer are wired and
run; evidential per-seed/LCB/headroom require the full frozen run (HANDOFF).

## Ablation results
Context-ablation and shuffle paths execute (smoke, non-evidential). Evidential collapse thresholds
(meta<=FLOOR+DELTA; shuffle headroom<=DELTA) require the full run.

## Replay result
Smoke replay exact = True. Full-run replay recomputes ideal+lower-reference+meta balanced accuracy
AND the verdict from recorded predictions without retraining.

## Stop conditions triggered
Compute-infeasibility STOP for the official run (measured): TF witness ~1035s/run vs 45s/call cap;
no cross-call background; full budget ~28-82h on 2 CPUs. Per the operator's instruction the frozen
budget was NOT shrunk (shrinking = forbidden post-hoc capacity/seed change -> INVALID). No
prereg-hash, leakage, replay, or forbidden-path-drift stop was triggered.

## Forbidden-path readback (mtime proof; all PREDATE session)
CLAUDE.md 06-11, AGENTS.md 06-18 12:35, pyproject.toml 06-06, src/tlgp_001a/*.py 06-18 19:49,
artifacts/TLGP-001A/* 06-18 19:47, artifacts/TLGP-001A-AUDIT-001/* 06-18 22:16, frozen prereg files
06-18 22:27, scripts/push.* 06-17 — none modified. git `M` flood is pre-existing CRLF/index drift.

## No-git readback
HEAD = c142443 (2026-06-18 16:32, pre-session), unchanged. Zero git add/commit/push/tag/anchor.

## Claim ceiling
Bounded offline. This task delivers a candidate-free harness + passing non-evidential guards +
a handoff. It is NOT meta-learner-capability evidence, NOT evidence on 001A headroom survival, and
NOT mechanism / learning / agency / self / feeling / subjectivity / intelligence / EGO-readiness.

## What this does NOT prove
Nothing about whether the within-episode headroom survives amortization (needs the full run);
nothing about meta capability (capacity control needs the full run); the smoke scores are
meaningless (2-epoch tiny nets). Drafter-implemented; requires independent audit before any future
banked verdict.

## Remaining unknowns
The actual TLGP-001B verdict (H0/H1/INVALID); per-seed headroom + LCB; whether the capacity-control
closes >=9/10. All deferred to the capable-machine run per HANDOFF.md.
