# LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A

Task ID: `LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A`

Upstream drafting task ID: `LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-AND-RUN-CARD-001A`

Status: bounded implementation/run task card draft only. Executable only after the operator
fills every field in
`docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md` and separately
authorizes implementation/run.

Auto-Remote-Anchor: forbidden.

## Hard Preflight Check

```text
If any freeze manifest field remains UNFROZEN_OPERATOR_REQUIRED, stop with `blocked_pending_operator_freeze`.
```

Future execution must also stop with:

```text
blocked_pending_canonical_readback
```

if any required source readback fails.

## Status Block

Current layer:

```text
engineering-governance / Tier 0-2 implementation-run card draft
```

Mainline integration status:

```text
none
```

No EGO runtime, mainline, bridge, admission, UI, product behavior, mechanism candidate,
Tier 3, Tier 4-5, remote anchor, or 001C path is integrated or touched by this card.

Enabled status:

```text
none
```

This draft enables no implementation/run until operator freeze is complete and a separate
authorization names this card.

Real trigger evidence:

```text
confirm_accept_for_operator_freeze_and_tier0_2_authorization
```

The confirmed upstream repair closed the admission-verdict claim leak: Tier 0-2 cheap-tier
cannot emit `admissible_for_candidate_preflight`, cannot prove headroom, cannot authorize
candidate-card drafting, and can only request separately authorized heavier tiers through the
bounded non-admission proceed label.

Claim ceiling:

```text
This card can only define a future bounded Tier 0-2 cheap-tier implementation/run after
operator freeze. It cannot prove LRGG admissibility, headroom, mechanism evidence, EGO
readiness, or any self/agency/subjectivity/emotion/consciousness/autonomy claim.
```

## Required Source Readback

Before implementation/run, future execution must read these repo-local sources by file/API
content readback:

- `docs/codex/tasks/LRGG-CANDIDATE-FREE-CHEAP-TIER-EXECUTION-001A.md`
- `docs/codex/tasks/LRGG-CANDIDATE-FREE-PREFLIGHT-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json`
- `docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md`

Do not rely on stale mount metadata, apparent file size, or mtime. If canonical readback
fails, stop with `blocked_pending_canonical_readback`.

## Task Card Fields

Problem definition:

```text
Implement and run only the LRGG Tier 0-2 cheap-tier plus leakage/replay/provenance debug
split after all operator-frozen values are resolved, in order to test executable plumbing
and cheap-tier saturation/invalidation conditions without authoring any mechanism candidate.
```

Current stage:

```text
implementation/run card draft; no execution authorized by this drafting task
```

Mainline target:

```text
none
```

Enabled-state requirement:

```text
future executor must prove the freeze manifest has zero UNFROZEN_OPERATOR_REQUIRED fields,
required sources are readable, and the work remains isolated to separately authorized
Tier 0-2 cheap-tier paths before any implementation/run
```

Real-trigger evidence requirement:

```text
future run evidence must come from callable generator, scorer, oracle, baseline,
leakage-positive-control, replay, provenance, tamper-probe, and verdict-aggregation paths
over the frozen debug split
```

Hypothesis for future execution:

```text
If Tier 0-2 cheap-tier plumbing is executable and not cheap-tier saturated under frozen
operator values, then callable debug-split generation, scoring, oracle solvability,
cheap baseline panel execution, leakage alarms, replay recomputation, provenance checks,
and tamper probes should complete without triggering a cheap-tier block or INVALID condition.
```

Strongest baseline:

```text
The strongest cheap legal-access baseline or degenerate control may already saturate the
debug metric. If so, the correct outcome is rejection/closure/redesign, not threshold
tuning, baseline weakening, or candidate drafting.
```

Ablation requirement:

```text
future ablations and tamper probes must rerun or recompute through real callable paths;
post-hoc score edits, stored-result rewrites, and synthetic degradation flags are forbidden
```

Trace/replay requirement:

```text
future replay must recompute the official score from serialized state and action trace;
stored JSON score is not sufficient
```

Computed-evidence provenance gate:

```text
future scores, verdicts, baseline comparisons, leakage alarms, replay reports, provenance
reports, and tamper probes must be produced by callable paths with function IDs, source
hashes, input artifacts, run IDs, seed/context IDs, aggregation rule, and code path hash
```

Acceptance gate:

```text
future run is acceptable only if all freeze fields are resolved before outputs, required
source readback succeeds, all required callable components run under legal access on the
debug split, positive controls are fail-able, replay recomputes score, provenance fields are
complete, tamper probes behave as frozen, no stop condition triggers, and the verdict stays
within the Tier 0-2 terminal verdict ceiling
```

Claim ceiling:

```text
Tier 0-2 cheap-tier debug plumbing result only. No admission, no candidate-free headroom
claim, no mechanism evidence, no EGO readiness, no 001C authorization.
```

Stop condition:

```text
any unresolved freeze field, source readback failure, cheap-tier saturation, leakage
positive-control failure, replay/provenance/tamper failure, threshold change after results,
forbidden path touch, or attempt to emit admissible_for_candidate_preflight stops execution
```

Rollback plan:

```text
future implementation must be isolated and reversible under separately authorized paths;
if a stop condition triggers, preserve the negative/invalid evidence under the authorized
artifact scope and do not patch toward positive-looking output
```

Expected changed files for this drafting task:

```text
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-FREEZE-MANIFEST-001A.md
docs/codex/tasks/LRGG-CANDIDATE-FREE-TIER0-2-IMPLEMENTATION-RUN-001A.md
```

