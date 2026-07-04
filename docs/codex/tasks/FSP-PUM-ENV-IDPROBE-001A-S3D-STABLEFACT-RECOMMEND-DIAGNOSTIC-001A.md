# FSP-PUM-ENV-IDPROBE-001A — S3d Stable-Fact Recommend Diagnostic 001A

Status: **AUTHORIZED bounded diagnostic** (cheap, pre-battery). Two jobs: (0) reconcile the
`factored_filter.py` provenance discrepancy by re-verifying the on-disk file passes the repair
gates, and (1) determine whether the `rag_should_win_stable_facts` cell yields a well-defined,
above-chance **recommend-conditional** ideal at aggregate scale — the operative metric for the rag
certificate (spec §3 / line 70: recommend-turn-conditional ρ ≥ 0.50). Does NOT run the full
battery, does NOT change the spec / ρ / thresholds / cert cells / the filter.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-STABLEFACT-RECOMMEND-DIAGNOSTIC-001A`

## why
The repair report shows, at eval user 640, `recommend_turn_conditional_metric = 0.0` for the
**ideal AND nearest_neighbor AND rag** on `stable_facts` — below chance (1/32 ≈ 0.03125). That is
the metric the rag should-win certificate is anchored on. The repair's ideal-sanity gate only
checked the OVERALL metric, so it did not validate this. Each user has only 7–9 recommend turns, so
single-user recommend-conditional is very coarse; all-three-0.0 with correct filter code points to a
cell/metric-scale question, not a filter bug. Running the full battery (~16–19 CPU-h) before
resolving this risks an ill-defined ρ_rag (denominator `ideal_recommend − chance ≤ 0`).

## step 0 — on-disk provenance reconciliation (BLOCKING)
Sandbox `factored_filter.py` sha256 = `0e367149…`; the repair report stated `31ee442c…` (the 4
other repair files matched). Not EOL (file is pure LF). Before diagnosing:
1. Recompute and report the host sha256 of `src/fsp_pum_env/factored_filter.py`.
2. Re-run the repair's regression + oracle gates on the **current on-disk** file:
   - `camouflage_off` one-eval-user ideal metric MUST equal `0.09948462995337995` exactly;
   - oracle two-user identical-recommend-prefix probe: identical posterior/prediction across
     different true stable-fact seeds.
   If either fails on the on-disk file → STOP (the delivered file is not the validated one; the
   repair must be re-delivered). This closes the hash discrepancy behaviorally regardless of the
   exact number.

## step 1 — multi-user recommend-conditional diagnostic
- Pre-registered users: k = 10 eval users from the `stable_facts` cell eval-user list sorted
  ascending, fractional indices {0, 1/9, …, 1} (deterministic; record resolved ids). Heldout
  800–999 forbidden.
- For each user run the on-disk exact **ideal**, `nearest_neighbor_user_matching`, and
  `rag_k5_episode_retrieval`; compute **recommend-conditional** macro-balanced-accuracy per user AND
  pooled over all recommend turns across the k users; report chance = 1/32.
- Posterior-concentration mechanism check (≥2 users): dump the ideal's stable-fact posterior entropy
  trajectory over recommend turns and whether its argmax converges to the true stable fact. The true
  stable fact MAY be referenced **post-hoc for this comparison only** — it must NEVER enter the
  belief update (oracle red line preserved).

## decision (report the verdict; do not act on the battery)
- `CELL_CERTIFIABLE` if pooled ideal recommend-cond ≥ chance + 0.02 AND ideal ≥ each member on
  pooled recommend-cond → the rag cell is well-posed at scale; green-light the battery + repair bank.
- `CELL_DEGENERATE` if pooled ideal recommend-cond ≤ chance → even the optimal predictor cannot beat
  chance on the recommend channel → escalate to an operator spec decision on the rag cell (adjust
  peaked strength 3.2 / recommend-turn density / threshold, or downgrade the rag cell). Do NOT run
  the battery.
- `METRIC_COARSENESS` if the ideal's posterior demonstrably concentrates on the true fact
  (entropy ↓, argmax → true) yet pooled recommend-cond stays low → the 7–9-turn metric is the
  limiter; the 160-user battery aggregate will resolve it; proceed with the caveat recorded.

## claim ceiling
Diagnostic only: classifies the rag-cell recommend-channel + reconciles filter provenance. No S3d
certificate, NULL, environment-validity, gap, mechanism, learning, agency, or EGO claim.

## stop condition
STOP + failure_manifest if: step-0 regression/oracle fails on-disk; any heldout user touched; the
posterior update is found to read the stable-fact truth/seed; a spec/threshold change would be
needed. Preserve failures; do not patch.

## artifacts (under artifacts/FSP-PUM-ENV-IDPROBE-001A/)
`s3d_stablefact_recommend_diagnostic.json` (on-disk filter hash + step-0 regression/oracle results;
per-user + pooled recommend-cond for ideal/NN/rag; chance; posterior-entropy trajectories for ≥2
users; verdict), a trace, `failure_manifest.json` if anything fails, `claim_ceiling`.

## rollback / dev rules
Read-only w.r.t. the filter and spec (no edits); isolated new diagnostic script; Codex runs no git;
emit an operator bank-ops proposal and STOP for Claude audit. Forbidden: touching heldout;
changing spec/ρ/thresholds/cert cells/filter; feeding stable-fact truth into the belief update;
patching; git.
