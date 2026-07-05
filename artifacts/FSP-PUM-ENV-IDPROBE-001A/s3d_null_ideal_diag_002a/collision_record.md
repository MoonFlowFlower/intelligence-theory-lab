# S3D-NULL-IDEAL-DIAG-002A collision record

## Candidate 1: minimal implementation

- Approach: copy or wrap the 001A diagnostic harness, score G1/G2 on the two requested
  cells, and read available G3 rows from `trace_void_line30_v1.jsonl`.
- Evidence produced: true-style oracle, wrong-style oracle, per-user support, and
  void/reference member rows.
- Strongest cheap baseline that could match it: a metric-only reproduction that
  accidentally reuses the true style map for both G1 and G2.
- Leakage / hard-coding risk: accidentally using cell labels to choose predictions or
  using stored ideal metrics instead of recomputing rows.
- Smallest falsifying test: G1 row-level recomputation fails to reproduce the void
  ideal metric for either cell.
- Expected failure mode: import/path mismatch with the 001A harness or canonical
  metric mismatch.

## Candidate 2: strongest baseline / shortcut explanation

- Approach: treat G2 collapse to chance as evidence that the real-cell oracle score is
  mostly a `style_map` privilege; compare against available member rows only as
  reference.
- Evidence produced: wrong-style oracle near chance and G3 far below G1.
- Strongest cheap baseline that could match it: a deranged style map that is invalid
  for the filter interface and collapses for an implementation reason rather than an
  access-boundary reason.
- Leakage / hard-coding risk: declaring wide privilege from recommend-only or small
  finite support instead of the full `640..799` overall metric.
- Smallest falsifying test: G2 stays near G1 on both requested real cells.
- Expected failure mode: mixed cell behavior that does not satisfy either binary
  branch.

## Candidate 3: mechanism-faithful implementation

- Approach: reuse the 001A row-level `FactoredExactFilter` path, use the same
  trajectory generation and true observations, vary only the `style_map`, and record
  full per-user support over users `640..799`.
- Evidence produced: a direct intervention on the oracle's `style_map` input while
  holding design, seeds, cells, eval users, actions, and target observations fixed.
- Strongest cheap baseline that could match it: real cells are dominated by
  action-conditioned or θ-conditioned structure rather than style privilege, so both
  true and wrong style can remain above chance.
- Leakage / hard-coding risk: thresholding `≈` after seeing the result; mitigated by
  the task-card retention rule before execution.
- Smallest falsifying test: wrong-style overall headroom retention below 80% in either
  requested cell or G1 reproduction mismatch.
- Expected failure mode: G2 partially degrades but does not collapse, yielding a mixed
  diagnostic rather than either pre-registered branch.

Selected approach: Candidate 3, with Candidate 1's void/reference G3 readback and an
artifact-local collapsed trust-state oracle for the two requested variants. The
collapsed path is allowed only because the full-atom direct attempt timed out before
evidence and because G1 must reproduce the void exact-filter metric before G2 can be
interpreted.
