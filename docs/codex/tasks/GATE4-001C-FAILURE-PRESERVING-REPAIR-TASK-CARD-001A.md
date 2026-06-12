# GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A

Task ID: GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A

Mode: Task-card drafting only.

Layer: Gate4 repair planning / evidence-contract drafting only.

Claim ceiling: bounded Gate4 001C failure-preserving repair task-card drafting only.

## Authorization Boundary

This task card does not execute Gate4 001C, Gate5, admission, runtime, bridge,
or mechanism validation. It does not restore, cherry-pick, merge, push, anchor,
import, copy, or use provisional Gate4 001C commit
`d7b5b7a33cc68cbe7e3ca0960b99e0082e1ac728`.

This task card authorizes only future task-card review. It does not authorize a
future Gate4 001C execution by itself. A separate bounded execution task must
name exact allowed files, tests, artifacts, and stop conditions before any
repair implementation begins.

Required authorization fields for this task card and its artifacts:

- `gate4_001c_execution_authorized`: false
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false
- `ego_mainline_authorized`: false

## Starting State

Starting HEAD: `2f01c49271bb76c7ddf5c8c5a449864b5d23c718`

Parent evidence anchors:

- `remote-anchor-evidence-harness-contract-enforcement-smoke-001a-5b4cdbe`
- `remote-anchor-evidence-harness-contract-enforcement-smoke-001b-69aa22d`
- `remote-anchor-evidence-harness-critical-risk-target-application-001a-241d69c`
- `remote-anchor-claude-audit-evidence-harness-critical-risk-application-001a-2f01c49`

## Problem Definition

Draft the minimum failure-preserving Gate4 001C repair contract that would let a
future execution produce computed, falsifiable, replayable, baseline-controlled
Gate4 evidence without reusing false-pass evidence and without restoring
provisional 001C.

The goal is not to make Gate4 pass. The goal is to define the executable repair
contract under which Gate4 001B remains preserved as rejected negative evidence
and a future Gate4 001C execution may fail cleanly if the repaired evidence path
does not survive baselines, ablations, leakage scans, replay recomputation, or
computed-provenance checks.

## Current Stage

Task-card drafting only. No Gate4 execution is authorized here.

## Anti-Sycophancy Audit

Strongest baseline explanation: the prior Gate4 line may have looked usable
because artifact shape, score fields, baseline labels, ablation labels, or replay
hashes resembled evidence without proving callable computation, independent
baseline comparison, real intervention, or behavior recomputation.

Strongest reason this task may be invalid: if the inherited Gate4 sources do not
contain enough non-contaminated contract material to define a new execution
boundary, then drafting a repair task card would create a false sense of forward
motion and should block instead.

What would falsify this framing: discovery that the proposed future execution
requires any pass evidence from Gate4 001B, any restored material from
provisional 001C, any non-fail-able clean report, or any downstream
authorization flag set to true.

What evidence would still be insufficient: a task card, parsed JSON artifacts,
green tests, or a remote tag would still not prove Gate4 validity, mechanism
validity, theory validity, architecture correctness, runtime readiness, bridge
readiness, admission readiness, or EGO-mainline readiness.

This task tests governance contract completeness only. It does not test a
mechanism and does not produce behavioral resemblance evidence.

## Inherited Negative Evidence Rules

- Gate4 001B is sealed but independently rejected.
- Gate4 001B may be cited only as rejected boundary, negative evidence input, or
  positive-control false-pass case.
- Gate4 001B must not be cited as pass evidence, Gate validity evidence,
  mechanism validity evidence, architecture correctness evidence, or downstream
  admission evidence.
- The current evidence harness is a conservative blocker, not a positive
  admission discriminator.
- Critical-risk targets 11-12 must not be cited as confirmed false-pass
  contamination. Their inherited status is `blocked_pending_audit` due to
  test-surface-only signal / label-inflation caveat.
- Non-fail-able clean fields are prohibited in the future 001C execution
  contract.

## Hypothesis

A valid Gate4 001C repair must preserve Gate4 001B as negative evidence while
creating a new executable evidence path with computed provenance, callable
baselines, real ablations, fail-able leakage scans, and replay recomputation.

## Future Execution Baseline Requirements

The future execution task must require independent callable baselines, including
at minimum:

- identity / partner-id lookup baseline
- preference-table baseline
- order-1 history baseline
- order-2 history baseline
- retrieval / imitation baseline
- frozen-policy baseline
- oracle-label or label-leakage control where applicable

Each baseline must have an implementation path, invocation record, input
artifact list, output artifact, aggregation rule, and code path hash. A baseline
label in a report is not sufficient.

## Future Execution Ablation Requirements

The future execution task must rerun episodes under real interventions. It must
not merely change labels, verdict fields, or summary text.

Required ablations:

- remove social latent state
- remove partner-specific history
- shuffle partner/context mapping
- freeze update path
- remove prediction-error/update signal
- remove memory write/read path if used

