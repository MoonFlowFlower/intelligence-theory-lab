# Strict Intelligence Mechanism Research Campaign Plan

Last updated: 2026-06-18

## Program Goal

Build a long-running, falsifiable, recovery-safe research campaign for finding
and eliminating candidate mechanisms that could support bounded functional-subject
proxies: self-modeling, affect/value regulation, active exploration, long-term
learning, and self/environment boundary tracking.

This campaign does not aim to prove consciousness, subjective experience, real
emotion, autonomy, electronic life, AGI, EGO readiness, companion readiness, or
stable user benefit. Those claims remain forbidden unless a later bounded task
defines computed evidence strong enough to support a narrower proxy claim.

## Current Phase

Task id: `RESEARCH-CAMPAIGN-PHASE0-RECOVERY-LEDGER-HARDENING-001A`

Layer: engineering implementation + mechanism-hypothesis governance.

Stage goal: recover the current dirty workspace state and harden the campaign
ledger so every future task records progress, failures, baselines, ablations,
trace/replay, and claim ceilings before any new mechanism experiment runs.

Mainline integration status: none.

Enabled status: none.

Real trigger evidence: repo readback and campaign ledger files only; no runtime,
Gate, EGO mainline, live path, or mechanism experiment is triggered by this
Phase 0 task.

Claim ceiling: campaign ledger recovery and evidence-hygiene hardening only.

Auto-Remote-Anchor: forbidden.

## Phase 0 Task Card

Problem definition: the repository is already ahead of origin with a modified
decision log and many untracked evidence-like artifacts. Continuing mechanism
experiments without recovering and classifying that state risks losing progress,
burying failures, or creating false pass narratives.

Hypothesis: a minimal recovery pass can make the current campaign state
auditable by adding a canonical plan entry, a computed dirty-state inventory,
an append-only ledger entry, an updated scorecard, and a progress checkpoint
without accepting any unverified artifact as mechanism evidence.

Strongest baseline explanation: the current dirty state may be a mixed pile of
prior user work, audit bundles, generated artifacts, and implementation surfaces;
file presence alone does not establish validity, acceptance, or readiness.

Ablation requirement: no candidate mechanism, baseline battery, ablation run,
replay run, or formal Gate is executed in Phase 0. The recovery output must
remain distinguishable from evidence acceptance.

Trace/replay requirement: the recovery inventory must be reproducible from live
`git status --porcelain=v1` plus repo readback. Future mechanism tasks must
define replay recomputation from `serialized_state + observation`, not hash-only
comparison.

Computed-evidence provenance gate: future scores must record producer function,
input artifacts, run id, seed/context/episode ids, aggregation rule, and code
path hash. Phase 0 records no mechanism scores.

Acceptance gate:

- `docs/research_campaign/plan.md` exists and states the active campaign rules.
- `artifacts/research_campaign/phase0_recovery_inventory_001a.json` parses as JSON.
- `artifacts/research_campaign/experiment_log.jsonl` has one append-only Phase 0 entry.
- `artifacts/research_campaign/stage_scorecard.json` parses as JSON and points to Phase 0.
- `docs/OVERALL_PROGRESS.md` has a current Phase 0 checkpoint.
- No existing evidence artifact is rewritten, deleted, promoted, pushed, tagged, or anchored.

Stop condition:

- Stop if JSON validation fails.
- Stop if `docs/decision_log.md` or pre-existing untracked evidence bundles would need to be
  overwritten or reinterpreted to complete the task.
- Stop if any command would run a mechanism experiment, Gate, runtime, EGO mainline,
  external service, push, tag, or remote anchor.

Rollback plan: remove only the Phase 0 files/entries created by this task:
`docs/research_campaign/plan.md`, the Phase 0 recovery inventory/validation
artifacts, the appended Phase 0 JSONL ledger entry, and the Phase 0 checkpoint
edits. Do not delete or rewrite pre-existing artifacts.

Expected changed files:

- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/phase0_recovery_inventory_001a.json`
- `artifacts/research_campaign/phase0_recovery_validation_001a.json`

Forbidden changes:

- No `src/` implementation or candidate mechanism changes.
- No `tests/` changes except future task-specific validation cards.
- No historical artifact rewrites.
- No old failure repair into pass-shaped language.
- No threshold tuning, baseline weakening, schema migration, Gate execution,
  runtime wiring, EGO mainline work, UI, LLM integration, external services,
  push, tag, or remote anchor.

## Campaign Loop Rules

Every future task must update the campaign state immediately:

1. Before work: write or update this plan with the task card, claim ceiling,
   expected changed files, forbidden changes, and stop condition.
2. During work: keep failures and blockers in the ledger; do not wait for a pass.
3. After work: append `experiment_log.jsonl`, update `stage_scorecard.json`,
   update `docs/OVERALL_PROGRESS.md`, and record the next minimal closed-loop action.
4. If two consecutive tasks do not increase discriminative evidence, route to
   `needs_reframing`; do not continue patching toward a pass.

## Research Phases

Phase 1: Problem formalization. Split self-awareness, emotion, agency, and
learning into measurable proxy variables: self-model, affect/value regulation,
active exploration, long-term update, and self/environment boundary.

Phase 2: Baseline-first headroom. Run candidate-free baseline batteries before
candidate mechanisms. If lookup, graph/cache, heuristic, or exhaustive baselines
saturate the surface, freeze no-headroom negative evidence and reframe.

Phase 3: Mechanism search. Search candidates only inside measured-headroom
surfaces. Change one mechanism variable per run. Do not tune thresholds after
seeing results.

Phase 4: Structure extraction. Extract low-complexity structure from passes and
failures using MDL, compressed causal structure, and replayable state transitions.
Do not treat language appearance as mechanism evidence.

Phase 5: Large-scale validation. Run distribution-shift, counterfactual,
intervention, ablation, source-deletion, replay-recomputation, and leakage
positive-control checks.

Phase 6: Formalization. Produce local formal proofs only for stable,
reproducible, baseline-resistant structures. State proof scope and failure
boundaries explicitly.

## Standing Anti-False-Pass Rules

- No static verdict dictionaries, handwritten scores, unconditional clean reports,
  or tests that only assert pass.
- Baselines must be independent callable implementations under the same budget
  and input boundary as the candidate.
- Ablations must rerun episodes under real interventions.
- Leakage scans must include a real scanner and at least one positive control.
- Replay must recompute behavior from serialized state and observation.
- Any unused frozen seed, heldout context, train context, or counterfactual pair
  blocks the evidence claim.

## Next Minimal Closed-Loop Action

Complete Phase 0 validation, then decide whether the next bounded task is
recovery closeout, independent audit of the recovery inventory, or a separate
Phase 1 problem-formalization task card.
