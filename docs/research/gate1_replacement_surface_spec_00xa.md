# GATE1 Replacement Surface Spec 00XA

Task id: `GATE1-REPLACEMENT-PREFLIGHT-00XA-SURFACE-SPEC-FREEZE-001A`

Surface spec id: `gate1_replacement_surface_spec_00xa`

Status: frozen candidate-free surface specification.

Author/source: Codex bounded execution agent in the current surface-spec freeze
session. This session is not authorized to implement the future preflight.

Freeze timestamp: recorded in
`docs/research/gate1_replacement_surface_spec_00xa.freeze.json`.

Canonical readback channel: file API read of this markdown spec, freeze JSON,
and artifacts under `artifacts/gate1_replacement_surface_spec_freeze_001a/`.

Spec SHA256: recorded in
`docs/research/gate1_replacement_surface_spec_00xa.freeze.json` and
`artifacts/gate1_replacement_surface_spec_freeze_001a/spec_hash_readback.json`.

Future implementer mutation ban: the future preflight implementer must not
author, mutate, normalize, amend, or re-freeze this surface spec or its freeze
metadata. If the future implementer touches this spec pack, the future preflight
must stop with `blocked_candidate_authored_or_mutated_surface_spec`.

Auto-Remote-Anchor: forbidden.

## Claim Ceiling

This file freezes a candidate-free surface specification only. It does not
authorize Gate1 execution, candidate authoring, candidate implementation,
baseline execution, ablation execution, replay execution, verifier admission,
runtime/mainline/admission/bridge wiring, Gate4/Gate5, Route C, push, tag, or
remote anchoring.

No Gate1 pass, Gate1 replacement admissibility, mechanism validity, candidate
success, baseline-immunity enforcement, Gate4/Gate5 readiness, runtime
readiness, mainline effect, agency, autonomy, consciousness, emotion, stable
user benefit, or EGO readiness is claimed.

## Target Definition

Target variable:
`gate1_replacement_surface_pre_candidate_admissibility`.

The target is a pre-candidate admissibility decision for a proposed Gate1
replacement surface. It asks whether a candidate-free, independently frozen
surface has enough legal, non-trivial, baseline-resistant, fail-able signal to
justify a later candidate-card draft.

The target is not a mechanism-success variable, not a Gate1 pass variable, and
not a runtime-readiness variable.

Target type:

- `admissible_for_candidate_card_drafting_only`: all required controls clear
  under the balanced metric, strongest fair baseline margin, partial
  inferability, oracle, leakage, provenance, replay/applicability, and
  ablation/applicability requirements below.
- rejection or block verdict: any required stop condition, degenerate metric,
  fair-baseline saturation, missing surface-spec input, candidate-authored
  spec, missing partial inferability, missing canonical readback, or illegal
  channel use.

## State Schema

The future preflight state is a frozen, candidate-inaccessible surface bundle.
Every state record must be serialized as JSON-compatible data with these
top-level fields:

```json
{
  "surface_id": "string",
  "episode_id": "string",
  "source_pin_id": "string",
  "split": "train|validation|heldout|test|not_applicable",
  "visible_state": {
    "context_fields": "object",
    "observable_features": "object",
    "legal_channel_metadata": "object"
  },
  "legal_actions": [
    {
      "action_id": "string",
      "action_type": "observe_context|probe_visible_transition|query_legal_channel|request_provenance",
      "budget_cost": "positive integer",
      "visible_inputs": "object"
    }
  ],
  "budget": {
    "max_total_queries_per_episode": 16,
    "max_probe_visible_transition_queries": 8,
    "max_query_legal_channel_queries": 8
  },
  "hidden_target": {
    "stored_outside_legal_observation": true,
    "candidate_access": false,
    "fair_baseline_access": false,
    "oracle_access": "diagnostic_only_unless_visible_channel_oracle"
  },
  "provenance": {
    "generator_id": "string",
    "generator_source_hash": "sha256-or-blocked",
    "seed": "integer-or-not_applicable",
    "source_artifacts": ["path"]
  }
}
```

The hidden target must not appear in `visible_state`, action names, observation
names, filenames, fixture names, artifact structure, baseline hints, planted
answer maps, label ordering, source-pin paths, or generator metadata visible to
fair baselines.

## Observation Schema

Each passive observation must contain only visible, legal fields:

```json
{
  "surface_id": "string",
  "episode_id": "string",
  "split": "train|validation|heldout|test|not_applicable",
  "observation_index": "integer",
  "visible_state": "object",
  "legal_action_manifest": "array",
  "budget_remaining": "integer",
  "source_pin_refs": ["path"],
  "readback_hashes": ["sha256"]
}
```

Passive observation must not include candidate outputs, candidate-authored
truth, hidden labels, planted truth, answer-key fields, mechanism-specific
oracle outputs, or future observations.

## Legal Action And Query Schema

Legal query envelope:

```json
{
  "query_id": "string",
  "episode_id": "string",
  "action_type": "observe_context|probe_visible_transition|query_legal_channel|request_provenance",
  "budget_cost": "positive integer",
  "query_payload": "object",
  "allowed_response_fields": ["visible_state_delta", "legal_channel_observation", "provenance_hash"]
}
```

Legal actions:

- `observe_context`: passive read of the current visible state. Cost: 0.
- `probe_visible_transition`: one legal transition/intervention probe that
  returns only visible-channel observations. Cost: 1.
- `query_legal_channel`: one legal query to a declared fair channel. Cost: 1.
- `request_provenance`: read source-pin metadata and hashes. Cost: 0.

Illegal actions:

- candidate call;
- candidate output read;
- hidden-answer read;
- planted-truth read;
- mechanism-specific oracle read;
- answer-key oracle used for admission;
- future observation read;
- training-context read from heldout/test splits;
- path/name/fixture/metadata leak used as a signal;
- post-hoc metric, threshold, band, or budget change after observing results.

## Fixed Action And Query Budget

The fixed budget is 16 paid legal queries per episode:

- maximum 8 `probe_visible_transition` queries;
- maximum 8 `query_legal_channel` queries;
- unlimited zero-cost provenance reads only for source-pin and hash readback;
- no candidate calls under any budget;
- identical budget for all fair active/query baselines and any budget-faithful
  visible-channel oracle;
- exhaustive legal query may run only as a challenger. If it saturates the
  ceiling band or ties the oracle within the equivalence band, the surface is
  rejected rather than admitted.

If the budget cannot be fixed before execution, the future verdict must be
`blocked_pending_canonical_readback`.

## Balanced Metric Definition

Primary metric: macro F1 over the binary target
`gate1_replacement_surface_pre_candidate_admissibility`, with beta fixed at
1.0.

Required reported components:

- precision for the admissible class;
- recall for the admissible class;
- precision for the rejection/block class;
- recall for the rejection/block class;
- macro F1;
- confusion counts;
- false-positive count;
- false-negative count.

Numeric thresholds:

- target ceiling minimum: macro F1 >= 0.90;
- equivalence band: 0.03 macro F1;
- ceiling band floor: 0.87 macro F1;
- per-class precision floor for admissibility: 0.85;
- per-class recall floor for admissibility: 0.85;
- legal-channel residual-uncertainty reduction required over passive-only
  family: >= 0.06 macro F1;
- visible-channel oracle margin over strongest fair baseline: > 0.03 macro F1.

Admissibility is forbidden from:

- recall-only;
- precision-only;
- coverage-only;
- specificity-only;
- abstention-only;
- size-only score;
- natural-language summary;
- verifier `provenance_wellformed_only`;
- any static verdict dictionary or detached report.

Degeneracy rule: if any degenerate predictor or size-only sweep reaches macro
F1 >= 0.87, the future verdict must be `rejected_metric_degenerate`.

Fair-baseline saturation rule: if the strongest fair baseline ties or beats the
budget-faithful visible-channel oracle within the 0.03 equivalence band, the
future verdict must be `rejected_baseline_saturated`.

## False-Positive And False-Negative Treatment

A false positive is admitting a surface for candidate-card drafting when the
surface is degenerate, trivially decodable, answer-key dependent,
fair-baseline-saturated, leakage-contaminated, missing canonical readback, or
candidate-authored. False positives are claim-inflation risks and must block.

A false negative is rejecting a surface that later evidence might show has fair
legal-channel signal. False negatives are acceptable under this governance
layer because this preflight is a fail-closed admission guard, not a mechanism
success search.

The future implementation must report both counts and must not hide a false
positive behind a high aggregate metric.

## Metric Degeneracy Controls

The future implementation must detect and consume these controls in final
verdict derivation:

- `predict_all`;
- `predict_none`;
- `constant_k_sweep`;
- `random`;
- `majority`;
- size-only sweep `0..N`;
- post-hoc threshold sweep on heldout split where applicable.