Forbidden changes for this drafting task:

```text
src/**
tests/**
artifacts/**
docs/research/**
docs/codex/contracts/**
EGO runtime/mainline/bridge/admission paths
SAME_AGENT_BRIDGE* docs
```

Auto-Remote-Anchor decision:

```text
forbidden
```

## Allowed Future Implementation/Run Scope

Future implementation/run scope, only after separate authorization:

```text
Tier 0-2 cheap-tier + leakage/replay/provenance debug split
```

Allowed components:

- isolated LRGG debug-split generator.
- scorer.
- `budget_faithful_visible_channel_oracle`.
- trivial predictors:
  - `predict_all`.
  - `predict_none`.
  - `constant_k_sweep`.
- six-member `graph_cache_family`:
  - `graph_lookup`.
  - `transition_table`.
  - `successor_map`.
  - `count_table`.
  - `fsm_planner`.
  - `episodic_traversal`.
- `direct_objective_optimizer`:
  - `discounted_wls`.
  - `least_squares`.
  - `convex_objective_solver`.
- `task_specific_classical`:
  - hand-coded DP solver under legal access.
  - finite-state filter under legal access.
  - classical planner under legal access.
- other cheap baselines:
  - random.
  - majority / mode.
  - obs-only predictor.
  - memoryless policy.
  - lookup table.
  - n-gram / short-history cache.
  - trajectory nearest-neighbor retrieval.
  - raw-observation latent decoder probe.
  - exhaustive legal probe on reduced worlds.
- value-level attacker family:
  - mean.
  - variance.
  - correlation.
  - PCA.
  - cross-episode.
  - supervised.
  - membership.
- leakage positive controls.
- replay/provenance.
- tamper probes.
- debug split only.

Forbidden:

- mechanism candidate.
- self/boundary route.
- Tier 3 unless separately authorized.
- Tier 4-5.
- training-heavy runs.
- EGO runtime/mainline/bridge/admission.
- UI/product/LLM/AIRI/external services/API keys.
- remote anchor.
- 001C.
- threshold tuning after results.
- emitting `admissible_for_candidate_preflight`.

## Terminal Verdict Ceiling

Tier 0-2 may emit only:

```text
rejected_metric_degenerate
rejected_no_fair_signal
rejected_trivially_decodable
rejected_baseline_saturated
INVALID
blocked_pending_canonical_readback
blocked_pending_operator_freeze
cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers
```

Tier 0-2 is explicitly forbidden from emitting:

```text
admissible_for_candidate_preflight
pass
ready
integrated
live
mechanism-valid
EGO-ready
001C-authorized
```

`cheap_tier_plumbing_valid_not_saturated__proceed_to_separately_authorized_heavier_tiers`
means only that Tier 0-2 debug-split plumbing did not trigger a cheap-tier block or
invalidation condition under frozen placeholders. It does not prove headroom, does not
authorize candidate-card drafting, and does not authorize admission.

## Required Future Evidence Artifacts

Future run artifacts are required, but this drafting task must not create them.

Required future artifacts:

```text
freeze_manifest_resolved_copy
source_readback_report
debug_split_manifest
generator_report
scorer_report
oracle_report
baseline_report
trivial_predictor_report
graph_cache_family_report
direct_objective_optimizer_report
task_specific_classical_report
value_level_attacker_report
leakage_positive_control_report
replay_report
provenance_report
tamper_probe_report
verdict_report
LIMITATIONS.md
```

The future verdict must be produced by callable aggregation over recorded evidence rows,
not by static dictionary or narrative assertion.

## Required Future Replay/Provenance Fields

Future evidence rows must include:

```text
generator_fn_id
generator_source_sha256
scorer_fn_id
scorer_source_sha256
oracle_fn_id
oracle_source_sha256
baseline_producer_fn_id
run_id
split_id
seed_ids
context_ids
hidden_rule_graph_id
hidden_rule_graph_hash
remapping_id
remapping_hash
initial_state_serialization
action_trace
observation_trace_hash
reward_trace_hash
replay_recomputed_score
aggregation_code_path_sha256
code_version
commit_hash
failure_path_tests
tamper_probe
```

Replay must recompute official score from serialized state and action trace.

Stored JSON score is not sufficient.

## Required Future Stop Conditions

Future execution must hard-stop if:

- any freeze manifest field remains unresolved.
- required source readback fails.
- oracle cannot solve debug distribution.
- oracle has unequal access.
- oracle reads hidden truth directly.
- nonreading oracle ablation does not collapse.
- trivial predictors defeat metric.
- metric is single-sided or unbalanced.
- graph-cache family saturates.
- direct objective optimizer saturates.
- task-specific classical solver saturates.
- lookup / n-gram / trajectory nearest-neighbor saturates.
- obs-only/value-level attacker decodes latent above ceiling.
- exhaustive legal probe reaches oracle band.
- replay cannot recompute score.
- leakage positive controls fail to alarm.
- provenance fields are missing.
- tamper probes fail.
- thresholds changed after results.
- implementation touches forbidden paths.
- any run attempts to emit `admissible_for_candidate_preflight`.

Stop means close/reject/redesign, not patch until positive-looking output appears.

## What This Does Not Prove

This card does not prove LRGG admissibility, candidate-free headroom, oracle validity,
baseline failure, replay/provenance validity, leakage scanner validity, mechanism evidence,
agency/self/subjectivity/emotion/consciousness/autonomy evidence, EGO readiness, H0/H1,
001A downgrade, 001C authorization, or TLGP-001B-R2 reinterpretation.
