# LCC Public I/O Schema

This schema defines the public interface for a future independent reimplementation. It is intentionally abstract. It must not expose implementation recipes, expected outputs, or current runner internals.

## Candidate-Visible Inputs

The candidate may receive:

- `observation`: current public observation vector or structured public observation.
- `action_handles`: anonymous executable action IDs.
- `intervention_history`: previous own actions and observed outcomes.
- `observed_outcomes`: outcomes already observed after prior actions.
- `goal_vector`: non-semantic goal or objective vector, when applicable.
- `constraint_vector`: non-semantic constraint vector, when applicable.
- `horizon`: public decision horizon or rollout limit.
- `budget`: public action, probe, or computation budget.

The candidate may maintain internal learned effect estimates only if they are derived from allowed observations and own-intervention history.

## Forbidden Candidate Inputs

The candidate must not receive:

- Semantic action labels.
- Object names.
- Entity names.
- Scenario ID.
- Cycle ID.
- Contract ID.
- Task ID.
- Goal ID.
- Semantic goal names.
- Hidden latent state.
- Hidden future state.
- Oracle transition table.
- Oracle plan table.
- Evaluator metric values.
- Expected output table.
- Baseline outputs.
- Test family label.
- Post-hoc trace explanatory fields.

## Public Records

### Observation Record

```yaml
observation:
  public_features: array
  optional_public_history_window: array
  timestamp_or_step: integer
```

`public_features` must not encode hidden labels, semantic names, future state, or evaluator metrics.

### Action Handle

```yaml
action_handle:
  action_id: opaque_string
  execution_only: true
```

`action_id` may be stable within an episode but must not contain semantic action text. If action IDs are permuted while effects stay fixed, behavior should remain invariant.

### Intervention History Record

```yaml
intervention_history_item:
  observation_before: observation
  action_id: opaque_string
  observation_after: observation
  observed_outcome: public_outcome
  delay: integer
```

This record is allowed only after the outcome is observed. It must not include hidden counterfactuals.

### Public Outcome

```yaml
public_outcome:
  observed_delta: array
  terminal: boolean
  public_failure_flag: optional_boolean
```

Outcome fields must be directly observable by the candidate after action execution.

### Candidate Decision

```yaml
candidate_decision:
  selected_action_id: opaque_string
  prediction_before_action:
    predicted_effect_summary: array
    prediction_confidence: optional_number
  decision_evidence:
    allowed_feature_refs: array
    used_intervention_history_refs: array
```

`decision_evidence` exists for replay/provenance. It must reference only allowed public inputs.

### Trace Record For Scoring

```yaml
trace_record:
  observation_before: observation
  candidate_visible_inputs_hash: string
  selected_action_id: opaque_string
  prediction_before_action: object
  observation_after: observation
  observed_outcome: public_outcome
  replay_fields:
    allowed_evidence_only: object
  redteam_metadata:
    hidden_from_candidate: true
```

Scorers may use redteam metadata, but the candidate must not.

## Behavior-Only Replay Input

Behavior-only replay may use:

- Public observations.
- Anonymous action IDs.
- Candidate predictions before action.
- Observed outcomes after action.
- Public goal/constraint vectors.
- Public horizon/budget.

Behavior-only replay must not use hidden state, scenario labels, semantic labels, expected outputs, or evaluator metrics.

## Leak Rule

If a field is needed by the evaluator but not by the candidate, it must be explicitly stored under metadata hidden from candidate access. Any leak of that field into candidate decision evidence invalidates the run.
