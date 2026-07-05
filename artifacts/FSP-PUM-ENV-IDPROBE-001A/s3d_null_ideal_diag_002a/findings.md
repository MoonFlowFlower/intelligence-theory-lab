# S3D-NULL-IDEAL-DIAG-002A findings

Verdict: `PRIVILEGE_RHO_WIDE`.

Decision branch: G2 collapsed to chance+margin in both requested real cells while G3 reference stayed below G1.

Decision basis: canonical overall macro-balanced accuracy for the two requested real cert cells. Recommend-conditional metrics are reported but do not decide these two cells.

## Numbers

| cell | G1 true overall | G2 wrong overall | G2-G1 | headroom retention | G1 recommend | G2 recommend | G3 reference member | G3 reference overall |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| low_diversity | 0.323781834160 | 0.020570678338 | -0.303211155821 | -0.036507 | 0.329924753273 | 0.016753004240 | nearest_neighbor_user_matching | 0.161947767114 |
| flat_theta | 0.115689127508 | 0.028979421374 | -0.086709706135 | -0.026890 | 0.077810694787 | 0.025570284476 | running_average_preference_regressor | 0.032208389833 |

## Reproduction gate

G1 reproduction passed: `True`.

| cell | G1 true overall | void ideal overall | delta | match |
|---|---:|---:|---:|---|
| low_diversity | 0.323781834160 | 0.323781834160 | 0 | True |
| flat_theta | 0.115689127508 | 0.115689127508 | 0 | True |

## Collapsed-oracle equivalence spot-check

Passed: `True` (eval user 640, both requested cells, both true and wrong style).

| cell | style | max distribution diff | prediction mismatches |
|---|---|---:|---:|
| low_diversity | true | 4.97e-14 | 0 |
| low_diversity | wrong_derangement | 3.04e-14 | 0 |
| flat_theta | true | 6.27e-14 | 0 |
| flat_theta | wrong_derangement | 8.22e-14 | 0 |

## Per-user support

Per-user support CSV: `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_null_ideal_diag_002a/per_user_support.csv` (320 rows, sha256 `4483bc2433a64b5d0561a4431b59838beddd5faa56c5c1ee130a1d669bc7f18b`).

| cell | users | overall retention min/median/max | recommend retention min/median/max |
|---|---:|---|---|
| low_diversity | 160 | -0.496938 / -0.074983 / 0.515999 | -0.523810 / -0.142857 / 1.000000 |
| flat_theta | 160 | -1.022259 / -0.026255 / 0.882534 | -0.454545 / -0.185185 / 1.000000 |

## G3 void/reference rows

G3 is reference-only and was read from `trace_void_line30_v1.jsonl`; no member fix or fresh member adjudication is claimed here.

### low_diversity

Missing assigned members in void trace: `[]`.

| member | metric | recommend metric | unit_id |
|---|---:|---:|---|
| count_table | 0.033978353131 | 0.034722222222 | `member::cert::count_table::low_diversity` |
| episodic_traversal | 0.042314544097 | 0.036115006672 | `member::cert::episodic_traversal::low_diversity` |
| fsm_planner | 0.032557497930 | 0.026648643223 | `member::cert::fsm_planner::low_diversity` |
| nearest_neighbor_user_matching | 0.161947767114 | 0.036320917417 | `member::cert::nearest_neighbor_user_matching::low_diversity` |
| seq_window_with_action_conditioning_W15_no_cross_session_persistence | 0.071855217617 | 0.029014661188 | `member::cert::seq_window_with_action_conditioning_W15_no_cross_session_persistence::low_diversity` |
| successor_map | 0.040623897497 | 0.029792860208 | `member::cert::successor_map::low_diversity` |
| transition_table | 0.030933953088 | 0.032517740160 | `member::cert::transition_table::low_diversity` |

### flat_theta

Missing assigned members in void trace: `['discounted_LS_lambda_0.95']`.

| member | metric | recommend metric | unit_id |
|---|---:|---:|---|
| running_average_preference_regressor | 0.032208389833 | 0.031250000000 | `member::cert::running_average_preference_regressor::flat_theta` |

## Claim ceiling

bounded S3D-NULL-IDEAL-DIAG-002A diagnostic evidence only: style-map privilege scope in low_diversity and flat_theta over eval users 640..799; no fix, no S3d gate pass, no environment-validity, no mechanism-validity, no EGO mainline, no agency, no consciousness claim

What this does not prove: no S3d gate pass, no fix sufficiency beyond this diagnostic branch, no environment validity, no mechanism validity, no EGO mainline effect, no agency, no consciousness.
