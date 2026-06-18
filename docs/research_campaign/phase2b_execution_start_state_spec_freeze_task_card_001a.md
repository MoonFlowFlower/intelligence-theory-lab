# Phase2B Execution Start-State / Spec-Freeze Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2B-EXECUTION-START-STATE-SPEC-FREEZE-001A`

Source task id: `RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HEADROOM-001A`

Source task card:
`docs/research_campaign/phase2b_candidate_free_headroom_task_card_001a.md`

Source spec draft:
`docs/research/phase2b_minimal_env_reframe_spec_001a.md`

Status: focused validation passed; read-only reviewer re-audit returned
`success_reached` after preserved stale-status repairs.

Auto-Remote-Anchor: forbidden.

## Problem Definition

The Phase2B candidate-free headroom task card has been locally validated and
read-only reviewer audited with `success_reached`. It defines a future
candidate-free baseline-first headroom measurement, but no Phase2B execution,
spec freeze, oracle score, baseline score, replay score, ablation score,
leakage score, or candidate mechanism has been run.

Before any future executable harness can be implemented or run, the campaign
must freeze the Phase2B environment spec, read back its source hashes and
authorized execution boundary, and validate the start state. This card opens
that future start-state/spec-freeze checkpoint. This card-opening step does not
create the freeze file and does not execute Phase2B.

## Bounded Audit

Layer: engineering implementation + mechanism-hypothesis governance.

Real objective: define a bounded future checkpoint for freezing and validating
the Phase2B spec start state before any candidate-free harness execution.

Strongest baseline explanation: a premature freeze can look like execution
readiness while still allowing lookup, graph-cache, exhaustive legal query,
full-bundle decoder, serialized-state decoder, path-name leak, fixture-name
leak, or semantic action-label shortcuts.

Strongest invalidating reason: if the start-state/spec-freeze checkpoint
freezes a spec that still exposes candidate-visible target labels,
final-action scores, answer maps, full legal response bundles, semantic
action-label leaks, source-path target leaks, or fixture-name target leaks, the
future harness would be invalid before measurement begins.

Falsifier for current framing: this card or its bookkeeping authorizes harness
implementation, oracle scoring, baseline scoring, candidate work, Phase 3,
runtime/EGO mainline work, push, tag, remote anchor, or mutation of the audited
Phase2B spec without a separate spec-revision task card.

Insufficient evidence: task-card creation, JSON parse success, a freeze hash
without source readback, a reviewer verdict not recorded in artifacts, or any
claim that a frozen spec alone proves headroom or mechanism validity.

Mechanism-vs-resemblance classification: this checkpoint is source-freeze and
start-state governance only. It does not test behavior, headroom, mechanism
evidence, learning, agency, or subjectivity.

Anti-hardcoding audit: the future start-state validation must explicitly check
for target-label fields, final-action-score fields, answer-map aliases, full
legal response bundles, semantic action-label leaks, fixture/path leaks,
unused frozen seeds, and any hidden test-only logic path before execution is
enabled.

Minimal validation for this card-opening checkpoint: local readback must prove
this card exists, references the audited candidate-free headroom task card and
Phase2B spec draft, keeps execution/spec-freeze unauthorized in this step, and
records the next frontier as read-only reviewer audit before any start-state
freeze is performed.

Stop condition for this checkpoint: stop if any freeze file, `src/`, `tests/`,
runtime/EGO mainline path, oracle score, baseline score, replay score, ablation
score, leakage score, candidate mechanism, Phase 3 search, route tournament,
push, tag, or remote anchor is created or authorized.

Rollback plan: revert only this task card, its validation artifact, and matching
plan/progress/scorecard/ledger entries. Do not delete or rewrite Phase 0,
Phase 1, Phase 2, no-headroom, reframing, Phase2B spec, validation, or audit
artifacts.

Acceptance signal for this card-opening checkpoint: focused validation passes
and the campaign state records
`phase2b_execution_start_state_spec_freeze_task_card_validated_pending_reviewer_audit`.

## Current Stage

This is a task-card-opening checkpoint for a future Phase2B start-state/spec
freeze. It does not freeze the spec and does not execute Phase2B.

## Mainline Target

None. No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, or
product path is targeted.

## Enabled-State Requirement

Only task-card drafting, campaign bookkeeping, and focused local validation are
enabled in this checkpoint.

Future spec freeze and start-state validation remain disabled until this card
opening is locally validated and a read-only reviewer audit reaches
`success_reached`.

Phase2B harness implementation, oracle scoring, baseline scoring, replay
scoring, ablation scoring, leakage scoring, candidate mechanisms, Phase 3,
route tournament, Gate execution, runtime/EGO mainline, UI, LLM, AIRI, external
services, deployment, push, tag, and remote anchor remain disabled.

## Real-Trigger Evidence Requirement

The card-opening validation must read back:

