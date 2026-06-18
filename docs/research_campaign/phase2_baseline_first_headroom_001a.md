# Phase 2 Baseline-First Headroom 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2-BASELINE-FIRST-HEADROOM-001A`

Harness card id: `BASELINE-FIRST-HARNESS-001A`

## Purpose

Open Phase 2 of the research campaign by defining the bounded executable task
card for a candidate-free baseline-first headroom harness.

This task card authorizes only a future candidate-free oracle/baseline harness
against the frozen `MINIMAL-ENV-SPEC-001A` environment contract after
start-state validation. It does not itself run the baseline battery, generate
oracle scores, implement candidates, validate mechanism evidence, or complete
the program goal.

## Current Layer

`engineering_implementation + mechanism_hypothesis_governance`

This is not a subjectivity-validation task and not a philosophical
consciousness task.

## Bounded Audit Before Implementation

Real objective: measure whether a frozen candidate-free surface has enough
headroom over fair cheap baselines to justify later candidate mechanism search.

Problem-definition risk: a "Phase 2" label could be misread as permission to
start candidate work or route tournaments. It is not. This card only opens a
candidate-free baseline/oracle harness task.

Strongest baseline explanation: exhaustive legal query, graph-cache challengers,
lookup imitation, passive decoders, degenerate predictors, or serialized-state
decoders may saturate the visible-channel oracle under the same budget.

Strongest invalidating reason: if the frozen environment spec is stale, mutated,
or not hash-matched, any harness result would be ungrounded. If the strongest
fair baseline reaches the visible-channel oracle inside the equivalence band,
the correct result is no-headroom negative evidence, not candidate rescue.

Falsifier for the current framing: any candidate implementation, route
tournament, threshold tuning, post-score budget edit, or baseline weakening
before candidate-free headroom is measured invalidates this phase.

Insufficient evidence: JSON parse success, a task card, green local validation,
or a reviewer `success_reached` on this card does not establish baseline
headroom. Headroom exists only after callable oracle and baseline producers run
under the same frozen budget and input boundary.

Mechanism-vs-behavior classification: Phase 2 tests candidate-free surface
discriminability and baseline headroom. It does not test a candidate mechanism.

Hard-coding / leakage / weak-baseline checks:

- no static verdict dictionaries;
- no hand-written scores;
- no candidate-authored truth;
- no hidden labels in observation names, action names, filenames, fixture names,
  artifact layout, source paths, or metadata;
- no second logic path for tests;
- no replay by stored hashes or stored outputs only;
- no omitted graph-cache, lookup, passive, exhaustive-query, or degenerate
  challengers;
- no unused frozen seeds, heldout contexts, train contexts, or counterfactual
  pairs.

## Prior Evidence And Source Pins

This card inherits these boundaries as challenge families, not as positive
mechanism proof:

- `docs/research/MINIMAL-ENV-SPEC-001A.md`
- `docs/research/MINIMAL-ENV-SPEC-001A.freeze.json`
- `artifacts/minimal_env_spec_001a/source_readback.json`
- `artifacts/minimal_env_spec_001a/environment_schema.json`
- `artifacts/minimal_env_spec_001a/validation_report.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-RUN-001A-HOSTILE-AUDIT-001A/audit_result.json`
- `artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-RUN-001A-HOSTILE-AUDIT-001A/audit_report.md`

Required frozen spec readback before future execution:

```text
spec_path = docs/research/MINIMAL-ENV-SPEC-001A.md
spec_sha256 = bf48145b165c5c847cecd7ecda6c2a78818ce326c44f5ad92be391d003daf658
freeze_status = frozen_before_any_baseline_or_oracle_scores
next_harness_may_mutate_spec = false
```

## Problem Definition

Phase 1 formalized broad functional-subject target terms into bounded proxy
families. Phase 2 must now decide whether the first frozen candidate-free
surface has measurable headroom over fair baselines before any candidate
mechanism search.

The task is to implement and run a candidate-free harness that computes visible
oracle, diagnostic oracle, passive, degenerate, size-only, exhaustive legal
query, graph-cache, lookup-imitation, and applicable classical baseline scores
under the same budget and input boundary.

## Mainline Target

None. This phase is offline research-campaign evidence preparation only.

