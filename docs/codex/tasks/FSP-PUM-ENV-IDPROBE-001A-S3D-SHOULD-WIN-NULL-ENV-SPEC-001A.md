# FSP-PUM-ENV-IDPROBE-001A — S3D-SHOULD-WIN-NULL-ENV-SPEC-001A

Status: DRAFT until operator banks this file; the checkpoint-commit act is the approval.
Drafted by: Claude (lab auditor role), 2026-07-03, at operator request, after the S3c-R3
bank (560d5cb + repair 0acb6e9). Drafted BEFORE any S3d certificate or NULL-env number
exists; every threshold below is pre-registered, not tuned.

Score exposure at drafting time (full disclosure): S2 PC-IDEAL-SANITY 1.0 (16-atom
micro); S3c internal-validation figures, all chance-level (0.0299–0.0332 vs chance
0.03125, documented in 001C). No cert-cell, NULL-env, gap, or heldout numbers exist.

Governing sources (read-only during S3d execution; modifying any = blocking
governance-self-modification failure): constitution `FSP-ENV-DESIGN-CONSTRAINTS-001A.md`
(§7 should-win table, §11 invalidators), task card, execution plan (T3.7),
`frozen_design.json`, 001A/001B/001C battery specs. This spec NARROWS them for S3d only:
no member additions/deletions, no threshold motion on any frozen gate, no metric change.

## 1. Scope

S3d = execution-plan T3.7: should-win capability certificate for EVERY battery member
(frozen `battery_membership`, 18 members) + NULL-env control. S3d is instrument
validation only. It is NOT gap measurement, NOT environment-validity certification
(S5/S6), and does not touch the ten frozen main trajectory sets (guard test required;
the BASE-invariance regression of §4 uses regeneration, not set files).

Out of scope, explicitly: T5.2 theta-decoder gate (different instrument, 001A
no-conflation rule); passive_tracker / oracle rows of constitution §7 (S2 objects;
oracle PC already banked; passive-vs-ideal match is S5 T5.4); any candidate mechanism.

## 2. Certificate metric and win criterion (pre-registered)

- Scoring frame: identical to the S3c internal-validation frame — next-symbol
  prediction under the LOGGED action, macro-balanced accuracy (frozen primary metric
  family), computed over eval users of the cert set.
- Class convention (needed for near-deterministic cells): macro-balanced accuracy is
  averaged over classes with >= 1 true occurrence in the eval slice; the per-cell class
  count is reported.
- chance_cell = 1/32 (analytic argmax-uniform reference).
- ideal_cell = S2 exact filter (generator access, prefix-only), run on the same cert
  set and eval points, argmax of its predictive distribution, same metric.
- Headroom-capture ratio: rho_member = (metric_member − chance_cell) /
  (ideal_cell − chance_cell).
- Cell validity guard: in every should-win cell, ideal_cell − chance_cell >= 0.10 is
  required. If violated the cell is defective → STOP `s3d_cell_headroom_defect`
  (spec gap; successor spec required; no threshold motion).
- Certificate PASS = rho_member >= the member's pre-registered rho threshold (§3).
- Uncertainty: report a bootstrap 95% CI on rho (frozen `bootstrap` stream, 1000
  resamples over eval users). PASS/FAIL is adjudicated on the point estimate; the CI is
  reported for audit (equivalence-style claims must cite it — L-H discipline).

## 3. Certificate assignment table (frozen at bank time)

Cert sets: users 0..799 only (fit 0..639, eval 640..799; NO 800..999 block generated),
20 sessions x 15 turns per user, logging policy = frozen `log_parity_trajectory_policy`
mixture, one set per cell. Master seeds (pre-registered, disjoint from the ten frozen
main seeds): constant_none=20260711, constant_saturated=20260712, camouflage_off=20260713,
low_diversity=20260714, stable_facts=20260715, flat_theta=20260716, NULL_env=20260717.

