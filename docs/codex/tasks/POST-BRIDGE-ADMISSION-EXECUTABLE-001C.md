# POST-BRIDGE-ADMISSION-EXECUTABLE-001C

## Task Identity

```text
task_id = POST-BRIDGE-ADMISSION-EXECUTABLE-001C
layer = bounded replacement executable post-bridge admission test only
current_stage = replacement executable for invalidated 001B nominal pass
claim_ceiling = bounded post-bridge admission evidence under computed-evidence provenance contract only
```

This task is a new bounded executable replacement for
`POST-BRIDGE-ADMISSION-EXECUTABLE-001B`. It must not patch 001B, rewrite 001B
artifacts, delete negative evidence, weaken thresholds, weaken baselines, enter
EGO mainline, create bridge runtime, create companion behavior, or create
LLM/RAG, user-model, relationship, emotion, personalization, product-demo,
romance, attachment, persistent-profile, or long-term human-user memory work.

## Required Contract Citation

This task cites and must enforce:

```text
docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md
```

If the executable path does not cite and enforce this contract, execution must
block with:

```text
post_bridge_admission_executable_001c_block_missing_computed_evidence_contract_citation
```

## Parent Evidence and Negative Evidence

```text
POST-BRIDGE-ADMISSION-EXECUTABLE-001B
commit = bd0e7158237671c1a5e527b64c8e06ca0ae4e5b3
remote_tag = remote-anchor-001h-bd0e715
nominal_verdict = post_bridge_admission_executable_001b_pass
current_status = invalidated as downstream positive evidence

POST-BRIDGE-ADMISSION-EXECUTABLE-001B-REDTEAM-FAILURE-ADMISSION-001A
commit = 1157c8dec0f0fc1299f7d64454545af161a97cd3
verdict = post_bridge_admission_executable_001b_redteam_failure_admission_001a_block_hardcoding_or_lookup_admitted

COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A
commit = 09cff85ac377aaa99f913c30e3d31f85264d1344
remote_tag = remote-anchor-001i-09cff85
verdict = computed_evidence_provenance_contract_001a_created

AGENTS computed-evidence instruction canonicalization
commit = 0a3babb40bd9b4ada3f01d3752ae43105596fb72
remote_tag = remote-anchor-001j-0a3babb
```

The 001B red-team admission is binding negative evidence. It admitted blockers
for source-generated constants/static values, non-behavior-causal replay,
unconsumed distribution surfaces, rejection-selected counterfactuals, and
provenance rows that were not resolvable to trace objects.

## Problem Definition

Run a replacement post-bridge admission executable test that directly fixes the
001B false-positive family. The test must determine whether candidate
post-bridge behavior depends on deserialized `serialized_state + observation`
through real measured computation, while fair baselines, ablations, contrasts,
leakage scans, and replay are computed through callable implementations with
metric provenance.

Wrong problem definitions:

```text
make 001B pass again
produce schema-complete artifacts
write pass values into JSON
assert all tests pass
verify only hash self-consistency
list baselines or ablations by name without callable implementations
use constants for verdict-bearing result values
```

## Hypothesis

A bounded synthetic candidate that computes action through the public
deserialize path from frozen serialized state plus reconstructable observation
will survive fair callable baseline comparison, real ablation reruns, frozen
contrast checks, scanner positive controls, and behavior-causal replay only if
the reported evidence is computed rather than literal/static.

## Stage0 Freeze Requirements

Before the canonical executable run:

1. Verify parent anchors:
   - `remote-anchor-001h-bd0e715 -> bd0e7158237671c1a5e527b64c8e06ca0ae4e5b3`
   - `remote-anchor-001i-09cff85 -> 09cff85ac377aaa99f913c30e3d31f85264d1344`
   - `remote-anchor-001j-0a3babb -> 0a3babb40bd9b4ada3f01d3752ae43105596fb72`
2. Verify `git rev-parse 1157c8d` resolves to
   `1157c8dec0f0fc1299f7d64454545af161a97cd3`.
3. Verify worktree is clean before Stage0 freeze.
4. Freeze before first canonical run:
   - task card content hash
   - computed-evidence contract hash
   - AGENTS.md hash
   - thresholds
   - metrics
   - baseline implementation registry
   - ablation intervention registry
   - leakage scanner registry
   - replay functions
   - distribution manifest
   - seed families
   - train contexts
   - heldout contexts
   - counterfactual pairs
   - cross-agent state swap pairs
   - duplicate identity-token contrast pairs
   - artifact schema
   - stop conditions
   - rollback plan
   - claim ceiling

