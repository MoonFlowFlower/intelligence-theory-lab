# TLGP 002A Queue-#4 Route-Audit Pre-Registration (001A)

Status: PRE-REGISTERED. Written BEFORE any `RUN/FULL_SCOUT/` result exists for
`TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A`.

Purpose: freeze the **independent (red-team) adjudication** I will apply to the 002A full-scout
route *before results are visible*, so that no admission criterion can be tuned post-hoc
(CLAUDE.md: "Do not change thresholds after seeing results").

Scope boundary: the numeric thresholds (delta 0.1, epsilon 0.1, trainability 0.9, C0 anchor
0.49, replay 1e-9, clear 2/3) are ALREADY frozen in `FREEZE/design.json`
(`ca22dbcea8c4e99b4b25ff96560d02ba4335cee9f6400fc21d6369ce6420f88c`) and enforced by the
runner. This document adds ONLY the auditor overturn layer that sits on top of the runner's
self-reported verdict — the part the runner cannot self-apply.

Anchors to re-verify at audit time (do not trust readback):
- HEAD `b812552a6dab645d7bd8df45ffed39d561979140`
- design canonical `ca22dbcea8c4e99b4b25ff96560d02ba4335cee9f6400fc21d6369ce6420f88c`
- runner (host) `71ca8584d56d5925f82bac3e3db05717cf8485055bbab27ffb201e3fef36f461`
- prereg `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`
- retrieval_model `0cba9239...` (Post-LN), meta_learners r2 `358d2bb2...`,
  rung3_powered `a0dcea8d...`

---

## R0 — Recompute from raw (do not trust result.json)
From `RUN/FULL_SCOUT/trace.jsonl` + `val_curves.jsonl`, independently recompute per
`(cell_id, seed)`:
- `meta_mean` = mean of per-episode `meta_balacc` rows where `mode="normal"`, `split="test"`.
- `ideal_mean`; `fair_max` = max over `fair_balacc` names; `headroom = ideal_mean - meta_mean`.
- Confirm my recompute equals `result.json` / `baseline_comparison.json` within 1e-9.
  Mismatch = provenance **BLOCKER** (same spirit as the replay gate).
- Confirm labels are records, not model inputs: `query_truth` appears in the trace as ground
  truth only; verify `meta_prediction` could not have consumed `query_e` (instrument is the
  pinned meta_learners r2; confirm pin match).

## R1 — Independent admissibility re-derivation
- Recompute trainability `meta@k=2` per capacity from raw; re-derive `admissible_caps` /
  `failed_caps` MYSELF; confirm they equal the runner's `trainability.admissible_caps`.
  Divergence between my derivation and the runner's = **BLOCKER**.
- Confirm phase2 breakpoint cells were generated ONLY for my-derived admissible caps
  (the 001A fix: untracked/untrained caps must not enter the breakpoint map).

## R2 — The 001A-echo falsifier (highest priority)
For every capacity marked `TRAINABILITY_FAIL`, or any cap that fails to clear, read
`val_curves.jsonl` and check the training actually happened under the recipe:
- warmup applied (lr rose toward peak over ~`warmup_epochs=15`), then cosine-decayed;
- ran at least `min_epochs=35`;
- val metric / loss **plateaued** at stop (not still monotonically improving).

Overturn rule: if a "failing" cap's val was still improving at stop, it is **UNDERTRAINED,
not architecture-limited**. Then the route verdict MUST be `INCONCLUSIVE_optimization`, never
`H_arch_legit`. (This exact confound — a bigger Post-LN model failing a task a smaller one
solves because it never trained — is what invalidated 001A.)

## R3 — Per-clear overturn (reject a "clear" the runner accepted)
For each phase2 cell the runner marks `admissible_clear`, recompute from raw and REJECT the
clear if any hold:
- **Memorization:** ablation not advantage-destroyed on TEST — i.e. not both modes
  (`shuffle_adapt`, `no_adapt`) have `ablated_balacc <= fair_max + epsilon`.
- **Fair saturation:** `fair_max >= ideal_mean - delta` — the environment gives the answer
  away; the "clear" is not a mechanism signal.
- **Leakage:** leakage detector invalid, or any planted channel decodable.
- **Hairline fragility:** report per-seed spread; if the 2/3 clear hinges on a single seed
  sitting a hair above the bar, downgrade to fragile (not a robust clear).

## R4 — Verdict-specific admission
- `H_cap` admissible ONLY IF: all admissible caps passed trainability (R2 clean); NO larger
  cap failed trainability; the breakpoint STRICTLY increases across caps; every contributing
  larger-cap clear survives R3; and the increase is robust across seeds (not a one-cell fluke).
- `H_arch_legit` admissible ONLY IF: all relevant caps are trainability-admissible with NO
  undertraining signature (R2 clean), breakpoints flat/non-increasing, AND the flat caps had
  real headroom (`ideal_mean - fair_max > delta`). If a flat cap has no headroom, that is a
  saturation/no-headroom environment artifact → downgrade to inconclusive-environment, not an
  architecture claim.
- `INCONCLUSIVE_optimization` is the MANDATORY verdict if ANY larger cap fails trainability
  under this recipe (R2), regardless of breakpoint shape.

## R5 — Replay + provenance
- `replay_report.max_abs_diff <= 1e-9`; re-run the replay reconstruction from raw independently.
- `manifest.json` pins match: runner `71ca8584`, retrieval_model `0cba9239`, design `ca22dbce`,
  prereg `6e61a831`, meta_learners r2 `358d2bb2`, rung3_powered `a0dcea8d`; `source_pins`
  `all_match: true`; `protected_tracked_diff_names == []`.

## R6 — Claim ceiling (unchanged)
Strongest admissible outcome = "bounded rung1 seen-rule capacity-vs-architecture diagnostic
over the swept, *trained* range." NOT transfer / rung3 / H0 / H1 / mechanism / agency / self /
subjectivity / AGI / EGO / mainline evidence. A clean `H_cap` only licenses re-opening the
powered rung1 confirm (then rung3); it is not itself rung3 evidence.

---

## Decision ladder (applied after R0–R6)
- **BLOCKER → reject route, require repair:** provenance mismatch (R0/R5), admissibility
  divergence (R1), governance / source-pin / protected-diff failure.
- **DOWNGRADE → accept as weaker/negative:** undertraining signature (R2) → INCONCLUSIVE;
  memorization / fair-saturation / leakage on a claimed clear (R3); no-headroom flat (R4).
- **ACCEPT (bounded) :** only if R2 clean AND every claimed clear survives R3 AND the
  verdict-specific R4 admission passes; then bank at the R6 claim ceiling, byte-as-recorded,
  explicit paths only, jsonl via LFS, no `git add -A`, no push.

## What this pre-registration does not do
It does not predict the outcome, does not weaken any frozen threshold, and does not authorize
any change to protected/frozen source. If the full scout changes the trace schema, the metric
definitions, or the decision rules relative to the frozen design, that is a
governance-self-modification issue and is a BLOCKER, not an input to re-tune this rubric.
