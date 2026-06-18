# GATE1-REPLACEMENT-PREFLIGHT-00XA

Status: draft only. This card is not implemented by `GATE1-REPLACEMENT-READBACK-OR-PREFLIGHT-SELECTION-001A`.

Auto-Remote-Anchor: forbidden.

## Problem Definition

Draft a candidate-free Gate1 replacement preflight that determines whether a proposed Gate1 measurement surface is admissible for later candidate-card drafting. The task must not implement a candidate, must not run old Gate1 modules, must not reuse old Gate1 positive inheritance, and must not design a new mechanism surface during execution.

The preflight consumes a frozen surface specification pack. If that pack is absent or cannot define the target variable, observable state, legal action/query budget, generator provenance, source pins, and strongest fair baseline panel without relying on old Gate1 positive inheritance, the task must stop with a blocking verdict.

## Current Stage / Layer

Engineering-governance / Gate1 pre-candidate mechanism-preflight.

Claim ceiling: candidate-free Gate1 replacement preflight only.

## Mainline Target

None. No EGO mainline, runtime, bridge, admission, Gate4/Gate5, Route C, scheduler, UI, LLM, AIRI, deployment, or companion path is targeted.

## Enabled-State Requirement

Only local candidate-free preflight execution is allowed if a separately audited implementation task later authorizes it. This draft itself enables nothing.

No Gate1 candidate, mechanism candidate, runtime path, admission path, or scheduler path may be enabled.

## Real-Trigger Evidence Requirement

The future task must read, before execution:

- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/selected_verdict.json`
- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate1_failure_readback.json`
- `artifacts/gate1_replacement_readback_or_preflight_selection_001a/gate_dependency_readback.json`
- `docs/research/GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A.md`
- `artifacts/post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation/baseline_comparison.json`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md`
- `docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.registry.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE-EVIDENCE-PROVENANCE-VERIFIER-001A-HOSTILE-AUDIT-001A/audit_result.json`

## Target Variable

`gate1_replacement_surface_pre_candidate_admissibility`.

This is a pre-candidate admissibility variable, not a mechanism-success variable. It asks whether a frozen proposed Gate1 surface has enough legal, non-trivial, baseline-resistant signal to justify a later candidate-card draft.

Allowed verdicts:

- `admissible_for_candidate_card_drafting_only`
- `rejected_metric_degenerate`
- `rejected_no_fair_signal`
- `rejected_trivially_decodable`
- `rejected_baseline_saturated`
- `blocked_pending_canonical_readback`
- `blocked_missing_candidate_free_surface_spec`

## Observable State

The only allowed observed input is a frozen surface specification pack containing:

- target definition;
- state schema;
- observation schema;
- legal action/query schema;
- fixed action/query budget;
- metric definition and equivalence band;
- generator provenance;
- train/validation/heldout/test seed policy, if applicable;
- source pins and readback paths;
- declared legal channels;
- declared illegal channels;
- negative-evidence pointers;
- baseline panel registry mapping each baseline to callable producer requirements.

The preflight must not observe candidate outputs because no candidate may exist.

## Action / Query Budget

The preflight must record a fixed budget before running any candidate-free probes.

Budget rules:

- no candidate calls;
- no hidden answer-key access for fair baselines;
- no post-hoc threshold or metric tuning;
- query/action budget must be equal for all fair active/query baselines;
- exhaustive legal query is allowed only as a challenger and must block if it saturates;
- if budget cannot be fixed before execution, verdict is `blocked_pending_canonical_readback`.

## Candidate-Forbidden Condition

Candidate code, candidate outputs, candidate-authored ground truth, mechanism-specific oracle functions, and any candidate implementation path are forbidden.

Stop immediately if a candidate is required to define the target, generate the data, author truth, compute the metric, or supply the oracle.

## Hypothesis

A Gate1 replacement surface is admissible for later candidate-card drafting only if candidate-free baselines and leakage controls show that the target is neither trivially decodable, metric-degenerate, fair-baseline saturated, graph-cache equivalent, lookup equivalent, nor blocked by canonical readback.

## Strongest Baseline

The strongest baseline explanation is that any apparent Gate1 replacement signal is reproduced by a graph/cache/lookup/replay/control family or by a degenerate metric, not by a mechanism-specific effect.

## Full Baseline Panel

Required panels:

- trivial predictors: `predict_all`, `predict_none`, `constant_k_sweep`, `random`, `majority`;
- passive baselines: `observation_only`, `value_decoder_mean`, `value_decoder_variance`, `value_decoder_correlation`, `value_decoder_pca`, `nearest_neighbor_passive`;
- active/query baselines when actions or queries exist: `exhaustive_legal_query`, `greedy_uncertainty_query_under_budget`;
- graph-cache challengers: `graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`;
- lookup imitation: `trace_only_replay`, `ngram_trace_lookup`, `full_bundle_decoder`, `serialized_state_decoder`, `belief_table`, `pair_count_table`;
- direct objective optimizer when applicable: `discounted_wls`, `least_squares`, `convex_solver`;
- amortized learner when adaptation/learning is claimed: a real fitted `trained_legal_channel_learner`, not a deterministic stub;
- task-specific classical baseline: strongest known classical method for the task type.

If any applicable panel member is missing, uninvoked, not independent, or weaker than a known fair challenger, the preflight cannot emit an admissibility verdict.

## Baseline-Immunity Standard Reference

The preflight must apply `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` as a static normative contract.

It must not treat the standard or registry as an executor. It must record whether each registry class is applicable, invoked, and consumed by final verdict derivation.

## Provenance Verifier Use

The local verifier may be used only as a provenance-shape prefilter after the future task emits an evidence bundle.

Allowed interpretation: `provenance_wellformed_only` means the bundle shape and internal cross-references are well-formed.

Forbidden interpretation: any verifier output as Gate pass, admission, baseline-immunity, replay validation, source validation, strongest-baseline validation, candidate success, or mechanism validity.

## Leakage Positive Controls

The task must include a leakage scanner with at least one positive control on the same admission path.

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

A positive control must be fail-able: injecting the leak must flip the corresponding gate to blocked. A scanner that always passes or always detects a hard-coded fixture is invalid.

## Replay Recalculation Requirement

Replay must recompute behavior from serialized state plus observation. Hash-only replay, stored-output replay, or natural-language trace comparison is insufficient.

If replay is not applicable to the proposed surface, the task must state why and cannot use replay language as evidence.

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

## Computed-Evidence Gate

Every score, baseline result, leakage result, replay result, and verdict must derive from callable computation paths.

Each row must record:

- producer_function;
- input artifacts;
- run_id;
- seed/context/episode IDs where applicable;
- aggregation rule;
- code_path_hash;
- consumed_by_final_verdict.

Literal verdicts, static score dictionaries, unconsumed controls, and tests that only assert pass are forbidden.

## Acceptance Gate

Accept only if all are true:

- target variable is clear and candidate-free;
- observable channel is legal and fixed;
- action/query budget is fixed before execution;
- full applicable baseline panel is invoked and consumed;
- all six graph-cache challengers are invoked when representational or environment claims are present;
- lookup imitation panel is invoked when replay/memory claims are present;
- direct objective optimizer is invoked when the objective admits one;
- leakage scanner has fail-able positive controls;
- replay recomputes where replay is claimed;
- source-pin/readback provenance is fail-closed;
- evidence bundle is verifier-compatible, with verifier used as prefilter only;
- no old Gate1 positive inheritance is reused;
- no candidate, Gate run, Route C run, runtime path, or admission path is added.

## Stop Condition

Stop with a blocking verdict if:

- candidate code or candidate output is needed;
- the surface spec is missing or mutable after execution starts;
- target, observable channel, or budget cannot be defined pre-run;
- any metric degeneracy trigger from the baseline-immunity standard fires;
- any fair baseline ties or beats the proposed admissibility target;
- any graph-cache challenger is omitted or saturates;
- any leakage positive control is absent, not detected, or not consumed;
- replay is hash-only or not recomputed;
- source readback conflicts and does not fail closed;
- verifier output is treated as admission;
- the baseline-immunity standard is treated as an executor;
- any Gate1/Gate4/Gate5, Route C, bridge, admission, runtime, EGO, UI, LLM, AIRI, deployment, or companion path is touched.

## Rollback Plan

Remove only artifacts and files created by the future preflight task under its explicit allowed paths. Do not modify old Gate1, Gate2, Gate3, integrated, Gate4, Route C, bridge, admission, runtime, or EGO artifacts.

## Expected Changed Files For A Future Implementation Task

This draft does not authorize implementation. A future implementation card must name its exact paths before any coding.

Candidate future paths, if separately authorized:

- `docs/codex/tasks/GATE1-REPLACEMENT-PREFLIGHT-00XA.md`
- `artifacts/gate1_replacement_preflight_00xa/`
- optionally, isolated preflight-only source/test paths named by a later audited implementation card

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
- EGO mainline, UI, LLM, AIRI, deployment, companion, product, relationship-learning, emotion, or proactive behavior files;
- commit, push, tag, or remote-anchor.

## Claim Ceiling

Candidate-free Gate1 replacement preflight only. No Gate pass, no Gate1 replacement success, no candidate success, no mechanism validity, no baseline-immunity enforcement, no Route C viability, no Gate4/Gate5 readiness, no mainline/runtime/live effect, no agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Next Minimal Closed-Loop Action

Send this draft to Claude or equivalent hostile audit before any Codex implementation. Do not implement it from this draft alone.
