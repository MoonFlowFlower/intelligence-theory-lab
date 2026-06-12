# EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B

## Mode

Bounded Gate4 executable preflight only.

This task executes the previously sealed Gate4 preflight task card as a bounded
evidence task.

Do not implement EGO runtime, bridge runtime, product runtime, user-facing
companion behavior, LLM/RAG integration, user profile, relationship memory,
emotion system, or mainline runtime behavior.

Do not claim Gate4 validity, mechanism validity, theory validity, architecture
correctness, agency, selfhood, consciousness, emotion, relationship learning,
stable user benefit, or EGO-mainline readiness.

## Current Sealed Boundary

Post-repair Gate4 task-card boundary:

```text
commit = fe2269313c0f45b18ef8fadcb45f4af7e1d8b9a7
remote_tag = remote-anchor-post-repair-gate4-task-card-001a-fe22693
verdict = remote_anchor_post_repair_gate4_task_card_001a_pass
```

## Source Task Card

Controlling source:

```text
docs/codex/tasks/EGO-MAINLINE-GATE4-PREFLIGHT-TASK-CARD-001A.md
```

Do not invent new Gate4 semantics. If the source task card is missing,
ambiguous, contradicted by canonical source evidence, or insufficient to execute
a bounded preflight, stop and return:

```text
gate4_preflight_executable_001b_blocked_contract_discovery_required
```

## Problem Definition

Execute a bounded Gate4 preflight over synthetic scripted partner processes to
test whether a canonical Gate0/Gate1/Gate2/Gate3 shared-state loop can be
extended with a bounded Gate4 social-latent / social representational-gap proxy.

The candidate must not be explainable by lookup, retrieval, profile table,
graph/cache, count/statistic, bounded-window order model, stitched output,
oracle label access, leakage, or trace-only replay.

## Current Stage

Planning/drafting boundary is sealed.

This task may execute only the bounded Gate4 preflight specified by the sealed
task card.

This task may create isolated test harness code, tests, and artifacts for Gate4
preflight evidence.

It may not modify prior sealed artifacts except by reading them.

## Hypothesis

If the candidate preserves one canonical shared state, updates a bounded social
latent state through interaction feedback, defeats callable fair baselines,
degrades under required ablations, passes leakage scans with positive controls,
and replays behavior from serialized_state plus observation, then it may provide
bounded Gate4 preflight evidence only.

## Baseline

Required independent callable baselines:

* partner-ID lookup
* static per-partner profile table
* preference-table lookup
* transcript retrieval
* summary retrieval
* bounded-order window model order-1
* bounded-order window model order-2
* shuffled-history same-loss control
* graph_lookup
* transition_table
* successor_map
* count_table
* fsm_planner
* episodic_traversal
* behavior-only imitation
* fixed social script / persona policy
* frozen social-latent model
* Gate0/Gate1/Gate2/Gate3 policy without social_latent_state
* stitched-output baseline with no shared social state
* random policy
* oracle partner/social-label control as upper-bound/leakage only
* trace-only replay as hygiene only

Each baseline must be a callable implementation invoked during the run.

Static dictionaries, literal verdicts, prefilled scores, or test-only mock pass
reports are not acceptable.

## Candidate Requirements

The candidate must:

* use synthetic scripted partner processes only;
* preserve one canonical shared state lineage from Gate0/Gate1/Gate2/Gate3;
* include bounded `social_latent_state`;
* update `social_latent_state` from interaction feedback and social prediction
  error;
* avoid access to oracle labels, partner identity shortcuts, future responses,
  hidden partner policy internals, answer keys, or heldout labels;
* produce behavior from current serialized state plus current observation;
* record prediction, action, feedback, state update, and next prediction path;
* support deterministic replay.

## Required Ablations

Rerun candidate episodes under real interventions:

* remove social_latent_state
* freeze social_latent_state
* replace social history
* remove social_prediction_error
* invert partner response mapping
* remove interaction feedback
* remove Gate1 replay input to social update
* remove Gate2 self-boundary input to social update
* remove Gate3 viability/action-priority input to interaction policy
* freeze shared state
* disable action
* delayed partner response
* partial observability
* heldout partner-context-action compositions
* counterfactual interaction contrast
* perturb partner policy
* perturb social feedback channel
* learning freeze

Required degradation must be computed, not asserted. If expected degradation is
absent, return blocked or failed with artifacts preserved.

## Computed-Evidence Provenance Gate

Every reported result, baseline, ablation, leakage, replay, route permission,
prerequisite, metric, and verdict-like value must record:

* `producer_function`
* `input_artifacts`
* `run_id`
* `seed/context/episode IDs`
* `aggregation_rule`
* `code_path_hash`
* `output_artifact_path`

Every score must be produced by callable computation paths.

Forbidden:

