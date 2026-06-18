# PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C-R1

Status: recorded required-revision repair to `PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C`.

Auto-Remote-Anchor: forbidden.

## Verdict

`design_constraints_002c_r1_recorded`

This R1 record applies the three Claude-required revisions to 002C before any
possible later consideration of `BATCH-ENV-HEADROOM-SCOUT-003A`.

002C-R1 remains a Phase-0 environment design-constraint repair. It does not
generate new sketches, run a scout, run a full harness, implement candidates,
start route tournament work, or wire runtime/mainline/admission/bridge paths.

## Current Layer

engineering-governance / Phase-0 environment design-constraint repair.

## Mainline Integration Status

none.

## Enabled Status

no runtime/mainline/admission/bridge path enabled.

## Real Trigger Evidence

R1 was triggered by the repo-local Claude independent hostile audit artifact:

- `artifacts/CLAUDE-INDEPENDENT-PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C-HOSTILE-AUDIT-001A/audit_result.json`

The audit verdict was:

`accept_design_constraint_record_with_required_revisions_before_003a_authorization`

The audit accepted 002C only as a negative-lineage design-constraint record and
explicitly reported that 002C did not authorize 003A.

## Source Readback

The R1 repair read the requested 002C sources:

- `docs/research/PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C.md`
- `artifacts/phase0_environment_design_constraints_002c/failure_taxonomy.json`
- `artifacts/phase0_environment_design_constraints_002c/design_constraints.json`
- `artifacts/phase0_environment_design_constraints_002c/forbidden_surface_patterns.json`
- `artifacts/phase0_environment_design_constraints_002c/required_positive_properties.json`
- `artifacts/phase0_environment_design_constraints_002c/next_batch_generation_brief.json`
- `artifacts/CLAUDE-INDEPENDENT-PHASE0-ENVIRONMENT-DESIGN-CONSTRAINTS-002C-HOSTILE-AUDIT-001A/audit_result.json`

The audit artifact path was available, so no operator-text fallback was needed.

## RF-1 Active Planner Gating Gap

002C-R1 adds `A10_ACTIVE_PLANNER_SATURATION` as a first-class forbidden surface
pattern.

The active budget-faithful planner family includes at minimum:

- `budget_limited_belief_state_planner`
- `greedy_information_gain_or_uncertainty_planner_under_budget`
- `strongest_active_planner_for_task_type`
- any task-specific budget-faithful active planner or strongest active classical
  method applicable to the task

Required detector/baseline fields:

- `planner_family_max`
- `budget_limited_belief_state_planner`
- `greedy_information_gain_or_uncertainty_planner_under_budget`
- `strongest_active_planner_for_task_type`
- `planner_field_access_manifest`
- `planner_budget_trace`
- `consumed_by_final_verdict`

Forbidden condition:

`planner_family_max >= visible_oracle_score - equivalence_band`

Primary rejection:

`reject_active_planner_saturated`

Promotion rule repair:

A sketch may promote only if:

`planner_family_max < visible_oracle_score - equivalence_band`

This planner gate is explicit and independent. It is not implied by
`strongest_fair_baseline`.

## RF-2 Positive Grammar / Oracle-vs-Planner Separation

002C-R1 replaces the load-bearing slogan that an oracle "earns signal through
budget-faithful information gathering" with a required per-sketch declaration:

`oracle_vs_planner_separation_argument`

Each later sketch must answer:

- what information or computation the budget-faithful oracle can exploit;
- why a fair budget-limited belief-state planner cannot exploit the same
  structure under the same budget;
- whether the oracle is actually just an active planner;
- what micro-probe result would falsify the claimed separation;
- why the claimed gap is not produced by weakening, omitting, aliasing, or
  underpowering the planner baseline.

R1 adds `P012_ORACLE_VS_ACTIVE_PLANNER_SEPARATION`.

Requirement:

The oracle advantage must be structurally distinct from fair budget-limited
planning. If the argument is absent or not credible, the sketch is treated as
active-planner-equivalent and rejected or the batch is blocked as:

`blocked_no_valid_environment_design_grammar`

Minimum pre-run evidence:

- oracle strategy description;
- planner family strategy description;
- same-budget comparison;
- falsification condition;
- expected `planner_family_max` below oracle-minus-band.

## RF-3 Operationalized `blocked_no_valid_environment_design_grammar`

002C-R1 makes the blocked grammar verdict mechanical. It must trigger if any of
the following conditions hold.

### Trigger A

A repaired batch all-rejects and every rejection belongs to a
saturation/leakage/direct-decode/oracle-invalid/metric-degenerate/active-planner-
equivalent hard-failure family, with no rejection attributable only to a fixable
implementation omission.

### Trigger B

Two consecutive repaired batches produce zero promoted full-harness candidates
after complete battery and independent static scan, and the only proposed way to
create a gap is to weaken, omit, alias, underpower, or restrict fair baselines.

### Trigger C

No proposed sketch can supply `oracle_vs_planner_separation_argument` without
relying on forbidden access, answer-key diagnostic oracle, hidden state,
baseline omission, or metric weakening.

## Cross-Batch Search Budget

002C-R1 is a precondition repair record only. It does not authorize 003A.

`BATCH-ENV-HEADROOM-SCOUT-003A` may be considered only after review of this
002C-R1 record. If 003A is separately authorized and then produces zero
promotions with all rejects in known hard-failure families, a new 004A batch is
not automatically authorized.

Before any 004A, a route-level review must choose one of:

- `continue_environment_search`
- `downgrade_current_environment_grammar`
- `replace_environment_grammar`
- `close_phase0_environment_search`

No indefinite "run another batch" loop is allowed.

## Generated Artifacts

- `artifacts/phase0_environment_design_constraints_002c_r1/revision_record.json`
- `artifacts/phase0_environment_design_constraints_002c_r1/forbidden_surface_patterns_r1.json`
- `artifacts/phase0_environment_design_constraints_002c_r1/required_positive_properties_r1.json`
- `artifacts/phase0_environment_design_constraints_002c_r1/next_batch_generation_brief_r1.json`
- `artifacts/phase0_environment_design_constraints_002c_r1/cross_batch_stop_rules.json`
- `artifacts/phase0_environment_design_constraints_002c_r1/source_readback.json`

## Claim Ceiling

Phase-0 environment design-constraint R1 repair only.

No headroom confirmation. No Gate1 pass. No mechanism validity. No candidate
feasibility. No runtime/mainline effect. No agency, autonomy, consciousness, or
EGO readiness.

## Next Minimal Closed-Loop Action

Review 002C-R1. Only if RF-1, RF-2, and RF-3 are accepted as closed should
`BATCH-ENV-HEADROOM-SCOUT-003A` be considered for separate authorization.

## What This Does Not Prove

This does not prove that any environment has headroom, that any candidate is
feasible, that 003A should run, or that any mechanism evidence exists. It does
not authorize scout execution, full-harness execution, candidate implementation,
route tournament, runtime/mainline/admission/bridge wiring, commit, push, tag, or
remote-anchor.
