# GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001B-AMENDMENT

Task ID: GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001B-AMENDMENT

Mode: Task-card amendment + external audit preservation only.

Layer: Gate4 repair planning / evidence-contract amendment only.

Claim ceiling: bounded Gate4 001C failure-preserving repair task-card amendment only.

## Authorization Boundary

This amendment is additive to
`docs/codex/tasks/GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A.md`.
It does not modify the original 001A task card and does not draft a Gate4 001C
execution card.

This amendment does not execute Gate4 001C, Gate5, admission, runtime, bridge,
or mechanism validation. It does not restore, read, copy, import, cherry-pick,
merge, push, anchor, or use provisional Gate4 001C commit
`d7b5b7a33cc68cbe7e3ca0960b99e0082e1ac728`.

Required authorization fields:

- `gate4_001c_execution_authorized`: false
- `gate4_001c_execution_card_authorized`: false
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false
- `ego_mainline_authorized`: false

## Starting State And Audit Input

Starting HEAD: `6e5b94b0d462d4abf597eaaeaddc54a281338d55`

Preserved task-card audit report:

`docs/research/AUDIT-GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A-CLAUDE-001.md`

Claude audit verdict: `task_card_audit_failed_contract_gap`

The optional project-wide risk-surface audit text was not provided verbatim in
this task. The only preserved route guidance from the task prompt is:
`block_and_redirect away from PROJECT-WIDE scan toward bounded closure/backlog`.

## Problem Definition

Close two blocking contract gaps in 001A without converting this amendment into
execution authorization:

- B1: ambiguous `Gate4 001B` references leave sibling Gate4 001B families
  available for false-pass reuse.
- B2: the leakage contract omits whitelist / exemption / allowlist escape
  detection and does not require an anchored evidence-harness challenger over
  future Gate4 001C output bundles.

## Amendment B1: Gate4 001B Lineage Pin

For all future Gate4 001C planning and execution-card drafting, `Gate4 001B`
means the canonical rejected Gate4 001B below unless another family is named
explicitly.

Canonical rejected Gate4 001B:

- task family: `ego_mainline_gate4_preflight_executable_001b`
- artifact family: `artifacts/ego_mainline_gate4_preflight_executable_001b/`
- task card: `docs/codex/tasks/EGO-MAINLINE-GATE4-PREFLIGHT-EXECUTABLE-001B.md`
- source family: `src/ego_mainline_gate4_preflight_executable_001b/`
- test family: `tests/test_ego_mainline_gate4_preflight_executable_001b.py`
- commit: `90dc4b9082593fabf06197b03eaf66c9c64014a2`
- known role: sealed rejected boundary / negative evidence /
  positive-control false-pass case only
- forbidden role: pass evidence, Gate validity evidence, mechanism validity
  evidence, architecture correctness evidence, downstream admission evidence

Sibling Gate4 001B families that remain quarantined:

- `gate4_social_latent_inference_001b`
- `gate4_social_representational_gap_preflight_001b`

These sibling families must not be cited as positive support evidence for future
Gate4 001C, even if their historical verdict strings contain bounded-pass
language.

All 12 targets from
`EVIDENCE-HARNESS-CRITICAL-RISK-TARGET-APPLICATION-001A` remain
`quarantined_from_downstream_use` for future Gate4 001C unless a later explicit
harness-admission record says otherwise:

- `ego_mainline_gate4_preflight_001b`
- `gate2_controllability_self_boundary_001b`
- `gate3_viability_functional_affect_001b`
- `gate4_social_latent_inference_001b`
- `gate4_social_representational_gap_preflight_001b`
- `r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b`
- `r_g_gate0_gate1_gate2_gate3_canonical_micro_agent_testbed_001b`
- `representational_gap_preflight`
- `representational_gap_preflight_001b`
- `gate1_replay_consolidation_001c`
- `process_intervention_hard_distribution_001b`
- `process_intervention_hard_distribution_001b_trace_replay_rca_001a`

Targets 11-12 must remain `blocked_pending_audit`, not confirmed false-pass
contamination:

- `process_intervention_hard_distribution_001b`
- `process_intervention_hard_distribution_001b_trace_replay_rca_001a`

Future Gate4 001C execution-card tests must fail if any quarantined target,
sibling Gate4 001B bounded-pass verdict, old score, old baseline, old ablation
summary, or old replay summary is used as positive support evidence.

## Amendment B2: Whitelist Escape Leakage Contract

Future Gate4 001C execution-card leakage requirements must include:

- predeclared scanner scope
- explicit included path classes
- explicit excluded path classes with reasons
- rule that excluded paths are `not_scanned`, never `clean`
- prohibition on broad whitelist / allowlist / trusted-prefix /
  known-safe-directory behavior