* literal pass/fail constants
* static dictionaries posing as metrics
* unconditional clean reports
* tests that only assert final verdict strings
* generated JSON that is not derived from executed code paths

## Leakage Scan

Implement real scanners over:

* generated markdown
* generated JSON
* generated text artifacts
* observations
* linkage keys
* artifact paths
* serialized states
* trace events

Required positive controls:

* unauthorized readiness claim
* oracle partner label leak
* partner-ID shortcut leak
* future-response leak
* hidden policy leak

The positive controls must be detected. Generated artifacts from the real run
must have no unauthorized positive hits.

## Replay Requirement

Replay must recompute candidate behavior and Gate4 route decisions from:

```text
serialized_state + observation
```

Replay must not only compare stored hashes.

Replay must verify:

* candidate action recomputation
* social_latent_state recomputation
* prediction error recomputation
* route/verdict recomputation
* linkage from state update to later behavior

## Old Artifact Guard

Before execution:

* inventory old sealed artifact paths;
* hash prior sealed artifacts.

After execution:

* inventory again;
* hash again;
* compare;
* report mutation.

Unexpected old artifact mutation is a hard failure.

## Allowed Files

Allowed new task card:

```text
docs/codex/tasks/EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B.md
```

Allowed new source directory:

```text
src/ego_mainline_gate4_preflight_executable_001b/
```

Allowed new test file:

```text
tests/test_ego_mainline_gate4_preflight_executable_001b.py
```

Allowed new artifact directory:

```text
artifacts/ego_mainline_gate4_preflight_executable_001b/
```

Do not modify previous sealed artifact directories. Do not modify EGO runtime or
bridge runtime directories.

## Required Artifacts

Create under:

```text
artifacts/ego_mainline_gate4_preflight_executable_001b/
```

Required artifacts:

* `anchor_verification.json`
* `source_contract_readback.json`
* `execution_manifest.json`
* `run_ledger.jsonl`
* `synthetic_partner_processes.json`
* `episode_manifest.json`
* `candidate_trace.jsonl`
* `candidate_state_snapshots.jsonl`
* `candidate_metric_report.json`
* `baseline_invocation_report.json`
* `baseline_metric_report.json`
* `contrast_report.json`
* `ablation_report.json`
* `leakage_scan_report.json`
* `leakage_positive_control_report.json`
* `replay_trace.jsonl`
* `replay_recomputation_report.json`
* `old_artifact_inventory_before.json`
* `old_artifact_inventory_after.json`
* `old_artifact_hash_comparison.json`
* `old_artifact_mutation_report.json`
* `computed_evidence_provenance_report.json`
* `claim_ceiling.txt`
* `result.json`

## Acceptance Gate

Pass only if all are true:

1. Current branch is `codex/meta-theory-scaffold`.
2. The sealed remote tag resolves exactly to
   `fe2269313c0f45b18ef8fadcb45f4af7e1d8b9a7`.
3. The source Gate4 task card is present and bounded.
4. Synthetic partner processes are used; no real user data is used.
5. Candidate preserves one canonical shared state lineage.
6. Candidate metrics are computed by callable paths.
7. All required baselines are callable and invoked.
8. Candidate is not beaten by simple lookup/retrieval/profile/cache/window/
   statistic/stitched baselines under the declared metric.
9. Required ablations rerun episodes under real interventions.
10. Required ablations show expected degradation or produce a bounded failure
    verdict.
11. Leakage scanner detects positive controls.
12. Real generated artifacts have no unauthorized positive leakage.
13. Replay recomputes from serialized_state plus observation.
14. Replay is not hash-only.
15. Old sealed artifacts are unchanged.
16. Full relevant tests pass.
17. Final git status is clean after commit.
18. Claim ceiling is not exceeded.

## Stop Conditions

Stop and return blocked if:

* anchor verification fails;
* source task card is missing or ambiguous;
* Gate4 semantics must be invented;
* any baseline cannot be implemented as a callable independent baseline;
* any ablation is simulated by static reports rather than rerun;
* leakage positive controls are not detected;
* replay is hash-only;
* old sealed artifacts mutate;
* EGO runtime, bridge runtime, or product runtime work begins;
* any stronger claim is made.

## Rollback Plan

If blocked:

* preserve failure artifacts under this task's artifact directory;
* do not patch old artifacts;
* do not weaken the source task card;
* do not create runtime workarounds;
* return the smallest next repair or contract-discovery task.

## Expected Claim Ceiling

At maximum:

```text
bounded Gate4 executable preflight evidence over synthetic partner-process proxy only
```

This cannot prove:

* Gate4 validity.
* Mechanism validity.
* Theory validity.
* Architecture correctness.
* EGO-mainline readiness.
* Agency.
* Selfhood.
* Consciousness.
* Emotion.
* Relationship learning.
* Stable user benefit.
