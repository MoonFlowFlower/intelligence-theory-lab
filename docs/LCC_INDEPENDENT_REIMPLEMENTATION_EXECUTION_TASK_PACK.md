# LCC Independent Reimplementation Execution Task Pack

## Current State

The public reimplementation contract package has verdict:

```text
independent_reimplementation_contract_ready
```

This is **not** LCC theory support and does **not** authorize a general LCC agent.

This task pack authorizes only a clean-room independent reimplementation execution of the public contract.

## Human Review Decision

```text
decision = authorize_independent_reimplementation_execution_contract_only
```

This authorization is narrow.

It does **not** authorize:

```text
Cycle 011
general LCC agent
autonomous theory search
EGO migration
LCC theory support
bottom intelligence principle claim
AGI / consciousness / self-awareness / life claims
reuse of current candidate/control/scorer/runner internals
```

---

## Required Clean-Room Rule

The implementer may use only the public package:

```text
docs/LCC_PUBLIC_THEORY_CARD.md
docs/LCC_PUBLIC_IO_SCHEMA.md
docs/LCC_PUBLIC_REDTEAM_GATES.md
docs/LCC_REPLICATION_CLAIM_BOUNDARY.md
docs/LCC_INDEPENDENT_REIMPLEMENTATION_CONTRACT.md
artifacts/independent_reimplementation/contract_manifest.json
```

The implementer must not inspect, import, copy, adapt, or tune against:

```text
current theory_lab implementation
current candidate/control code
cycle-specific runner internals
current scorer internals
current test internals
expected-output tables
hidden transition tables
oracle plan tables
existing artifacts beyond the public package
```

Strong recommendation:

```text
Run in a fresh repo or fresh Codex session containing only the public contract package.
```

If forced to run inside the existing repository, the implementation must be placed under a clearly separated path and must pass scans proving it does not import from current implementation modules.

---

## Maximum Possible Claim After Execution

Even if all gates pass:

```text
independent_reimplementation_bounded_pass
```

This still does not prove:

```text
LCC theory support
bottom intelligence principle
AGI
consciousness
subjective experience
self-awareness
life
EGO readiness
robust universal support
```

It only says:

```text
The core LCC public contract survived one clean-room independent bounded replication.
```

---

## Global Stop Rules

Stop immediately and record failure if:

```text
semantic action labels are used by candidate
semantic goal labels are used by candidate
object/entity names are used by candidate
scenario/task/cycle/contract IDs are used by candidate
hidden latent or future state is used by candidate
oracle transition table or oracle plan table is used by candidate
evaluator metric is used as candidate feature
expected output table is used
baseline output leaks into candidate
behavior depends on action labels when effects stay fixed
behavior fails to change when effects change but labels stay fixed
passive correlation is treated as own-intervention effect
diagnostic intervention is not selected under useful uncertainty
closed-loop replanning fails after unexpected observations
behavior-only replay cannot reconstruct decision evidence
strong non-oracle baseline matches candidate within declared equivalence band
candidate/control code changes after blind holdout generation
```

A clean failure is more valuable than a fake pass.

---

# IR-000: Clean-Room Workspace and Manifest

## Goal

Create a clean-room implementation workspace that contains only allowed public materials.

## Required Artifacts

```text
artifacts/independent_execution/IR-000/STATUS.md
artifacts/independent_execution/IR-000/clean_room_manifest.json
artifacts/independent_execution/IR-000/allowed_materials_report.md
```

## Required Checks

Record:

```text
public docs used
files explicitly not used
hashes of public docs
implementation root
module import roots
```

## Stop Conditions

```text
lineage_dependency_detected
current_internal_code_import_detected
expected_output_table_detected
unauthorized_artifact_access_detected
```

## Verdicts

```text
clean_room_ready
clean_room_failed
```

---

# IR-001: Public I/O Schema Implementation

## Goal

Implement only the public I/O schema and trace record structures.

## Required Implementation

```text
Observation
ActionHandle
InterventionHistoryItem
PublicOutcome
CandidateDecision
TraceRecord
BehaviorOnlyReplayInput
```

