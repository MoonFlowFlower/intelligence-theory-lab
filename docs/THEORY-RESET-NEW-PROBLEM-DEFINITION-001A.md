# THEORY-RESET-NEW-PROBLEM-DEFINITION-001A

## current_layer

```text
task_id = THEORY-RESET-NEW-PROBLEM-DEFINITION-001A
layer = mechanism-hypothesis / problem-definition-reset
execution_type = audit + problem-contract drafting + falsification-design only
mechanism_training_authorized = false
agent_training_authorized = false
model_class_reset_authorized = false
gate1_reopen_authorized = false
same_agent_bridge_authorized = false
ego_integration_authorized = false
```

This task defines a successor problem. It does not run an experiment, train a
model, reopen Gate1, draft a bridge, touch EGO mainline, or implement any
future mechanism.

## parent_lineage_summary

The following inputs were read as immutable parent state:

```text
Gate0_001C_closeout_claim_ceiling = bounded isolated Gate 0 predictive-action mechanism evidence only
Gate1_failed_graph_cache_collapse_closeout = closed; bounded negative mechanism evidence only
Candidate_A_closeout = closed_current_operationalization
Candidate_B_residue_closeout = closed_shuffled_same_loss_and_function_approximation_collapse
same_agent_bridge_status = blocked_no_clean_local_mechanism
REPRESENTATIONAL-GAP-PREFLIGHT-001A = audit_superseded; narrow residue only
REPRESENTATIONAL-GAP-PREFLIGHT-001B = failed_validly; fair controls solved target
```

No required parent input was unavailable. The claim ceiling is therefore not
lowered for missing-input reasons.

## wrong_problem_definition

The failed problem definition was:

```text
Can we find an output-level representational gap that cheap controls cannot solve?
```

This is the wrong problem after 001B. Fair full-history count/statistic controls,
finite-state controls, graph/cache controls, kNN/episodic controls, and summary
controls solved the frozen target. The remaining K<=4 suffix-window collision
was only a bounded-window residue, not a fair-control mechanism gap.

## most_likely_wrong_abstraction

The most likely wrong abstraction was treating output separability as mechanism
evidence. A hidden state variable, parity bit, cache key, FSM state, or summary
statistic can all be compact representations of the same input-output function.
Calling one of them a mechanism does not create mechanism evidence.

The reset must therefore stop asking whether a witness can compute the right
label and ask whether the process that changes internal state under controlled
intervention remains distinguishable from fair cheap controls with the same
access.

## strongest_objection

The proposed framing may still be wrong because cheap controls may match not only outputs but also traces if the trace schema is too shallow. Unless intervention, deletion, counterfactual, and replay probes force a divergence that cannot be replayed by graph/cache/statistic systems under the same access contract, the framing remains another output-equivalence trap.

This objection is strong enough that the surviving definition is only a future
preflight candidate, not an implementation authorization.

## cheap_control_lessons

All future mechanism tasks must carry forward these mandatory adversaries:

```text
full-history count/statistic controls
finite-state / automaton controls
graph/cache controls
kNN / episodic retrieval controls
summary/statistic controls
oracle/leakage probes
shuffled-label or shuffled-outcome controls where applicable
behavior-only replay controls
trace-only replay controls
random-representation controls
ablation controls
```

Any future task that omits these is preflight-incomplete.

## candidate_successor_framings

```text
F1 Output Representational Gap = reject_or_demote
F2 Process / Intervention Gap = survives_as_primary_candidate
F3 Adaptation-Under-Distribution-Shift Gap = survives_as_supporting_constraint
F4 Causal Model Update Gap = survives_as_supporting_constraint
F5 Viability / Value-State Update Gap = demote_to_later_only
F6 Replay / Consolidation Reframing = reject_for_now
```

F2 is the only viable primary reset because it changes the evidence target from
output prediction to process-level state change under intervention. F3 and F4
remain useful constraints: the future task should include distribution shift
and causal intervention probes. F5 is too close to value/viability language and
must not be used until a strictly bounded, non-affective contract exists. F6 is
blocked by the closed Gate1 lineage and same-agent bridge status.

## rejected_framings

Rejected:

```text
searching for obscure XOR/parity/count tasks
raising K until controls fail
lowering challenger capacity
banning useful summary/count/statistic controls
calling cache/FSM state a mechanism by label
using output prediction success as mechanism evidence
reopening Gate1
drafting a same-agent bridge
moving directly to model-class reset
```

