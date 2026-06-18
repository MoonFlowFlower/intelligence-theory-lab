# Goal Stage Audit Loop Historical Appendix 001A

Captured at: 2026-06-18T07:55:29.5783534-05:00

Source card: `docs/research_campaign/goal_stage_audit_loop_001a.md`

Pre-compaction SHA-256: `793ee8c170dad4074281fb11c45ce83dec8026a751df93d23621aa20e72cca59`

Pre-compaction line count: `520`

Task card: `docs/research_campaign/goal_stage_audit_loop_representation_compaction_task_card_001a.md`

Claim ceiling: append-only preservation of the pre-compaction governance card
text and section inventory only. This appendix is not live campaign frontier,
mechanism evidence, Phase 3 authorization, route exhaustion proof, or program
completion.

## Section Inventory

- line 5: ## Purpose
- line 24: ## Current Layer
- line 31: ## Program Goal
- line 43: ## Completion Level Vocabulary
- line 60: ## Program Terminal Contract
- line 86: ## Long-Term Phase Cycle
- line 103: ## Stage Goal
- line 113: ## Mainline Target
- line 118: ## Enabled-State Requirement
- line 124: ## Real-Trigger Evidence Requirement
- line 144: ## Hypothesis
- line 157: ## Strongest Baseline / False Explanation
- line 171: ## Required Prior-Evidence Search
- line 193: ## Phase Loop Protocol
- line 225: ## Reviewer Verdict Vocabulary
- line 244: ## Baseline Requirement
- line 263: ## Surface Redesign Requirement After No-Headroom
- line 319: ## Ablation Requirement
- line 328: ## Trace / Replay Requirement
- line 339: ## Computed-Evidence Provenance Gate
- line 356: ## controller_card_acceptance_gate
- line 373: ## Program Goal Acceptance Gate
- line 402: ## Do Not Complete Program When
- line 418: ## Continuation Rule
- line 433: ## Claim Ceiling
- line 453: ## Stop Conditions
- line 471: ## Rollback Plan
- line 485: ## Expected Changed Files
- line 494: ## Forbidden Changes
- line 505: ## Auto-Remote-Anchor
- line 509: ## Immediate Next Action After This Card

## Full Pre-Compaction Governance Card Snapshot