Use anonymous actions only.

## Required Artifacts

```text
artifacts/independent_execution/IR-001/STATUS.md
artifacts/independent_execution/IR-001/io_schema_report.md
```

## Stop Conditions

```text
semantic_action_label_field_added
hidden_state_field_added
future_oracle_field_added
metric_feature_field_added
scenario_id_field_added
```

---

# IR-002: Minimal Candidate Mechanism

## Goal

Implement a minimal independent LCC candidate from public theory only.

## Candidate Requirement

The candidate must:

```text
learn intervention-conditioned action effects from own-action outcomes
select anonymous actions by predicted effects
remain label-invariant under action ID renaming
change behavior under effect perturbation
produce prediction_before_action
produce decision evidence using only allowed public fields
```

## Forbidden

```text
explicit effect table as candidate mechanism
semantic action names
oracle transition tables
hard-coded expected action for test cases
metric-based scoring
copying current implementation logic
```

Diagnostic oracles may exist only as baselines marked diagnostic-only.

## Required Artifacts

```text
artifacts/independent_execution/IR-002/STATUS.md
artifacts/independent_execution/IR-002/candidate_mechanism_report.md
```

## Stop Conditions

```text
candidate_requires_explicit_effect_table
action_label_shortcut_detected
metric_feature_leak
hidden_oracle_leak
```

---

# IR-003: Gate 1 — Label / Effect Decoupling

## Required Split

```text
same effects + changed labels -> behavior invariant
same labels + changed effects -> behavior changes
```

## Required Baselines

```text
ActionLabelHeuristic
StaticActionTable
OracleEffectUpperBound diagnostic only
```

## Required Artifacts

```text
artifacts/independent_execution/IR-003/label_effect_report.md
artifacts/independent_execution/IR-003/label_effect_results.json
artifacts/independent_execution/IR-003/traces.jsonl
```

## Stop Conditions

```text
label_shortcut_detected
intervention_effect_not_learned
action_label_heuristic_equivalent
```

---

# IR-004: Gate 2 — Passive Observation Versus Own Intervention

## Required Split

```text
passively correlated transition does not imply do(action) causation
weak passive correlation can still be true do(action) effect
```

## Required Baselines

```text
PassiveCorrelationPolicy
NearestNeighborTracePolicy
OracleInterventionUpperBound diagnostic only
```

## Required Artifacts

```text
artifacts/independent_execution/IR-004/passive_vs_intervention_report.md
artifacts/independent_execution/IR-004/passive_vs_intervention_results.json
```

## Stop Conditions

```text
passive_correlation_treated_as_intervention
nearest_neighbor_equivalent
behavior_only_replay_failed
```

---

# IR-005: Gate 3 — Active Diagnostic Intervention

## Required Split

```text
ambiguous state -> diagnostic intervention selected when useful
certain state -> diagnostic intervention not overused
identified effect reused for later control
```

## Required Baselines

```text
AlwaysDiagnosePolicy
NeverDiagnosePolicy
GreedyImmediatePolicy
OracleDiagnosticUpperBound diagnostic only
```

## Required Artifacts

```text
artifacts/independent_execution/IR-005/diagnostic_intervention_report.md
artifacts/independent_execution/IR-005/diagnostic_intervention_results.json
```

## Stop Conditions

```text
diagnostic_intervention_failed
always_diagnose_equivalent
never_diagnose_equivalent
greedy_immediate_equivalent
```

---

# IR-006: Gate 4 — Sequential Closed-Loop Replanning

## Required Split

```text
one-step greedy fails on multi-step or trap tasks
open-loop cached plan fails after unexpected observation
closed-loop effect-conditioned replanning succeeds
```

## Required Baselines

```text
OneStepGreedyPolicy
OpenLoopSequencePolicy
SequenceLookupPolicy
OracleReplannerUpperBound diagnostic only
```

## Required Artifacts

```text
artifacts/independent_execution/IR-006/closed_loop_replanning_report.md
artifacts/independent_execution/IR-006/closed_loop_replanning_results.json
```

## Stop Conditions