## surviving_candidate_problem_definition_if_any

Surviving bounded successor definition:

```text
Can a bounded mechanism show intervention-sensitive internal update,
counterfactual action-conditioned adaptation, or process-level state change
under intervention that remains distinguishable from fair full-history cheap
controls under trace/replay, ablation, deletion, and counterfactual probes?
```

This is not a claim that such a mechanism exists. It is a problem definition
worth turning into a future preflight task card only if the future card freezes
fair controls, trace schema, interventions, ablations, and failure conditions
before any run.

Minimum process probes:

```text
state intervention
memory deletion
counterfactual action substitution
observation perturbation
prediction-error intervention
representation freezing
history-preserving causal perturbation
```

The key evidence target is not better output accuracy. The target is whether
the allowed update path produces a state-change pattern that fair controls
cannot reproduce from the same trace and access contract.

## trace_replay_requirements

Future trace records must include:

```text
episode_id
step_id
observation
action
allowed_history
prediction_before_action
action_conditioned_prior_or_state_before_observation
actual_observation
prediction_error_or_update_signal
internal_state_before_update
internal_state_after_update
state_delta
memory_read_keys
memory_write_keys
retrieval_hits
counterfactual_action_probe
intervention_probe_id
ablation_condition
system_output
verifier_label_or_outcome
access_manifest
lineage_id
```

Future replay must verify:

```text
same traces reproduce same metrics
non-oracle systems did not access forbidden data
internal state changed only through allowed update path
behavior changes after deletion/intervention are traceable
cheap controls received fair access
graph/cache/kNN/summary/FSM controls were not disabled
```

## future_preflight_requirements

A future preflight must freeze:

```text
problem definition
environment family
intervention set
trace schema
state-delta metric
replay contract
cheap-control adversary set
oracle/leakage probes
ablation conditions
shuffle/random-representation controls
acceptance gate
claim ceiling
stop conditions
```

It must fail if graph/cache, kNN, FSM, summary, trace-only replay, or
behavior-only replay controls reproduce both outputs and declared process
traces under fair access.

## anti_hardcoding_audit

```text
Does this merely rename a small explicit variable as an internal state? risk_present; future task must prove otherwise.
Does this hide an if-else policy behind mechanism language? risk_present; intervention probes required.
Does this ban controls that should be fair? no; carryforward requires fair controls.
Does this reward looking alive rather than showing mechanism evidence? no; no UI, companion, or affect behavior.
Can a graph/cache replay the behavior and trace? unknown; future preflight must test and fail if yes.
Can a summary statistic reproduce the alleged internal state? unknown; future preflight must test and fail if yes.
Can a finite-state controller implement the same update? unknown; future preflight must test and fail if yes.
Can kNN or episodic retrieval match the behavior? unknown; future preflight must test and fail if yes.
Does shuffled-label or shuffled-outcome control preserve performance? unknown; mandatory future control.
Does random representation preserve performance? unknown; mandatory future control.
Does deletion or perturbation change future behavior in a mechanism-specific way? required future evidence.
```

Audit verdict:

```text
anti_hardcoding_audit_passed = true_for_problem_definition_only
```

## claim_ceiling

```text
bounded successor problem-definition evidence only
```

This does not prove:

```text
new model class readiness
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

Authorization state:

```text
MODEL_CLASS_RESET = not_authorized
Gate1_reopen = not_authorized
same_agent_bridge = blocked
EGO_integration = not_authorized
LLM_RAG_companion_emotion_relationship_user_model_modules = not_authorized
```

## stop_conditions

```text
stop_conditions_encountered = []
```

No stop condition was triggered. The task did not define an output-only rescue,
ban fair controls, require model-class reset, reopen Gate1, draft a bridge,
touch EGO mainline, introduce LLM/RAG/companion/emotion/relationship modules,
or rely on consciousness/agency/functional-subject language.

## rollback_plan

If this reset is later found to violate scope:

```text
revert only THEORY-RESET-NEW-PROBLEM-DEFINITION-001A allowed outputs
preserve failure manifest
do not patch around the violation
do not create successor implementation task
do not update AGENTS.md without separate authorization
```

## next_allowed_task

```text
final_verdict = theory_reset_001a_problem_definition_bounded_pass
next_allowed_task = NEW-PROBLEM-PREFLIGHT-001A task-card drafting
```

The next allowed task is drafting a future preflight task card only. It is not
implementation, model training, model-class reset, Gate1 reopening, bridge
drafting, or EGO integration.
