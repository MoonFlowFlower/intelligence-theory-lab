# Codex Goal Task — PROCESS-INTERVENTION-PREFLIGHT-001A Drafting

You are working in the `intelligence-theory-lab` repo.

This is an overnight bounded Goal task.
Do not run open-ended exploration.
Do not continue beyond the authorized scope.
If the task finishes early, perform only self-audit, consistency checks, and test cleanup. Do not start implementation.

## Goal

Prepare `PROCESS-INTERVENTION-PREFLIGHT-001A` as a bounded executable-preflight task-card draft.

This task must convert the accepted `NEW-PROBLEM-PREFLIGHT-001A` proxy contract into a future executable preflight design.

It must not implement the mechanism.

## Current Canonical State

Read the following as immutable parent state:

```text
Gate0 = PREDICTIVE-ACTION-LEARNING-CONTRACT-001C
Gate0 claim ceiling = bounded isolated Gate 0 predictive-action mechanism evidence only

Gate1 replay/consolidation lineage = closed
same-agent bridge = blocked

REPRESENTATIONAL-GAP-PREFLIGHT-001A = audit superseded
REPRESENTATIONAL-GAP-PREFLIGHT-001B = failed because fair full-history cheap controls solved target

THEORY-RESET-NEW-PROBLEM-DEFINITION-001A = bounded pass
primary surviving framing = F2 process/intervention gap
supporting constraints = F3 online adaptation, F4 causal model update

NEW-PROBLEM-PREFLIGHT-001A = bounded pass
primary proxy = P1 Intervention-Sensitive State Update Proxy
supporting constraints = P2 online adaptation, P3 causal model update
P4 = symmetric resource accounting only
P5 = non-affective regulatory scalar boundary only
claim ceiling = bounded process/intervention proxy-contract evidence only
```

## Strict Authorization Boundary

Authorized:

```text
docs/PROCESS-INTERVENTION-PREFLIGHT-001A.md
docs/process_intervention_preflight_001a/
artifacts/process_intervention_preflight_001a/
tests/test_process_intervention_preflight_001a_contract.py
```

Forbidden:

```text
src/ implementation
mechanism implementation
training scripts
agent runtime changes
EGO mainline changes
Gate1 reopen
same-agent bridge
MODEL-CLASS-RESET
LLM/RAG/companion/emotion/relationship/user-model modules
agency/consciousness/functional-subject/companion/AGI claims
```

If any forbidden area becomes necessary, stop and return a scope-failure verdict.

## Correct Problem

Draft a future executable preflight card answering:

```text
Can a bounded process/intervention mechanism show intervention-sensitive internal update and later behavior change that cannot be reproduced by fair full-history and online cheap controls under the same access contract?
```

This card must test whether fair cheap controls can reproduce all three:

```text
1. intervention response
2. internal update trace
3. later behavior change
```

If any fair cheap control can reproduce all three, the future executable preflight must fail.

## Required Control Families

Carry forward mandatory fair controls:

```text
full-history count/statistic
online count/statistic
FSM / automaton
online FSM
graph/cache
online graph/cache
kNN / episodic retrieval
online kNN
summary/statistic
causal table
behavior-only replay
trace-only replay
graph/cache trace generator
random representation
shuffled-label / shuffled-outcome
oracle/leakage probes
```

Do not weaken these controls.

## Required Intervention Families

The future preflight card must define at least:

```text
state deletion
memory deletion
representation freezing
prediction-error injection
counterfactual action substitution
observation perturbation
history-preserving causal perturbation
online distribution shift
```

For each intervention, define:

```text
what changes
what must not change
expected internal update effect
expected later behavior effect
cheap-control collapse risk
failure condition
```

## Required Failure Gates

The future preflight must fail if:

```text
trace does not causally affect later behavior
intervention does not change update path
deletion/freezing has no later behavior effect
prediction error is only logged but not used
counterfactual action does not alter state update
graph/cache trace generator matches trace + behavior
trace-only replay matches trace + behavior
behavior-only replay matches intervention response
online FSM or online summary matches
online graph/cache or online kNN matches
causal table matches
random representation preserves performance
shuffled outcome preserves performance
resource limits starve controls
value-state language leaks into emotion/subjectivity
```