`````markdown
# Goal Task Card: Stage Audit Loop 001A

Task id: `RESEARCH-CAMPAIGN-GOAL-STAGE-AUDIT-LOOP-001A`

## Purpose

Convert the user's long-running instruction into a bounded, auditable campaign
control task:

```text
Open the current phase, run a reviewer/subagent audit, repair audit failures
until the phase reaches an auditable pass, then open the next phase. Repeat this
phase-by-phase, but never treat subagent output, green tests, or local artifacts
as proof of consciousness, real emotion, autonomy, EGO readiness, or mechanism
validity.
```

This is a standing governance card and long-running program controller. It
defines how future phase tasks are advanced and when the overall campaign may
or may not stop. It does not itself execute Phase 2, run a baseline battery,
implement a candidate mechanism, validate any subjectivity claim, or complete
the program goal.

## Current Layer

`engineering_implementation + mechanism_hypothesis_governance`

This card is not a subjectivity-validation task and not a philosophical
consciousness task.

## Program Goal

Run a long-term, falsifiable research campaign for bounded
functional-subject proxy mechanisms by repeatedly:

1. reducing broad target terms into executable phase gates;
2. recording progress before and after every task;
3. preserving failures as evidence;
4. using reviewer/subagent audits as phase gates;
5. repairing only the failing bounded surface;
6. advancing only after recorded audit success.

## Completion Level Vocabulary

The campaign has three distinct completion levels. They must not be collapsed:

- `single_task_complete`: one bounded task card has been executed, recorded,
  validated, and audited if required.
- `phase_complete`: the current phase has a reviewer/subagent
  `success_reached` verdict recorded in phase artifacts, `experiment_log.jsonl`,
  `stage_scorecard.json`, and `OVERALL_PROGRESS.md`.
- `program_complete`: the long-running campaign has either found and validated
  a bounded functional-subject proxy mechanism/theory/formula through the full
  required chain, or all currently definable routes have been closed by
  recorded negative evidence.

`single_task_complete` and `phase_complete` are progress states only. They do
not complete the program.

## Program Terminal Contract

The program remains `active_not_complete` until one of the allowed terminal
verdicts is recorded with machine-readable evidence and reviewer audit.

Allowed terminal verdicts:

- `program_candidate_validated_bounded`
- `program_needs_reframing`
- `program_route_exhausted_with_negative_evidence`
- `program_blocked_by_external_dependency`

Forbidden terminal verdicts:

- `consciousness_proven`
- `real_emotion_proven`
- `electronic_life_proven`
- `self_awareness_proven`
- `autonomy_proven`
- `agi_proven`
- `ego_ready`
- `companion_ready`

No terminal verdict may be recorded from narrative confidence, a single
subagent response, a passing local validation, or a task-card creation event.

## Long-Term Phase Cycle

The controller advances through this audited loop:

1. Phase 0: Recovery and Ledger Hardening.
2. Phase 1: Problem Formalization.
3. Phase 2: Baseline-First Headroom.
4. Phase 3: Mechanism Search.
5. Phase 4: Structure Extraction.
6. Phase 5: Large-Scale Validation.
7. Phase 6: Formalization.

If Phase 6 produces only local or partial formalization, the campaign returns to
Phase 1 or Phase 2 with a stronger problem representation. A Phase 6 local
proof does not prove consciousness, subjective experience, real emotion,
electronic life, EGO readiness, or companion readiness.

## Stage Goal

Define a strict phase-advancement protocol for Phase 1 and all later phases:

```text
phase task card -> bounded execution -> immediate ledger update -> reviewer
audit -> preserve failure -> repair -> re-audit -> record success -> open next
phase task card
```

## Mainline Target

None. This card has no runtime, EGO mainline, UI, LLM, AIRI, external service,
deployment, or product target.

## Enabled-State Requirement

No mechanism, baseline battery, Gate, bridge, runtime path, EGO mainline path,
UI, LLM integration, external service, push, tag, or remote anchor may be
enabled by this card alone.

## Real-Trigger Evidence Requirement

Before each phase loop begins, Codex must read back and record:

- current repo root;
- current branch;
- current HEAD;
- upstream/ahead-behind state when relevant;
- `git status --short --branch -uall`;
- active `docs/research_campaign/plan.md` task card;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- tail of `artifacts/research_campaign/experiment_log.jsonl`;
- relevant prior failure/audit artifacts for the same mechanism or stage family.

If a reviewer/subagent verdict exists only in chat or notification output, it is
not yet campaign evidence. It must be recorded into the audit artifact,
`experiment_log.jsonl`, `stage_scorecard.json`, and `OVERALL_PROGRESS.md`, then
validated by local parse/consistency checks before it can unlock the next phase.

## Hypothesis

A strict phase-audit loop can reduce false pass risk by making every phase
transition depend on:

- a bounded task card;
- machine-readable ledger state;
- preserved failed audits;
- independent reviewer/subagent read-only audit;
- focused repair;
- fresh validation after repair;
- recorded `success_reached` before phase advancement.

## Strongest Baseline / False Explanation

The weakest but dangerous baseline is "process theater":

- a phase appears complete because a subagent says `success_reached`;
- plan/progress/scorecard/ledger disagree;
- failed audits are overwritten or hidden;
- the next phase opens before audit success is recorded;
- a task card is broad enough to authorize runtime, candidate, or claim drift;
- historical mechanism evidence leaks into the current phase as inherited proof;
- reviewer checks only document shape, not evidence chain and claim ceiling.

This card is valid only if it blocks that baseline.

## Required Prior-Evidence Search

Before any phase task or audit prompt, Codex must search relevant prior negative
evidence and audit artifacts in the repo. For mechanism or Gate-like work, the
audit prompt may reference prior project gate, Claude, reviewer, and mechanism
audit patterns, but only as challenge families, not as inherited proof.

At minimum, each audit prompt must ask the reviewer to check:

- stale plan/progress/scorecard/ledger state;
- unrecorded chat-only verdicts;
- historical-evidence scope inflation;
- hidden second logic paths;
- static verdicts or hand-written scores;
- missing callable producers;
- weak or non-independent baselines;
- unused frozen seeds, heldout contexts, or counterfactual pairs;
- trace/replay that compares hashes without recomputing behavior;
- leakage without positive control;
- ablations that do not rerun real interventions;
- claim inflation beyond the phase layer.

## Phase Loop Protocol

For each phase `N`:

1. Open the phase by writing an active task card before execution.
2. Record the active task in `plan.md` with task id, objective, layer, baseline,
   ablation, trace/replay, claim ceiling, stop condition, expected files, and
   `Auto-Remote-Anchor: forbidden`.
3. Execute only the bounded task surface authorized by that card.
4. Immediately update:
   - `docs/research_campaign/plan.md`;
   - `docs/OVERALL_PROGRESS.md`;
   - `artifacts/research_campaign/experiment_log.jsonl`;
   - `artifacts/research_campaign/stage_scorecard.json`;
   - phase-specific artifacts.
5. Run focused local validation before reviewer audit.
6. Dispatch a read-only reviewer/subagent audit with exact scope and verdict
   vocabulary.
7. If the reviewer verdict is not `success_reached`:
   - append the failure to the audit artifact and ledger;
   - update progress and scorecard as failed or repaired-pending-reaudit;
   - repair only the cited bounded failure surface;
   - rerun focused validation;
   - rerun reviewer audit.
8. If the reviewer verdict is `success_reached`:
   - record the pass in the audit artifact, ledger, scorecard, and progress;
   - validate that the recorded pass parses and agrees across files;
   - open the next phase task card only after the recorded pass exists.
9. Do not execute the next phase in the same step that merely records a
   previously chat-only audit verdict unless the new phase task card is already
   recorded and its start conditions pass.

## Reviewer Verdict Vocabulary

Reviewer/subagent audits must return exactly one:

- `success_reached`
- `needs_more_implementation`
- `needs_more_exploration`
- `blocked_by_external_dependency`
- `needs_reframing`

Mapping:

- `success_reached`: record pass, then open the next bounded phase task card.
- `needs_more_implementation`: repair the bounded surface and re-audit.
- `needs_more_exploration`: return to explorer/problem framing before repair.
- `blocked_by_external_dependency`: stop and record blocker.
- `needs_reframing`: stop patching; rewrite the phase gate/problem
  representation before further execution.

## Baseline Requirement

Every executable mechanism or proxy-evidence phase after Phase 1 must run a
candidate-free baseline-first headroom step before candidate search.

Minimum baseline families when relevant:

- random / majority;
- observation-only;
- lookup / transition table / graph-cache;
- nearest-neighbor;
- heuristic or finite-state planner;
- post-hoc classifier when applicable;
- trace-only replay baseline when replay validity is relevant.

If the strongest fair baseline saturates the measured surface within the
equivalence band, record no-headroom negative evidence and reframe. Do not
implement candidates to rescue the phase.

## Surface Redesign Requirement After No-Headroom

After a candidate-free surface is saturated by visible-surface baselines, the
next redesign must not simply make the task larger.

The redesign must ask first:

```text
Does this surface require learning, exploration, or memory to reproduce oracle
behavior on heldout latent structure?
```

It must not ask first:

```text
Can a candidate beat the baseline on another visible-surface task?
```

Any next surface after no-headroom must include:

- hidden latent state or latent causal rule;
- current observations that do not directly determine the oracle action;
- frozen train seeds and heldout seeds;
- heldout task families, not only heldout instances;
- online exploration or hypothesis-testing actions;
- cross-episode memory or update-relevant state;
- memory deletion and latent-rule swap interventions;
- heldout transfer and forgetting checks where sequence learning is claimed;
- machine-readable failure taxonomy;
- leakage positive controls;
- preserved strongest baselines, including lookup, count table, transition
  table, graph-cache, successor map, nearest neighbor, finite-state planner,
  episodic traversal, trace-only replay, and exhaustive legal query.

The design analogies are:

- Procgen-style procedural train/test diversity;
- MiniGrid/MiniWorld-style low-cost controllable partial observability;
- Alchemy-style latent causal inference through exploration and hypothesis
  testing;
- Meta-World-style heldout task-family transfer;
- Continual World-style forward transfer, forgetting, and capacity/compute
  constraints;
- AgentBench-style failure taxonomy as an artifact;
- Craftax-style exploration, planning, memory, and continual adaptation under
  feasible compute.

These analogies are not inherited proof. They only constrain future task-card
design. A surface fails this requirement if a non-learning visible-surface
baseline can match the oracle on heldout latent rules or heldout task families
under the same budget.

Do not treat `program_needs_reframing`, route closure, or claim downgrade as
the next default after no-headroom while a bounded hidden-latent heldout surface
contract can still be specified and audited.

## Ablation Requirement

Governance-only phases must define future ablation requirements. Executable
phases must rerun real interventions, not only mutate reports.

Every mechanism-evidence phase must include at least one ablation that removes
or perturbs the claim-critical variable and recomputes the score through the
same producer path.

## Trace / Replay Requirement

Replay evidence must recompute candidate behavior or scores from:

```text
serialized_state + observation + allowed context
```

Hash equality, stored verdict equality, or candidate self-reported provenance is
not sufficient.

## Computed-Evidence Provenance Gate

All phase evidence must come from callable producer paths. Every score or
verdict-bearing result must record:

- producer function or command;
- input artifacts;
- run id;
- seed/context/episode ids where applicable;
- aggregation rule;
- code path hash or source file digest when applicable;
- generated artifacts;
- failure paths and positive controls where applicable.

Static verdict dictionaries, handwritten scores, unconditional clean reports,
and tests that only assert pass are forbidden.

## controller_card_acceptance_gate

This controller card is accepted only if:

- the card exists under `docs/research_campaign/`;
- `plan.md` references it as a standing governance card;
- `OVERALL_PROGRESS.md` records that this card was created without executing
  Phase 2;
- `experiment_log.jsonl` has an append-only entry for this card;
- `stage_scorecard.json` points to the card without changing unrecorded Phase 1
  audit success into a recorded pass;
- local validation confirms JSON/JSONL parseability and expected dirty paths;
- no `src/`, `tests/`, runtime, Gate, EGO mainline, push, tag, or remote anchor
  is touched.

Controller-card acceptance is not program completion.

## Program Goal Acceptance Gate

The program goal is accepted as complete only if one of these has been recorded:

- `program_candidate_validated_bounded`: at least one candidate
  method/theory/formula has survived Phase 2 through Phase 6 with recorded
  baseline-first headroom, mechanism search, structure extraction,
  large-scale validation, local formalization, and reviewer/subagent audit.
- `program_route_exhausted_with_negative_evidence`: all currently defined
  routes have been closed by preserved negative evidence, including baseline
  saturation or no-headroom evidence where applicable.
- `program_needs_reframing`: two consecutive phase loops failed to increase
  discriminative evidence or the current phase gate was found invalid, and the
  reframing decision is recorded in artifacts and ledger.
- `program_blocked_by_external_dependency`: the same external blocker has been
  recorded across the required blocked-audit threshold and no meaningful local
  progress remains possible.

For `program_candidate_validated_bounded`, the evidence chain must include:

- Phase 2 candidate-free baseline-first headroom under equal budget and input
  boundary;
- Phase 3 candidate mechanism search only inside measured-headroom surfaces;
- Phase 4 low-complexity structure extraction from both pass and fail cases;
- Phase 5 distribution-shift, counterfactual, intervention, ablation,
  source-deletion, replay-recomputation, and leakage positive-control checks;
- Phase 6 local formalization with proof scope and failure boundaries;
- recorded reviewer/subagent `success_reached` for every phase in the chain.

## Do Not Complete Program When

Do not mark the program complete when only one of these is true:

- a task card was created;
- this controller card was accepted;
- a local validation passed;
- JSON or JSONL parses;
- a subagent says `success_reached` but the verdict is not yet recorded;
- one phase receives an audited pass;
- Phase 1 problem formalization is accepted;
- Phase 2 baseline-first headroom has not yet run;
- a candidate looks promising without baseline, ablation, replay, validation,
  and formalization evidence;
- a result is only governance, documentation, schema, or report consistency.

## Continuation Rule

Every continuation must recover state from the repository before acting. It must
read:

- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/experiment_log.jsonl`;
- the active task card in `docs/research_campaign/plan.md`;
- relevant phase-specific artifacts and prior failures.

