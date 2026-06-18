# Phase2B Candidate-Free Headroom Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HEADROOM-001A`

Source task id: `RESEARCH-CAMPAIGN-PHASE2B-MINIMAL-ENV-REFRAME-SPEC-001A`

Source spec draft:
`docs/research/phase2b_minimal_env_reframe_spec_001a.md`

Status: task card opened pending focused validation.

Auto-Remote-Anchor: forbidden.

## Problem Definition

Audited Phase 2 evidence showed `MINIMAL-ENV-SPEC-001A` had no measured
headroom. The visible-channel oracle macro F1 was `1.0`, and the strongest fair
baseline, `count_table`, also reached macro F1 `1.0` inside the `0.03`
equivalence band. That surface is preserved as no-headroom negative evidence.

The Phase2B environment-reframe spec is now validated and read-only reviewer
audited as a candidate-free spec draft. It is not an executable result and does
not measure headroom. The next bounded task must freeze/read back the Phase2B
spec surface and run a candidate-free baseline-first headroom harness before
any candidate mechanism or Phase 3 work.

## Bounded Audit

Layer: engineering implementation + mechanism-hypothesis governance.

Real objective: define the execution card for a future candidate-free
headroom measurement on the Phase2B surface without running it in this
card-opening checkpoint.

Strongest baseline explanation: any measured success may still collapse into a
lookup/count-table/graph-cache/exhaustive-query/full-bundle/serialized-state
decoder shortcut if the legal interaction boundary leaks action-aligned answer
structure.

Strongest invalidating reason: if the Phase2B surface can be solved by a fair
baseline under the same budget, no candidate mechanism search is justified.

Falsifier for current framing: strongest fair baseline reaches
`visible_channel_oracle - equivalence_band`, or any candidate-visible field,
legal response, path, fixture name, or serialized-state field exposes target
labels, final-action scores, answer maps, full legal response bundles, or
semantic action-label leaks.

Insufficient evidence: task-card creation, JSON parse success, reviewer praise,
one green test, oracle score without full fair-baseline battery, replay by hash
comparison only, leakage scan without positive controls, or provenance that is
not consumed by the final verdict.

Mechanism-vs-resemblance classification: this task tests only candidate-free
surface headroom. It does not test a candidate mechanism and does not produce
mechanism evidence.

Anti-hardcoding audit: the future harness must not replace the control problem
with if/else label lookup, hide a classifier behind mathematical language,
encode the answer in fixture names/action names/path names, tune thresholds
after seeing scores, add a test-only logic path, change schema to erase failure,
or use renderer-visible behavior as causal evidence.

Minimal validation for this card-opening checkpoint: local parse/readback checks
must prove this card exists, references the audited Phase2B spec, preserves
Phase 2 no-headroom evidence, keeps execution and candidate work unauthorized,
and records the next frontier as read-only reviewer audit before execution.

Stop condition for this checkpoint: stop if any `src/`, `tests/`, executable
harness, baseline run, oracle score, candidate mechanism, Phase 3 search,
route tournament, runtime/EGO mainline path, push, tag, or remote anchor is
touched or authorized by current bookkeeping.

Rollback plan: revert only this task card, its validation artifact, and matching
plan/progress/scorecard/ledger entries. Do not delete or rewrite Phase 0,
Phase 1, Phase 2, no-headroom, reframing, Phase2B spec, validation, or audit
artifacts.

Acceptance signal for this card-opening checkpoint: focused validation passes
and the campaign state records
`phase2b_candidate_free_headroom_task_card_validated_pending_reviewer_audit`.

## Current Stage

This is a task-card-opening checkpoint for a future executable
candidate-free headroom measurement. It does not execute Phase2B.

## Mainline Target

None. No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, or
product path is targeted.

## Enabled-State Requirement

Only task-card drafting, campaign bookkeeping, and focused local validation are
enabled in this checkpoint.

Future execution is still disabled until this card-opening state is validated
and a read-only reviewer audit reaches `success_reached`.

Candidate mechanisms, Phase 3, route tournament, Gate execution, runtime/EGO
mainline, UI, LLM, AIRI, external services, deployment, push, tag, and remote
anchor remain disabled.

## Real-Trigger Evidence Requirement

The card-opening validation must read back:

- current repo root, branch, HEAD, and worktree status;
- Phase 2 audited no-headroom result;
- Phase 2 no-headroom negative-evidence artifact;
- Phase2B spec draft;
- Phase2B validation artifact;
- Phase2B read-only reviewer audit artifact;
- current `plan.md`, `OVERALL_PROGRESS.md`, `stage_scorecard.json`, and
  `experiment_log.jsonl`;