Each control row must record `producer_function`, input artifacts, `run_id`,
seed/context/episode IDs where applicable, aggregation rule, code path hash,
and `consumed_by_final_verdict=true`.

Any missing, uninvoked, static, unconsumed, or non-independent control blocks
admissibility.

## Positive Partial-Inferability Requirements

Admissibility requires positive, fail-able evidence that:

- passive observation does not trivially decode the target;
- the target is not independent of all fair observable channels;
- residual uncertainty remains under passive observation;
- the legal channel or intervention class can reduce residual uncertainty in
  principle.

Required controls:

- passive-only attacker family;
- visible-channel decodability check;
- random or matched-marginal baseline;
- non-reading oracle or null oracle negative control;
- budget-faithful visible-channel oracle.

Fail-closed conditions:

- passive-only family reaches macro F1 >= 0.87:
  `rejected_trivially_decodable`;
- random or matched-marginal baseline reaches macro F1 >= 0.87:
  `rejected_no_fair_signal`;
- null oracle reaches macro F1 >= 0.87:
  `rejected_trivially_decodable`;
- visible-channel oracle fails to beat passive-only family by at least 0.06
  macro F1:
  `blocked_missing_partial_inferability_demonstration` or
  `rejected_no_fair_signal`;
- visible-channel oracle fails to beat strongest fair baseline by more than
  0.03 macro F1:
  `rejected_baseline_saturated`.

## Oracle Boundary

Only a budget-faithful visible-channel oracle may support candidate-card
drafting admissibility.

The oracle must be:

- budget-faithful;
- visible-channel only;
- legal-access only;
- not reading hidden answer keys;
- not reading planted truth;
- not presupposing the mechanism;
- using the same action/query budget as fair active/query baselines;
- required to clear the strongest fair baseline by more than the 0.03
  equivalence band.

An answer-key oracle may be diagnostic only. Answer-key-only headroom must lead
to `rejected_no_fair_signal` or `rejected_answer_key_oracle_gap`.

## Generator Provenance

This freeze creates no generator implementation and no generated episodes. The
future preflight implementation may use a generator only if the generator is
candidate-inaccessible, source-pinned, hashed, and callable through an
authorized future implementation task.

Required generator provenance fields:

- `producer_function`;
- generator source path;
- generator source SHA256;
- generator version or code path hash;
- run_id;
- split;
- seed list;
- episode IDs;
- aggregation rule;
- candidate access: false;
- fair baseline access: same legal channel and same budget;
- hidden target storage location;
- assertion that no candidate-authored field determines truth.

If generator provenance is absent, unverifiable, self-readback-only, or
candidate-authored, the future verdict must be
`blocked_pending_canonical_readback`.

## Train, Validation, Heldout, And Test Seed Policy

No seeds are generated by this freeze.

If the future preflight uses generated episodes, it must predeclare disjoint
split ranges before any score is computed:

- train: 1001..1099;
- validation: 2001..2099;
- heldout: 3001..3099;
- test: 4001..4099;
- leakage positive controls: 9001..9099.

Train, validation, heldout, test, and counterfactual-pair seeds must be
disjoint. Any unused frozen seed, train context, heldout context, or
counterfactual pair must block the evidence claim unless the future task card
explicitly narrows the split plan before execution.

## Source Pins And Readback Paths

Hard-trigger source pins required by this freeze:

- `docs/codex/tasks/GATE1-REPLACEMENT-PREFLIGHT-00XA.md`
- `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-CARD-HOSTILE-AUDIT-001A/audit_result.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-CARD-HOSTILE-AUDIT-001A/audit_report.md`
- `artifacts/gate1_replacement_preflight_00xa_implementation_card_draft_001a/source_readback.json`
- `artifacts/gate1_replacement_preflight_00xa_implementation_card_draft_001a/constraint_traceability_matrix.json`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json`

Supporting negative-evidence source pins used by this spec:

- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/selected_verdict.json`
- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate1_failure_readback.json`
- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate_dependency_readback.json`
- `docs/research/GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A.md`
- `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE-EVIDENCE-PROVENANCE-VERIFIER-001A-HOSTILE-AUDIT-001A/audit_result.json`

Authoritative SHA256 values are recorded in
`artifacts/gate1_replacement_surface_spec_freeze_001a/source_readback.json`.

## Declared Legal Channels

Legal channels for future preflight:

- frozen surface spec fields;
- visible state fields declared by the frozen spec;
- legal action/query outputs under the fixed budget;
- source-pin readback hashes;
- candidate-free baseline outputs;
- candidate-free leakage scanner outputs;
- candidate-free ablation outputs where applicable;
- candidate-free replay recomputation outputs where applicable;
- local provenance-shape verifier output used only as `provenance_wellformed_only`.

## Declared Illegal Channels

Illegal channels:

- candidate code;
- candidate outputs;
- candidate-authored target definitions;
- candidate-authored truth;
- candidate-authored metric, oracle, labels, or baseline inputs;
- hidden answer key;
- planted truth;
- future observation;
- train/validation leakage into heldout/test;
- filenames, fixture names, action names, observation names, artifact structure,
  baseline hints, label order, source-pin paths, or generator metadata as answer
  channels;
- answer-key oracle as admission support;
- provenance verifier as Gate pass, admission, replay validation, source
  validation, strongest-baseline validation, candidate success, or mechanism
  validity;
- `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` as an executor.

## Negative-Evidence Pointers

This surface spec preserves these negative evidence boundaries:

- old Gate1 positive inheritance is closed by graph-cache/replay collapse:
  `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate1_failure_readback.json`;
- Gate1 literal pass is not upgraded:
  `docs/research/GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A.md`;
- fair graph/cache controls matched or beat candidate behavior:
  `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json`;
- downstream Gate2/Gate3/Gate4/Gate5 dependencies do not bypass Gate1 closure:
  `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate_dependency_readback.json`;
- Route C false-positive and single-sided/size-saturating metric failures are
  normative baseline-immunity inputs:
  `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md`;
- the local provenance verifier is accepted only as a shape prefilter, not as
  admission:
  `artifacts/CLAUDE-INDEPENDENT-GATE-EVIDENCE-PROVENANCE-VERIFIER-001A-HOSTILE-AUDIT-001A/audit_result.json`.

These pointers do not rehabilitate old evidence. They are blockers and
challengers for any future candidate-free preflight.

## Baseline Panel Registry

Every applicable baseline below must be implemented as an independent callable
producer in a future separately authorized task. Each produced row must include
`producer_function`, input artifacts, run_id, seed/context/episode IDs where
applicable, aggregation rule, code path hash, invoked status, independence
status, and `consumed_by_final_verdict=true`.

| Class | Members | Callable producer requirement | Consumption rule |
|---|---|---|---|
| Trivial predictors | `predict_all`, `predict_none`, `constant_k_sweep`, `random`, `majority` | Independent control producers over the target space. `constant_k_sweep` must sweep all k in `0..N`. | Any member reaching macro F1 >= 0.87 yields `rejected_metric_degenerate`. |
| Size-only sweep | `size_only_sweep_0_to_N` | Vary prediction-set size only while holding content policy fixed or matched. | If score climbs to macro F1 >= 0.87 by size alone, verdict is `rejected_metric_degenerate`. |
| Passive baselines | `observation_only`, `value_decoder_mean`, `value_decoder_variance`, `value_decoder_correlation`, `value_decoder_pca`, `nearest_neighbor_passive` | Same passive visible observations as a fair passive attacker, zero paid queries. | Ceiling-band passive result yields `rejected_trivially_decodable`; no signal yields `rejected_no_fair_signal`. |
| Active/query baselines | `exhaustive_legal_query`, `greedy_uncertainty_query_under_budget` | Same legal action/query budget as the oracle and any fair active method. Exhaustive query is a challenger only. | Ceiling-band or within-band tie against oracle yields `rejected_baseline_saturated`. |
| Graph-cache challengers | `graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal` | All six are mandatory whenever representational or environment claims are present. No substitutions. | Any saturation or within-band tie blocks admissibility. |
| Lookup imitation | `trace_only_replay`, `ngram_trace_lookup`, `full_bundle_decoder`, `serialized_state_decoder`, `belief_table`, `pair_count_table` | Required when replay, memory, state-continuity, or serialized-state claims appear. | Any saturation or within-band tie blocks admissibility. |
| Direct objective optimizers | `discounted_wls`, `least_squares`, `convex_solver` | Required when the surface objective admits a direct optimizer. | Any saturation or within-band tie blocks admissibility. |
| Amortized learner | `trained_legal_channel_learner` | Required only if adaptation or learning is claimed. Must record a real fit, training data, fit procedure, `ml_library_used=true` or equivalent concrete fit evidence, and must not be a deterministic stub. | Stub, no-fit, or within-band tie blocks learning/adaptation claims and admissibility. |
| Task-specific classical | `strongest_known_classical_method_for_task_type` | Strongest known non-candidate method for the task type. | If omitted or within-band tie, no admission. |

