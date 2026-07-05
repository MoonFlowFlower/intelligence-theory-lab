# S3D-NULL-IDEAL-DIAG-002A attempt log

- Attempt 1: direct 001A-style full `FactoredExactFilter` scoring for G1/G2 over both
  requested cells and all users `640..799`.
- Result: no evidence artifact was produced before the local command timed out after
  approximately 1204 seconds. The spawned Python process was stopped by Codex.
- Preserved lesson for this diagnostic: direct full-atom scoring is too slow for the
  requested 4 full cell/style passes in this execution window.
- Bounded repair to the diagnostic harness, not to project source: switch the 002A
  artifact script to a collapsed trust-state exact oracle for only `low_diversity` and
  `flat_theta`, guarded by exact G1 reproduction against the void trace.
- Claim ceiling: failed attempt / diagnostic-plumbing evidence only; no result claim.
