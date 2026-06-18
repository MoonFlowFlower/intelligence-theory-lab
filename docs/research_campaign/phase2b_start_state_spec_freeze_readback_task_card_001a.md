# Phase2B Start-State / Spec-Freeze Readback Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2B-START-STATE-SPEC-FREEZE-READBACK-001A`

Source task id:
`RESEARCH-CAMPAIGN-PHASE2B-EXECUTION-START-STATE-SPEC-FREEZE-001A`

Source task card:
`docs/research_campaign/phase2b_execution_start_state_spec_freeze_task_card_001a.md`

Source spec draft:
`docs/research/phase2b_minimal_env_reframe_spec_001a.md`

Status: focused validation passed; read-only reviewer audit returned
`success_reached`.

Auto-Remote-Anchor: forbidden.

## Problem Definition

The Phase2B execution start-state/spec-freeze task card has been locally
validated and read-only reviewer audited with `success_reached`, after two
preserved stale-status reviewer failures and repairs. It established that a
separately bounded start-state/spec-freeze readback checkpoint is required
before any Phase2B harness implementation or measurement.

This checkpoint opens that readback task card only. It does not create the
spec-freeze manifest, does not create a start-state readback artifact, does not
execute Phase2B, and does not authorize candidate mechanisms, Phase 3, route
tournaments, runtime/EGO mainline work, push, tag, or remote anchor.

## Bounded Audit

Layer: engineering implementation + mechanism-hypothesis governance.

Real objective: define the bounded task surface for a later spec-freeze and
start-state readback, while keeping freeze/readback execution disabled until
this task card is locally validated and read-only reviewer audited.

Strongest baseline explanation: a readback checkpoint can become process
theater if a freeze manifest is treated as measured headroom or execution
readiness, or if source hashes are recorded without proving that candidate-
visible leak channels and saturation baselines remain guarded.

Strongest invalidating reason: if this card or its bookkeeping creates a freeze
file, creates a readback result, weakens the known saturation-family baseline
battery, authorizes Phase2B execution, or reinterprets the Phase 2 no-headroom
result as positive mechanism evidence, the checkpoint is invalid.

Falsifier for current framing: any current-state artifact shows
`phase2b_spec_freeze_authorized = true`, `phase2b_execution_authorized = true`,
candidate work, Phase 3, route tournament, runtime/EGO mainline work, or a
freeze/readback artifact created before this card is validated and audited.

Insufficient evidence: task-card creation, JSON parse success, stale
bookkeeping, a reviewer verdict not recorded in artifacts, a freeze hash
without source and validator readback, or any claim that freeze/readback alone
proves headroom or mechanism validity.

Mechanism-vs-resemblance classification: this checkpoint is task-card and
start-state governance only. It does not test behavior, headroom, mechanism
validity, learning, agency, subjectivity, or consciousness.

Anti-hardcoding audit: the future freeze/readback task must prove that the spec
boundary still blocks target labels, final-action scores, answer maps, full
legal response bundles, semantic action-label leaks, fixture/path target leaks,
unused frozen seeds, and hidden test-only logic paths before any harness
implementation or measurement is enabled.

Minimal validation for this card-opening checkpoint: local readback must prove
this card exists, references the audited Phase2B execution start-state/spec-
freeze task card, preserves the audited Phase 2 no-headroom result and Phase2B
spec hash, keeps freeze/readback/execution unauthorized, records no forbidden
future paths, and updates plan/progress/scorecard/ledger consistently.

Stop condition for this checkpoint: stop if any freeze file, readback result,
`src/`, `tests/`, harness output, oracle score, baseline score, replay score,
ablation score, leakage score, candidate mechanism, Phase 3, route tournament,
runtime/EGO mainline path, push, tag, or remote anchor is created or
authorized.

Rollback plan: revert only this task card, its validation artifact, and matching
plan/progress/scorecard/ledger entries. Do not delete or rewrite Phase 0,
Phase 1, Phase 2, no-headroom, reframing, Phase2B spec, validation, or audit
artifacts.