If any freeze item is missing, block with:

```text
post_bridge_admission_executable_001c_block_stage0_freeze_gap
```

## Distribution Requirement

Minimum frozen inputs:

```text
minimum_train_contexts = 24
minimum_heldout_bridge_contexts = 48
minimum_counterfactual_state_pairs = 16
minimum_cross_agent_state_swap_pairs = 16
minimum_duplicate_identity_token_contrasts = 16
minimum_independent_seed_families = 4
```

Every frozen train context, heldout context, seed family, counterfactual pair,
cross-agent swap pair, duplicate identity-token contrast, and ablation
definition must be consumed by a callable computation path or removed before
execution. Any unused frozen item blocks with:

```text
post_bridge_admission_executable_001c_failed_unused_frozen_input
```

## Candidate Requirement

Candidate behavior must load serialized state, deserialize it through a public
deserializer function, reconstruct observation from artifact or frozen seed,
compute `candidate_action_id` from deserialized state plus observation, record
deserializer and candidate producer provenance, prove state replacement changes
behavior under frozen contrasts, and prove identity token alone does not explain
behavior.

Forbidden candidate paths:

```text
compute action from in-memory pre_state while serialized_state is decoration
identity-token lookup as carried-state causality
memory-key lookup as carried-state causality
```

## Required Baselines

Every fair baseline must be an independent callable implementation that accepts
comparable legal inputs, emits per-episode outputs before aggregation, records
producer function and code-path hash, records consumed artifacts, and has
failure-path/perturbation tests proving scores can change.

