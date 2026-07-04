# FSP-PUM-ENV-IDPROBE-001A — S3C-BATTERY-SPEC-001A

Status: DRAFT until operator banks this file; the checkpoint-commit act is the approval.
Drafted by: Claude (lab auditor role), 2026-07-02, at operator request after the S3c
executor STOP `blocked_by_missing_or_ambiguous_frozen_s3c_spec`
(artifacts/FSP-PUM-ENV-IDPROBE-001A/s3c_failure_manifest.json, sha256 640ce345…).
Drafted BEFORE any S3c model fitting; no battery scores of any kind exist at drafting
time, so all numbers below are pre-registered, not tuned.

Relationship to frozen sources: this addendum NARROWS `frozen_design.json` (blob
32d2cbd538f31694246b2e6bb7fd5377a329478f) for the five S3c battery members only. It adds
no members, deletes none, changes no thresholds, and does not modify any frozen file.
Where it borrows structure from the T5.2 `obs_decoder_gate` section it borrows the
architecture classes and budget discipline BY REFERENCE ONLY; targets, labels, and data
access are entirely different (no-conflation rule below).

## 1. Scope and no-conflation rule

Members covered (exactly the frozen `battery_membership` names):
`obs_decoder_logreg`, `obs_decoder_gbt`, `obs_decoder_gru`,
`seq_full_history_no_action_conditioning`,
`seq_window_with_action_conditioning_W15_no_cross_session_persistence`.

All five are fair-battery members under the PrefixOnlyPredictor contract:
- input: member-view fields only (action, observation.symbol, session_boundary,
  session_index, step_index, turn_in_session); never theta, z, seeds, trust internals,
  or any adjudicator-only file;
- output: the frozen prediction format (per-counterfactual-action full distribution over
  the 32-symbol response alphabet);
- training labels: next response symbols from the member view itself. NEVER theta labels.

The T5.2 `obs_decoder_gate` (theta-decoding attacker family) is a different instrument
and is NOT implemented in S3c.

## 2. Data contract

- Fitting data: the 10 frozen S3a trajectory sets (set_00..set_09), TRAIN partitions
  only (user_id 0..799 per set), pooled across sets — identical in shape to the banked
  S3b fitting contract, for cross-slice consistency.
- Known registered risk: pooled-across-sets fitting may underpower members relative to
  per-set fitting. Adequacy is adjudicated by the S3d should-win certificates; any
  certificate failure is FAIL_BASELINE_UNDERPOWERED and the pre-registered repair path
  is per-set refitting under a successor addendum. Do not switch silently.
- HELDOUT partitions (user_id 800..999) must never be touched in S3c: not for fitting,
  tuning, early stopping, or model selection. A guard test is required.
- Internal validation split (deterministic, no RNG): within each set's train partition,
  user_id 0..639 = fit users, user_id 640..799 = internal-validation users, pooled
  across sets the same way.
- Training examples: for user u at turn t, example = (prefix of u up to t-1, logged
  action a_t, next symbol o_t). Empty-prefix convention: uniform distribution (existing
  `base.py` helper).
- All stochastic fitting draws from the frozen `rng_scheme` stream `baseline_fit`
  (seed derivation as frozen); per-config seeds = SHA256(stream_seed || config_id).

## 3. Decoder members — exact grids (24 configs total; 8 per architecture,
identical count per architecture, within the frozen "max 24 per architecture" cap)

Feature families are anchored to the frozen `mi_structural_check` families.
Feature sets:
- F1 = per-turn unigram bag over the prefix + per-session aggregates (symbol counts,
  rates, first-order transition counts) + last-symbol one-hot + candidate-action one-hot.
- F2 = F1 + within-session n-gram counts, n <= 3.
Action conditioning: candidate action enters as a feature; at query time the action
feature is swapped for each of the 9 frozen counterfactual actions.

- `obs_decoder_logreg` (multinomial logistic regression, lbfgs, max_iter=200 fixed):
  grid = features {F1, F2} x C {0.01, 0.1, 1.0, 10.0}  → 8 configs.
- `obs_decoder_gbt` (histogram gradient-boosted trees; features F2 fixed):
  grid = learning_rate {0.05, 0.1} x max_iter {100, 300} x max_leaf_nodes {31, 63}
  → 8 configs.
- `obs_decoder_gru` (1-layer GRU; symbol embedding dim 16 fixed, action embedding dim 8
  fixed, batch 256 fixed, Adam fixed, max 10 epochs, early stop patience 2 on
  internal-validation loss):
  grid = hidden {32, 64} x lr {1e-3, 3e-4} x dropout {0.0, 0.1} → 8 configs.

Selection rule (frozen now): for each member, the config with the highest
macro-balanced accuracy (frozen primary metric family) on the internal-validation
users, predicting the next symbol under the LOGGED action. Ties → lower config index.
Per-config internal-validation metrics and wall-clocks go to
`s3c_decoder_tuning_report.json`. `family_max` over the three decoder members is
computed at scoring stages (S3d/S5), not in S3c.

## 4. Sequence members — exact specs

Both use the GRU class above with the same 8-config grid, same selection rule, same
epoch/early-stop caps.

- `seq_full_history_no_action_conditioning`: input = symbol sequence only, full history
  across all sessions of the user. NO action information anywhere in features (its role
  is the action-insensitive LOG-PARITY contrast). Its emitted distribution is therefore
  identical across the 9 counterfactual actions by construction.
- `seq_window_with_action_conditioning_W15_no_cross_session_persistence`: input =
  (symbol, action) pairs over a window of the last 15 turns; hidden state is reset at
  every session boundary. The no-cross-session-persistence property must be enforced in
  code and covered by an explicit test (prediction after a boundary must be invariant to
  pre-boundary content given the in-session window).
Padding: zero-embedding padding for short prefixes; declare in manifest.

## 5. Compute budget and framework

- Pre-registered S3c compute line: total fitting + tuning across all five members
  <= 24 CPU-h (same line family as the S2 precedent; fixed before any run).
  PART 0 projection gate: fit ONE cheapest config on ONE set first, project the full
  sweep, write `s3c_compute_projection.json` BEFORE launching; projection > 24 CPU-h
  = STOP with failure manifest (honest negative; no silent shrinking).
- Emit `offline_compute_units` per the frozen `cost_metering_fields` (parameter-update
  passes x data size touched), per member.
- Frameworks: use only already-installed libraries (report exact versions in the
  manifest). If a required library for a member (e.g., torch for GRU, scikit-learn for
  logreg/GBT) is not installed: STOP and report — do not install anything.

## 6. Artifacts and persistence

- `s3c_battery_manifest.json`: the five members, feature maps, conventions, fitting
  contract (with this addendum + frozen_design source fields cited), framework versions,
  selected configs, code hashes.
- `s3c_decoder_tuning_report.json`, `s3c_compute_projection.json`,
  `s3c_collision_record.json`.
- Fitted parameters under `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3c_models/` with sha256
  each if the total is < 50 MB; otherwise deterministic training recipes (config + seeds
  + code hash) per the S3a convention. Recipes must regenerate selected models
  bit-identically or within a declared, tested tolerance (floating-point nondeterminism
  must be declared, not hidden).

## 7. Claim ceiling

Instrument code + tuning-procedure evidence only. No environment-validity, no
baseline-power, no gap, no headroom, no mechanism, no learning-capability, no agency,
no EGO claims. Should-win certification and any scoring live in S3d/S5 under the frozen
plan.