No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, product,
or companion path is targeted.

## Enabled-State Requirement

This task card enables only future local candidate-free harness implementation
inside the expected paths below. It does not enable:

- candidate mechanism implementation;
- Phase 3 mechanism search;
- route tournament;
- Gate execution;
- runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, push,
  tag, or remote anchor.

## Real-Trigger Evidence Requirement

Before future execution, Codex must read and record:

- repo root, branch, HEAD, upstream/ahead-behind, and
  `git status --short --branch -uall`;
- this task card;
- `docs/research_campaign/plan.md`;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- tail of `artifacts/research_campaign/experiment_log.jsonl`;
- Phase 1 audit success artifact;
- `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- `docs/research/MINIMAL-ENV-SPEC-001A.freeze.json`;
- `artifacts/minimal_env_spec_001a/source_readback.json`;
- relevant prior baseline-saturation and graph-cache negative evidence.

## Hypothesis

If the frozen minimal environment has discriminative headroom, then a
candidate-free harness should measure:

```text
battery_max_fair_baseline < visible_channel_oracle - equivalence_band
```

under the same budget and input boundary, while passive, degenerate, size-only,
exhaustive legal query, and graph-cache challengers remain outside the oracle
equivalence band.

## Strongest Baseline

The strongest fair baseline is defined as:

```text
max(all applicable callable baseline battery members)
```

Required families:

- random / majority / constant predictors;
- observation-only and passive decoder family;
- nearest-neighbor and episodic replay;
- lookup / transition table / graph-cache family;
- graph lookup;
- transition table;
- successor map;
- count table;
- FSM planner;
- episodic traversal;
- exhaustive legal query under the same budget;
- trace-only replay / n-gram trace lookup;
- full-bundle decoder and serialized-state decoder only as diagnostic
  collapse checks, not admissible support;
- strongest known classical method applicable to the frozen task type.

## Baseline Requirement

Future execution must run the baseline battery before any candidate mechanism
work. Every baseline result must record:

- `producer_function`;
- input artifacts;
- run id;
- seed/context/episode ids;
- aggregation rule;
- code path hash or source file digest;
- whether the result is consumed by the final verdict.

Any baseline omitted, uninvoked, unconsumed, or not independent blocks the
headroom claim.

## Ablation Requirement

This Phase 2 card is candidate-free, so no candidate mechanism ablation is run.
The future harness must still include fail-able controls:

- remove or corrupt legal observation fields;
- remove legal query budget;
- force strongest fair baseline to equal the visible oracle;
- inject a leakage positive control;
- tamper replay state;
- omit source/generator provenance.

Each control must be callable and consumed by the final verdict.

## Trace / Replay Requirement

Replay must recompute behavior or scores from:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Hash equality, stored output equality, stored verdict equality, and
self-reported provenance are insufficient. At least one replay tamper negative
control is required.

## Leakage Requirement

The future harness must include a scanner with positive controls over:

- observation names;
- action names;
- filenames;
- fixture names;
- artifact structure;
- baseline hints;
- planted answer maps;
- value-level fields;
- label ordering;
- generator metadata;
- source-pin paths.

The scanner must detect an injected leak, record the detection id, clear after
leak removal, and block the final verdict when leakage remains.

## Computed-Evidence Provenance Gate

All verdict-bearing values must come from callable producers. The final result
must derive from consumed producer outputs, not literals or static report text.

Required provenance rows:

- generator/source provenance;
- visible-channel oracle invocation;
- answer-key diagnostic oracle invocation;
- every baseline invocation;
- every leakage scan and positive control;
- every replay recomputation and tamper control;
- final verdict derivation.

## Acceptance Gate

Future Phase 2 execution may report `headroom_present` only if all are true:

- frozen spec hash matches
  `bf48145b165c5c847cecd7ecda6c2a78818ce326c44f5ad92be391d003daf658`;
- visible-channel oracle macro F1 is at least `0.90`;
- passive family max is below `0.87`;
- degenerate predictor max is below `0.87`;
- size-only sweep max is below `0.87`;
- strongest fair baseline is below `visible_channel_oracle - 0.03`;
- exhaustive legal query is below `visible_channel_oracle - 0.03`;
- every graph-cache challenger is below `visible_channel_oracle - 0.03`;
- leakage positive controls pass and no unresolved leak remains;
- replay recomputes from serialized state plus observation and legal context;
- generator/source provenance is complete and consumed;
- JSON/JSONL artifacts parse;
- no source/test/runtime path outside this task card's allowed scope is touched.

If any cheap/fair baseline reaches the oracle equivalence band, the required
verdict is `no_headroom_baseline_saturated` or equivalent negative evidence,
and the campaign must reframe before candidate search.

## Claim Ceiling

This card proves only that Phase 2 has been opened with a bounded
candidate-free baseline-first headroom task card.

Future execution can prove only measured headroom or no-headroom for the frozen
surface. It cannot prove mechanism validity, self-awareness, subjective
experience, real emotion, autonomy, agency success, EGO readiness, companion
readiness, runtime readiness, user benefit, or mainline effect.

## Stop Conditions

Stop and record a blocker if:

- frozen spec hash does not match the freeze metadata;
- `MINIMAL-ENV-SPEC-001A` is mutated, normalized, amended, or refrozen;
- Phase 2 execution starts before this card and start-state validation are
  recorded;
- a candidate mechanism, route tournament, Gate, runtime, EGO mainline, UI,
  LLM, AIRI, external service, deployment, push, tag, or remote anchor is
  attempted;
- baseline, oracle, leakage, replay, or provenance results are static,
  handwritten, unconsumed, or not produced by callable code;
- strongest fair baseline is hand-picked instead of max over the full battery;
- any graph-cache challenger is omitted;
- leakage positive control is absent;
- replay is hash-only or stored-output-only;
- unused frozen seed, train context, heldout context, or counterfactual pair is
  present;
- no-headroom is found and candidate work is still proposed.

## Rollback Plan

Rollback this card-opening task only by reverting:

- `docs/research_campaign/phase2_baseline_first_headroom_001a.md`;
- the Phase 2 task-card section in `docs/research_campaign/plan.md`;
- the Phase 2 checkpoint in `docs/OVERALL_PROGRESS.md`;
- the matching append-only ledger entry only if rollback is explicitly
  authorized and the rollback itself is recorded;
- the Phase 2 pointer in `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/phase2_baseline_first_headroom_task_card_validation_001a.json`.

Do not delete or rewrite Phase 0, Phase 1, `MINIMAL-ENV-SPEC-001A`, 00XA,
Route C, graph-cache, or other historical negative evidence artifacts.

## Expected Changed Files For This Card Opening

- `docs/research_campaign/phase2_baseline_first_headroom_001a.md`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/phase2_baseline_first_headroom_task_card_validation_001a.json`