- positive control placed behind a whitelist-like context
- positive control placed in an excluded-looking path
- clean control evaluated through the same callable scanner path
- failure if a positive control is missed
- failure if scanner output is an unconditional clean report
- failure if scanner has a broad exemption that bypasses `result.json`,
  reports, matrices, tests, manifests, or output bundles

No future execution-card leakage scanner may mark an excluded path as clean. A
scanner may exclude a path only by recording `not_scanned` with a reason, and
the future execution verdict must treat any required unscanned path class as a
blocker unless the execution card predeclares a narrower, reviewable reason.

## Harness Challenger Requirement

The future Gate4 001C execution card must require running the anchored
evidence-harness / 001A `evaluate_bundle`-style challenger over the future 001C
output bundle.

The challenger is only a blocker, not a positive admission discriminator.

If the challenger returns `rejected_false_pass_risk`,
`blocked_pending_audit`, `insufficient_visibility`, or equivalent non-clean risk,
the future execution must block.

A clean challenger result cannot by itself authorize Gate4 001C, Gate5,
admission, runtime, bridge, or EGO mainline.

## Execution-Card Delta Requirements

If a separate future task drafts a Gate4 001C execution card, it must add these
fields before implementation:

- candidate mechanism definition with exact `src/` path and entrypoint
- exact allowed and forbidden file list
- exact test files and commands
- exact execution artifact names
- data / episode / context schema
- episode count, partner/context set, seed list, train/heldout split rule, and
  counterfactual pair construction
- per-baseline metric definitions and aggregation rules
- predeclared pass/fail thresholds and threshold-selection rule
- minimum distribution strength / sample size guard
- replay comparison rule, including exact versus tolerance and deterministic
  seed strategy
- explicit verdict taxonomy containing:
  - `failed_mechanism_test`
  - `failed_baseline_control`
  - `failed_ablation_integrity`
  - `failed_leakage_positive_control`
  - `failed_replay_recomputation`
  - `failed_provenance_gate`
  - `blocked_quarantined_evidence_reuse`
  - `blocked_provisional_001c_contamination`
- execution stop conditions and budget
- baseline independence constraints forbidding reuse of the candidate latent
  module
- same-episode-set evaluation for candidate and baselines
- provenance with input artifact hashes
- protected-artifact before/after hashes
- explicit anchored evidence-harness challenger invocation

Empty arrays such as `static_dependency=[]` must be either computed by a
callable scanner with positive controls or explicitly marked `not_tested` with
reason. Non-fail-able clean fields are forbidden.

## Acceptance Gate

This amendment is acceptable only if:

- the Claude task-card audit report is preserved verbatim
- the original 001A task card is not modified
- B1 is closed by exact task-family, artifact-family, commit-hash, and
  quarantine-inheritance entries
- B2 is closed by explicit whitelist-escape leakage requirements and positive
  controls
- all 12 quarantined targets remain forbidden as positive support evidence
- targets 11-12 remain `blocked_pending_audit`
- future execution-card authorization remains false
- Gate5/admission/runtime/bridge/EGO-mainline authorization remains false
- all JSON artifacts parse as UTF-8 without BOM
- no Gate validity, mechanism validity, theory validity, architecture
  correctness, or EGO-mainline readiness is claimed

Allowed verdicts:

- `gate4_001c_task_card_amendment_created_contract_gaps_closed`
- `blocked_missing_external_audit_report`
- `blocked_gate4_001b_lineage_ambiguity_unresolved`
- `blocked_leakage_whitelist_contract_gap_unresolved`
- `blocked_start_state_mismatch`
- `blocked_scope_violation`

## Stop Conditions

Stop and report blocked if:

- starting HEAD mismatch
- worktree has content changes before generation beyond known EOL noise
- external audit report cannot be preserved without paraphrase
- amendment cannot pin the Gate4 001B lineage unambiguously
- amendment cannot close whitelist/allowlist leakage escape
- amendment attempts to authorize execution-card drafting or Gate4 001C
  execution
- task requires touching old Gate artifacts/tests/verdicts
- task uses provisional Gate4 001C
- any authorization field becomes true

## Rollback Plan

If acceptance fails, remove only newly generated amendment/report-preservation
files:

- `docs/research/AUDIT-GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A-CLAUDE-001.md`
- `docs/codex/tasks/GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001B-AMENDMENT.md`
- `artifacts/gate4_001c_failure_preserving_repair_task_card_001b_amendment/`

Do not modify historical evidence, original 001A task card, harness artifacts,
or Gate artifacts.

## What This Does Not Prove

This amendment does not prove Gate4 validity, Gate5 readiness, admission
readiness, runtime readiness, bridge readiness, mechanism validity, theory
validity, architecture correctness, EGO-mainline readiness, agency, selfhood,
consciousness, real emotion, relationship learning, or stable autonomy.