No baseline result may be replaced by a literal dictionary, static verdict, or
test-only second logic path.

## Leakage Scan Channels

The future leakage scanner must cover:

- observation names;
- action names;
- filenames and fixture names;
- artifact structure;
- baseline hints;
- planted answer maps;
- value-level fields;
- label ordering;
- generator metadata;
- source-pin paths;
- hidden answer aliases;
- serialized-state fields;
- split/seed identifiers.

## Leakage Positive-Control Expectation

At least one positive control must be injected on the same admission path. The
positive control must be fail-able:

- inject a known leak into a declared channel;
- scanner must detect it;
- detected positive control ID must be consumed by final verdict derivation;
- removing the injected leak must remove the positive-control detection;
- a non-detected or unconsumed positive control blocks admissibility.

The future implementation may not use a hard-coded fixture scanner that always
passes or always detects only one known dictionary.

## Replay Applicability

Replay is applicable if the future surface uses serialized state, transitions,
memory, trajectory, or temporal continuity claims.

When applicable, replay must recompute candidate-free behavior from
`serialized_state + observation` through a callable producer. Hash-only replay,
stored-output replay, and natural-language trace comparison are insufficient.

If no replay state exists, the future implementation must record
`replay_not_applicable_no_serialized_state` and must not use replay language as
positive evidence.

## Ablation Applicability

Ablation is applicable when legal actions, transitions, interventions, state
updates, memory, or legal channels are claimed to reduce uncertainty.

When applicable, ablations must rerun episodes under real interventions such as
no-action, no-transition, passive-only, legal-channel-disabled, and
budget-reduced variants. Each ablation row must be independently callable and
consumed by final verdict derivation.

If no action/intervention channel exists, the future implementation must record
why ablation is not applicable and must not claim legal-channel headroom from
ablation. If a surface depends on legal-channel signal but ablation is absent,
the future verdict must be `blocked_missing_partial_inferability_demonstration`
or `rejected_no_fair_signal`.

## Computed-Evidence Provenance Gate

Every future score, baseline result, ablation result, contrast, leakage result,
replay result, source-pin result, and verdict must derive from callable
computation paths.

Each evidence row must record:

- producer_function;
- input artifacts;
- run_id;
- seed/context/episode IDs where applicable;
- aggregation rule;
- code path hash;
- consumed_by_final_verdict.

Forbidden evidence forms:

- literal verdicts;
- static score dictionaries;
- unconditional clean reports;
- detached reports;
- tests that only assert pass;
- self-readback-only source validation;
- unconsumed controls.

Any unused frozen seed, train context, heldout context, or counterfactual pair
must block the evidence claim.

## Final Allowed Verdict List

The future preflight may emit only one of:

- `admissible_for_candidate_card_drafting_only`
- `rejected_metric_degenerate`
- `rejected_no_fair_signal`
- `rejected_answer_key_oracle_gap`
- `rejected_trivially_decodable`
- `rejected_baseline_saturated`
- `blocked_missing_partial_inferability_demonstration`
- `blocked_pending_canonical_readback`
- `blocked_missing_candidate_free_surface_spec`
- `blocked_candidate_authored_or_mutated_surface_spec`

No pass-shaped alias is allowed.

## Acceptance Signal For This Freeze

This freeze is acceptable only if:

- this spec exists at the declared path;
- freeze metadata exists;
- the spec SHA256 is recorded outside the spec file;
- author/source is recorded;
- freeze timestamp is recorded;
- canonical readback channel is recorded;
- the future preflight implementer mutation ban is explicit;
- required fields are present;
- metric definition, equivalence band, and ceiling band are pre-specified;
- baseline panel producer requirements are specified;
- negative-evidence pointers are included;
- no implementation path is created;
- no source, test, runtime, admission, bridge, candidate, Route C, Gate4, or
  Gate5 path is touched;
- no commit, push, tag, or remote anchor occurs.

Expected freeze verdict:
`gate1_replacement_surface_spec_00xa_frozen`.

## Next Minimal Closed-Loop Action

Send this spec, its freeze metadata, the final report, and the validation report
to Claude for hostile audit. Only if Claude accepts the frozen surface spec and
the operator gives explicit implementation authorization may a separate future
implementation task run the candidate-free preflight against this spec.
