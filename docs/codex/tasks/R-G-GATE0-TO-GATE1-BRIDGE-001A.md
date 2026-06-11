# R-G-GATE0-TO-GATE1-BRIDGE-001A

## Title

Bounded implementation task card for a same-agent Gate0-to-Gate1 bridge test
under `SAME_AGENT_BRIDGE_PROTOCOL_001`.

## Authorization Boundary

This task card authorizes future bounded implementation only after all
implementation-blocking unknowns are resolved and frozen. It does not implement
anything by itself.

It does not authorize:

- EGO mainline integration
- companion behavior
- UI behavior
- LLM integration
- AIRI integration
- relationship learning
- proactive social behavior
- affect simulation
- self-awareness simulation
- personality behavior
- deployment
- API keys or external services

## Prior Negative Evidence

This task inherits the negative Gate 1 lineage and must not imply Gate 1 is
untouched or unexplored.

Prior task:

```text
GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001
verdict = gate1_preflight_failed_graph_cache_collapse
```

The graph-cache family collapse included:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

Related residue:

```text
LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A
relevant negative pattern = shuffled_same_loss_and_function_approximation_collapse
```

Standing negative evidence: window, graph, cache, table, and cheap
function-approximation models can dominate weak belief/replay claims. This
bridge task differs from the failed lineage only if it establishes same-agent
bridge dependency, state lineage continuity, first-class graph/cache challenger
failure resistance, and held-out delta under frozen margins.

## Problem Definition

Build a minimal offline same-agent bridge test that evaluates whether Gate 1
replay/consolidation demonstrably uses Gate 0 action-conditioned
prediction-error traces and improves same-agent held-out behavior in
`CausalMemoryGrid-v0`.

The task is not to prove functional subject success. The task is to test one
bounded bridge dependency under a frozen trace/replay contract.

## Current Stage

Gate 0 is frozen as `PREDICTIVE-ACTION-LEARNING-CONTRACT-001C`.

Current allowed claim ceiling for Gate 0:

```text
001C has passed-with-caveats the independent evidence audit for bounded
isolated Gate 0 predictive-action mechanism evidence.
```

This task depends on these governance documents as read-only rule sources:

- `docs/research/SAME_AGENT_BRIDGE_PROTOCOL_001.md`
- `docs/research/SAME_AGENT_BRIDGE_TRACE_SCHEMA_001.md`
- `docs/research/SAME_AGENT_BRIDGE_BASELINES_001.md`
- `docs/research/SAME_AGENT_BRIDGE_FAILURE_TAXONOMY_001.md`
- `docs/research/SAME_AGENT_BRIDGE_EVIDENCE_SCHEMA_001.md`

During implementation, these files must not be modified by the same task that
is judged by them.

## Gate 0 Mechanism Provenance

The bridge experiment does not automatically consume frozen 001C traces unless
explicitly implemented and authorized.

Default bridge claim:

```text
re-instantiated Gate 0 contract within the bridge environment
```

Before implementation begins, freeze exactly one:

- reuse 001C mechanism code inside the new bridge environment
- reimplement the 001C contract inside the new bridge environment
- import frozen 001C artifacts as read-only historical inputs

Current status:

```text
gate0_provenance_choice = implementation_blocking_unresolved
```

Do not imply direct continuity from 001C frozen evidence to
`CausalMemoryGrid-v0` unless the implementation actually establishes it.

## Implementation-Blocking Decision Package

Implementation is blocked until the following values are filled and frozen
before the first run:

```text
metrics = implementation_blocking_unresolved
training_seed_count = implementation_blocking_unresolved
held_out_seed_count = implementation_blocking_unresolved
held_out_split_rule = implementation_blocking_unresolved
baseline_equivalence_margin = implementation_blocking_unresolved
minimum_same_agent_held_out_delta = implementation_blocking_unresolved
minimum_ablation_sensitivity_margin = implementation_blocking_unresolved
matches_or_beats_definition = implementation_blocking_unresolved
margin_freeze_ordering_requirement = freeze_before_first_execution_run
baseline_competence_checks = implementation_blocking_unresolved
control_competence_checks = implementation_blocking_unresolved
run_ledger_schema = required_for_completed_failed_and_aborted_runs
```