```text
closed_loop_replanning_failed
one_step_greedy_equivalent
open_loop_equivalent
sequence_lookup_equivalent
```

---

# IR-007: Gate 5 — Blind Holdout After Candidate Freeze

## Goal

Prevent tuning to the holdout.

## Required Process

```text
freeze candidate/control hash
generate blind holdout after freeze
run once on predeclared seeds
no candidate/control code changes after holdout generation
independent trace-only scorer recomputes metrics
negative controls included
```

## Required Baselines

```text
NearestNeighborTracePolicy
ContextualHeuristic
ModelBasedMPCBaseline
EmpowermentProxyBaseline
OracleDiagnosticUpperBound diagnostic only
```

## Required Artifacts

```text
artifacts/independent_execution/IR-007/freeze_manifest.json
artifacts/independent_execution/IR-007/blind_holdout_manifest.json
artifacts/independent_execution/IR-007/blind_holdout_report.md
artifacts/independent_execution/IR-007/blind_holdout_results.json
artifacts/independent_execution/IR-007/independent_metrics.json
artifacts/independent_execution/IR-007/negative_control_report.md
```

## Stop Conditions

```text
freeze_integrity_violation
hidden_or_metric_leak_detected
behavior_only_replay_failed
strong_baseline_equivalent
negative_control_failed
```

---

# IR-008: Required Baseline Tournament Summary

## Goal

Summarize all baseline comparisons.

## Required Baselines

At minimum:

```text
ActionLabelHeuristic
NearestNeighborTracePolicy
ContextualHeuristic
ModelBasedMPCBaseline
EmpowermentProxyBaseline
OracleDiagnosticUpperBound diagnostic only
```

## Required Artifacts

```text
artifacts/independent_execution/IR-008/baseline_tournament_report.md
artifacts/independent_execution/IR-008/baseline_tournament_results.json
```

## Stop Conditions

```text
strong_baseline_equivalent
model_based_mpc_dominates
empowerment_proxy_dominates
```

---

# IR-009: Behavior-Only Replay and Provenance Audit

## Goal

Verify decision evidence is reconstructed from allowed public trace fields only.

## Required Tests

```text
behavior-only trace replay
identity mutation
forged self-report injection
scenario/task/cycle/contract ID mutation
semantic label leak scan
hidden-state leak scan
metric feature leak scan
oracle transition/plan table scan
expected-output table scan
baseline output leakage scan
```

## Required Artifacts

```text
artifacts/independent_execution/IR-009/behavior_only_replay.json
artifacts/independent_execution/IR-009/provenance_audit_report.md
artifacts/independent_execution/IR-009/identity_mutation_report.md
```

## Stop Conditions

```text
behavior_only_replay_failed
agent_identity_leak
self_report_leak
scenario_shortcut_leak
hidden_or_metric_leak_detected
action_label_leak
expected_output_table_leak
baseline_output_leak
```

---

# IR-010: Independent Reimplementation Decision

## Goal

Close the independent execution. Do not continue automatically.

## Required Artifacts

```text
artifacts/independent_execution/IR-010/INDEPENDENT_REIMPLEMENTATION_DECISION.md
artifacts/independent_execution/IR-010/independent_reimplementation_decision.json
```

## Allowed Verdicts

```text
independent_reimplementation_bounded_pass
label_shortcut_detected
intervention_effect_not_learned
diagnostic_intervention_failed
closed_loop_replanning_failed
behavior_only_replay_failed
hidden_or_metric_leak_detected
strong_baseline_equivalent
freeze_integrity_violation
inconclusive_contract_needs_revision
```

## If Passes

Maximum claim:

```text
LCC_v0 survived one clean-room independent bounded replication of the core public contract.
```

Do not claim:

```text
LCC theory support
bottom intelligence principle
AGI
consciousness
subjective experience
self-awareness
life
EGO readiness
robust universal support
```

## If Fails

Do not patch the current implementation to recover.

Correct consequence:

```text
downgrade LCC_v0 to bounded single-lineage evidence
record failure as successor constraint
return to human review
```
