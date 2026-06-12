# POST-BRIDGE-ADMISSION-EXECUTABLE-001C-REDTEAM-LEAKAGE-BLOCKER-ADMISSION-001A

## Verdict

`post_bridge_admission_executable_001c_redteam_leakage_blocker_admission_001a_block_leakage_scanner_not_fail_able_admitted`

The external red-team blocker is admitted. The committed 001C leakage gate does
not provide sufficient fail-able coverage for real leakage surfaces under
`COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A`.

## Layer

Bounded external red-team leakage blocker admission only.

This is not a new 001C run, not a repair, not a rerun, not an EGO mainline
entry, and not a readiness claim.

## Anchors Verified

- 001C remote anchor: `remote-anchor-001k-df0e3e5` ->
  `df0e3e545db56f302f4c27f5e39b549470972b33`
- EGO readiness audit remote anchor: `remote-anchor-001l-ed9355b` ->
  `ed9355b464162065dfbba77a6a6ebfad22cb1767`

## Bounded Audit

Strongest baseline explanation:

001C attempted to add computed leakage scans with positive and clean controls.
The nominal artifact shows `leakage_gate_passed=true`, positive controls passed,
clean controls passed, and real scans clean.

Strongest reason the task could be invalid:

If the committed scanner had consumed full real candidate inputs, full trace
rows, full observation objects, full artifact inventory paths, and full metric
provenance rows, with positive controls injected into copies of those same
surfaces, then the red-team claim would fail. The current committed code does
not show that.

Falsifier for the current admission framing:

Evidence would need to show that each scanner's real scan receives the same
surface class that the positive control mutates, and that injected forbidden
fields such as `future_observation` or `oracle` block when inserted into copies
of actual trace rows, candidate inputs, observations, artifact path lists, and
metric provenance rows.

Insufficient evidence:

Synthetic positive-control detection alone is insufficient. A clean report over
sanitized projections is insufficient. Metric provenance rows that name broad
input artifacts but not actual scanned surface IDs are insufficient.

Mechanism versus resemblance:

This task tests evidence-gate fail-ability. It does not test bridge mechanism
validity, EGO readiness, agency, selfhood, consciousness, or real user benefit.

## Evidence

1. `src/post_bridge_admission_executable_001c/core.py:1375-1402` builds
   `real_surfaces` from projections and constants. `candidate_inputs` are only
   `serialized_state_hash` and `observation_hash`; `trace_rows` are only
   `episode_id`, `candidate_input_hash`, and
   `forbidden_candidate_inputs_absent`; `artifact_paths` is a constant object,
   not an artifact inventory.

2. `src/post_bridge_admission_executable_001c/core.py:1404-1407` uses the same
   decoupled synthetic positive control for every scanner:
   `{"positive_control": "future_observation"}`. It does not inject forbidden
   fields into the corresponding real scanned surface.

3. `src/post_bridge_admission_executable_001c/core.py:163-177` lists required
   leakage scanners. There is no `metric_provenance` scanner.

4. `src/post_bridge_admission_executable_001c/runner.py:576-584` records
   leakage metric provenance using broad input artifact paths
   `trace.jsonl`, `serialized_state_snapshots.jsonl`, and
   `serialized_state_provenance.jsonl`. The provenance does not identify the
   in-memory sanitized surfaces actually consumed by `run_leakage_scanners`.

5. `src/post_bridge_admission_executable_001c/core.py:671` emits
   `forbidden_source_scan_result: {"clean": True, "hits": []}` as a constant in
   serialized-state provenance rows.

6. `tests/test_post_bridge_admission_executable_001c.py:288-301` asserts that
   positive controls detect, clean controls do not detect, and real scans are
   clean. It does not assert failure when forbidden fields are injected into
   copies of actual real surfaces.

7. A read-only probe against committed artifacts showed that a copied real
   trace row with an injected `future_observation` field is detectable by
   `leakage_scan_surface`, but the canonical 001C gate did not run that probe
   against the full row. It scanned the projected `trace_rows` surface instead.

## Decision

- 001C nominal pass remains a historical artifact result.
- 001C nominal pass is blocked as current downstream positive evidence.
- `EGO-MAINLINE-READINESS-AUDIT-001A` is conditional and non-actionable until a
  new bounded executable rerun fixes the leakage scanner gate.
- The next allowed executable repair path is a bounded 001D or equivalent task
  card. This admission does not create that task card.

## Minimum Patch Direction

The next executable should preserve 001C baseline, ablation, replay,
frozen-input, and mutation improvements, but repair leakage fail-ability by
scanning full real surfaces and coupling positive controls to those same
surfaces.

Required repair themes:

- scan full trace rows, not sanitized trace projections
- scan full candidate inputs, including serialized state text and observation
  object
- add observation artifact and row scanners
- scan actual artifact filename and path inventory
- scan full metric provenance rows
- remove or replace unconditional clean constants
- inject forbidden fields into copies of real trace rows, serialized states,
  observation rows, artifact path lists, and metric provenance rows
- keep clean controls on the same real surface classes
- make leakage metric provenance identify real consumed surface IDs
- add tests that fail before the scanner repair and pass after it

## Stop Conditions

This admission must not modify old 001C artifacts, old 001B artifacts,
`EGO-MAINLINE-READINESS-AUDIT-001A` artifacts, or any EGO mainline runtime.

## Claim Ceiling

Bounded external red-team leakage blocker admission evidence only.

This cannot prove bridge readiness, EGO readiness, companion readiness,
mechanism validity, theory validity, agency, selfhood, consciousness, real
relationship learning, real emotion, subjective experience, stable user benefit,
or future EGO runtime correctness.
