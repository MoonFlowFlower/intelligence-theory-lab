# POST-BRIDGE-ADMISSION-EXECUTABLE-001B

## Task Identity

```text
task_id = POST-BRIDGE-ADMISSION-EXECUTABLE-001B
layer = bounded executable post-bridge admission test only
parent_contract = POST-BRIDGE-ADMISSION-TASK-CARD-001A
parent_contract_commit = 9e39feeae8c6974110832e6902bd28614d2d3b19
execution_authorized = true
bridge_runtime_authorized = false
ego_mainline_authorized = false
companion_behavior_authorized = false
llm_rag_authorized = false
user_model_authorized = false
relationship_authorized = false
emotion_authorized = false
personalization_product_demo_authorized = false
romance_attachment_authorized = false
persistent_profile_authorized = false
long_term_human_user_memory_authorized = false
```

## Problem Definition

Execute the bounded admission test defined by
`POST-BRIDGE-ADMISSION-TASK-CARD-001A` and determine whether candidate
post-bridge behavior depends on serialized carried state rather than hidden
lookup, identity-token lookup, memory-key lookup, state-table lookup,
transcript or summary retrieval, snapshot reload, graph/cache controls,
behavior imitation, frozen-state carryover, oracle leakage, or stitched-output
replay.

Wrong problem: prove bridge readiness, authorize EGO mainline, build bridge
runtime, create companion behavior, add LLM/RAG, model users, create
relationship/emotion/personalization/product-demo/romance/attachment behavior,
or claim mechanism validity, theory validity, agency, selfhood, consciousness,
real emotion, subjective experience, real relationship learning, or stable user
benefit.

## Current Stage

```text
post_bridge_admission_execution_status = executable bounded run
same_agent_bridge_001b_parent = 59ad22246823da107b9df4beb977fdfa34b7f986
same_agent_bridge_result_audit_parent = 797fced1f1409897d7c02bef5ebfb51a92533a3a
ego_mainline_readiness_audit_status = not authorized
```

## Hypothesis

If a single canonical serialized state carries identity, memory, replay,
self-boundary, viability, and social-latent fields across the bridge, then
heldout post-bridge behavior should change under counterfactual carried-state
replacement while remaining stable under token-only identity changes with
equivalent carried state.

## Baseline

The executable run must compare the candidate with:

```text
snapshot reload
stitched-output baseline
state-table lookup
identity-token lookup
memory-key lookup
summary retrieval
transcript retrieval
graph_lookup
transition_table
successor_map
count_table
fsm_planner
episodic_traversal
bounded-order window model order-1
bounded-order window model order-2
shuffled-history same-loss control
behavior imitation
frozen-state carryover
oracle control as upper-bound/leakage only
trace-only replay as hygiene only
random policy
fresh-agent no-carryover
```

Oracle and trace-only replay controls are diagnostics only and do not count as
fair baselines.

## Ablation

The executable run must include:

```text
reset all memory
corrupt serialized state
replace serialized state
remove replay carryover
remove self-boundary carryover
remove viability carryover
remove social-latent carryover
remove identity_continuity_state
remove memory_carryover_state
time-shift state
cross-agent state swap
duplicate identity-token contrast
freeze post-bridge learning
remove post-bridge observation update
disable action
invert bridge mapping
```

## Trace / Replay Requirement

Trace rows must include the frozen fields specified by the parent contract,
including hashed identity/memory tokens, pre/serialized/post/counterfactual
state hashes, state-field provenance hash, post-bridge observation hash,
candidate and baseline actions, later behavior, replay hashes, trace hash
chain, leakage result, and mutation check result.

The run must emit:

```text
state_replay_report.json
serialized_state_replay_report.json
provenance_replay_report.json
mutation_check_report.json
tracked_old_artifact_mutation_report.json
```

## Stage0 Freeze

Before the executable run starts, freeze:

```text
parent remote anchor verification
parent contract commit verification
task-card content hash
thresholds
metrics
baselines
ablations
distribution manifest
seed families
artifact schema
stop conditions
rollback policy
claim ceiling
```

Block before execution if any required freeze item is missing.

## Acceptance Gate

Pass only if:

```text
stage0_freeze_before_any_run = true
parent_remote_anchors_verified = true
parent_contract_verified_and_frozen = true
broader_distribution_manifest_frozen = true
heldout_contexts_independent = true
candidate_depends_on_carried_state = true
same_identity_different_state_contrast_sensitive = true
different_identity_equivalent_state_control_passed = true
memory_carryover_not_retrieval_or_key_lookup = true
serialized_state_provenance_replay_passed = true
fair_baselines_do_not_match_or_beat_candidate = true
required_ablations_sensitive = true
leakage_report_clean = true
trace_replay_passed = true
state_replay_passed = true
old_artifacts_not_mutated = true
claim_ceiling_preserved = true
```

## Claim Ceiling

```text
bounded post-bridge admission evidence under the frozen contract only
```

## Stop Condition

Stop and emit the most specific blocked or failed verdict if any of these
occur:

```text
parent_anchor_missing
remote_anchor_missing_or_hash_mismatch
scope_leak
claim_inflation
baseline_equivalence
ablation_insensitive
trace_replay_failure
state_replay_failure
serialized_state_provenance_gap
distribution_too_small_or_deterministic
hidden_lookup_suspicion
identity_token_lookup_equivalence
memory_key_lookup_equivalence
snapshot_reload_equivalence
state_table_equivalence
transcript_or_summary_retrieval_equivalence
graph_cache_equivalence
oracle_leakage
artifact_mutation
threshold_tuning_after_results
```

## Rollback Plan

If failed or blocked, preserve negative evidence, do not patch thresholds after
results, do not weaken baselines, do not delete failure artifacts, do not enter
EGO mainline, do not create bridge runtime, and repair only the exact blocker
in a later bounded task.

## Artifact Path

```text
artifacts/post_bridge_admission_executable_001b/
```

## What This Cannot Prove

This cannot prove bridge readiness, EGO readiness, companion readiness,
mechanism validity, theory validity, agency, selfhood, consciousness, real
relationship learning, real emotion, subjective experience, or stable user
benefit.