## Required Documents

Create:

```text
docs/PROCESS-INTERVENTION-PREFLIGHT-001A.md
docs/process_intervention_preflight_001a/problem_contract.md
docs/process_intervention_preflight_001a/intervention_contract.md
docs/process_intervention_preflight_001a/trace_replay_contract.md
docs/process_intervention_preflight_001a/control_adversary_contract.md
docs/process_intervention_preflight_001a/resource_contract.md
docs/process_intervention_preflight_001a/collapse_audit.md
docs/process_intervention_preflight_001a/claim_ceiling.md
artifacts/process_intervention_preflight_001a/verdict_manifest.json
artifacts/process_intervention_preflight_001a/contract_summary.json
tests/test_process_intervention_preflight_001a_contract.py
```

## Required Main Sections

The main document must include:

```text
current_layer
parent_lineage_summary
wrong_proxy_to_avoid
correct_problem_definition
future_environment_requirements
intervention_contract
online_update_contract
trace_replay_contract
state_delta_metric_contract
future_behavior_effect_metric
cheap_control_adversaries
oracle_leakage_probes
resource_contract
ablation_contract
anti_hardcoding_audit
trace_theater_audit
acceptance_gate
failure_verdicts
claim_ceiling
stop_conditions
rollback_plan
next_allowed_task
```

## Acceptance Gate

Return:

```text
process_intervention_preflight_001a_task_card_bounded_pass
```

only if all are true:

```text
no_mechanism_implementation = true
no_training = true
problem_is_not_output_level = true
intervention_response_required = true
internal_update_trace_required = true
later_behavior_change_required = true
trace_theater_failure_gate_defined = true
fair_online_controls_required = true
graph_cache_trace_generator_required = true
trace_only_replay_required = true
behavior_only_replay_required = true
random_representation_control_required = true
shuffled_outcome_control_required = true
resource_contract_symmetric = true
value_state_boundary_non_affective = true
claim_ceiling_enforced = true
```

## Allowed Verdicts

```text
process_intervention_preflight_001a_task_card_bounded_pass
process_intervention_preflight_001a_failed_output_level_proxy
process_intervention_preflight_001a_failed_trace_theater
process_intervention_preflight_001a_failed_no_future_behavior_effect
process_intervention_preflight_001a_failed_control_banning
process_intervention_preflight_001a_failed_resource_asymmetry
process_intervention_preflight_001a_failed_value_state_scope_leak
process_intervention_preflight_001a_failed_implementation_leak
process_intervention_preflight_001a_failed_gate1_reopen_leak
process_intervention_preflight_001a_failed_same_agent_bridge_leak
process_intervention_preflight_001a_failed_model_class_reset_leak
process_intervention_preflight_001a_failed_EGO_scope_leak
process_intervention_preflight_001a_inconclusive_no_clean_executable_preflight
```

## Claim Ceiling

Maximum allowed claim:

```text
bounded process/intervention executable-preflight task-card evidence only
```

This does not prove:

```text
mechanism success
online adaptation success
causal model success
model-class reset readiness
Gate1 readiness
same-agent bridge readiness
EGO readiness
agency
consciousness
functional subjectivity
emotion
relationship learning
companion readiness
AGI
```

## Verification

Run:

```bash
python -m pytest tests/test_process_intervention_preflight_001a_contract.py -q
```

Also run any lightweight JSON/Markdown consistency checks needed for the artifacts.

## Final Report Required

Report:

```text
files_created_or_changed
parent_inputs_read
future_problem_definition
intervention_contract_summary
trace_replay_contract_summary
control_adversary_summary
resource_contract_summary
collapse_audit_summary
anti_hardcoding_audit_summary
stop_conditions_encountered
final_verdict
strongest_allowed_claim_ceiling
next_allowed_task_if_any
commands_run
test_results
```

Do not recommend implementation unless this task passes and the next task is separately authorized.
