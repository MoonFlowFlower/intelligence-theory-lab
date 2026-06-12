# SAME-AGENT-BRIDGE-EXECUTABLE-PREFLIGHT-001B

Task ID: SAME-AGENT-BRIDGE-EXECUTABLE-PREFLIGHT-001B

Layer: bounded same-agent bridge executable preflight only.

## Purpose

Implement and execute an isolated bounded same-agent bridge executable
preflight. The test checks whether one canonical serialized shared state crosses
a bridge boundary, preserves traceable identity, memory, viability, and
social-latent continuity, updates under post-bridge observations, and affects
later behavior under heldout bridge conditions while resisting required
baselines, ablations, leakage, replay, and mutation checks.

## Authorization Boundary

Allowed isolated write paths:

```text
docs/codex/tasks/SAME-AGENT-BRIDGE-EXECUTABLE-PREFLIGHT-001B.md
src/same_agent_bridge_001b/
tests/test_same_agent_bridge_001b_executable_preflight.py
artifacts/same_agent_bridge_001b/
```

Not authorized:

```text
bridge runtime
EGO mainline
companion behavior
LLM/RAG integration
user modeling
relationship learning
emotion systems
personalization/product demo behavior
romance or attachment behavior
persistent human-user profile
long-term human-user memory modules
```

## Parent Anchors

```text
EXEC-001 / graph_cache_collapse = d7ffc393
RESIDUE-001A / shuffled-same-loss + order-2 window model result = 495300cb
GATE1-REPLAY-CONSOLIDATION-LINEAGE-CLOSEOUT-001 = 307da77
Gate1 replay/consolidation executable preflight = 6b362e0
Gate2 controllability/self-boundary executable preflight = 7046d6f
Gate3 viability/functional-affect executable preflight = 3f36ca0
Gate0/Gate1/Gate2/Gate3 canonical micro-agent integration executable preflight = 693c215
Gate4 social representational-gap executable preflight = a083db2
Gate4 social-latent inference executable preflight = a57fa2e
SAME-AGENT-BRIDGE-READINESS-AUDIT-001A = b1cafc2
SAME-AGENT-BRIDGE-READINESS-AUDIT-001A-AMENDMENT-001 = 977fab2
SAME-AGENT-BRIDGE-TASK-CARD-001A = 5c67f94
```

## Stage-0 Freeze Requirement

Before any bridge run, freeze:

```text
task_card_hash
bridge_environment_family
bridge_boundary_definition
canonical_agent_state_schema
serialization_format
allowed_persistence_manifest
forbidden_persistence_manifest
reset_boundary_definition
memory_carryover_boundary_definition
identity_continuity_metric
state_lineage_hash_contract
replay_contract
leakage_controls
baseline implementation signatures
ablation implementation signatures
metric formulas
equivalence thresholds
heldout split
seed schedule
artifact schema
rollback policy
claim ceiling
external anchor
```

## Canonical Shared State

The run must use one canonical serialized shared state containing:

```text
belief_state
prediction_error_state
replay_memory
consolidation_state
controllability_model
self_boundary_state
viability_state
viability_model
action_priority_state
recovery_policy_state
resource_budget_state
social_latent_state
partner_model_state
social_prediction_error_state
interaction_policy_state
bridge_state_metadata
identity_continuity_state
memory_carryover_state
reset_boundary_state
```

Forbidden:

```text
hidden profile tables
transcript indexes
summary indexes
external memory databases
identity-token lookup tables
user profiles
relationship caches
persona scripts
prompt-only identity statements
second hidden policy layers
```

## Required Baselines

```text
fresh-agent baseline with no carryover
snapshot-reload baseline without active state update
transcript retrieval
summary retrieval
state-table lookup
identity-token lookup
memory-key lookup
static profile table
partner/profile table
graph_lookup
transition_table
successor_map
count_table
fsm_planner
episodic_traversal
bounded-order window model order-1
bounded-order window model order-2
shuffled-history same-loss control
behavior-only imitation
stitched-output baseline with no single shared state
frozen-state bridge baseline
oracle bridge-state control as upper-bound/leakage only
trace-only replay as hygiene only
random policy
```

If a fair baseline matches or beats the candidate, the task must fail or block.
Oracle bridge-state and trace-only replay controls are not fair pass evidence.

## Required Ablations

```text
remove bridge state
reset all memory at bridge
freeze post-bridge learning
corrupt serialized state
replace serialized state with wrong episode state
remove replay/consolidation carryover
remove self-boundary carryover
remove viability carryover
remove social-latent carryover
remove identity_continuity_state
invert bridge mapping
perturb post-bridge environment
delayed post-bridge effect
partial observability
heldout bridge-context compositions
counterfactual bridge contrast
replace history before bridge
learning freeze
disable action
```

## Required Artifacts

Write artifacts only under:

```text
artifacts/same_agent_bridge_001b/
```

Required artifact set:

```text
stage0_freeze_manifest.json
execution_manifest.json
execution_manifest.sha256
run_ledger.jsonl
bridge_environment_manifest.json
canonical_agent_state_schema.json
allowed_persistence_manifest.json
forbidden_persistence_manifest.json
trace.jsonl
serialized_state_trace.jsonl
shared_state_trace.jsonl
linkage_report.json
baseline_comparison.json
ablation_report.json
leakage_report.json
replay_integrity_report.json
mutation_check_report.json
protected_artifact_inventory_before.json
protected_artifact_hashes_before.json
protected_artifact_hashes_after.json
tracked_old_artifact_mutation_report.json
result.json
claim_ceiling.txt
failure_manifest.json if failed
```

## Acceptance Gate

Pass only if Stage-0 freeze happens before any bridge run; one canonical
serialized shared state crosses the bridge boundary; identity continuity and
memory carryover are operationally defined and traceable; post-bridge behavior
depends on carried state under heldout conditions; fair baselines do not match
or beat the candidate; required ablations are sensitive; linkage keys are
deterministic, label-free, and collision-free; leakage report is clean; trace
replay and state replay pass; protected old artifacts do not mutate; and no
forbidden claim is made.

## Bounded Deep Audit

Strongest baseline explanation:
lookup, retrieval, window, graph/cache, state-table, identity-token, summary,
frozen-state, stitched-output, or behavior-imitation controls can mimic bridge
continuity.

Strongest reason this task may be invalid:
serialized state or identity continuity can become a hidden lookup key, or a
second hidden policy layer can select post-bridge actions.

Falsification condition:
fair baseline equivalence, insensitive required ablations, leakage, replay/state
replay failure, missing carried-state effect, or old-artifact mutation.

Evidence still insufficient:
trace-only replay, hash-chain integrity, task-card existence, local bounded
passes, natural-language continuity, and remote anchors are insufficient for
bridge readiness or mechanism validity.

Mechanism or behavioral resemblance:
this tests only bounded executable-preflight behavior under a synthetic
state-transfer contract.

## Verdicts

Allowed pass verdict:

```text
same_agent_bridge_001b_bounded_preflight_pass
```

Allowed failure classes include baseline equivalence, ablation insensitivity,
leakage, replay failure, hermeticity failure, scope leak, and claim inflation.

## Claim Ceiling

```text
bounded same-agent bridge executable preflight evidence only
```

This does not prove bridge readiness, bridge mechanism validity, EGO readiness,
companion readiness, mechanism validity, theory validity, agency, selfhood,
consciousness, real relationship learning, real emotion, subjective experience,
or stable user benefit.
