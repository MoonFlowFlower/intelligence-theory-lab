# TLGP-001B INVALID Capacity-Control Audit — Final Report
Task: `TLGP-001B-INVALID-CAPACITY-CONTROL-AUDIT-001` · Date: 2026-06-18 · Role: independent read-only auditor

## 1. Audit verdict
**`positive_control_design_flaw_likely__r2_required`** (bucket B).
The TLGP-001B official run is correctly **INVALID** and must NOT be read as H1. The mandatory
capacity-control failed 0/10 across all three meta families because the pre-registered
CAPACITY_CONTROL is **not a valid capability witness**: it relaxes only value-novelty {3,4} in
training queries while the test task stays byte-identical to REAL (held-out values on 125 UNSEEN
rules). "Control closes" therefore demands ~the H1 success condition itself. Route → TLGP-001B-R2
capacity-control redesign. Preserve 001B-R1 as negative governance evidence.

## 2. Current layer
Engineering implementation + mechanism-hypothesis preflight audit. Candidate-free
baseline-completeness audit only.

## 3. Mainline integration status
None. No EGO mainline / runtime / admission / bridge / product / agent capability touched.

## 4. Enabled status
TLGP-001B official GPU full run (RTX 5070 Ti, torch 2.9.1+cu128) completed and emitted INVALID,
not H0/H1. This audit is read-only + one torch-free non-evidential diagnostic.

## 5. Real trigger evidence
- `result.json.verdict = tlgp001b_invalid_capacity_or_leakage_or_replay`; `official_run=true`.
- `capacity_control_closed_seeds = {amortized_summary_mlp:0, in_context_gru:0, in_context_transformer:0}`,
  `verdict_detail.need_close_seeds=9`, `capacity_control_fails=true`, `invalid_branch=true`.
- `failure_manifest.json = {invalid:true, stop_triggered:true}`.

## 6. Artifact / source readback summary
- Provenance: 6/6 `src/tlgp_001b/*.py` on-disk sha256 == `result.json.source_hashes_delivered_equals_executed`
  == `HANDOFF/source_manifest.json.delivered_src_tlgp_001b`. Frozen prereg canonical
  sha256 = `c9f4ba279b75…c580d41`, `prereg_pin_match=true`. Post-handoff change was a
  **device-only GPU patch** (harness.py, meta_learners.py); inspection confirms it moves
  tensors/model to CUDA and changes NO experimental semantics (splits/regime/value/world logic
  unchanged; all thresholds READ from frozen prereg).
- World (inherited 001A, read-only): K=5, D=3, M=5, ACTION_CARD=5, N_ADAPT=24, N_QUERY=30,
  TRAIN_VALUES={0,1,2}, HELDOUT_VALUES={3,4}; rule = (Σ wᵢxᵢ + c·a) mod 5; 5⁴=625 rules; split 500/125.
- ideal_mean=1.0. Every fair learner at chance: lower_reference {predict_all, no_adaptation, lookup,
  knn1, logistic, mlp, random_forest, count_table} ≈ 0.198–0.210; meta REAL & CONTROL test_balacc ≈ 0.19–0.22.
- Leakage (`positive_control_report.json`): all_planted_caught, renamed_leak_caught,
  no_clean_false_flag, detector_valid, structural_boundary_ok all true; meta forbidden inputs
  {rule_id, query_e} structurally excluded.
- Replay (`replay_report.json`): replay_exact=true over 200 rows (ideal + REAL meta from recorded preds).
- Ablation (`ablation_report.json`): context_ablation_meta ≈ 0.194–0.202 (≤ FLOOR+DELTA=0.3);
  shuffle_headroom ≈ −0.005…+0.0001 (≤ DELTA).
- Tamper: 5/5 probes flip verdict class (incl. p5 degrade-capacity); 3 distinct classes observed.

## 7. Verdict recomputation summary
`compute_verdict` (frozen precedence): INVALID iff capacity fails OR planted-leak missed OR
clean false-flag OR replay not exact. cap_ok = closed≥9 ⇒ all False (0≥9 false) ⇒
capacity_control_fails=true ⇒ INVALID. **Computed from fields, not asserted.** Independent recompute
of closed seeds from `result.json.headroom_vs_meta_per_seed.control_headroom_vs_meta`: 0/0/0,
matches official (all control headrooms 0.797–0.816, none ≤ 0.1). Note: `survives_branch=true`
(REAL LCB≈0.79>0.1; ablation+shuffle "collapse") — i.e. the H1-shaped pattern is present, but
INVALID precedence correctly overrides it; H1 cannot be emitted.

