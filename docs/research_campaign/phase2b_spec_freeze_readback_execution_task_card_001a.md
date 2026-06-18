# Phase2B Spec-Freeze / Readback Execution Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2B-SPEC-FREEZE-READBACK-EXECUTION-001A`

Source task id:
`RESEARCH-CAMPAIGN-PHASE2B-START-STATE-SPEC-FREEZE-READBACK-001A`

Source task card:
`docs/research_campaign/phase2b_start_state_spec_freeze_readback_task_card_001a.md`

Source spec draft:
`docs/research/phase2b_minimal_env_reframe_spec_001a.md`

Status: read-only reviewer re-audited `success_reached` after stale next-action
and claim-ceiling repair; freeze/readback execution remains unauthorized.

Auto-Remote-Anchor: forbidden.

## Problem Definition

The Phase2B start-state/spec-freeze readback task card has been locally
validated and read-only reviewer audited with `success_reached`. It established
that a separately bounded checkpoint is required before any Phase2B spec freeze
or start-state readback execution can occur.

This checkpoint opens the execution task card only. It does not create the
freeze manifest, does not create the readback artifact, does not execute
Phase2B, and does not authorize candidate mechanisms, Phase 3, route
tournaments, runtime/EGO mainline work, push, tag, or remote anchor.

## Bounded Audit

Layer: engineering implementation + mechanism-hypothesis governance.

Real objective: define the future executable surface for freezing and reading
back the Phase2B spec start state, while keeping the execution itself disabled
until this task card is locally validated and read-only reviewer audited.

Strongest baseline explanation: the campaign may confuse a freeze/readback
manifest with measured headroom or mechanism evidence. A freeze proves only
source identity and boundary readiness; it does not score oracle or baselines.

Strongest invalidating reason: if this card authorizes immediate freeze file
creation, creates a readback result, weakens saturation baselines, authorizes
Phase2B harness execution, or turns no-headroom negative evidence into a
candidate route, the checkpoint is invalid.

Falsifier for current framing: any current-state artifact shows
`phase2b_spec_freeze_authorized = true`,
`phase2b_start_state_readback_authorized = true`,
`phase2b_execution_authorized = true`, candidate work, Phase 3, route
tournament, runtime/EGO mainline work, or a freeze/readback artifact created
before this card is validated and reviewer audited.

Insufficient evidence: task-card creation, JSON parse success, stale
bookkeeping, a reviewer verdict not recorded in artifacts, a hash-only freeze
without source and validator readback, or any claim that freeze/readback alone
proves headroom or mechanism validity.

Mechanism-vs-resemblance classification: this checkpoint is task-card
governance for a future freeze/readback execution. It does not test behavior,
headroom, mechanism validity, learning, agency, subjectivity, or consciousness.

Anti-hardcoding audit: the future freeze/readback execution must prove that the
spec boundary still blocks target labels, final-action scores, answer maps,
full legal response bundles, semantic action-label leaks, fixture/path target
leaks, unused frozen seeds, and hidden test-only logic paths before any harness
implementation or measurement is enabled.

Minimal validation for this card-opening checkpoint: local readback must prove
this card exists, references the audited Phase2B start-state/spec-freeze
readback task card, preserves the audited Phase 2 no-headroom result and
Phase2B spec hash, keeps freeze/readback/execution unauthorized, records no
forbidden future paths, and updates plan/progress/scorecard/ledger
consistently.

Stop condition for this checkpoint: stop if any freeze file, readback result,
`src/`, `tests/`, harness output, oracle score, baseline score, replay score,
ablation score, leakage score, candidate mechanism, Phase 3, route tournament,
runtime/EGO mainline path, push, tag, or remote anchor is created or
authorized.

Rollback plan: revert only this task card, its validation artifact, and matching
plan/progress/scorecard/ledger entries. Do not delete or rewrite Phase 0,
Phase 1, Phase 2, no-headroom, reframing, Phase2B spec, validation, or audit
artifacts.

Acceptance signal for this card-opening checkpoint: focused validation passes,
read-only reviewer audit reaches `success_reached`, the stale source-hash
reviewer finding is preserved and repaired, and the campaign state records
`phase2b_spec_freeze_readback_execution_task_card_audited_success`.

## Current Stage

This is a task-card-opening checkpoint for a future Phase2B spec-freeze and
start-state readback execution. It does not create the freeze manifest, does
not create the readback artifact, and does not execute Phase2B.

## Mainline Target

None. No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, or
product path is targeted.

## Enabled-State Requirement

Only task-card drafting, campaign bookkeeping, focused local validation, and
read-only reviewer audit are enabled in this checkpoint.

This completed checkpoint does not enable future spec freeze, start-state
readback, or Phase2B harness work. Those remain disabled until a separate
future execution checkpoint explicitly authorizes them.

Phase2B oracle scoring, baseline scoring, replay scoring, ablation scoring,
leakage scoring, candidate mechanisms, Phase 3, route tournament, Gate
execution, runtime/EGO mainline, UI, LLM, AIRI, external services, deployment,
push, tag, and remote anchor remain disabled.

## Real-Trigger Evidence Requirement

The card-opening validation must read back:

