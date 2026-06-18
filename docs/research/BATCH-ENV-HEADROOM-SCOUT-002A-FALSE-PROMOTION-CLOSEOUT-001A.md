# BATCH-ENV-HEADROOM-SCOUT-002A False Promotion Closeout 001A

Status: closed as false-positive promotion / scout-method negative evidence.

Created: 2026-06-17.

Auto-Remote-Anchor: forbidden.

## Decision

`BATCH-ENV-HEADROOM-SCOUT-002A` is closed with verdict:

`blocked_promotion_false_positive_direct_decode`

Affected promoted sketch:

`relational_contrast_budget_probe`

Blocked downstream artifact:

`artifacts/batch_env_headroom_scout_002a/full_harness_task_card_relational_contrast_budget_probe.md`

That full-harness task card must not be executed. The 002A promotion must not be
cited as positive promotion evidence, headroom evidence, Gate1 evidence,
candidate feasibility evidence, route-tournament evidence, or mechanism
validity evidence.

BATCH-ENV-HEADROOM-SCOUT-002A cannot be cited as positive promotion evidence.

## Current Layer

engineering-governance / Phase-0 environment portfolio scouting audit closeout
and repair-card drafting.

## Mainline Integration Status

none.

## Enabled Status

no runtime/mainline/admission/bridge path enabled.

## Real Trigger Evidence

The closeout is based on repo-local readback of:

- `scripts/research/batch_env_headroom_scout_002a.py`;
- `artifacts/batch_env_headroom_scout_002a/promoted_full_harness_candidates.json`;
- `artifacts/batch_env_headroom_scout_002a/micro_probe_results.json`;
- `artifacts/batch_env_headroom_scout_002a/static_kill_scan.json`;
- `artifacts/batch_env_headroom_scout_002a/sketch_registry.json`;
- `artifacts/batch_env_headroom_scout_002a/full_harness_task_card_relational_contrast_budget_probe.md`.

Source readback shows the promoted sketch generator computes:

`oracle_index = (contrast_a + 2 * contrast_b + phase) % 3`

from the legal channels `contrast_a`, `contrast_b`, and `phase_probe`.

The visible-channel oracle reads exactly those three legal channels under
budget 3 and applies the same formula. Its trace records no hidden-state,
answer-key, or future-label access. Therefore the oracle is itself a
budget-faithful legal-channel compute baseline. Because the same computation was
not registered and scored as a fair baseline, the reported promotion gap is not
accepted.

## Audit Findings

1. Static-kill outputs are not accepted evidence. They echo author-provided
   `static_kill_flags` as kill reasons. A set-equality check over all 16 sketches
   showed the scan-derived reasons equal the self-declared true flags for 16/16
   sketches.
2. The promoted micro-probe battery was underpowered for promotion. It invoked
   only:
   `budget_limited_belief_state_planner`,
   `greedy_information_gain_or_uncertainty_planner_under_budget`,
   `graph_lookup`, `transition_table`, `successor_map`, `fsm_planner`,
   `passive_decoder`, `size_only`, and `degenerate_controls`.
3. Required compute/fitted baselines were missing for this promotion decision:
   `exhaustive_legal_query`, `count_table`, `episodic_traversal`,
   `trace_only_replay`, `ngram_trace_lookup`, and a fitted legal-channel
   learner.
4. The promoted sketch reported oracle score `0.883417548044231`, strongest
   cheap baseline `transition_table` score `0.3388257153474545`, and preliminary
   gap `0.5445918326967765`. This gap is now interpreted as
   memorize-vs-compute asymmetry, not environment headroom.
5. Train/test legal-signature disjointness defeats lookup/memorization but does
   not defeat legal-channel computation. It is insufficient as a promotion
   argument unless compute-capable fair baselines are scored and remain below
   oracle.
6. Numeric computation was not fabrication. The micro-probe produced real
   differentiated scores and hashes. The failure is methodological:
   incomplete baselines, oracle/fair-compute asymmetry, and non-independent
   static kill scanning.

## Route Decision

- do not execute the promoted full-harness task card;
- do not start route tournament;
- do not implement candidates;
- do not implement WM-P, VSB-C, or CSL;
- do not treat 002A promotion as headroom evidence;
- preserve 002A only as scout-method negative evidence;
- treat reject/safe directions as heuristic hints only, not canonical evidence;
- draft 002B repair card, but do not run 002B in this task.

## Claim Ceiling

002A false-promotion closeout and 002B repair-card drafting only.

No headroom confirmation. No Gate1 pass. No mechanism validity. No candidate
feasibility. No runtime/mainline effect. No agency, autonomy, consciousness, or
EGO readiness.

## Next Minimal Closed-Loop Action

Review the drafted
`docs/research/BATCH-ENV-HEADROOM-SCOUT-002B-INDEPENDENT-STATIC-AND-COMPUTE-BASELINE-SCOUT-TASK-CARD-001A.md`.
Run 002B only as a separate candidate-free scout task after that review.

## What This Does Not Prove

This does not prove that any environment has headroom. It does not prove that
all 002A rejections are canonical; static-kill rejections are heuristic only
because the static scanner was not independent. It does not authorize candidate
implementation, route tournament, full harness execution, runtime/mainline
wiring, Gate1, mechanism validity, agency, autonomy, consciousness, or EGO
readiness.