## Future Allowed Execution Paths

Future Phase 2 execution, if performed after start-state validation, is limited
to:

- `src/baseline_first_harness_001a/`
- `tests/baseline_first_harness_001a/`
- `artifacts/baseline_first_harness_001a/`
- `artifacts/research_campaign/phase2_baseline_first_headroom_001a.json`
- `artifacts/research_campaign/phase2_baseline_first_headroom_audit_001a.json`
- campaign bookkeeping files listed above.

## Forbidden Changes

- No candidate mechanism implementation.
- No Phase 3 mechanism search.
- No route tournament.
- No formal Gate execution.
- No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, push,
  tag, or remote anchor.
- No mutation, normalization, amendment, or refreeze of
  `docs/research/MINIMAL-ENV-SPEC-001A.md`.
- No rewrite of prior failed artifacts into passes.
- No threshold or budget tuning after seeing scores.
- No claim of consciousness, subjective experience, real emotion, autonomy,
  EGO readiness, companion readiness, mechanism validity, or mainline effect.

## Auto-Remote-Anchor

`forbidden`

## Immediate Next Action After This Card

Run focused start-state validation for this task card:

- JSON/JSONL parse checks;
- frozen spec hash readback;
- plan/progress/scorecard/ledger agreement;
- no Phase 2 baseline battery executed;
- no `src/`, `tests/`, runtime, Gate, EGO mainline, push, tag, or remote anchor
  touched by this card-opening step.

Only after that validation passes may a future implementation step begin the
candidate-free baseline-first harness.
