# Preserve Candidate-Free Route C Separation Probe 001A Hostile-Audit Rejection 001A

## Verdict

`route_c_separation_probe_rejection_preserved`

## Layer

engineering-governance / hostile-audit rejection preservation only

## Mainline Integration Status

none

## Enabled Status

local docs/artifacts preservation only

## Real-Trigger Evidence

- Hostile audit artifact: `artifacts/CLAUDE-INDEPENDENT-CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A-HOSTILE-AUDIT-001A/audit_result.json`
- Clean-room reproduction output: `cleanroom_reproduction_output.txt`

## Evidence Readback

- Original probe reported oracle recall `1.0`, strongest fair baseline `mean = 0.5833333333333334`, delta `0.41666666666666663`, and verdict `separation_exists_route_c_may_repromote_one_surface`.
- Preserved clean-room reproduction reports oracle recall `1.0000`.
- Preserved clean-room reproduction reports `predict_all` recall `1.0000`.
- Preserved clean-room reproduction reports `threshold_min` recall `1.0000`.
- Preserved clean-room reproduction reports the probe `mean` baseline per-episode pattern `0.500, 0.250, 0.750, 0.250, 1.000, 0.750`, mean `0.5833`.
- Preserved clean-room reproduction reports `corr(visible_score, hidden_membership) = 0.0029`.

## Decision

The candidate-free Route C baseline-separation probe is rejected as false positive / weakened-baseline evidence. Route C cannot be re-promoted from this probe. Current Route C resurrection from this probe is blocked.

## Commands Run

```powershell
python cleanroom_reproduction.py
git diff --check -- docs/decision_log.md docs/research/CLAUDE-INDEPENDENT-CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A-HOSTILE-AUDIT-REJECTION-001A.md
```

JSON parse validation was run for `audit_verdict.json`, `result.json`, and `readback.json`.

Path allowlist check passed. Forbidden-claim scan passed. `git diff --check` exited `0` with the existing `docs/decision_log.md` LF-to-CRLF warning.

## Artifacts Generated

- `audit_verdict.json`
- `cleanroom_reproduction.py`
- `cleanroom_reproduction_output.txt`
- `result.json`
- `readback.json`
- `claim_ceiling.txt`
- `final_report.md`

## Baseline Results

- Decisive fair baseline: `predict_all`
- `predict_all` score: `1.0000`
- oracle score: `1.0000`
- delta under strongest admissible fair baseline: `0.0`

## Ablation Results

No new mechanism ablation was required or run. The preserved audit records that the old probe computed a full-budget saturation control but did not consume it in the decision path.

## Replay Result

No new replay was required or run. This preservation only reran the clean-room reproduction script.

## Stop Conditions Triggered

none

## Git Status

- Branch: `codex/meta-theory-scaffold`
- HEAD: `b45598b1c56080f2f850ae088f42cf585950483e`
- Index/staged changes: none
- Tracked diff: `docs/decision_log.md`
- New preservation paths from this task:
  - `docs/research/CLAUDE-INDEPENDENT-CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A-HOSTILE-AUDIT-REJECTION-001A.md`
  - `artifacts/claude_independent_candidate_free_route_c_baseline_separation_probe_001a_hostile_audit_rejection_001a/`
- Pre-existing dirty state remained present and was not cleaned.
- Commit/push/tag/remote-anchor: not performed.

## Claim Ceiling

Hostile-audit rejection preservation only. This proves only that this probe cannot be used as Route C re-promotion evidence.

## What This Does Not Prove

This does not prove Route C mechanism validity, Route C impossibility, hidden-self-set inference, self-boundary evidence, candidate success, Gate pass, mainline/runtime/live effect, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.