Continuation starts from the recorded `next_frontier` or
`current_phase_frontier`. It must not reset the campaign, skip failed evidence,
or treat a previous single-task completion as program completion.

## Claim Ceiling

This card proves only that a stricter controller and terminal-contract protocol
has been drafted and recorded for phase-by-phase campaign advancement.

It does not prove:

- mechanism validity;
- baseline headroom;
- learning/adaptation success;
- agency or selfhood proxy success;
- self-awareness;
- subjective experience;
- real emotion;
- autonomy;
- electronic life;
- EGO readiness;
- companion readiness;
- runtime or mainline effect.

## Stop Conditions

Stop and record the blocker if any of these occur:

- next phase opens before prior phase audit success is recorded;
- program completion is claimed before a permitted terminal verdict is recorded;
- a single task or phase completion is used as a program completion substitute;
- reviewer/subagent verdict exists only in chat and is treated as ledger truth;
- plan/progress/scorecard/ledger disagree after repair;
- two consecutive repair loops do not increase discriminative evidence;
- baseline-first phase finds no headroom and candidate work is still proposed;
- audit failure is deleted, overwritten, or summarized away;
- dirty paths escape the phase task card scope;
- `src/`, `tests/`, runtime, Gate, EGO mainline, push, tag, or remote anchor are
  touched without explicit phase-card authorization;
