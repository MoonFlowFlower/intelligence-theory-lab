# S3D-NULL-IDEAL-DIAG-002A task card

Task id: `S3D-NULL-IDEAL-DIAG-002A`

Problem definition: diagnose whether the oracle-ideal's `style_map` privilege from
`S3D-NULL-IDEAL-DIAG-001A` is local to `NULL_env` or also drives the oracle score in
real should-win certificate cells, which would inflate the ρ denominator beyond the
NULL control.

Current layer: engineering implementation + mechanism-instrument diagnostic. This is
not a mechanism-validity, agency, EGO-mainline, or consciousness task.

Mainline target: no mainline target. Artifact-local diagnostic only under
`artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_null_ideal_diag_002a/`.

Enabled-state requirement: use current repo worktree read-only and reuse the 001A
artifact-local diagnostic harness/import path. No `src/`, spec, runner, or banked
artifact edits.

Real-trigger evidence requirement: run the callable diagnostic on the two requested
real certificate cells (`low_diversity`, `flat_theta`) over eval users `640..799`,
with a trace and per-user support generated from the run.

Hypothesis: if wrong/deranged `style_map` leaves the real-cell oracle score near the
true-style oracle score, the `style_map` privilege isolated in 001A is NULL-local.

Strongest baseline / shortcut explanation: the exact ideal may score high in real
cells because `style_map` directly exposes the target symbol surface, so deranging the
map could collapse the real-cell oracle score toward chance and reveal a wide
equal-access violation.

Ablation requirement: for each requested cell, compute:
- G1 oracle-ideal with true `style_map`;
- G2 same oracle path with deranged/wrong `style_map`;
- G3 assigned should-win member metric as reference-only, by reading the void trace
  where available and reporting missing assigned rows explicitly.

Trace/replay requirement: write row-level trace for G1/G2 and a per-user support CSV;
record input hashes, producer function names, run id, eval user ids, aggregation rule,
and code path hash.

Computed-evidence provenance gate: verdict, metrics, per-user support, and G3
reference values must be produced by the callable 002A script, not hand-entered
literals.

Performance/equivalence gate: a first direct full-atom exact-filter attempt exceeded
the local execution window without producing evidence. The diagnostic may use an
artifact-local collapsed trust-state exact oracle for `low_diversity` and `flat_theta`
only because those two variant tables are independent of non-trust theta coordinates.
This acceleration is admissible only if G1 true-style reproduces the void exact-filter
ideal metric for both cells within `1e-12` and a one-user spot-check matches the
full-atom filter for true and wrong style in both cells; otherwise STOP.

Acceptance gate:
- G1 reproduces the banked/void ideal metrics for the two requested cells exactly or
  within floating serialization tolerance.
- G2 is computed on the full `640..799` eval range with a deranged `style_map`.
- Findings report overall and recommend-conditional metrics per cell, plus per-user
  support location.
- Existing dirty work outside the 002A directory remains unstaged and unmodified by
  this task.

Decision rule:
- `PRIVILEGE_NULL_LOCAL` if both requested cells retain at least 80% of true-style
  overall headroom over chance under G2.
- `PRIVILEGE_RHO_WIDE` if both requested cells have G2 overall at or below
  `chance + 0.005` and the available G3 reference metric is well below G1.
- Otherwise stop as `INCONCLUSIVE_MIXED_STYLEMAP_EFFECT`.
Decision basis is the canonical overall metric for these two cells; recommend-
conditional is reported as supporting evidence only.

Claim ceiling: bounded diagnostic evidence about the scope of `style_map` privilege in
two S3d certificate cells. No fix, no S3d Gate/pass claim, no environment-validity
claim, no mechanism-validity claim, no EGO readiness, no agency, no consciousness.

Stop condition: heldout user `800..999` touched; any need to edit `src/`, specs,
runner, or banked artifacts; G1 fails to reproduce the banked/void ideal values; the
001A harness cannot be reused; or output would need to be written outside the 002A
directory.

Rollback plan: delete only the newly created
`artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_null_ideal_diag_002a/` directory if the
diagnostic must be abandoned before commit. Do not revert or modify pre-existing
worktree changes.

Expected changed files: new files only under
`artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_null_ideal_diag_002a/`.

Forbidden changes: any `src/`, `tests/`, docs outside this directory, S3d runner,
frozen design/spec files, void/banked artifacts, thresholds, ρ rules, or fix
implementation.

Auto-Remote-Anchor decision: forbidden.