Required fair baselines:

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
random policy
fresh-agent no-carryover
```

If a baseline is name-only, static, or not invoked, block with:

```text
post_bridge_admission_executable_001c_failed_baseline_invocation_missing
post_bridge_admission_executable_001c_failed_static_baseline_detected
```

## Required Ablations

Required ablations:

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

Each ablation must define an intervention function, record target fields,
record pre/post intervention hashes, rerun candidate behavior, recompute score
from outputs, emit per-episode outputs, prove the intervention was applied, and
record code-path provenance.

## Required Contrasts

Use pre-frozen contrast pairs only. Do not perform rejection sampling after
observing desired behavior.

Required contrasts:

```text
same_identity_different_state
different_identity_equivalent_state
same_memory_key_corrupted_memory
equivalent_memory_without_original_token
state_replacement_with_wrong_episode
cross_agent_state_swap
duplicate_identity_token_contrast
```

Each contrast consumes frozen pair IDs, reruns candidate behavior, computes
delta from observed outputs, emits per-pair outcomes, and records code-path
provenance.

## Leakage Scanners

Leakage scanners must inspect candidate inputs, trace rows, serialized state,
provenance rows, artifact paths, fixture names, labels, verifier-only fields,
future observations, future partner responses, later-action labels, post-hoc
metrics, and test-only schema paths. Every scanner must include one positive
control and one clean control.

## Replay Requirement

Behavior-causal replay must load serialized state from artifact, deserialize it
through the same public path used by candidate behavior, reconstruct
observation from artifact or frozen seed, recompute candidate action from
`serialized_state + observation`, compare it to recorded action, and emit
mismatches. Trace and state hash replay are integrity hygiene only.

## Required Artifacts

Create isolated artifacts under:

```text
artifacts/post_bridge_admission_executable_001c/
```

Minimum files:

```text
stage0_freeze_manifest.json
execution_manifest.json
execution_manifest.sha256
run_ledger.jsonl
distribution_manifest.json
serialized_state_provenance.jsonl
metric_provenance.jsonl
baseline_invocation_log.jsonl
ablation_invocation_log.jsonl
leakage_scanner_invocation_log.jsonl
contrast_pair_consumption_log.jsonl
frozen_input_consumption_report.json
trace.jsonl
observation_seed_manifest.json
serialized_state_snapshots.jsonl
candidate_action_replay_report.json
behavior_causal_replay_report.json
trace_hash_replay_report.json
state_hash_replay_report.json
baseline_comparison.json
ablation_report.json
contrast_report.json
leakage_report.json
mutation_check_report.json
protected_artifact_inventory_before.json
protected_artifact_hashes_before.json
protected_artifact_hashes_after.json
tracked_old_artifact_mutation_report.json
computed_evidence_provenance_report.json
result.json
claim_ceiling.txt
failure_manifest.json if failed
```

## Required Source and Tests

Create isolated package:

```text
src/post_bridge_admission_executable_001c/
```

Create focused tests:

```text
tests/test_post_bridge_admission_executable_001c.py
```

Tests must verify artifact schema validity, metric provenance schema validity,
producer functions and code-path hashes, non-literal metric generation,
baseline invocation, ablation invocation and rerun, leakage positive controls,
behavior-causal replay, frozen input consumption, blocker verdicts, and that
tests do not merely assert `verdict == pass`.

## Allowed Verdicts

```text
post_bridge_admission_executable_001c_pass
post_bridge_admission_executable_001c_failed_computed_evidence_provenance
post_bridge_admission_executable_001c_failed_literal_metric_detected
post_bridge_admission_executable_001c_failed_static_baseline_detected
post_bridge_admission_executable_001c_failed_ablation_not_rerun
post_bridge_admission_executable_001c_failed_unconditional_leakage_clean
post_bridge_admission_executable_001c_failed_replay_not_behavior_causal
post_bridge_admission_executable_001c_failed_unused_frozen_input
post_bridge_admission_executable_001c_failed_candidate_not_using_serialized_state
post_bridge_admission_executable_001c_failed_missing_metric_provenance
post_bridge_admission_executable_001c_failed_positive_control_missing
post_bridge_admission_executable_001c_failed_baseline_invocation_missing
post_bridge_admission_executable_001c_failed_ablation_invocation_missing
post_bridge_admission_executable_001c_failed_baseline_equivalence
post_bridge_admission_executable_001c_failed_hidden_lookup_suspicion
post_bridge_admission_executable_001c_failed_identity_token_lookup_equivalence
post_bridge_admission_executable_001c_failed_memory_key_lookup_equivalence
post_bridge_admission_executable_001c_failed_state_table_equivalence
post_bridge_admission_executable_001c_failed_transcript_or_summary_retrieval_equivalence
post_bridge_admission_executable_001c_failed_graph_cache_equivalence
post_bridge_admission_executable_001c_failed_snapshot_reload_equivalence
post_bridge_admission_executable_001c_failed_ablation_insensitive
post_bridge_admission_executable_001c_failed_leakage
post_bridge_admission_executable_001c_failed_artifact_mutation
post_bridge_admission_executable_001c_block_parent_anchor_missing
post_bridge_admission_executable_001c_block_stage0_freeze_gap
post_bridge_admission_executable_001c_block_scope_leak
post_bridge_admission_executable_001c_block_claim_inflation
post_bridge_admission_executable_001c_block_missing_computed_evidence_contract_citation
```

## Acceptance Gate

Pass only if parent anchors are verified, the computed-evidence contract is
cited and enforced, the AGENTS computed-evidence instruction is included in the
freeze, Stage0 freeze happens before the canonical run, all frozen inputs are
consumed or removed before execution, candidate action is computed from
deserialized serialized state plus observation, all verdict-bearing metrics
have provenance, no verdict-bearing metric is literal/static/self-reported,
all baselines are callable and invoked, all ablations rerun under intervention,
required contrasts consume pre-frozen pairs, leakage scanners have positive
controls, behavior-causal replay recomputes candidate action, hash replay is
classified only as hygiene, failure paths exist and are tested, fair baselines
do not match or beat the candidate under frozen thresholds, required ablations
are sensitive, old artifacts are not mutated, and the claim ceiling is
preserved.

## Stop Conditions

Stop and preserve failure artifacts on missing parent anchor, missing computed
contract citation, Stage0 freeze gap, dirty worktree before canonical freeze,
unused frozen input, missing metric provenance, literal/static evidence,
baseline invocation missing, static baseline, ablation not rerun, ablation
invocation missing, unconditional leakage clean, missing scanner positive
control, behavior replay that only checks hashes, candidate not using
serialized state, lookup equivalence, baseline equivalence, ablation
insensitivity, leakage, old artifact mutation, scope leak, or claim inflation.

## Rollback Plan

Preserve failure artifacts, do not patch thresholds after results, do not
weaken baselines, do not delete negative evidence, do not enter EGO mainline,
and make only the minimum patch in a new bounded task or rerun under a new
freeze if a blocker is found.

## What This Cannot Prove

This cannot prove bridge readiness, EGO readiness, companion readiness,
mechanism validity, theory validity, agency, selfhood, consciousness, real
relationship learning, real emotion, subjective experience, stable user
benefit, or correctness of any future EGO runtime.