Acceptance signal for this card-opening checkpoint: focused validation passes
and the campaign state records
`phase2b_start_state_spec_freeze_readback_task_card_validated_pending_reviewer_audit`.

## Current Stage

This is a task-card-opening checkpoint for a future Phase2B start-state/spec-
freeze readback. It does not create the freeze manifest, does not create the
readback artifact, and does not execute Phase2B.

## Mainline Target

None. No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, or
product path is targeted.

## Enabled-State Requirement

Only task-card drafting, campaign bookkeeping, and focused local validation are
enabled in this checkpoint.

Future spec freeze, start-state readback, and harness implementation remain
disabled until this card opening is locally validated and a read-only reviewer
audit reaches `success_reached`.

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
- current `plan.md`, `OVERALL_PROGRESS.md`, `stage_scorecard.json`, and
  `experiment_log.jsonl`;
- SHA256 for `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- SHA256 for `docs/research/phase2b_minimal_env_reframe_spec_001a.md`.

## Hypothesis

A separately audited readback task card can prevent the campaign from
collapsing start-state governance into freeze execution, while preserving the
route to a later candidate-free baseline-first headroom measurement.

## Strongest Baseline

The strongest false route is freeze-readiness theater: a manifest or hash
record is treated as evidence that headroom exists. The future readback
checkpoint must therefore preserve:

- strongest fair baseline as `max(all applicable callable baselines)`;
- graph lookup, transition table, successor map, FSM planner, episodic
  traversal, count table, exhaustive legal query, full-bundle decoder,
  serialized-state decoder, passive attackers, and trace-only replay baselines;
- equal budget and input boundary for oracle and all fair baselines;
- no candidate mechanism before measured headroom exists.

## Ablation Requirement

This card-opening checkpoint runs no ablations. The future start-state/spec-
freeze readback checkpoint must preserve all ablation/control requirements
already defined in
`RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HEADROOM-001A` and must not weaken
any control family.

## Trace / Replay Requirement

This card-opening checkpoint runs no replay. The future start-state/spec-freeze
readback checkpoint must preserve the replay requirement:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Hash-only, stored-output, or self-reported replay remains invalid.

## Computed-Evidence Provenance Gate

This card-opening checkpoint must record source hashes in its validation
artifact. The future start-state/spec-freeze readback checkpoint must record:

- source spec path and SHA256;
- freeze manifest path and SHA256;
- producer function or command for freeze/readback;
- input artifacts;
- run id;
- aggregation rule for start-state validation;
- source file digests or code path hashes for validators;
- generated artifact paths;
- consumed-by-final-verdict flags for validation checks.

Static verdict dictionaries, handwritten clean reports, unconditional pass
reports, and tests that only assert pass are forbidden.

## Future Freeze / Readback Surface

This card-opening checkpoint does not authorize creating any future
freeze/readback file. If a later audited start-state task explicitly authorizes
freeze/readback, the intended isolated future write paths are:

- `docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json`
- `artifacts/research_campaign/phase2b_start_state_spec_freeze_readback_001a.json`
- `artifacts/research_campaign/phase2b_start_state_spec_freeze_readback_validation_001a.json`
- `artifacts/research_campaign/phase2b_start_state_spec_freeze_readback_audit_001a.json`

No such future freeze/readback path may be touched in this card-opening
checkpoint.

## Acceptance Gate For This Checkpoint

- this task card exists;
- it references the audited Phase2B execution start-state/spec-freeze task
  card;
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

Phase2B start-state/spec-freeze readback task-card opening only. No spec
freeze, start-state readback execution, Phase2B execution, new headroom
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

- `docs/research_campaign/phase2b_start_state_spec_freeze_readback_task_card_001a.md`
- `artifacts/research_campaign/phase2b_start_state_spec_freeze_readback_task_card_validation_001a.json`
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

Run focused local validation of this task-card-opening checkpoint. If it passes,
record validation and keep the next frontier at read-only reviewer audit before
any Phase2B spec freeze or start-state readback is executed.
