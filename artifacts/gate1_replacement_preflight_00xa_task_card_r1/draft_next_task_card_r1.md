# GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-R1

Status: repaired draft only. This R1 card repairs the drafted
`GATE1-REPLACEMENT-PREFLIGHT-00XA` task card after hostile audit verdict
`requires_one_bounded_task_card_repair`.

Auto-Remote-Anchor: forbidden.

## Purpose

Define a bounded, candidate-free Gate1 replacement preflight task card that is
eligible for brief hostile R1 re-audit. This card does not implement the
preflight, run Gate1, create a candidate, create source/tests, or modify any
runtime, mainline, admission, Route C, Gate4, or Gate5 path.

## Problem Definition

The previous draft was directionally correct but failed narrowly because metric
degeneracy controls were not operationalized enough to block the known
candidate-free Route C false-positive pattern. This R1 card must preserve the
existing pre-candidate boundaries while explicitly requiring:

- balanced metric shape and metric-degeneracy controls consumed by final
  verdict derivation;
- a positive, fail-able fair-signal admission basis;
- an independently frozen surface specification pack that is not authored or
  mutated by the future preflight implementer.

## Current Stage / Layer

Engineering-governance / Gate1 replacement preflight task-card repair only.

Claim ceiling: repaired task-card draft only.

## Mainline Integration Status

None. This R1 card does not target EGO mainline, runtime, bridge, admission,
Gate4/Gate5, Route C, scheduler, UI, LLM, AIRI, deployment, or companion paths.

## Enabled-State Requirement

This card enables no executable path. A future implementation may proceed only
after this R1 draft is independently accepted for implementation-card drafting.

No Gate1 candidate, mechanism candidate, runtime path, admission path, scheduler
path, or baseline-immunity executor may be enabled by this card.

## Real-Trigger Evidence Requirement

The future implementation task must read and record authoritative hashes for:

- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/selected_verdict.json`
- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate1_failure_readback.json`
- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate_dependency_readback.json`
- `docs/research/GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A.md`
- `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE-EVIDENCE-PROVENANCE-VERIFIER-001A-HOSTILE-AUDIT-001A/audit_result.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-HOSTILE-AUDIT-001A/audit_result.json`

The future implementation must preserve the current negative evidence context:
old Gate1 positive inheritance is closed by graph-cache reconciliation failure,
and candidate-free Route C false positive showed that single-sided or
size-saturating metrics can admit empty mechanism evidence.

## Target Variable

`gate1_replacement_surface_pre_candidate_admissibility`.

This is a pre-candidate admissibility variable, not a mechanism-success
variable. It asks whether an independently frozen proposed Gate1 surface has
enough legal, non-trivial, baseline-resistant signal to justify a later
candidate-card draft.

Allowed verdicts:

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

## Surface Specification Authorship And Immutability

The frozen surface specification pack is a required input, not a deliverable of
the future implementation task.

Requirements:

- the surface specification pack must exist before Codex implements the
  preflight;
- the preflight implementer must not author, mutate, amend, normalize, or freeze
  the surface spec inside the implementation task;
- the spec must be authored and frozen by a separate authority, or exist as a
  pre-existing artifact explicitly accepted for use before implementation;
- the implementation task must record the spec path, SHA256, author/source,
  freeze timestamp or decision-log pointer, and canonical readback channel;
- if no independently frozen spec exists, final verdict must be
  `blocked_missing_candidate_free_surface_spec`;
- if the implementer authors or mutates the spec during the implementation task,
  final verdict must be `blocked_candidate_authored_or_mutated_surface_spec`.

This is a card-level requirement only. This R1 task does not create a surface
spec.

## Observable State

The only allowed observed input is the independently frozen surface
specification pack containing:

- target definition;
- state schema;
- observation schema;
- legal action/query schema;
- fixed action/query budget;
- balanced metric definition and equivalence band;
- generator provenance;
- train/validation/heldout/test seed policy, if applicable;
- source pins and readback paths;
- declared legal channels;
- declared illegal channels;
- negative-evidence pointers;
- baseline panel registry mapping each baseline to callable producer
  requirements.

The preflight must not observe candidate outputs because no candidate may exist.

## Action / Query Budget

The preflight must record a fixed budget before running any candidate-free
probes.

Budget rules:

- no candidate calls;
- no hidden answer-key access for fair baselines;
- no post-hoc threshold or metric tuning;
- query/action budget must be equal for all fair active/query baselines;
- exhaustive legal query is allowed only as a challenger and must block if it
  saturates;
- if budget cannot be fixed before execution, verdict is
  `blocked_pending_canonical_readback`.

## Candidate-Forbidden Condition

Candidate code, candidate outputs, candidate-authored ground truth,
mechanism-specific oracle functions, and candidate implementation paths are
forbidden.

Stop immediately if a candidate is required to define the target, generate the
data, author truth, compute the metric, or supply the oracle.

## Hypothesis

A Gate1 replacement surface is admissible for later candidate-card drafting only
if candidate-free computed controls show that the target is neither trivially
decodable, metric-degenerate, fair-baseline saturated, graph-cache equivalent,
lookup equivalent, nor blocked by canonical readback.

## Strongest Baseline

The strongest baseline explanation is that any apparent Gate1 replacement signal
is reproduced by a graph/cache/lookup/replay/control family or by a degenerate
metric, not by a mechanism-specific effect.

## Full Baseline Panel

Required panels:

- trivial predictors: `predict_all`, `predict_none`, `constant_k_sweep`,
  `random`, `majority`;
- passive baselines: `observation_only`, `value_decoder_mean`,
  `value_decoder_variance`, `value_decoder_correlation`, `value_decoder_pca`,
  `nearest_neighbor_passive`;
- active/query baselines when actions or queries exist:
  `exhaustive_legal_query`, `greedy_uncertainty_query_under_budget`;
- graph-cache challengers: `graph_lookup`, `transition_table`,
  `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`;
- lookup imitation: `trace_only_replay`, `ngram_trace_lookup`,
  `full_bundle_decoder`, `serialized_state_decoder`, `belief_table`,
  `pair_count_table`;
- direct objective optimizer when applicable: `discounted_wls`,
  `least_squares`, `convex_solver`;
- amortized learner when adaptation/learning is claimed: a real fitted
  `trained_legal_channel_learner`, not a deterministic stub;
- task-specific classical baseline: strongest known classical method for the
  task type.

If any applicable panel member is missing, uninvoked, not independent, weaker
than a known fair challenger, or not consumed by final verdict derivation, the
preflight cannot emit an admissibility verdict.

## Metric Shape And Degeneracy Controls

The future implementation must make the metric non-degenerate by construction
and by consumed controls.

### Balanced Metric Requirement

Any set/classification/recovery metric must report one of:

- precision and recall jointly;
- F-beta with stated beta;
- explicit cost-weighted utility with false-positive and false-negative costs;
- another explicitly balanced metric that prevents single-sided saturation.

The implementation must explicitly forbid using any single-sided metric as an
admissible success basis, including:

- recall-only;
- precision-only;
- coverage-only;
- specificity-only;
- abstention-only;
- size-only score.

If an admissibility verdict relies on any single-sided metric, final verdict
must be `rejected_metric_degenerate`.

### Degenerate Predictor Controls

The baseline panel must explicitly compute and report:

- `predict_all`;
- `predict_none`;
- `constant_k_sweep`;
- `random`;
- `majority`.

These controls must appear as callable baseline rows, not only prose. Each row
must include producer/provenance fields and `consumed_by_final_verdict=true`.

If any degenerate predictor reaches the ceiling band, final verdict must be
`rejected_metric_degenerate`.

### Size-Only Sweep

The implementation must compute an explicit size-only sweep:

- vary prediction-set size from `0..N`;
- hold content policy fixed or matched;
- record score as a function of output size;
- reject if score climbs to the ceiling band by size alone.

This sweep must be a consumed control in final verdict derivation. If size alone
can drive the score to the ceiling band, final verdict must be
`rejected_metric_degenerate`.

### Control Consumption

It is not enough to compute `predict_all`, `predict_none`, `constant_k_sweep`,
`random`, `majority`, or the size-only sweep and leave them in a report.

If any metric-degeneracy control fails and final verdict ignores it, the
preflight bundle is invalid and must not emit an admissibility verdict.

### No By-Reference Escape

Citing `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` is not sufficient. The Codex
implementation task must compute the metric-degeneracy controls, record their
producer/provenance rows, and consume them in final verdict derivation.

The baseline-immunity standard remains a static normative contract, not an
executor.

## Positive Admission Basis

Admissibility cannot be framed only as "baselines did not saturate." The
preflight must provide a positive, fail-able basis showing that the fair legal
channel has signal but passive observation does not trivialize the target.

### Partial-Inferability Demonstration

The preflight must demonstrate all of:

- passive observation does not trivially decode the target;
- the target is not information-theoretically independent of all fair observable
  channels;
- there is genuine residual uncertainty under passive observation;
- the proposed legal channel or intervention class can reduce that residual
  uncertainty in principle.

Required controls:

- passive-only attacker family;
- visible-channel decodability check;
- random/matched marginal baseline;
- non-reading oracle or null oracle negative control that cannot reach ceiling;
- fail-closed result if the fair channel has no signal.

If this demonstration is absent, final verdict must be either
`blocked_missing_partial_inferability_demonstration` or
`rejected_no_fair_signal`.

### Budget-Faithful Visible-Channel Oracle

If an oracle is used to argue headroom, it must be:

- budget-faithful;
- visible-channel only;
- legal-access only;
- not reading a hidden answer key;
- not reading planted truth;
- not presupposing the mechanism.

It must clear the strongest fair baseline by at least the equivalence band.

An answer-key oracle may be included only as a non-admissive diagnostic. It must
never support preflight admission. If oracle headroom is answer-key-only, final
verdict must be `rejected_no_fair_signal` or
`rejected_answer_key_oracle_gap`.

## Baseline-Immunity Standard Reference

The preflight must apply `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` as a static
normative contract.

It must not treat the standard or registry as an executor. It must record
whether each registry class is applicable, invoked, and consumed by final
verdict derivation.

## Provenance Verifier Use

The local verifier may be used only as a provenance-shape prefilter after the
future task emits an evidence bundle.

Allowed interpretation: `provenance_wellformed_only` means the bundle shape and
internal cross-references are well-formed.

Forbidden interpretation: any verifier output as Gate pass, admission,
baseline-immunity, replay validation, source validation, strongest-baseline
validation, candidate success, or mechanism validity.

## Leakage Positive Controls

The task must include a leakage scanner with at least one positive control on
the same admission path.

Leakage channels must include, where applicable:

- observation names;
- action names;
- filenames and fixture names;
- artifact structure;
- baseline hints;
- planted answer maps;
- value-level fields;
- label ordering;
- generator metadata;
- source-pin paths.

A positive control must be fail-able: injecting the leak must flip the
corresponding gate to blocked. A scanner that always passes or always detects a
hard-coded fixture is invalid.

## Replay Recalculation Requirement

Replay must recompute behavior from serialized state plus observation.
Hash-only replay, stored-output replay, or natural-language trace comparison is
insufficient.

If replay is not applicable to the proposed surface, the task must state why and
cannot use replay language as evidence.

## Source-Pin / Readback Requirement

The task must read source pins through authoritative file APIs and record:

- input artifacts;
- source paths;
- SHA256 hashes;
- readback channels;
- conflicts;
- fail-closed behavior on conflict;
- code path hashes for each producer function.

Self-readback only is invalid.

## Computed-Evidence Provenance Gate

Every score, baseline result, ablation result, leakage result, replay result,
control result, and verdict must derive from callable computation paths.

Each row must record:

- producer_function;
- input artifacts;
- run_id;
- seed/context/episode IDs where applicable;
- aggregation rule;
- code_path_hash;
- consumed_by_final_verdict.

Literal verdicts, static score dictionaries, unconsumed controls, and tests that
only assert pass are forbidden.

## Ablation Requirement

The future preflight must rerun applicable episodes under real interventions,
including no-action or no-transition ablations when action conditioning is being
tested. Ablation results must be independent callable rows and consumed by final
verdict derivation.

If ablations are not applicable to the frozen surface, the implementation must
state why and cannot use ablation language as positive evidence.

## Acceptance Gate

Accept only if all are true:

- target variable is clear and candidate-free;
- observable channel is legal and fixed;
- independently frozen surface spec exists before implementation;
- implementer did not author, mutate, amend, normalize, or freeze the surface
  spec;
- action/query budget is fixed before execution;
- metric reports precision plus recall, stated F-beta, cost-weighted utility, or
  another explicitly balanced metric;
- no single-sided metric supports admission;
- `predict_all`, `predict_none`, `constant_k_sweep`, `random`, `majority`, and
  size-only sweep are computed and consumed by final verdict;
- if any degenerate predictor or size-only sweep reaches the ceiling band,
  verdict is `rejected_metric_degenerate`;
- partial-inferability demonstration exists and is fail-able;
- any oracle supporting headroom is budget-faithful, visible-channel only,
  legal-access only, and not answer-key based;
- full applicable baseline panel is invoked and consumed;
- all six graph-cache challengers are invoked when representational or
  environment claims are present;
- lookup imitation panel is invoked when replay/memory claims are present;
- direct objective optimizer is invoked when the objective admits one;
- leakage scanner has fail-able positive controls;
- replay recomputes where replay is claimed;
- source-pin/readback provenance is fail-closed;
- evidence bundle is verifier-compatible, with verifier used as prefilter only;
- `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` is cited as static contract only,
  not executor;
- no old Gate1 positive inheritance is reused;
- no candidate, Gate run, Route C run, runtime path, or admission path is added.

Success authorizes at most candidate-card drafting. It does not authorize
candidate implementation, Gate1 pass claims, Gate4/Gate5 progression, mainline
integration, runtime integration, admission wiring, or remote anchoring.

## Stop Condition

Stop with a blocking or rejection verdict if:

- candidate code or candidate output is needed;
- the surface spec is missing before execution starts;
- the future implementer authors, mutates, amends, normalizes, or freezes the
  surface spec;
- target, observable channel, or budget cannot be defined pre-run;
- a metric is recall-only, precision-only, coverage-only, specificity-only,
  abstention-only, size-only, or otherwise single-sided;
- any metric-degeneracy trigger from the baseline-immunity standard fires;
- any degenerate predictor reaches the ceiling band;
- size alone can drive score to the ceiling band;
- metric-degeneracy controls are computed but not consumed by final verdict;
- partial-inferability demonstration is missing;
- fair channel has no signal;
- oracle headroom is answer-key-only;
- any fair baseline ties or beats the proposed admissibility target;
- any graph-cache challenger is omitted or saturates;
- any leakage positive control is absent, not detected, or not consumed;
- replay is hash-only or not recomputed;
- source readback conflicts and does not fail closed;
- verifier output is treated as admission;
- the baseline-immunity standard is treated as an executor;
- any Gate1/Gate4/Gate5, Route C, bridge, admission, runtime, EGO, UI, LLM,
  AIRI, deployment, or companion path is touched.

## Rollback Plan

Remove only artifacts and files created by the future preflight task under its
explicit allowed paths. Do not modify old Gate1, Gate2, Gate3, integrated,
Gate4, Route C, bridge, admission, runtime, or EGO artifacts.

## Expected Changed Files For A Future Implementation Task

This R1 card does not authorize implementation. A future implementation card
must name exact paths before any coding.

Candidate future paths, if separately authorized:

- `docs/codex/tasks/GATE1-REPLACEMENT-PREFLIGHT-00XA.md`
- `artifacts/gate1_replacement_preflight_00xa/`
- optionally, isolated preflight-only source/test paths named by a later audited
  implementation card

## Forbidden Files And Changes

Forbidden:

- Gate1 candidate source or tests;
- old Gate1 source/tests/artifacts except read-only inputs;
- Gate2/Gate3/integrated-route source/tests/artifacts except read-only inputs;
- Gate4/Gate5 source/tests/artifacts;
- Route C source/tests/modules;
- baseline-immunity executor;
- provenance verifier source/tests;
- runtime/mainline/admission/bridge files;
- EGO mainline, UI, LLM, AIRI, deployment, companion, product,
  relationship-learning, emotion, or proactive behavior files;
- commit, push, tag, or remote-anchor.

## Claim Ceiling

Gate1 replacement preflight task-card repair only. No Gate1 pass, no replacement
admissibility, no mechanism validity, no candidate success, no baseline-immunity
enforcement, no Gate4/Gate5 readiness, no mainline/runtime/live effect, no
agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Next Minimal Closed-Loop Action

Send
`artifacts/gate1_replacement_preflight_00xa_task_card_r1/draft_next_task_card_r1.md`
to Claude for brief R1 re-audit.

Only if Claude accepts R1 may the next Codex implementation card be drafted.