- current repo root, branch, HEAD, and worktree status;
- Phase 2 audited no-headroom result;
- Phase 2 no-headroom negative-evidence artifact;
- Phase2B spec draft;
- Phase2B spec validation and read-only audit artifacts;
- Phase2B candidate-free headroom task card validation and read-only audit
  artifacts;
- current `plan.md`, `OVERALL_PROGRESS.md`, `stage_scorecard.json`, and
  `experiment_log.jsonl`;
- SHA256 for `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- SHA256 for `docs/research/phase2b_minimal_env_reframe_spec_001a.md`.

## Hypothesis

A separate start-state/spec-freeze checkpoint can prevent the campaign from
collapsing task-card audit success into execution readiness, while preserving
the route to a later candidate-free baseline-first harness.

## Strongest Baseline

The strongest false route is start-state theater: a spec is frozen and then
treated as if headroom has been measured. The future freeze checkpoint must
therefore preserve:

- strongest fair baseline as `max(all applicable callable baselines)`;
- graph lookup, transition table, successor map, FSM planner, episodic
  traversal, count table, exhaustive legal query, full-bundle decoder,
  serialized-state decoder, passive attackers, and trace-only replay baselines;
- equal budget and input boundary for oracle and all fair baselines;
- no candidate mechanism before measured headroom exists.

## Ablation Requirement

This card-opening checkpoint runs no ablations. The future start-state/spec
freeze checkpoint must preserve the ablation requirements already defined in
`RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HEADROOM-001A` and must not weaken
any control family.

## Trace / Replay Requirement

This card-opening checkpoint runs no replay. The future start-state/spec freeze
checkpoint must preserve the replay requirement:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Hash-only, stored-output, or self-reported replay remains invalid.

## Computed-Evidence Provenance Gate

This card-opening checkpoint must record source hashes in its validation
artifact. The future start-state/spec-freeze checkpoint must record:

- source spec path and SHA256;
- freeze manifest path and SHA256;
- producer function or command for the freeze/readback;
- input artifacts;
- run id;
- aggregation rule for start-state validation;
- source file digests or code path hashes for validators;
- consumed-by-final-verdict flags for validation checks.

Static verdict dictionaries, handwritten clean reports, unconditional pass
reports, and tests that only assert pass are forbidden.

## Future Start-State / Freeze Surface

This card-opening checkpoint does not authorize creating any future execution
file. If a later audited start-state task explicitly authorizes freeze/readback,
the intended isolated future write paths are:

- `docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json`
- `artifacts/research_campaign/phase2b_execution_start_state_spec_freeze_001a.json`
- `artifacts/research_campaign/phase2b_execution_start_state_spec_freeze_validation_001a.json`
- `artifacts/research_campaign/phase2b_execution_start_state_spec_freeze_audit_001a.json`

No such future freeze/readback path may be touched in this card-opening
checkpoint.

## Acceptance Gate For This Checkpoint

- this task card exists;
- it references the audited Phase2B candidate-free headroom task card;
- it references the Phase2B spec draft;
- it preserves the Phase 2 `no_headroom_baseline_saturated` result;
- it states that no freeze file is created in this checkpoint;
- it requires future freeze/readback before harness implementation or
  execution;
- it preserves candidate-free baseline-first headroom measurement before
  candidate work;
- it preserves the full saturation-family baseline battery;
- `phase2b_spec_freeze_authorized = false`;
- `phase2b_execution_authorized = false`;
- `candidate_mechanism_run = false`;
- `phase3_opened = false`;
- plan/progress/scorecard/ledger agree on task-card opening or validation
  state;
- no `src/`, `tests/`, freeze file, harness output, candidate, runtime/EGO
  mainline, push, tag, or remote anchor is touched.

## Claim Ceiling

Phase2B execution start-state/spec-freeze task-card opening only. No spec
freeze, Phase2B execution, new headroom measurement, mechanism validity,
subjective experience, consciousness, real emotion, autonomy, agency success,
EGO readiness, companion readiness, or mainline-effect claim.

## Stop Conditions

Stop if:

- a freeze file is created in this checkpoint;
- Phase2B execution, oracle scoring, baseline execution, replay scoring,
  ablation scoring, leakage scoring, candidate search, Phase 3, route
  tournament, Gate, runtime/EGO mainline, UI, LLM, AIRI, external service,
  deployment, push, tag, commit, or remote anchor is attempted in this
  checkpoint;
- `MINIMAL-ENV-SPEC-001A` is edited or refrozen;
- `docs/research/phase2b_minimal_env_reframe_spec_001a.md` is edited without a
  separate spec-revision task card;
- known saturation baselines are weakened;
- no-headroom negative evidence is rewritten as positive mechanism evidence.

## Expected Changed Files For This Checkpoint

- `docs/research_campaign/phase2b_execution_start_state_spec_freeze_task_card_001a.md`
- `artifacts/research_campaign/phase2b_execution_start_state_spec_freeze_task_card_validation_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes For This Checkpoint

- No `src/` or `tests/` changes.
- No spec freeze file creation.
- No Phase2B execution.
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
any Phase2B start-state/spec-freeze task is executed.
