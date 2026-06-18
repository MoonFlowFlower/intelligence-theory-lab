# Phase2B Candidate-Free Harness Execution Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2B-CANDIDATE-FREE-HARNESS-EXECUTION-001A`

Source task id:
`RESEARCH-CAMPAIGN-PHASE2B-SPEC-FREEZE-READBACK-EXECUTION-001A`

Source freeze manifest:
`docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json`

Source readback result:
`artifacts/research_campaign/phase2b_spec_freeze_readback_execution_001a.json`

Status: focused validation passed; three read-only reviewer
`needs_more_implementation` findings about stale current-state readbacks are
preserved and repaired; read-only reviewer re-audit returned `success_reached`.
Phase2B harness execution remains unauthorized in this checkpoint.

Auto-Remote-Anchor: forbidden.

## Problem Definition

The Phase2B spec-freeze/readback artifacts were validated and read-only
reviewer audited with `success_reached`. They freeze the source identity and
start-state readback for the candidate-free Phase2B surface. They do not
execute a harness, compute oracle or baseline scores, run replay, run
ablations, run leakage scans, establish headroom, or authorize candidate
mechanisms.

This checkpoint opens the separate candidate-free harness execution task card.
It does not implement or execute the harness. It does not create `src/`,
`tests/`, harness outputs, oracle scores, baseline scores, replay reports,
ablation reports, leakage reports, headroom verdicts, no-headroom verdicts,
candidate mechanisms, Phase 3, route tournaments, runtime/EGO mainline work,
push, tag, or remote anchor.

## Bounded Audit

Layer: engineering implementation + mechanism-hypothesis governance.

Real objective: define the exact future candidate-free harness execution
surface after freeze/readback audit success, while keeping execution disabled
until this task card is focused-validated and read-only reviewer audited.

Strongest baseline explanation: the Phase2B surface may still collapse into a
cheap fair baseline such as graph lookup, transition table, successor map, count
table, exhaustive legal query, full-bundle decoder, serialized-state decoder,
or passive observation shortcut. If the strongest fair baseline reaches
`visible_channel_oracle - equivalence_band`, no candidate mechanism search is
justified.

Strongest invalidating reason: if this checkpoint runs the harness, weakens the
baseline battery, omits leakage positive controls, omits replay recomputation,
omits ablation/control invocation, treats freeze/readback as headroom evidence,
or opens candidate work before measured candidate-free headroom, the checkpoint
is invalid.

Falsifier for current framing: any current-state artifact shows Phase2B harness
execution, oracle/baseline/replay/ablation/leakage scores, candidate mechanism
work, Phase 3, route tournament, runtime/EGO mainline work, push, tag, or
remote anchor before this card is validated and reviewer audited.

Insufficient evidence: task-card creation, JSON parse success, source hashes,
freeze/readback artifacts, reviewer praise without recorded artifact, a single
green test, oracle score without all fair baselines, replay by stored hash,
leakage scan without positive controls, or provenance that is not consumed by
the final verdict.

Mechanism-vs-resemblance classification: the future execution tests only
candidate-free surface headroom. It does not test a candidate mechanism and
cannot produce mechanism, learning, agency, subjectivity, consciousness,
emotion, autonomy, EGO readiness, companion readiness, or mainline-effect
evidence.

Anti-hardcoding audit: the future harness must not replace the control problem
with if/else label lookup, hide a classifier behind mathematical language,
encode the answer in fixture names/action names/path names, tune thresholds
after seeing scores, add a test-only logic path, change schema to erase
failure, use renderer-visible behavior as causal evidence, or make any
diagnostic-only field candidate-visible.

Minimal validation for this checkpoint: local readback must prove this card
exists, references audited freeze/readback artifacts, preserves Phase 2
`no_headroom_baseline_saturated`, keeps Phase2B execution and candidate work
disabled, records no new execution paths, and updates plan/progress/scorecard
and ledger consistently.

Stop condition for this card-opening checkpoint: stop if any `src/`, `tests/`,
harness output, oracle score, baseline score, replay score, ablation score,
leakage score, candidate mechanism, Phase 3, route tournament, runtime/EGO
mainline path, push, tag, or remote anchor is created or authorized.

Rollback plan: revert only this task card, its validation/audit artifacts, and
matching plan/progress/scorecard/ledger entries. Do not delete or rewrite Phase
0, Phase 1, Phase 2, no-headroom, reframing, Phase2B spec, freeze/readback,
validation, or audit artifacts.

Acceptance signal for this card-opening checkpoint: focused validation passes,
read-only reviewer audit reaches `success_reached`, and campaign state records
`phase2b_candidate_free_harness_execution_task_card_audited_success` while
Phase2B harness execution remains disabled until a later execution step.

## Current Stage

This is a task-card-opening checkpoint for a future candidate-free harness
execution. It does not execute the harness.

## Mainline Target

None. No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, or
product path is targeted.

## Enabled-State Requirement

Only task-card drafting, campaign bookkeeping, focused local validation, and
read-only reviewer audit are enabled in this checkpoint.

Future candidate-free harness implementation/execution remains disabled until
this task card is focused-validated and read-only reviewer audited with
`success_reached`.

Candidate mechanisms, Phase 3, route tournament, Gate execution, runtime/EGO
mainline, UI, LLM, AIRI, external services, deployment, push, tag, and remote
anchor remain disabled.

## Real-Trigger Evidence Requirement

The card-opening validation must read back:

