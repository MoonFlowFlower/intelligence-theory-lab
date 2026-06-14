# NEXT-CONCRETE-SURFACE-ADMISSION-TASK-CARD-001A

## Verdict

`next_concrete_surface_admission_task_card_001a_pass`.

This document is a bounded task card only. It does not execute a surface,
implement candidate behavior, modify validators, run Gate4 or Gate5 candidates,
enter bridge/runtime/mainline scope, or claim mechanism validity.

## Current Status

- Current layer: `engineering-governance / concrete surface-admission task-card drafting only`
- Mainline integration status: `none`
- Enabled status: `task card only; no enabled runtime, bridge, Gate, tournament, candidate, mechanism surface, companion, or EGO-mainline path`
- Real trigger evidence: current repo/artifact readback matched the preserved `NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C-RERUN-001A` closure boundary before this card was drafted
- Claim ceiling: `concrete surface-admission task-card drafting only`
- Next minimal closed-loop action: run the future card below only after review of this drafting result and without upgrading claims

## Drafting Start-State Readback

- Branch: `codex/meta-theory-scaffold`
- Local HEAD: `1cbc680b9209707c3142168db6f2d65ef9367265`
- Remote branch: `1cbc680b9209707c3142168db6f2d65ef9367265`
- Local tag: `remote-anchor-next-surface-admission-manifest-instantiation-001c-rerun-001a-1cbc680`
- Local tag target: `1cbc680b9209707c3142168db6f2d65ef9367265`
- Local tag type: `commit`
- Remote tag target: `1cbc680b9209707c3142168db6f2d65ef9367265`
- Ahead/behind: `0 0`
- Worktree status before drafting: clean

Rerun artifact readback from
`artifacts/next_surface_admission_manifest_instantiation_001c_rerun_001a/result.json`
and
`artifacts/next_surface_admission_manifest_instantiation_001c_rerun_001a/verification_readback.json`:

- Rerun verdict: `next_surface_admission_manifest_instantiation_001c_rerun_001a_pass`
- Valid manifest authorized: `true`
- Negative controls blocked: `6/6`
- Ablations blocked: `10/10`
- Dependency-structure controls blocked: `4/4`
- Replay recomputation: `true` over `21` trace rows
- Stop conditions: none

## Inherited Boundaries

This card inherits only the authorization-validator closure boundary and prior
negative evidence below:

1. Original blocked dependency-enforcement failure:
   `NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001C` preserved
   `blocked_validator_gap_repair_001b_dependency_not_enforced`.
   It recorded `6/6` negative controls blocked, `9/10` ablations blocked, and
   `0/4` dependency-structure controls blocked.
2. Repaired validator boundary:
   `FUTURE-SURFACE-ADMISSION-AUTHORIZATION-VALIDATOR-GAP-REPAIR-001C`
   repaired the dependency-structure enforcement gap for the 001C manifest.
3. Preservation boundary:
   `b6f659588099e9eeecf4815d779784b5e80df630`.
   The preservation tag
   `remote-anchor-future-surface-admission-authorization-validator-gap-repair-001c-0ae1bcd`
   points to this preservation commit, not directly to the preserved repair
   commit `0ae1bcd530247338224e9bda2e179fb1b0538c80`.
4. Closure rerun boundary:
   `1cbc680b9209707c3142168db6f2d65ef9367265` with tag
   `remote-anchor-next-surface-admission-manifest-instantiation-001c-rerun-001a-1cbc680`.

## Known Stale Legacy Check

A broader legacy check still expects the pre-repair 001C blocker when the old
001C runner is executed against the repaired validator. This card does not edit
that stale legacy test. The future task below must either scope that check out
as a known stale expectation for this concrete surface-admission step or require
a separate legacy expectation reconciliation task before any broad-suite green
claim.

## Future Executable Task Card

### Task ID

`MINIMAL-NON-CANDIDATE-SURFACE-ADMISSION-PREFLIGHT-001A`

### Concrete Surface Identifier

