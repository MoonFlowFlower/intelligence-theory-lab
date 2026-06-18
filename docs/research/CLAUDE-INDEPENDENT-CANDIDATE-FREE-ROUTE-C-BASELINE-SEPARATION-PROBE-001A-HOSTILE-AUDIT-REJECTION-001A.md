# Claude Independent Candidate-Free Route C Baseline-Separation Probe 001A Hostile-Audit Rejection 001A

## Verdict

`reject_as_false_positive_or_weakened_baseline`

## Authorization Status

- Implementation authorized: `false`
- Route C re-promotion authorized: `false`
- New surface preflight authorized: `false`
- Candidate implementation authorized: `false`
- Gate run authorized: `false`
- Auto-Remote-Anchor: `forbidden`

## Current Layer

engineering-governance / hostile-audit rejection preservation only

## Mainline Integration Status

none

## Enabled Status

local docs/artifacts preservation only

No runtime path, no Gate path, no mainline path, no candidate path, and no enabled Route C re-promotion path are authorized by this preservation.

## Real-Trigger Evidence

The trigger evidence is the hostile audit bundle:

`artifacts/CLAUDE-INDEPENDENT-CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A-HOSTILE-AUDIT-001A/`

and the normalized clean-room reproduction preserved under:

`artifacts/claude_independent_candidate_free_route_c_baseline_separation_probe_001a_hostile_audit_rejection_001a/`

The clean-room reproduction independently regenerates the toy episodes without importing the Codex probe module.

## Rejected Probe Claim

The rejected probe reported:

- oracle score: `1.0`
- strongest fair baseline: `mean = 0.5833333333333334`
- delta: `0.41666666666666663`
- verdict: `separation_exists_route_c_may_repromote_one_surface`

This probe output is rejected as a false positive / weakened-baseline result.

## Blocking Reasons

1. The scoring function was recall-only:

   `score = |truth & prediction| / |truth|`

   It did not penalize false positives and did not cap prediction-set size for passive baselines.

2. The baseline panel omitted the strongest legal fair baseline:

   `predict_all`

   That baseline predicts all legal items and reaches recall `1.0 == oracle` under the probe metric.

3. The visible feature stream and hidden-set stream were generated from independent salts. The preserved reproduction reports `corr(visible_score, hidden_membership) = 0.0029`, so visible features carry approximately zero signal about hidden membership.

4. The full-budget saturation control was computed but not consumed by the final decision path.

5. The old probe's green tests are not evidence of Route C separation because they asserted the false-positive condition, including the original `separation_exists_route_c_may_repromote_one_surface` verdict.

## Clean-Room Reproduction Readback

Required command:

```powershell
python cleanroom_reproduction.py
```

Preserved output facts:

- `oracle(reads hidden_set)` mean recall: `1.0000`
- `mean (probe strongest_fair)` mean recall: `0.5833`
- `predict_all (fair, omitted)` mean recall: `1.0000`
- `threshold_min (mean-family)` mean recall: `1.0000`
- `corr(visible_score, hidden_membership) = 0.0029`
- conclusion: strongest admissible fair baseline reaches oracle recall, so delta is `0.0`

## Decision

The candidate-free Route C baseline-separation probe cannot be cited as Route C re-promotion evidence.

Current Route C resurrection from this probe is blocked. The next route decision must return to Gate-oriented or alternative mechanism route selection unless a separately authorized route-level decision provides a new mechanism rationale and baseline-immunity argument.

## Claim Ceiling

Hostile-audit rejection preservation only.

This preservation proves only that the Codex candidate-free Route C separation probe cannot be used as Route C re-promotion evidence.

This does not prove:

- Route C mechanism validity
- Route C impossibility
- hidden-self-set inference
- self-boundary evidence
- candidate success
- Gate pass
- mainline/runtime/live effect
- agency
- autonomy
- consciousness
- emotion
- stable user benefit
- EGO readiness

## Next Minimal Closed-Loop Action

Return to Gate-oriented or alternative mechanism route selection.

Do not continue repairing Route C unless a separately authorized route-level decision provides a new mechanism rationale and baseline-immunity argument.