Threshold tuning after seeing results triggers `threshold_tuning_dependency`.

## Hypothesis

H1:
Gate 1 replay/consolidation can use same-agent Gate 0 action-conditioned
prediction-error traces to produce a measurable held-out behavior improvement
against the same-agent no-replay version.

H0:
Any apparent improvement is explained by graph/cache family lookup,
transition-table lookup, successor-map lookup, RAG summary, nearest-neighbor
trace lookup, frequency heuristics, random/majority baselines,
observation-only memory, no-action-conditioning, no-replay behavior, corrupted
replay that preserves the effect, seed overfit, or oracle leakage.

## Baseline

Required first-class graph/cache family baselines:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

Other required baselines:

- `random_baseline`
- `majority_baseline`
- `RAG_summary_baseline`
- `nearest_neighbor_trace_baseline`
- `frequency_heuristic_baseline`
- `observation_only_memory_baseline`
- `no_action_conditioning_baseline`
- `same_agent_no_replay_baseline`
- `corrupted_replay_ablation`
- `oracle_leak_scan`

Baselines must receive comparable legal inputs under a declared runtime access
manifest and must pass frozen competence checks. Incompetent or sandbagged
controls invalidate comparison; they do not become candidate evidence.

## Ablation

Required ablations:

- remove Gate 0 trace
- remove prediction-error trace
- corrupt replay order
- replace trace with observation-only memory
- replace trace with RAG summary
- run same-agent no-replay version
- run corrupted-replay ablation

## Trace/Replay Requirement

The implementation must emit the canonical fields from
`SAME_AGENT_BRIDGE_TRACE_SCHEMA_001`, including:

- `agent_id`
- `schema_version`
- `episode_id`
- `step_id`
- `state_snapshot_id`
- `parent_state_snapshot_id`
- `state_hash`
- `parent_state_hash`
- `observation`
- `action`
- `belief_before`
- `action_conditioned_prior`
- `predicted_outcome`
- `actual_outcome`
- `prediction_error`
- `belief_after`
- `memory_write`
- `replay_event`
- `consolidated_model_delta`
- `policy_delta`
- `decision_reason_source`

Same-agent continuity must be verified through a state lineage chain or
hash-chain-equivalent record. A shared `agent_id` string alone is insufficient.

## Acceptance Gate

The task may pass only if all are true:

- governance docs remain read-only during implementation
- decision package is fully resolved and frozen before first run
- Gate 0 provenance choice is resolved and frozen before first run
- `CausalMemoryGrid-v0` generated environment contract is used
- held-out seeds are evaluated
- same-agent continuity is verified by state lineage
- same-agent replay/consolidation beats same-agent no-replay on held-out seeds
  by the frozen minimum delta
- Gate 1 improvement depends on Gate 0 action-conditioned prediction-error
  traces
- graph/cache family baselines do not match or beat the mechanism
- all other required baselines do not match or beat the mechanism
- required ablations weaken or remove the claimed bridge effect by the frozen
  margin
- trace causality can be established from artifacts
- oracle/leak scan passes
- no EGO mainline files are touched
- evidence artifacts match `SAME_AGENT_BRIDGE_EVIDENCE_SCHEMA_001`

## Claim Ceiling

The strongest possible pass claim is:

```text
bounded same-agent Gate0-to-Gate1 bridge evidence under the specified
trace/replay contract.
```

Forbidden claims:

- consciousness
- subjective experience
- real emotion
- agency
- stable autonomy
- functional subject success
- companion readiness
- EGO mainline readiness

## Stop Condition

Stop and report `fail` or `blocked` if any occur:

- any graph/cache family baseline matches or beats the mechanism
- RAG baseline matches or beats the mechanism
- random or majority baseline matches or beats the mechanism
- heuristic baseline matches or beats the mechanism
- nearest-neighbor baseline matches or beats the mechanism
- observation-only memory matches the mechanism
- no-action-conditioning matches the mechanism
- no-replay version matches the mechanism
- corrupted replay preserves the claimed effect
- replay improves seen seeds only
- no held-out improvement
- trace causality cannot be established
- same-agent continuity cannot be established from state lineage
- Gate 1 works without Gate 0 trace
- schema fragmentation
- threshold tuning dependency
- hidden oracle/leak suspicion
- baseline or control competence check missing
- governance docs are modified by the implementation task
- accidental EGO mainline change

