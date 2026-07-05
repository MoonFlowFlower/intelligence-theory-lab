# FSP-PUM-ENV-IDPROBE-001A — S3d Battery Unit-Level Resume 001A

Status: **PROPOSAL — authorized for Codex only after `S3D-BUDGET-DECISION-002A` §6 is signed +
banked and the L=30 STOP evidence is banked.** Self-gating: if either precondition is unmet, write a
precondition failure manifest and STOP. Author: Claude (auditor), 2026-07-05.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A`

## problem / objective
The L=30 battery STOPped at 31.95 CPU-h with 41/43 units complete (only `discounted_LS_lambda_0.95`
cert+NULL missing) because the cost **projection was ~1.7–1.8× biased low** on the memory-heavy
ideal/NN units (measured, not noise). Add **unit-level resume** so a re-run reuses the 41 already-
computed units and executes only the missing ones, gated by a spot-check that reused results are
bit-exact. This is an **execution-layer** change only. It certifies nothing scientific.

## precondition (BLOCKING)
1. `...-S3D-BUDGET-DECISION-002A.md` §6 signed (`[x]` mode, concrete L, endgame `[x]`, firewall
   `[x]`, operator, date) AND banked; read L from it.
2. The L=30 STOP evidence banked (corrected bank-ops — see note below).
If unmet → precondition failure manifest + STOP.

## pre-registered reuse rule (governance — decide before coding)
A **void aggregate verdict does not invalidate the correctness of a completed unit's computation.**
Per frozen spec 001A: units are independent, own-seeded, no shared mutable state (§parallelism
line 124), and reruns are contemplated with `*_v1` preservation (line 161). Therefore a completed
unit's result **MAY** be reused in the resume run **iff all hold**:
- the resume runner's `code_path_hash` == the committed runner's hash the unit was produced under
  (`2a4502a` runner, per the void `result.json` `code_path_hash`), AND
- the unit's frozen inputs (cell/member/seeds/frozen_design hash) match, AND
- the spot-check gate (below) passes.
"Void" discards the **aggregate cert/NULL adjudication**; it asserts nothing about unit miscomputation.
Reuse is provenance reuse, **not** patching a failure into a pass. If spec single-execution semantics
are later found, STOP and report (none found in this audit).

## DELTA 1 — persist per-unit results
Write each completed unit's full result (the `_score_payload` output incl. `per_user_confusion` +
`metric_digest` + `process_cpu_seconds` + `code_path_hash` + input-hash) to a per-unit artifact
keyed by `unit_id`. (The void `trace.jsonl` already carries per-unit metric + digest + timing; if it
also carries `per_user_confusion`, resume MAY reconstruct from it — verify and state which source.)

## DELTA 2 — skip-completed on resume
For each of the 43 units: if a persisted result exists AND code_hash + input-hash match → **reuse**
(load; add its **recorded** `process_cpu_seconds` to the runtime-guard cumulative). Else → **run**.
A partially-computed unit is never resumed mid-computation — it re-runs from scratch (no serialized
in-flight state; no new leakage surface).

## DELTA 3 — spot-check gate (BLOCKING)
Before trusting any reuse: select **3 completed units at random (seeded, logged)**, recompute each
bit-exact, and compare `metric_digest` + `per_user_confusion` sha256 to the persisted value. **Any
mismatch → discard ALL reuse, fall back to full re-run under L (or STOP if L cannot cover it).**
Record the 3 unit_ids, seeds, recomputed vs stored digests, pass/fail.

## DELTA 4 — _v1 preservation (spec line 161)
Before the resume run, preserve the void run's outputs under `*_wall...`-style `*_v1` names:
`result.json`, `failure_manifest.json`, `trace.jsonl`, `trace.csv`, and the stale
`s3d_certificate_report.json` / `s3d_null_env_report.json` / `baseline_comparison.json` /
`replay_report.json` → `*_void_line30_v1.json`. Do not overwrite the void evidence in place.

## runtime guard / line (from 002A)
Cumulative CPU = reused-recorded + newly-executed-measured; STOP at L; a breach of L → **battery
close per 002A §4 endgame** (no further budget note). Keep the CPU-time (contention-robust) guard;
disclose wall alongside. Threads=1 workers, N×1 ≤ physical cores, GPU prohibited.

## analysis-only one-pager (folded option 4 — NO code change unless trivial existing path)
Answer in a short note `s3d_ideal_kernel_analysis_001a.md`: does the cert-cell **per-cell ideal**
(`FactoredExactFilter` / `ideal_observer`) already run through the S2e-optimized **log-domain kernel**
(banked tractable path), or a slower path? If it is already the S2e path → record it, no change. If a
faster path exists behind an existing flag with a byte-identical result → enabling it is permitted
**only** with a regression proof (camouflage_off ideal `0.09948462995337995` bit-identical + ideal
`metric_digest` unchanged on ≥1 cell). If speedup would need a **new equivalence certificate** → do
**not** attempt it here (41/43 already computed; defer to a future battery). Analysis only; no
mechanism/threshold change.

## gates (all BLOCKING)
1. Spot-check bit-exact on 3 reused units (DELTA 3).
2. Reused units' code_hash + input-hash match the frozen producer.
3. `*_v1` void evidence preserved (DELTA 4); banked STOP/probe/spec artifacts byte-unchanged.
4. No science rule touched: ρ thresholds / 18-member set / cert cells / NULL MDE / strength / k=5 /
   frozen spec / metric definitions all identical. Resume is scheduling only; **no metric may depend
   on reuse-vs-fresh** (assert a resumed unit's metric == its void-run metric bit-exact).
5. `py_compile` + focused `pytest` for the resume/skip/spot-check logic pass.
6. If the battery now completes: `s3d_certificate_report` / `s3d_null_env_report` / `baseline_comparison`
   / `ablation_report` / `replay_report` freshly written by the committed runner (N1), internally
   consistent with the merged (reused + new) trace.

## claim ceiling
Execution-layer resume only. A completed battery under this card = at most **bounded S3d should-win +
NULL-env instrument evidence under the frozen contract at line L**, still bound by
`...-S3D-BATTERY-INTERPRETATION-PREREG-001A` (N1 provenance / N2 constant cells = controls / N3
stable_facts = fragile). Proves nothing about mechanism, learning, agency, EGO, or theory correctness.

## stop condition
STOP + failure manifest if: precondition unmet; spot-check mismatch (→ full re-run or STOP, never
silent); L breached (→ 002A endgame close); any heldout 800–999 touched; BASE-invariance fail; NULL
false-headroom; any required frozen-threshold change; reuse would require ignoring a code_hash/input
mismatch. Preserve every failure; do not patch.

## rollback / dev rules
Resume logic is isolated new code in the committed runner + per-unit artifacts (new files). Rollback
= revert the resume code + delete per-unit/`_v1` artifacts; void evidence + banked STOP untouched.
Codex runs **no git**; emit an operator bank-ops proposal (HEAD-pin + `git reset` first + allowlist of
**only** freshly-changed files + staged-count + zero-deletion + per-file Get-FileHash + scoped
`git commit -- paths` + no push) and STOP for Claude audit. Forbidden: touching frozen spec/thresholds/
filter semantics; mid-computation serialized state; making any metric depend on reuse; using the void
stale reports as if fresh; auto-raising L.

## note — the L=30 STOP bank-ops is DEFECTIVE (fix before banking the STOP)
`s3d_operator_bank_ops_proposal_line30.ps1` allowlists 4 **untracked stale** reports
(`s3d_certificate_report` / `s3d_null_env_report` / `baseline_comparison` / `replay_report`, NOT
regenerated this run) → would bank stale content mislabeled as battery output; and includes the
**unchanged tracked** `s3d_battery_runner_line30.py` → zero-stages → the strict staged-count gate
throws. Corrected STOP bank-ops must allowlist **only** the freshly-written STOP evidence
(`result.json`, `failure_manifest.json`, `trace.jsonl`, `trace.csv`, `s3d_freshness_manifest.json`,
plus any of `s3d_compute_projection_line30.0.json` / `s3d_cert_sets_manifest.json` / `ablation_report.json`
that actually changed, + the `.ps1` itself), exclude the 4 stale reports + the unchanged runner, and
retitle the commit "STOP runtime_guard_exceeded (results void)".