## 8. Capacity-control failure analysis
Diagnostic (`capacity_control_design_diagnostic.json`, torch-free, regenerated from frozen splits.py):
- **CONTROL test ≡ REAL test**, episode-for-episode over 300 episodes (rule_id, adapt_*, query_* all equal).
- **Only difference**: CONTROL adds {3,4} to TRAIN/VAL queries (CONTROL_train_query_values={0,1,2,3,4},
  REAL={0,1,2}); adapt stays {0,1,2}; test = adapt{0,1,2}/query{3,4}.
- **Both regimes still require unseen-RULE generalization**: test rules ⊂ TEST_RULES, disjoint from train.
Consequence: the "positive control" still embeds the full held-out-rule difficulty. Empirically the
value relaxation buys ~nothing (CONTROL headroom 0.81 ≈ REAL 0.80). A valid capability-positive control
must be closeable by a working learner *independently of the experimental question*; this one asks the
learner to reach ≥0.9 balanced accuracy on 125 unseen mod-5 rules — essentially the H1 outcome. Hence its
0/10 failure cannot witness "underpowered meta"; it is confounded with "the held-out-rule task is hard."
That confound was pre-registered into `positive_control.meta_learner_capable` + `split_construction.value_regime`,
so it is a pre-registration **design** defect surfaced by the run, not an implementation defect.

## 9. Strongest alternative explanation
(C) **baseline family genuinely underpowered for this world.** Plausible — in-context modular-rule
system-identification generalizing to unseen rules, with fair non-one-hot numeric inputs, is genuinely
hard, and the meta floors. BUT C is NOT established: no *valid easy* control was ever run, so we never
gave the family a fair capability test. Asserting C would over-claim a negative the evidence does not
support. (A) implementation/optimization bug — no positive evidence: code paths correctly wired
(context consumed by GRU/Transformer/MLP; target aligned; CE loss; best-val checkpoint; device patch
neutral), provenance clean, independent sklearn baselines also floor (test split genuinely hard). A
cannot be fully *excluded* from artifacts alone (torch unavailable in audit sandbox), so it remains a
low-probability secondary suspect. Both A and C are dispositioned by the same R2 fix (add a valid easy
control + a learnability smoke), so neither displaces B as primary.

## 10. (covered above — secondary suspects: C then A)

## 11. Minimal next action
Draft **TLGP-001B-R2** (candidate-free) adding a true capability-positive control the meta family must
demonstrably close BEFORE it is allowed to adjudicate REAL — e.g. a **seen-rule / in-distribution**
control (train+test on the same rule pool) and/or a seen-value control, isolating "can the family learn
at all" from "can it generalize to unseen rules." Include a tiny learnability smoke (overfit on seen
rules) to close suspect A. Keep DELTA/FLOOR/world frozen; record CONTROL predictions so the
capacity decision is replayable. Do NOT enlarge capacity to chase H1.

## 12. Stop condition
Audit complete: INVALID confirmed real, primary bucket assigned (B). STOP — no route advance, no 001C,
no candidate insertion, no repair-in-audit. Implementation/redesign requires a separate operator-authorized R2 card.

## 13. Rollback / preservation plan
Nothing to roll back (read-only). Official `artifacts/TLGP-001B/` untouched (mtimes unchanged). Audit
outputs isolated under `artifacts/TLGP-001B-INVALID-AUDIT-001/` (diag.py, capacity_control_design_diagnostic.json,
README.md, this report), all NON-EVIDENTIAL, no git. Preserve 001B-R1 INVALID as negative governance evidence;
do NOT patch into a pass, do NOT downgrade 001A.

## 14. What this does not prove
Does NOT prove H1 (within-episode headroom survives a capable meta) — capability was never established.
Does NOT prove H0 (headroom amortized) — meta never closed any control. Does NOT prove the meta family is
underpowered (C) — no valid easy control was tested. Does NOT prove 001A stronger/weaker. Proves only:
the 001B-R1 capacity control, as pre-registered, cannot serve as a capability witness because its test
task is identical to REAL's unseen-rule task; therefore 001B-R1 cannot adjudicate 001A and is correctly
INVALID. No consciousness / subjectivity / emotion / agency / autonomy / intelligence / learning-as-mechanism /
EGO-readiness claim is implied. Bounded to THIS world + THIS meta family + this frozen capacity grid.
