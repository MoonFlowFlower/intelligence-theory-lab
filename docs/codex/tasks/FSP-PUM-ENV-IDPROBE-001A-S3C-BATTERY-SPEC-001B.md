# FSP-PUM-ENV-IDPROBE-001A — S3C-BATTERY-SPEC-001B (delta supersede of 001A)

Status: DRAFT until operator banks this file; the checkpoint-commit act is the approval.
Drafted by: Claude (lab auditor role), 2026-07-03, after the S3c-R1 PART 0 STOP
`stop_projection_exceeds_24_cpu_hours` (s3c_compute_projection.json sha256 35039fb8…,
projection 4748.76 CPU-h; failure manifest 323c336c… preserved).

Supersede relationship: 001A (blob 2da9e569325500074cd5e43c3ca4e9fe9032c839) remains in
force EXCEPT the amendments below. Frozen members, grids-as-config-counts, validation
split (fit 0..639 / internal-val 640..799), selection rule, metric, heldout prohibition,
claim ceiling: all UNCHANGED. The 24 CPU-h line: UNCHANGED (precedent: held through two
honest S2 failures; it is not raised in response to a projection breach).

Disclosure of numbers known at drafting time: S2 tractability numbers; one S3c internal
figure exists — logreg cfg00 internal-val macro-balanced accuracy 0.0299 (≈ chance 1/32,
single most-regularized config). No selection, scoring, gap, or heldout numbers exist.
The amendments below are cost/feasibility-driven, not performance-driven, and cannot be
tuned toward any existing result.

## Amendment 1 — F2 n-gram block (replaces the F2 definition in 001A §3)

Root cause: the full n-gram vocabulary (32+32^2+32^3 = 33,824 dims) is memory-infeasible
for dense HGB at pooled scale (hundreds of GB).

New F2 definition:
- n-gram vocabulary = within-session n-grams (n <= 3) whose pooled count over FIT users
  only (user_id 0..639, all 10 sets) is >= 100, ranked by pooled count, truncated to the
  top 1024; deterministic tie-break = lexicographic n-gram key. Built once, persisted to
  `s3c_models/f2_ngram_vocabulary.json` with sha256, before any tuning.
- F2 = F1 (unchanged, 1133 dims) + the 1024-dim thresholded n-gram counts.
- Vocabulary construction may not touch internal-validation or heldout users. A guard
  test is required.

## Amendment 2 — GBT data budget (amends 001A §3 obs_decoder_gbt)

HGB requires dense input; even at F2-new (≈2157 dims) the full pooled fit matrix is a
multi-GB dense object. Pre-registered data budget:
- obs_decoder_gbt fits on the deterministic half of fit users: user_id % 2 == 0
  (i.e. 320 of 640 fit users per set, pooled). Internal validation unchanged (all
  640..799).
- DISCLOSED HANDICAP: this halves GBT's fitting data relative to other members. It is a
  challenger-weakening concession to memory, recorded here so S3d should-win
  certification adjudicates adequacy; if the GBT certificate fails, the pre-registered
  repair is a full-data refit under a successor addendum on a larger-memory plan — not
  silent acceptance.

## Amendment 3 — mandatory implementation efficiency properties (adds to 001A §3/§4)

- Prefix features (F1/F2) must be maintained INCREMENTALLY (O(1) amortized update per
  turn; no per-example prefix recomputation). A mandatory equivalence test compares
  incremental features against a naive reference implementation on a small declared
  sample (>= 2 users x >= 50 turns, exact match for count features).
- GRU-class members (obs_decoder_gru and both seq members) must train TEACHER-FORCED,
  one pass per user-sequence per epoch (every step of the sequence is one training
  example, processed once). Per-example prefix re-encoding is forbidden. Example
  ordering convention (sequence batching, shuffle seed from `baseline_fit` stream) is
  declared in the manifest.
- Query-time: prefix encoded once per query point; the 9 counterfactual actions swap
  only the final-step action input (decoders) or are emitted identically by construction
  (seq_full member), per 001A.

## Amendment 4 — compute accounting and R2 projection protocol (replaces 001A §5 PART 0)

- Accounting: single-thread accounting as in the S2e precedent — sweep processes run
  with threads=1 (OMP/MKL/torch num_threads=1), CPU-h = measured wall-clock at
  threads=1. Report `single_thread_accounting: true` fields.
- PART 0 (R2): measure ONE config on ONE set for EACH cost class:
  logreg-F1, logreg-F2, gbt, gru, seq_full, seq_W15 (6 measurements; cheapest config of
  each class; fit + internal validation).
- Projection = sum over all 40 configs x 10 sets using the measured per-class one-set
  cost, linear-in-sets scaling (declared assumption), plus measured one-time costs
  (vocabulary build, data materialization).
- Write `s3c_compute_projection_v2.json` BEFORE the sweep. Projection > 24 CPU-h = STOP
  with failure manifest (that STOP would be decision-grade evidence for an operator-level
  spec fork; still no grid shrinking or member substitution by the executor).
- v1 projection artifact is preserved as an honest record; its cross-architecture
  heuristic weights (unmeasured GRU multipliers) are superseded by R2's measured basis.

## Amendment 5 — GPU prohibition (clarifies 001A §5)

torch 2.9.1+cu128 is installed on the host; GPU use is PROHIBITED for the S3c sweep.
The 24 CPU-h line is CPU-denominated and offline-compute parity accounting (constitution
section 5) stays CPU-denominated. Enforce torch device=cpu explicitly.

## Everything else

Inherited from 001A unchanged, including artifacts list (manifest/tuning report/
collision record/models-or-recipes), framework no-install rule, ANTI-IDLE, claim
ceiling. R2 pins BOTH 001A and this 001B; a sha mismatch on either = STOP.
