# FSP-PUM-ENV-IDPROBE-001A — S3d GRU Seed Determinism Diag + Repair 001A

Status: **PROPOSAL — requires operator §7 signature before Stage 2/3.** Stage 1 (diagnosis,
no code change) is authorized by this card alone. Author: Claude (auditor), 2026-07-05.
Predecessor evidence: `STOP_RESUME_REUSE_GATE_FAILED` (resume run under
`...-S3D-BATTERY-RESUME-001A`, spot-check mismatch on
`member::null::seq_full_history_no_action_conditioning::NULL_env`).

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-GRU-SEED-DETERMINISM-REPAIR-001A`

## problem definition (audited evidence, 2026-07-05)
The resume spot-check recomputed 3 of 41 void-completed units. Two matched bit-exact
(`obs_decoder_gbt::NULL_env`, `running_average_preference_regressor::flat_theta`); one did not
(`seq_full_history_no_action_conditioning::NULL_env`: stored metric_digest `46d28b73…` /
PUC sha `76d12a07…` vs recomputed `6934ec2f…` / `cb992a7b…`). Audit facts:

1. **Stored side is faithful to banked evidence.** The banked void trace blob
   (`git show d983b59:artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.jsonl`) reproduces exactly the
   stored digests (metric 0.031293262103089706, n=48000, 160 users; PUC sha recomputed from the
   blob = `76d12a07…`). The mismatch is entirely on the recompute side.
2. **Env + shared pipeline excluded.** `obs_decoder_gbt::NULL_env` recomputed bit-exact through the
   same cell, same `_collect_train_events_one_set`, same frozen design ⇒ NULL-env records and the
   scoring/canonicalization path are identical between void run and recompute.
3. **Science code unchanged.** `_run_unit_worker` and the member scoring path are textually
   identical between the void runner (d983b59 blob) and the current runner; `src/fsp_pum_env/*.py`
   match HEAD blobs (apparent mount diffs were FUSE truncation artifacts; verified via file-API).
4. **Root cause (mechanism hypothesis, high confidence):**
   `seq_full_history_no_action_conditioning` is a torch GRU
   (`src/fsp_pum_env/battery/obs_decoders.py::_fit_eval_gru_sequences`, line ~1369). It seeds
   **numpy only** (`np.random.default_rng(_derive_config_seed(...))` for epoch shuffling).
   **`torch.manual_seed` is never called anywhere in `src/fsp_pum_env/`** (grep-verified), so GRU
   weight init + dropout draw from torch's per-process global RNG ⇒ every GRU-family unit is
   **process-nondeterministic by construction**. The TLGP lineage (`src/tlgp_001b*`) seeds torch
   correctly; this module never did.
5. **Failure geometry matches.** GRU-family units = 6 of 43 (`obs_decoder_gru`,
   `seq_full_history…`, `seq_window_W15…` × cert+NULL). P(spot-check sample of 3 hits ≥1 GRU unit)
   ≈ 0.386; it fired. sklearn members pass explicit `random_state=_derive_config_seed(...)`;
   running_average has no RNG — both recomputed bit-exact.
6. **Cost facts (void trace):** 6 GRU units = 0.26 CPU-h total; 35 non-GRU units = 30.69 CPU-h;
   2 missing `discounted_LS_lambda_0.95` units are prefix members (~0.06–0.09 CPU-h).
7. Consequence: the resume card's bit-exact reuse premise ("units are own-seeded", frozen spec
   §parallelism) is **falsified for GRU members** — they are numpy-seeded but not torch-seeded.
   The void GRU unit values can never be recomputed bit-exact by anyone. This is a latent
   instrument-provenance defect, not a defect introduced by the resume implementation, and not
   evidence of any environment or mechanism property.

## current stage
S3d battery resume blocked at reuse gate; L=38 signed (002A §6); 002A §4 endgame active
(next L breach ⇒ battery close). Budget headroom for route A ≈ 7 CPU-h.

## hypothesis
H-GRU-SEED: unseeded torch global RNG (init + dropout) makes GRU-family unit results
process-nondeterministic; all other units are deterministic given the frozen design.

## falsifier (Stage 1 must be able to kill the hypothesis)
If two fresh worker-context recomputes of the failing unit agree with each other bit-exact
(A==B), H-GRU-SEED is **false** (nondeterminism would need a per-process source; if additionally
A==void, the defect would instead be main-process-vs-worker context) → STOP, report, re-audit.

## STAGE 1 — diagnosis (authorized now; no science-code change)
1. Recompute `member::null::seq_full_history_no_action_conditioning::NULL_env` **twice**, each in
   a fresh spawned worker process (same context as the void battery: `_configure_worker_environment`,
   threads=1, GPU prohibited), current committed science code, no seeding change.
2. Persist **full** recomputed payloads (metric, per_user_confusion, digests, CPU) to
   `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/` — fix the diagnosability gap
   (the resume spot-check stored only digests).
3. Positive control: recompute `member::null::obs_decoder_gbt::NULL_env` once; must equal void
   digests bit-exact.
4. Decision table (pre-registered):
   - A≠B (any digest) → H-GRU-SEED confirmed → Stage 2 eligible.
   - A==B≠void → deterministic drift vs void context → STOP, report (do not proceed to Stage 2).
   - A==B==void → spot-check harness defect → STOP, report.
   - gbt control mismatch → wider defect → STOP, report.
5. CPU is verification overhead: disclose, do not count toward L.

## STAGE 2 — repair (requires §7 route A signature + Stage 1 confirmation)
1. Single isolated edit in `src/fsp_pum_env/battery/obs_decoders.py::_fit_eval_gru_sequences`:
   seed torch from the already-derived config seed before model construction
   (`torch.manual_seed(_derive_config_seed(design, str(config["config_id"])))`).
   No hyperparameter, feature, metric, threshold, member-set, or recipe change. Do not touch
   `_measure_gru_one_set` (cost measurement only), recipes, or frozen spec.
2. Determinism gate: recompute the failing unit twice post-fix → bit-identical (metric_digest +
   PUC sha). Both runs in fresh worker processes.
3. Regression gate (non-torch paths must be untouched): recompute
   `obs_decoder_gbt::NULL_env` + `running_average_preference_regressor::flat_theta` post-fix →
   still bit-exact to void digests. `py_compile` + focused pytest
   (`test_s3d_certificates.py`, `test_s3d_cert_variants.py`, launchpath test) pass.
4. Pre-registration: post-fix GRU unit values **will differ** from void values (void init was
   unseeded and is unreproducible). New values are computed fresh under seeded init, uniformly for
   cert AND NULL cells — no selection channel. Nobody may compare new GRU values against void
   values to pick the better one; the void trace remains banked historical evidence, untouched.

## STAGE 3 — resume amendment (DELTA3′; requires the same §7 signature)
1. Reuse the **35 non-GRU units** (recorded CPU 30.69 h enters the runtime guard as before).
   Reuse gating unchanged otherwise (void provenance hash + reconstruction equality).
2. Spot-check redraw: 3 units from the **35 deterministic units only**, seed text
   `FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A:spot-check:002`, same all-or-nothing rule
   within that set (any mismatch → discard all reuse → STOP; full re-run is then a separate
   operator decision under 002A §4).
3. Fresh-run **8 units**: 6 GRU-family (seeded) + 2 missing `discounted_LS_lambda_0.95`.
4. Runtime guard: reused-recorded + newly-measured ≤ **L=38** (002A §6, unchanged; do not re-read
   as higher). Projection ≈ 30.69 + ~0.4 ≪ 38. Breach ⇒ battery close per 002A §4 (no 002B).
5. If the battery completes: cert/null/baseline/ablation/replay reports freshly written by the
   committed runner (N1), consistent with the merged trace; interpretation pre-reg
   (N1/N2/N3) applies unchanged; heldout users 800–999 untouched; BASE-invariance and NULL
   false-headroom checks as per frozen spec.

## claim ceiling
Instrument determinism/provenance repair + bounded S3d execution evidence only. Establishes, at
most: (a) GRU-family units were process-nondeterministic due to unseeded torch RNG (negative
instrument evidence, banked); (b) post-fix units are replay-deterministic; (c) if completed, S3d
should-win + NULL-env instrument evidence under the frozen contract at L=38. No environment-validity,
gap, mechanism, learning, agency, EGO, companion, or theory-correctness claim. S3c's banked
selection results are historical records under their own declared nondeterminism; this card does
not re-adjudicate them.

## stop conditions
Stage-1 falsifier fires; regression gate fails; any banked artifact byte-changes; any frozen
spec/threshold/member-set/cert-cell/metric change required; heldout touched; L=38 breached
(⇒ 002A §4 close); spot-check:002 mismatch. Preserve all failure artifacts; never patch.

## rollback
Stage 2 is one isolated function edit → revert the edit; delete
`s3d_gru_determinism_diag/` outputs if invalidated (before banking only); void evidence and all
banked artifacts untouched throughout.

## forbidden
git (Codex runs no git); touching frozen spec 001A/001B, thresholds, ρ, k, NULL MDE, 18-member
set, cert cells, recipes, `_measure_*` cost paths, banked artifacts; auto-raising L; comparing
new GRU values to void values for selection; test-only logic paths; temp/inline report drivers.

## §7 operator signature (required before Stage 2/3)
Route (pick one):
- [x] **A (auditor-recommended)** — Stage 2 seed repair + Stage 3 partial reuse (35 reused + 8 fresh under L=38).
- [ ] B — no code fix; declare GRU nondeterminism; reuse 35 + fresh-run 8 unseeded (instrument stays non-replayable at unit level; weakest).
- [ ] C — no code fix; discard all reuse; full fresh re-run ~32 CPU-h under L=38 (costly; replay defect remains).

L stays 38 CPU-h per 002A §6: [x] acknowledged (no re-raise).
Operator: Leo  Date: 2026-07-05

## appendix — Codex prompt (paste as-is, only after §7 is signed)
```
ROLE: Executor for FSP-PUM-ENV-IDPROBE-001A-S3D-GRU-SEED-DETERMINISM-REPAIR-001A.
Compute + code only. You run NO git. You change NO science rule. You do not bank.
READ (read-only): this card; ...-S3D-BATTERY-RESUME-001A.md; ...-S3D-BUDGET-DECISION-002A.md (§6
L=38); ...-S3D-BATTERY-INTERPRETATION-PREREG-001A.md; frozen spec 001A/001B.
PRECONDITION (self-check, else failure manifest + STOP): this card §7 signed with route A AND
banked; the resume STOP evidence banked.
IMPLEMENT: Stage 1 exactly as §STAGE 1 (decision table is binding). If and only if outcome is
A≠B and gbt control passes: Stage 2 (single seeding edit in _fit_eval_gru_sequences) + its gates;
then Stage 3 resume (reuse 35, spot-check:002 from deterministic set, fresh-run 6 GRU + 2
discounted_LS, guard ≤ 38, breach = close per 002A §4). Persist full payloads for every recompute.
Preserve current STOP artifacts before overwriting result.json/failure_manifest.json (copy to
*_reuse_gate_stop_v1 names). ON COMPLETION OR STOP: emit HEAD-pinned operator bank-ops proposal
(git reset first, allowlist only freshly-changed files, required-core-subset + zero-deletion +
no-unexpected gates, per-file Get-FileHash, scoped commit, no push), then STOP for Claude audit.
Report: verdict; Stage-1 decision-table outcome with all digests; files changed; commands; tests;
CPU accounting (guard vs verification overhead separately); artifacts; any STOP fired.
```