Each ablation must record intervention implementation path, affected episodes,
run id, before/after metric comparison, and whether behavior changed under the
intervention.

## Future Execution Replay Requirement

The future Gate4 001C execution must recompute candidate behavior from
`serialized_state + observation`.

Forbidden replay substitutes:

- hash-only replay
- action-only replay
- verdict-only replay
- trace-only replay
- report-text replay

Replay must record the serialized state artifact, observation artifact,
recompute function, recomputed action/behavior, original action/behavior,
comparison rule, mismatch handling, and code path hash.

## Future Execution Leakage Requirement

The future Gate4 001C execution must include real scanners with positive
controls. At minimum it must detect:

- partner-id leakage
- target-label leakage
- oracle outcome leakage
- direct answer table leakage
- fixture-name/task-id leakage
- train/heldout contamination
- counterfactual-pair leakage

Each scanner must include a positive-control artifact that is expected to fail
and a clean-control artifact that may pass only through the same callable scanner
path.

## Computed-Evidence Provenance Gate

Every score, classification, comparison, and verdict in the future execution
must record:

- producer_function
- input artifacts
- run_id
- seed/context/episode IDs
- aggregation rule
- source/code path hash
- baseline implementation path
- ablation intervention path
- replay recomputation path
- leakage scanner path and positive-control result

The future execution contract explicitly forbids:

- constants as metrics
- static dictionaries as verdict sources
- unconditional clean reports
- tests that only assert final pass
- non-fail-able scanner outputs
- unused frozen seeds
- unused train/heldout contexts
- unused counterfactual pairs
- claiming pass from artifact shape alone

## Required Future Test Requirements

The future execution task must include tests that fail if:

- Gate4 001B is used as pass evidence
- provisional Gate4 001C is read, restored, copied, or used
- a metric is produced by a literal, constant, or static verdict dictionary
- a baseline is declared but not invoked
- an ablation changes labels without rerunning episodes
- replay does not recompute behavior from serialized state plus observation
- leakage positive controls are not detected
- train/heldout or counterfactual pairs are declared but unused
- any downstream authorization field becomes true

Tests that only assert final pass are forbidden.

## Required Output Paths For This Drafting Task

- `docs/codex/tasks/GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A.md`
- `artifacts/gate4_001c_failure_preserving_repair_task_card_001a/`

## Required Artifacts For This Drafting Task

- `task_card_result.json`
- `inherited_negative_evidence_matrix.json`
- `parent_anchor_matrix.json`
- `prohibited_evidence_use_matrix.json`
- `computed_evidence_contract.json`
- `baseline_requirement_matrix.json`
- `ablation_requirement_matrix.json`
- `replay_requirement_matrix.json`
- `leakage_requirement_matrix.json`
- `test_requirement_matrix.json`
- `downstream_authorization_matrix.json`
- `claim_ceiling.txt`
- `execution_manifest.json`
- `json_parse_verification.json`

## Acceptance Gate For This Drafting Task

Pass only if:

- starting HEAD equals `2f01c49271bb76c7ddf5c8c5a449864b5d23c718`
- worktree is clean before generation
- only the task-card doc and task-card artifacts are added
- no old Gate artifacts/tests/verdicts are modified
- 001A/001B enforcer/audit artifacts are not modified
- Claude audit report is not modified
- provisional Gate4 001C is not used
- Gate4 001B is explicitly marked rejected/non-admissible
- targets 11-12 label caveat is inherited accurately
- future 001C execution is not authorized by this task
- Gate5/admission/runtime/bridge remain unauthorized
- no Gate validity, mechanism validity, theory validity, architecture
  correctness, or EGO-mainline readiness is claimed
- all JSON artifacts parse

Allowed verdicts:

- `gate4_001c_failure_preserving_repair_task_card_created`
- `blocked_inherited_evidence_inconsistency`
- `blocked_start_state_mismatch`
- `blocked_provisional_001c_contamination_risk`

## Stop Conditions

Stop and report blocked if:

- starting HEAD mismatch
- worktree dirty before generation
- task requires restoring or reading provisional Gate4 001C
- task requires modifying old Gate artifacts/tests/verdicts
- task attempts to convert Gate4 001B into pass evidence
- task authorizes Gate4 001C execution
- task authorizes Gate5/admission/runtime/bridge
- task cannot preserve all inherited caveats and negative evidence
- any required matrix would be filled by static boilerplate rather than concrete
  referenced contract entries

## Rollback Plan

If acceptance fails, revert only newly generated task-card files and artifacts:

- `docs/codex/tasks/GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A.md`
- `artifacts/gate4_001c_failure_preserving_repair_task_card_001a/`

Do not modify or repair existing historical evidence.

## What This Does Not Prove

This task card does not prove Gate4 validity, Gate5 readiness, admission
readiness, runtime readiness, bridge readiness, mechanism validity, theory
validity, architecture correctness, EGO-mainline readiness, agency, selfhood,
consciousness, real emotion, relationship learning, or stable autonomy.