- SHA256 for `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- SHA256 for `docs/research/phase2b_minimal_env_reframe_spec_001a.md`.

## Hypothesis

If the Phase2B candidate-free environment surface is frozen and measured with a
full fair-baseline battery under the same budget, the campaign can make a
computed headroom/no-headroom decision before any candidate mechanism work.

## Strongest Baseline

The strongest fair baseline is the maximum over every applicable callable
baseline under the same budget and input boundary, including:

- random, majority, and constant predictors;
- passive observation-only attacker;
- nearest-neighbor passive attacker;
- supervised passive attacker;
- count table;
- graph lookup;
- transition table;
- successor map;
- FSM planner;
- episodic traversal;
- exhaustive legal query under the same budget;
- greedy uncertainty query under the same budget;
- trace-only replay;
- n-gram trace lookup;
- full-bundle decoder positive/negative boundary;
- serialized-state decoder;
- strongest known classical method for the generated task type.

If any fair baseline reaches `visible_channel_oracle - equivalence_band`,
candidate search remains blocked and the result must be recorded as no-headroom
negative evidence.

## Ablation Requirement

Future execution must include callable ablations or controls that rerun the
episode pipeline under real interventions for:

- legal-query removal or corruption;
- answer-map injection;
- final-action-score injection;
- semantic action-label leakage;
- full legal response bundle injection;
- source-path target leak injection;
- source-provenance omission;
- replay tamper;
- strongest-baseline equality;
- passive observation shortcut;
- full-bundle decoder shortcut;
- serialized-state decoder shortcut.

Each detected control must be consumed by the final verdict.

## Trace / Replay Requirement

Future replay must recompute from:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Replay that compares only stored hashes, stored verdicts, or self-reported
provenance is invalid.

## Computed-Evidence Provenance Gate

Future execution must record, and final verdict aggregation must consume:

- producer functions or commands;
- input artifacts;
- run id;
- seed/context/episode ids;
- aggregation rule;
- source file digests or code path hashes;
- generated artifact paths;
- leakage positive-control ids;
- replay tamper-control ids;
- ablation/control ids;
- `consumed_by_final_verdict` flags.

Static verdict dictionaries, handwritten scores, unconditional clean reports,
and tests that only assert pass are forbidden.

## Future Execution Surface

This card-opening checkpoint does not authorize file edits outside campaign
bookkeeping. If a later audited start-state explicitly authorizes execution, the
intended isolated future write paths are:

- `docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json`
- `src/phase2b_candidate_free_headroom_001a/`
- `tests/phase2b_candidate_free_headroom_001a/`
- `artifacts/phase2b_candidate_free_headroom_001a/`
- `artifacts/research_campaign/phase2b_candidate_free_headroom_001a.json`
- `artifacts/research_campaign/phase2b_candidate_free_headroom_audit_001a.json`

No such future execution path may be touched in this card-opening checkpoint.

## Acceptance Gate For This Checkpoint

- this task card exists;
- it references the audited Phase2B spec draft;
- it preserves the Phase 2 `no_headroom_baseline_saturated` result;
- it requires a future spec freeze/readback before harness execution;
- it requires candidate-free baseline-first headroom measurement before
  candidate work;
- it requires strongest fair baseline as max over the full callable battery;
- it requires leakage positive controls, replay recomputation, ablations, and
  computed provenance consumed by the final verdict;
- `phase2b_execution_authorized = false`;
- `candidate_mechanism_run = false`;
- `phase3_opened = false`;
- plan/progress/scorecard/ledger agree on task-card opening or validation
  state;
- no `src/`, `tests/`, harness output, candidate, runtime/EGO mainline, push,
  tag, or remote anchor is touched.

## Claim Ceiling

Phase2B candidate-free headroom task-card opening only. No Phase2B execution,
new headroom measurement, mechanism validity, subjective experience,
consciousness, real emotion, autonomy, agency success, EGO readiness,
companion readiness, or mainline-effect claim.

## Stop Conditions

Stop if:

- Phase2B execution, oracle scoring, baseline execution, candidate search,
  Phase 3, route tournament, Gate, runtime/EGO mainline, UI, LLM, AIRI,
  external service, deployment, push, tag, commit, or remote anchor is attempted
  in this checkpoint;
- `MINIMAL-ENV-SPEC-001A` is edited or refrozen;
- `docs/research/phase2b_minimal_env_reframe_spec_001a.md` is edited after its
  read-only audit without a new spec-revision card;
- the task card weakens known saturation baselines;
- no-headroom negative evidence is rewritten as positive mechanism evidence;
- the future harness is allowed to expose target labels, final-action scores,
  answer maps, full legal response bundles, semantic action-label leaks, source
  path target leaks, or fixture-name target leaks.

## Expected Changed Files For This Checkpoint

- `docs/research_campaign/phase2b_candidate_free_headroom_task_card_001a.md`
- `artifacts/research_campaign/phase2b_candidate_free_headroom_task_card_validation_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes For This Checkpoint

- No `src/` or `tests/` changes.
- No Phase2B execution.
- No spec freeze file creation.
- No oracle score, baseline score, ablation score, replay score, or leakage
  score generation.
- No candidate mechanism, Phase 3, route tournament, Gate, runtime/EGO
  mainline, UI, LLM, AIRI, external service, deployment, push, tag, commit, or
  remote anchor.
- No mutation or refreeze of `docs/research/MINIMAL-ENV-SPEC-001A.md`.
- No mutation of `docs/research/phase2b_minimal_env_reframe_spec_001a.md`.

## Auto-Remote-Anchor

`forbidden`

## Next Minimal Closed-Loop Action

Run focused local validation of this task-card-opening checkpoint. If it passes,
record validation and keep the next frontier at read-only reviewer audit before
any Phase2B execution.