| member | cell (variant) | rho threshold | notes |
|---|---|---|---|
| predict_none | degenerate_should_win_constant_none | >= 0.90 | one-hot symbol 0 |
| majority | degenerate_should_win_constant_none | >= 0.90 | prefix-modal one-hot |
| global_prior | degenerate_should_win_constant_none | >= 0.90 | argmax = modal symbol |
| seq_full_history_no_action_conditioning | degenerate_should_win_constant_none | >= 0.90 | WEAK cert, disclosed: certifies trainability at the deterministic floor only |
| predict_all | degenerate_should_win_constant_saturated | >= 0.90 | one-hot symbol 31 |
| obs_decoder_logreg / _gbt / _gru | camouflage_off | family_max >= 0.80; individual rho reported | family-row interpretation of §7 (disclosed, §7 lists obs_decoder as one family row; frozen_design speaks family_max). GBT runs under its frozen half-data budget (001B Am.2) |
| seq_window_with_action_conditioning_W15... | graph_cache_should_win_low_diversity_templates | >= 0.50 | action-conditioned templates are its favorable regime |
| successor_map, transition_table, count_table, fsm_planner, episodic_traversal | graph_cache_should_win_low_diversity_templates | each >= 0.50 | per constitution §7 family row; family_max also reported |
| episodic_traversal (additional clause) | same cell | fallback_rate_in_cell < 0.50 | if the cert passes mainly via fallback distributions the cert is VACUOUS = treated as FAIL (context: 0.6936 heldout coverage / ~31% fallback on main sets, S3b) |
| rag_k5_episode_retrieval | rag_should_win_stable_facts | recommend-turn-conditional rho >= 0.50 | the stable-fact channel exists only under action==recommend; overall-cell rho also reported (disclosed subset metric) |
| nearest_neighbor_user_matching | graph_cache_should_win_low_diversity_templates | >= 0.50 | WEAK cert, disclosed: cell favors any retrieval-class member |
| discounted_LS_lambda_0.95 | flat_theta | >= 0.80 | §7 "approaches ideal" |
| running_average_preference_regressor | flat_theta | >= 0.80 | same row |

Fitting contract per cell: each member is fitted ON the cert set's fit users
(0..639) under its banked conventions — S3a/S3b members per their banked manifests;
S3c members refit with their SELECTED configs (banked recipes; frozen F2 vocabulary
REUSED by sha, per 001B — the certificate tests the member AS CONFIGURED for S5,
including its vocabulary). No re-tuning, no config search, no threshold search.

## 4. Two cert-only simulator variants (redesign-ledger entry, embedded)

What changes: `SimulatorVariant` gains two cert-only members implemented as constructor
parameters of the SAME sealed generator (no second code path):

- `degenerate_should_win_constant_none`: response symbol 0 with probability >= 0.97 for
  every action and every theta; trust/probe channels inert.
- `degenerate_should_win_constant_saturated`: same with response symbol 31.

Why: constitution §7 requires every member to have a winnable cell; the frozen
`env_knob_variants` list contains none for the constant one-hot degenerates
(predict_all=31 / predict_none=0). Triggering signature: spec gap recorded in
SESSION-HANDOFF-FSP-20260703 §4.2. What does NOT change: BASE and all eight frozen
variants, thresholds, metric, battery membership, `frozen_design.json` (file untouched;
this spec is the supersede-narrowing record).

Mandatory guards on the code change:

- BASE-invariance regression: regenerate a declared slice of main set_00 (>= 2 users,
  full horizon) with the post-change code and verify byte/hash equality against the
  banked S3a recipe hashes. Mismatch = STOP (the sealed generator drifted).
- New-variant unit tests: target-symbol concentration >= 0.95 measured on >= 10k steps;
  theta-independence (conditional response distributions identical across >= 3 distinct
  theta draws, tolerance 1e-9 in probability space); no new observation fields.
- Ideal-filter sanity on each NEW variant: on an enumerable micro-config, filter
  predictive distribution == simulator conditional within 1e-9.

## 5. NULL-env control (pre-registered MDE)