## Rollback Plan

If a stop condition triggers:

- preserve all generated artifacts
- write `failure_manifest.json`
- label failures using `SAME_AGENT_BRIDGE_FAILURE_TAXONOMY_001`
- do not patch thresholds or seeds in the same run
- do not delete failed evidence
- rollback to protocol/task-card revision if the failure is design-level
- rollback to baseline parity repair if the failure is input comparability
- block Gate 1 bridge claims if bridge dependency is missing
- keep Gate 0 frozen and make no stronger claim

## Required Files

Allowed future implementation write paths:

- `src/same_agent_bridge_001a/`
- `tests/same_agent_bridge_001a/`
- `artifacts/same_agent_bridge_001a/`

Read-only governance dependencies during implementation:

- `docs/research/SAME_AGENT_BRIDGE_PROTOCOL_001.md`
- `docs/research/SAME_AGENT_BRIDGE_TRACE_SCHEMA_001.md`
- `docs/research/SAME_AGENT_BRIDGE_BASELINES_001.md`
- `docs/research/SAME_AGENT_BRIDGE_FAILURE_TAXONOMY_001.md`
- `docs/research/SAME_AGENT_BRIDGE_EVIDENCE_SCHEMA_001.md`
- `docs/codex/tasks/R-G-GATE0-TO-GATE1-BRIDGE-001A.md`

Expected future artifact files:

- `artifacts/same_agent_bridge_001a/result.json`
- `artifacts/same_agent_bridge_001a/trace.jsonl`
- `artifacts/same_agent_bridge_001a/state_lineage.jsonl`
- `artifacts/same_agent_bridge_001a/run_ledger.json`
- `artifacts/same_agent_bridge_001a/decision_freeze_record.json`
- `artifacts/same_agent_bridge_001a/baseline_comparison.json`
- `artifacts/same_agent_bridge_001a/graph_cache_family_comparison.json`
- `artifacts/same_agent_bridge_001a/baseline_competence_report.json`
- `artifacts/same_agent_bridge_001a/control_competence_report.json`
- `artifacts/same_agent_bridge_001a/ablation_report.json`
- `artifacts/same_agent_bridge_001a/replay_report.json`
- `artifacts/same_agent_bridge_001a/bridge_dependency_report.json`
- `artifacts/same_agent_bridge_001a/same_agent_continuity_report.json`
- `artifacts/same_agent_bridge_001a/trace_causality_report.json`
- `artifacts/same_agent_bridge_001a/leak_scan_report.json`
- `artifacts/same_agent_bridge_001a/failure_manifest.json` if any failure occurs

## Forbidden Files

Forbidden unless a later governance document explicitly authorizes them:

- EGO mainline runtime files
- UI files
- companion behavior files
- LLM integration files
- AIRI integration files
- deployment files
- API key or external service configuration
- historical Gate 0 frozen artifacts
- prior failed artifacts
- governance rule files during the same implementation task

## Verification Commands

Future implementation should run only available lightweight checks unless the
task card is updated before execution.

Minimum expected commands:

```powershell
python -m pytest tests\same_agent_bridge_001a -q
git status --short
```

If dependencies are missing, do not install heavy dependencies silently. Report
the missing dependency and the reduced verification level.

## Final Report Requirements

End the future implementation task with:

- Verdict
- Layer
- Files changed
- Commands run
- Artifacts generated
- Baseline results
- Graph/cache family results
- Baseline competence results
- Control competence results
- Ablation results
- Replay result
- Same-agent continuity result
- Bridge dependency result
- Trace causality result
- Leak scan result
- Run ledger summary
- Integration debt status
- Stop conditions triggered
- Claim ceiling
- What this does not prove

## Implementation Readiness

Current status:

```text
implementation_status = blocked_until_decision_package_and_gate0_provenance_are_frozen
```

No bridge implementation may proceed from this card until those blockers are
resolved.

## What This Task Card Does Not Prove

This task card does not prove Gate 1 works. It does not prove replay or
consolidation is useful. It does not prove consciousness, subjective
experience, real emotion, agency, stable autonomy, functional subject success,
companion readiness, or EGO mainline readiness.