`minimal_non_candidate_surface_admission_preflight_for_future_mechanism_family_direction`

This identifier is the normalized form of the current artifact field
`proposed_surface_admission_direction`:

`Minimal non-candidate surface-admission preflight for a future mechanism-family direction`

This is not a mechanism candidate, Gate4 candidate, Gate5 candidate, bridge,
runtime, tournament, companion, or EGO-mainline surface. If a future executor
cannot derive this identifier from
`artifacts/next_surface_admission_manifest_instantiation_001c/manifest.json`
without memory or guesswork, it must stop with
`blocked_no_concrete_surface_identifier`.

### Problem Definition

Execute a local, offline surface-admission preflight that tests whether the
normalized concrete surface identifier above can be admitted as a later
mechanism-family task-card direction using enforceable dependency, baseline,
ablation, leakage, replay, and claim-ceiling checks.

The task must produce computed evidence for admission or fail-closed blockers.
It must not execute a mechanism surface, implement candidate behavior, run Gate4
or Gate5, enter bridge/runtime/mainline/tournament scope, or use old invalid
surface artifacts as mechanism evidence.

### Stage / Layer

`engineering-governance / concrete surface-admission preflight only`

The task may implement an isolated local validator/harness for the preflight.
It may not implement or evaluate the mechanism family itself.

### Mainline Target

None.

No EGO runtime, bridge, Gate, tournament, candidate, companion, UI, API,
external service, deployment, or mainline integration is a target of this task.

### Enabled Requirement

The only enabled path may be an explicit local/offline command for this preflight,
for example a repository-local Python module or script under the allowed isolated
paths. The task must not create a passive import side effect, background runner,
UI path, service, runtime hook, bridge hook, Gate entrypoint, tournament runner,
candidate behavior path, or EGO-mainline trigger.

### Real-Trigger Requirement

Before execution, the future task must read current repo/artifact state and
record:

- current branch;
- local HEAD;
- worktree status;
- relevant remote branch/tag readback when the task depends on anchored state;
- source manifest path and hash:
  `artifacts/next_surface_admission_manifest_instantiation_001c/manifest.json`;
- closure rerun artifact paths and hashes under
  `artifacts/next_surface_admission_manifest_instantiation_001c_rerun_001a/`;
- preservation tag target for
  `remote-anchor-future-surface-admission-authorization-validator-gap-repair-001c-0ae1bcd`;
- closure tag target for
  `remote-anchor-next-surface-admission-manifest-instantiation-001c-rerun-001a-1cbc680`;
- explicit readback of the known stale legacy check status.

The executable preflight must then invoke its real callable validation path on
the serialized concrete surface input and on each baseline, ablation, leakage,
and replay case. Stored verdicts, static dictionaries, hand-written scores, and
tests that only assert pass are not evidence.

### Hypothesis

If the 001C authorization-validator closure is valid, then this concrete
non-candidate surface-admission preflight can distinguish an enforceable,
dependency-complete surface-admission direction from narrative authorization,
missing-dependency authorization, label leakage, stored-verdict replay, and
forbidden scope expansion.

### Strongest Baseline / False Success Explanation

The strongest false success is a polished admission report or checklist that
passes because it recognizes expected text, task IDs, filenames, or stored
verdicts rather than recomputing authorization from the serialized surface
input. A second false success is a validator that blocks only hard-coded
negative cases while accepting equivalent narrative, alias, metadata-only, or
scope-leaking forms.

The future result must compare against independent callable baselines and must
report baseline equivalence as a blocker, not as admission evidence.

### Required Independent Baselines

The task must implement and invoke independent callable baselines:

- `static_required_field_check_baseline`: checks only required keys and types;
- `keyword_or_task_id_match_baseline`: checks expected labels, task IDs, or
  phrases without enforcing structural dependencies;
- `stored_verdict_replay_baseline`: attempts to reuse stored verdicts or trace
  hashes without recomputation;
- `dependency_name_lookup_baseline`: recognizes dependency names without
  verifying required task IDs, hashes, or tag targets.