- any wording claims consciousness, real emotion, autonomy, electronic life,
  EGO readiness, companion readiness, mechanism validity, or mainline effect.

## Rollback Plan

Revert only this card and its campaign bookkeeping entries:

- `docs/research_campaign/goal_stage_audit_loop_001a.md`;
- the `plan.md` standing-card reference;
- the `OVERALL_PROGRESS.md` checkpoint text for this governance card;
- the matching append-only ledger entry, only if rollback is explicitly
  authorized and the rollback itself is recorded;
- the matching `stage_scorecard.json` governance-card pointer.

Do not delete or rewrite prior Phase 0/Phase 1 artifacts, failed validations,
failed audits, or historical evidence.

## Expected Changed Files

- `docs/research_campaign/goal_stage_audit_loop_001a.md`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`

## Forbidden Changes

- No `src/` or `tests/` changes.
- No new mechanism experiment.
- No Phase 2 baseline battery execution.
- No candidate mechanism search.
- No formal Gate execution.
- No runtime, EGO mainline, UI, LLM, AIRI, external service, or deployment work.
- No push, tag, commit, or remote anchor.
- No rewriting old failed artifacts into passes.

## Auto-Remote-Anchor

`forbidden`

## Immediate Next Action After This Card

After this controller and terminal contract is validated, the next valid
campaign action is one of:

1. record the existing Hegel Phase 1 `success_reached` audit verdict into
   artifacts and validate it; or
2. rerun a fresh Phase 1 reviewer audit if chat-only audit output is judged
   insufficient for ledger truth.

Only after a recorded and validated Phase 1 audit pass exists may Phase 2 be
opened. The program remains `active_not_complete` after this card.
`````
