# TLGP-001A — Independent Read-Only Audit (CANONICAL)  ·  AUDIT-001

- audit_id: TLGP-001A-AUDIT-001 · date: 2026-06-18 · role: Same-Agent Bridge Audit Role 001
- **Verdict: BANK as candidate-free gap-testbed** (claim ceiling unchanged; no upgrade). No blocker.
- implementation_authorized: **false**

## Method
Independent audit script (`audit_independent.py`, reproduced here) imports NO repo module: it
re-enumerates the 625 mod-K rules, reimplements the ideal observer and balanced-accuracy, and
**re-fits all 7 baselines from the raw `trace.jsonl` data**. This is strictly more independent
than the run's own `replay_report.json`, which trusts the recorded predictions/scores.

## A. Independent replay (recomputed from raw trace)
- integrity 0/200 violations: every recorded `query_e == (w·x + c·a) mod 5` for the recorded rule.
- n_consistent 200/200 match; ideal_mean = 1.000000 (exact); single-step clean = 0.198 (floor).
- max_fair recomputed 0.2025 vs recorded 0.1968 — divergence is the stochastic `no_adaptation`
  only; **all fitted baselines match to 4 dp** (knn 0.1957 / logistic 0.1954 / mlp 0.1940 /
  rf 0.1945), predict_all & lookup exact. Both far below FLOOR+DELTA=0.30 → `baselines_fail` robust.
- Independent reimplemented verdict == recorded verdict == `world_discriminates_structure_inference`;
  all 6 checks True.

## B. Fail-ability (tamper) probes — all 5 flip the verdict
baseline→0.50 ⇒ weak; planted leak marked missed ⇒ invalid; shuffle headroom→0.50 ⇒ weak;
replay_exact→False ⇒ weak; single-step→0.50 ⇒ weak. The verdict is genuinely fail-able along
every axis (not a non-fail-able field).

## C. Provenance
prereg sha256 recomputed from the embedded dict == recorded == `3fdad0f3…`. All 9 live source
files' sha256 == recorded delivered == executed. The audited source is the run's source, byte
for byte; no FUSE fork, no hidden second path.

## D. Candidate-free
`candidate_free=True`; AGENTS = ideal + 7 fair baselines; no candidate token. Confirms tests NO
candidate.

## Non-blocking residuals (disclosed)
1. Shuffle + leakage live in separate-seed datasets not in the trace; covered by source-logic +
   internal arithmetic consistency + fail-ability (T2/T3), **not regenerated from seed**. Zero
   residual = a full re-run from the sha-verified source.
2. Prereg "frozen-before-run" rests on hash self-consistency, not an external timestamp; the wide
   margins (0.197 vs 0.30; 1.0 vs 0.40) argue against post-hoc tuning.

## What this does NOT prove
Not mechanism / learning / intelligence / agency / self / feeling / subjectivity / EGO-readiness.
Does not show any **learner** can acquire the rule family — the headroom is, by construction, the
value of KNOWING the family. That is exactly the TLGP-001B (cross-episode meta-learner) question.

## Next
TLGP-001B candidate-free meta-learner panel extension (R1 card). Requires explicit operator
implementation authorization + frozen prereg before any execution.