If the candidate preflight is behaviorally equivalent to any simpler baseline on
admission, blockers, or replay outcomes, the verdict must be
`blocked_baseline_equivalence`.

### Required Ablations

The task must rerun the callable preflight under real interventions that mutate
serialized inputs. Required ablations include:

- remove the concrete surface identifier;
- replace the surface identifier with Gate5, bridge, runtime, tournament,
  candidate, companion, or EGO-mainline scope;
- remove the 001C blocker inheritance;
- remove the 001C validator repair inheritance;
- replace the preservation tag target with the preserved repair commit as if it
  were the tag target;
- remove the closure rerun boundary;
- remove code path hash, producer function, run ID, or input case IDs;
- remove baseline invocation;
- remove ablation invocation;
- remove leakage positive-control invocation;
- replace replay recomputation with stored hash comparison only;
- hide or delete the known stale legacy check caveat;
- add a mechanism score, readiness claim, agency claim, autonomy claim,
  subjectivity claim, consciousness claim, emotion claim, runtime-readiness
  claim, companion-readiness claim, stable-user-benefit claim, or mainline-effect
  claim.

Every ablation must rerun the same callable path. Expected outcome: blocked.

### Leakage Scan With Positive Controls

The task must implement a real scanner with at least one positive-control case
for each leakage channel below:

- expected verdict embedded in a filename, task ID, case ID, artifact path, or
  serialized input field;
- label leakage through strings such as `authorized`, `blocked`, `pass`, or
  `expected`;
- future-observation or downstream-result leakage into admission input;
- old invalid surface artifacts cited as mechanism evidence;
- renderer-visible or narrative-only behavior treated as causal evidence;
- hidden allowlist keyed to known case IDs;
- stored-verdict or hash-only replay substitution.

Each positive control must be detected. Any undetected positive control must
block the evidence claim with `blocked_leakage_positive_control_failed`.

### Replay / Recomposition Requirement

Replay must recompute the preflight decision from `serialized_surface_input`
plus the current observation/readback fields. It must not accept stored
verdicts, stored actions, trace-only equality, or hash-only equality as replay.
Replay output must record the recomputed decision, reasons, producer function,
input hashes, code path hash, and match status for every case.

### Computed-Evidence Provenance Gate

Every future result, baseline, ablation, leakage scan, replay report, and final
verdict must record:

- producer function;
- input artifact paths and hashes;
- input case IDs;
- run ID;
- seed, context, or episode IDs when applicable, or `not_applicable` with a
  reason;
- aggregation rule;
- code path hash;
- baseline producer function;
- ablation intervention and rerun evidence;
- leakage scanner and positive-control case;
- replay producer function and evidence that replay recomputed from serialized
  state plus observation, not stored hashes only.

Any missing provenance field, unused frozen seed, unused train context, unused
heldout context, unused counterfactual pair, unused baseline, unused ablation,
unused leakage positive control, or unused replay case must block the evidence
claim.

### Acceptance Gate

The future task may report
`minimal_non_candidate_surface_admission_preflight_001a_pass` only if all of the
following hold:

1. The concrete surface identifier is derived from the current 001C manifest,
   not from memory or a newly invented direction.
2. The inherited 001C blocker, 001C repair, preservation boundary, and closure
   rerun boundary are read and preserved.
3. The known stale legacy check is preserved as a caveat or routed to a separate
   reconciliation task before any broad-suite green claim.
4. All required independent baselines are invoked.
5. Baseline equivalence is absent under the predeclared equivalence rule.
6. All required ablations are invoked through the same callable path and block.
7. Leakage scanner positive controls are invoked and detected.
8. Replay recomputes from serialized input plus observation and is not hash-only.
9. Computed-evidence provenance is complete for every result.
10. No forbidden scope opens.
11. No forbidden positive claim appears.
12. Changed files stay within the allowed paths.
13. Worktree status and git diff are reported at start and end.

### Expected Verdicts

Expected pass verdict:

`minimal_non_candidate_surface_admission_preflight_001a_pass`

Expected blocker verdicts include:

- `blocked_no_concrete_surface_identifier`
- `blocked_start_state_or_anchor_mismatch`
- `blocked_missing_inherited_boundary`
- `blocked_stale_legacy_check_hidden`
- `blocked_report_shaped_preflight_without_failability`
- `blocked_baseline_not_invoked`
- `blocked_baseline_equivalence`
- `blocked_ablation_not_invoked`
- `blocked_ablation_authorized`
- `blocked_leakage_positive_control_missing`
- `blocked_leakage_positive_control_failed`
- `blocked_replay_not_recomputed`
- `blocked_computed_evidence_provenance_gap`
- `blocked_forbidden_scope_opened`
- `blocked_claim_ceiling_violation`
- `blocked_scope_violation`

### Claim Ceiling

Concrete surface-admission preflight evidence only.

This does not prove mechanism validity, Gate validity, Gate4 validity, Gate5
validity, candidate behavior, agency, autonomy, consciousness, emotion,
subjectivity, companion readiness, EGO readiness, runtime readiness, stable user
benefit, or mainline effect.

### Stop Condition

Stop immediately if:

- the concrete surface identifier cannot be derived from the current manifest;
- inherited boundary readback differs from current repo/artifact evidence;
- the known stale legacy check is hidden or silently edited;
- the task would execute a mechanism surface or candidate behavior;
- the task would enter Gate4, Gate5, bridge, runtime, tournament, companion, or
  EGO-mainline scope;
- baseline, ablation, leakage, replay, or provenance requirements would be
  bypassed;
- forbidden files would be modified;
- forbidden positive claims appear.

### Rollback Plan

If the identifier, inherited boundaries, or stale legacy caveat cannot be
verified, preserve a blocker result under the task artifact directory and do not
invent a replacement identifier. If implementation starts and a scope violation
appears, revert only the future task's own uncommitted changes and preserve the
blocker readback. Do not modify prior artifacts or legacy tests to make the
result pass-shaped.

### Changed / Forbidden Files

Allowed future changes:

- `src/minimal_non_candidate_surface_admission_preflight_001a/**`
- `tests/test_minimal_non_candidate_surface_admission_preflight_001a.py`
- `artifacts/minimal_non_candidate_surface_admission_preflight_001a/**`
- `docs/research/MINIMAL-NON-CANDIDATE-SURFACE-ADMISSION-PREFLIGHT-001A.md`

Forbidden future changes:

- existing authorization-validator source;
- existing tests outside the allowed future test file;
- prior artifacts;
- Gate files;
- mechanism files;
- bridge/runtime files;
- candidate/tournament files;
- companion/product files;
- EGO-mainline runtime;
- unrelated governance templates.

### Auto-Remote-Anchor Decision

`forbidden`

The future task may not auto-anchor its result in the same session. Any future
surface-admission preflight result must first be reviewed because it would be
new executable evidence, not just task-card drafting. A separate task card may
authorize publication after review.

## Acceptance Gate For This Drafting Task

This drafting task passes because:

- start-state readback matched the preserved `1cbc680...` boundary;
- the output is a concrete executable future task card;
- no concrete surface was executed;
- 001C blocker, repair, preservation, and rerun closure boundaries are
  inherited;
- the known stale legacy check is preserved as caveat;
- the future card requires fail-able baseline, ablation, leakage, replay, and
  computed-evidence checks;
- claims stay bounded to surface-admission task-card drafting;
- changed files are restricted to
  `docs/research/NEXT-CONCRETE-SURFACE-ADMISSION-TASK-CARD-001A.md` and
  `artifacts/next_concrete_surface_admission_task_card_001a/**`.

## What This Does Not Prove

This does not prove mechanism validity, Gate validity, Gate4 validity, Gate5
validity, candidate behavior, agency, autonomy, consciousness, emotion,
subjectivity, companion readiness, EGO readiness, runtime readiness, stable user
benefit, or mainline effect.