Full battery (all 18 members, fitted on the NULL cert set per §3 contract) + the S2
ideal observer, scored in the same frame. Requirement (frozen positive_controls row,
operationalized): metric <= chance + 0.005 absolute for EVERY member AND the ideal
(0.005 ≈ 6x the binomial SE at p=1/32, n≈48,000 eval points; pre-registered MDE margin).
Any breach = FAIL_NULL_FALSE_HEADROOM (instrument), all S3d results void; preserve
artifacts, STOP.

## 6. Compute budget and PART 0 projection gate

- Pre-registered S3d budget line: 12.0 CPU-h TOTAL (generation + fitting + ideal runs +
  scoring). Provenance disclosure: budget convention in the 001A line family, NOT
  claim-bearing, operator-adjustable only by signed decision note (001C precedent and
  firewall: never cite against the S2 tractability line).
- Accounting: threads=1 per process (OMP/MKL/torch num_threads=1), CPU-h = sum of
  per-unit wall-clock at threads=1; cell/member-level process parallelism permitted;
  wall-clock and CPU-h both reported; GPU prohibited; torch device=cpu.
- PART 0 (before the full run): measure one-unit costs — one cert-set generation, ideal
  per-user on one cell, one fit+score for each cost class (logreg-F1/F2, gbt, gru, seq,
  table-family, retrieval-family, degenerates) — project the full S3d linearly
  (declared assumption), write `s3d_compute_projection.json` BEFORE launching.
  Projection > 12.0 = STOP with failure manifest. No grid/member/threshold shrinking by
  the executor.
- Runtime guard during the run: cumulative per-completed-unit CPU-h trace; > 12.0 =
  STOP immediately with failure manifest; a second breach returns to the operator.

## 7. Adjudication rules (pre-registered, from standing obligations)

- All certificates PASS + NULL clean → verdict `s3d_all_certificates_green`; pooled
  fitting (001A §2) is thereby adjudicated ADEQUATE for S5; GBT half-data handicap
  (001B Am.2) is adjudicated ACCEPTABLE.
- Any certificate FAIL → verdict `FAIL_BASELINE_UNDERPOWERED` listing members; candidate
  bank actions void; pre-registered repairs (successor spec required, no silent switch):
  S3c-member failure → per-set refit path (001A §2); GBT failure → full-data refit on a
  larger-memory plan (001B Am.2); any other member → fix that baseline.
- NULL breach → `FAIL_NULL_FALSE_HEADROOM` (dominates; all cert results void).
- Verdicts are emitted by the artifact producer from recorded numbers only; no
  narrative upgrades. S3d green does NOT authorize any environment-validity, headroom,
  or gap claim — it only clears the instrument precondition for S5.

## 8. Artifacts (all under artifacts/FSP-PUM-ENV-IDPROBE-001A/)

- `s3d_cert_sets_manifest.json` — per cell: variant, master seed, generation sha256s,
  record counts.
- `s3d_compute_projection.json` (PART 0), then `s3d_certificate_report.json` — per
  member: cell, n_eval points, classes present, metric, ideal_cell, chance, rho,
  threshold, CI, PASS/FAIL, per-unit wall-clocks, cumulative CPU-h trace, runtime-guard
  decision, verdict field, claim_ceiling field.
- `s3d_null_env_report.json` — per member + ideal: metric, margin vs chance+0.005, PASS/FAIL.
- `s3d_collision_record_001a.json` — approach record per lab convention.
- Failure manifests on ANY stop, preserved verbatim. Defect-preservation rule (R3
  lesson, binding): if an instrument defect is discovered after a run, preserve the
  defective outputs under versioned `*_v1` names BEFORE any rerun.
- Code: simulator variant addition + tests in `src/fsp_pum_env/` + `tests/fsp_pum_env/`
  only. Tests must extend the existing suite (from 72 items); sealing import-graph test
  must still pass.

## 9. Claim ceiling

Baseline-capability-certificate and NULL-control instrument evidence only. No
environment-validity, no headroom, no gap, no baseline-power-beyond-certificate, no
mechanism, no learning-capability, no agency, no EGO claim. The strongest possible S3d
claim: "every battery member demonstrated capability in its pre-registered favorable
cell, and the NULL environment showed no false headroom, under the frozen metric and
budget."