- current repo root, branch, HEAD, upstream/ahead-behind state, and worktree
  status;
- Phase 2 audited no-headroom result;
- Phase 2 no-headroom negative-evidence artifact;
- Phase2B spec draft;
- Phase2B freeze manifest;
- Phase2B freeze/readback result;
- Phase2B freeze/readback validation artifact;
- Phase2B freeze/readback audit artifact;
- current `plan.md`, `OVERALL_PROGRESS.md`, `stage_scorecard.json`, and
  `experiment_log.jsonl`;
- SHA256 for `docs/research/MINIMAL-ENV-SPEC-001A.md`;
- SHA256 for `docs/research/phase2b_minimal_env_reframe_spec_001a.md`;
- SHA256 for this task card.

## Hypothesis

A separately validated and reviewer-audited execution task card can preserve
the freeze/readback boundary and define the future candidate-free harness
surface without accidentally running the harness or opening candidate work.

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
candidate search remains blocked and the result must be recorded as
no-headroom negative evidence.

## Ablation Requirement

This card-opening checkpoint runs no ablations. Future execution must include
callable ablations or controls that rerun the episode pipeline under real
interventions for:

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

This card-opening checkpoint runs no replay. Future replay must recompute from:

```text
serialized_state + current_observation + legal_action_or_query_schema + budget_state
```

Replay that compares only stored hashes, stored verdicts, or self-reported
provenance is invalid.

## Computed-Evidence Provenance Gate

This card-opening checkpoint must record source hashes in its validation
artifact. Future execution must record, and final verdict aggregation must
consume:

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
- baseline invocation records;
- `consumed_by_final_verdict` flags.

Static verdict dictionaries, handwritten scores, unconditional clean reports,
and tests that only assert pass are forbidden.

## Future Execution Surface

This card-opening checkpoint does not authorize file edits outside campaign
bookkeeping. If a later audited execution step explicitly authorizes
implementation/execution, the intended isolated future write paths are:

- `src/phase2b_candidate_free_headroom_001a/`
- `tests/phase2b_candidate_free_headroom_001a/`
- `artifacts/phase2b_candidate_free_headroom_001a/`
- `artifacts/research_campaign/phase2b_candidate_free_headroom_001a.json`
- `artifacts/research_campaign/phase2b_candidate_free_headroom_validation_001a.json`
- `artifacts/research_campaign/phase2b_candidate_free_headroom_audit_001a.json`

No such future execution path may be touched in this card-opening checkpoint.

## Acceptance Gate For This Checkpoint

- this task card exists;
- it references the audited Phase2B freeze/readback artifacts;
- it preserves the Phase 2 `no_headroom_baseline_saturated` result;
- it requires candidate-free baseline-first headroom measurement before
  candidate work;
- it requires strongest fair baseline as max over the full callable battery;
- it requires leakage positive controls, replay recomputation, ablations, and
  computed provenance consumed by the final verdict;
- `phase2b_execution_authorized = false`;
- `candidate_mechanism_run = false`;
- `phase3_opened = false`;
- plan/progress/scorecard/ledger agree on task-card validation, repair, or audit
  state;
- no `src/`, `tests/`, harness output, candidate, runtime/EGO mainline, push,
  tag, or remote anchor is touched.

## Claim Ceiling

Phase2B candidate-free harness execution task-card validation/reviewer-audit
success only. No Phase2B harness execution, new headroom measurement, mechanism
validity, subjective experience, consciousness, real emotion, autonomy, EGO
readiness, companion readiness, or mainline-effect evidence.

## Stop Conditions

Stop if:

- focused validation fails;
- read-only reviewer audit returns anything other than `success_reached`;
- source hashes are stale or missing;
- any future harness execution path exists before explicit execution
  authorization;
- any `src/`, `tests/`, harness output, oracle score, baseline score, replay
  score, ablation score, leakage score, candidate mechanism, Phase 3, route
  tournament, runtime/EGO mainline path, push, tag, or remote anchor is
  created or authorized;
- prior no-headroom evidence, baseline requirements, ablation requirements,
  replay requirements, or claim ceilings are weakened.

## Expected Changed Files

- `docs/research_campaign/phase2b_candidate_free_harness_execution_task_card_001a.md`
- `artifacts/research_campaign/phase2b_candidate_free_harness_execution_task_card_validation_001a.json`
- `artifacts/research_campaign/phase2b_candidate_free_harness_execution_task_card_audit_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes For This Checkpoint

- No `src/` or `tests/` changes.
- No harness output creation.
- No oracle, baseline, replay, ablation, leakage, or headroom scores.
- No candidate mechanism, Phase 3, route tournament, runtime/EGO mainline,
  UI, LLM, AIRI, external service, deployment, push, tag, or remote anchor.
- No mutation of `docs/research/phase2b_minimal_env_reframe_spec_001a.md`.
- No mutation of `docs/research/phase2b_minimal_env_reframe_spec_001a.freeze.json`.
- No mutation of `artifacts/research_campaign/phase2b_spec_freeze_readback_execution_001a.json`.

## Auto-Remote-Anchor

`forbidden`

## Next Minimal Closed-Loop Action

A later separately bounded checkpoint may consider implementing/running the
candidate-free harness only after preserving this audit-success boundary. Do not
execute the harness, implement candidates, open Phase 3, run a route tournament,
touch runtime/EGO mainline, push, tag, or remote-anchor in this checkpoint.
