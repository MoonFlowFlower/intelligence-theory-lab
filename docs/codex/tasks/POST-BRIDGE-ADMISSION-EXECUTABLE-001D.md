# POST-BRIDGE-ADMISSION-EXECUTABLE-001D

## Task ID

`POST-BRIDGE-ADMISSION-EXECUTABLE-001D`

## Layer

Bounded leakage-gate repair executable post-bridge admission rerun only.

## Mandatory Contract

This task cites and enforces:

`docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md`

## Problem Definition

Run a bounded 001D replacement executable that preserves 001C's working
baseline, ablation, behavior-causal replay, frozen-input consumption,
source/artifact integrity, and mutation protections while repairing only the
001C leakage scanner fail-ability gap and directly related provenance/test
gaps.

The repaired leakage gate must scan full real surfaces, inject positive controls
into copies of those same surface classes, pass clean controls on those same
surface classes, and identify actual consumed scanned surface IDs in leakage
metric provenance.

## Wrong Problem

- Make 001C pass by weakening the leakage gate.
- Scan sanitized projections while claiming full-surface coverage.
- Use decoupled synthetic positive controls.
- Report clean leakage from constants.
- Modify old 001C artifacts or old result files.
- Proceed to EGO mainline admission.

## Current Stage

Replacement rerun after
`POST-BRIDGE-ADMISSION-EXECUTABLE-001C-REDTEAM-LEAKAGE-BLOCKER-ADMISSION-001A`.

## Parent Anchors

- `remote-anchor-001k-df0e3e5` ->
  `df0e3e545db56f302f4c27f5e39b549470972b33`
- `remote-anchor-001l-ed9355b` ->
  `ed9355b464162065dfbba77a6a6ebfad22cb1767`
- `remote-anchor-001m-557b61e` ->
  `557b61ed94b3580128ccbc8f9c164eedbbbcb462`
- `remote-anchor-001i-09cff85` ->
  `09cff85ac377aaa99f913c30e3d31f85264d1344`

## Hypothesis

If 001C's leakage scanner gap is repaired by scanning full real surfaces and by
coupling fail-able positive controls to copies of those same surfaces, then the
bounded post-bridge admission executable can produce a replacement evidence
package that is no longer blocked by the 001C leakage fail-ability defect.

## Baseline

Preserve 001C callable fair baseline implementations and invocation logging.
No baseline may be weakened or converted to a literal/static score.

## Ablation

Preserve 001C real ablation reruns under interventions and invocation logging.
No ablation sensitivity may be declared without rerunning candidate behavior.

## Trace / Replay Requirement

Behavior-causal replay must recompute candidate action from serialized state
plus observation. Trace/state hash replay remains hygiene only and must not be
reported as behavior-causal replay.

## Leakage Repair Requirement

Required full real surfaces:

- candidate input rows, including serialized state text and observation object
- trace rows
- serialized state snapshots
- observation rows
- serialized state provenance rows
- metric provenance rows
- actual artifact filename/path inventory
- fixture-name, label, verifier-only, future-observation,
  future-partner-response, later-action-label, post-hoc-metric, and
  test-only-schema surfaces when present or explicitly absent before execution

Each scanner must record scanned surface identity, surface type, source artifact
or in-memory source, scanner function, code path hash, positive-control surface
identity, and clean-control surface identity.

## Acceptance Gate

Pass only if:

- parent anchors are verified remotely
- Stage0 freeze happens before the canonical run
- the computed-evidence contract is cited and enforced
- the 001C leakage blocker is explicitly addressed
- full real leakage surfaces are scanned
- positive controls are injected into copies of those same surface classes
- clean controls pass on the same surface classes
- leakage metric provenance identifies actual scanned surface IDs
- no unconditional leakage clean constants remain
- candidate score is derived from candidate outputs or behavior-causal replay
- 001C baseline, ablation, replay, frozen-input, and mutation protections remain
  intact
- old 001B/001C and EGO readiness audit artifacts are not modified
- claim ceiling is preserved

## Stop Condition

Stop and emit the most specific blocker if any parent anchor, Stage0 freeze
item, contract citation, leakage fail-ability requirement, metric provenance
surface ID, behavior-causal replay, baseline invocation, ablation invocation,
frozen-input consumption, mutation protection, scope boundary, or claim ceiling
fails.

## Rollback Plan

Preserve failure artifacts, do not patch thresholds after results, do not weaken
baselines, do not delete negative evidence, do not modify old artifacts, and do
not enter EGO mainline.

## Claim Ceiling

Bounded post-bridge admission evidence under computed-evidence provenance
contract after leakage-gate repair only.

This cannot prove bridge readiness, EGO readiness, companion readiness,
mechanism validity, theory validity, agency, selfhood, consciousness, real
relationship learning, real emotion, subjective experience, stable user benefit,
or correctness of any future EGO runtime.