- current repo root, branch, HEAD, upstream/ahead-behind state, and worktree
  status;
- Phase 2 audited no-headroom result;
- Phase 2 no-headroom negative-evidence artifact;
- Phase2B spec draft;
- Phase2B spec validation and read-only audit artifacts;
- Phase2B candidate-free headroom task-card validation and read-only audit
  artifacts;
- Phase2B execution start-state/spec-freeze task-card validation and read-only
  audit artifacts;
- Phase2B start-state/spec-freeze readback task-card validation and read-only
  audit artifacts;
- current `plan.md`, `OVERALL_PROGRESS.md`, `stage_scorecard.json`, and
  `experiment_log.jsonl`;
- SHA256 for `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- SHA256 for `docs/research/phase2b_minimal_env_reframe_spec_001a.md`.

## Hypothesis

A separately audited execution task card can prevent the campaign from
collapsing readback-task-card audit success into actual freeze execution, while
preserving the route to a later candidate-free baseline-first headroom
measurement.

## Strongest Baseline

The strongest false route is freeze/readback theater: a manifest, source hash,
or static clean report is treated as evidence that headroom exists. The future
execution checkpoint must therefore preserve:

- strongest fair baseline as `max(all applicable callable baselines)`;
- graph lookup, transition table, successor map, FSM planner, episodic
  traversal, count table, exhaustive legal query, full-bundle decoder,
  serialized-state decoder, passive attackers, and trace-only replay baselines;
- equal budget and input boundary for oracle and all fair baselines;
- no candidate mechanism before measured headroom exists.

## Ablation Requirement

This card-opening checkpoint runs no ablations. The future freeze/readback
execution checkpoint must preserve all ablation/control requirements already
defined in `RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HEADROOM-001A` and must
not weaken any control family.

## Trace / Replay Requirement

This card-opening checkpoint runs no replay. The future freeze/readback
execution checkpoint must preserve the replay requirement:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Hash-only, stored-output, or self-reported replay remains invalid.

## Computed-Evidence Provenance Gate

This card-opening checkpoint must record source hashes in its validation
artifact. The future freeze/readback execution checkpoint must record:

- source spec path and SHA256;
- freeze manifest path and SHA256;
- readback result path and SHA256;
- producer function or command for freeze/readback;
- input artifacts;
- run id;
- aggregation rule for start-state validation;
- source file digests or code path hashes for validators;
- generated artifact paths;
- consumed-by-final-verdict flags for validation checks.

Static verdict dictionaries, handwritten clean reports, unconditional pass
reports, and tests that only assert pass are forbidden.

## Future Freeze / Readback Execution Surface

This card-opening checkpoint does not authorize creating any future execution
file. If a later audited start-state task explicitly authorizes freeze/readback
execution, the intended isolated future write paths are:

- `docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json`
- `artifacts/research_campaign/phase2b_spec_freeze_readback_execution_001a.json`
- `artifacts/research_campaign/phase2b_spec_freeze_readback_execution_validation_001a.json`
- `artifacts/research_campaign/phase2b_spec_freeze_readback_execution_audit_001a.json`

No such future freeze/readback execution path may be touched in this
card-opening checkpoint.

## Acceptance Gate For This Checkpoint

- this task card exists;
- it references the audited Phase2B start-state/spec-freeze readback task card;
- it references the Phase2B spec draft;
- it preserves the Phase 2 `no_headroom_baseline_saturated` result;
- it states that no freeze file or readback result is created in this
  checkpoint;
- it requires future freeze/readback before harness implementation or
  execution;
- it preserves candidate-free baseline-first headroom measurement before
  candidate work;
- it preserves the full saturation-family baseline battery;
- `phase2b_spec_freeze_authorized = false`;
- `phase2b_start_state_readback_authorized = false`;
- `phase2b_execution_authorized = false`;
- `candidate_mechanism_run = false`;
- `phase3_opened = false`;
- plan/progress/scorecard/ledger agree on task-card opening or validation
  state;
- no `src/`, `tests/`, freeze file, readback result, harness output,
  candidate, runtime/EGO mainline, push, tag, or remote anchor is touched.

## Claim Ceiling

Phase2B spec-freeze/readback execution task-card reviewer-audit success only.
No spec freeze, start-state readback execution, Phase2B execution, new headroom
measurement, mechanism validity, subjective experience, consciousness, real
emotion, autonomy, agency success, EGO readiness, companion readiness, or
mainline-effect claim.

## Stop Conditions

Stop if:

- a freeze file or readback result is created in this checkpoint;
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

- `docs/research_campaign/phase2b_spec_freeze_readback_execution_task_card_001a.md`
- `artifacts/research_campaign/phase2b_spec_freeze_readback_execution_task_card_validation_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes For This Checkpoint

- No `src/` or `tests/` changes.
- No spec freeze file creation.
- No start-state readback result creation.
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

A future separately authorized checkpoint may perform the actual Phase2B
spec-freeze/readback execution. Do not create a freeze file, create a readback
result, execute Phase2B, implement candidates, open Phase 3, run a route
tournament, touch runtime/EGO mainline, push, tag, or remote-anchor under this
task-card-audit checkpoint.
