# TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A

```yaml
task_id: TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A
status: DRAFT  # awaiting operator authorization + Codex canonical freeze; DO NOT implement yet
layer: mechanism-hypothesis / learning-adaptation measurement (rung1-only diagnostic, corrective)
supersedes_interpretation_of: TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-001A  # 001A route H_arch is INVALID (see §1)
depends_on:
  - scout 001A full_scout  # C1/C2 collapsed to chance -> optimization confound, not architecture ceiling
  - bank d00932d9          # banked rung1-eligibility negative (C0 256/4/4/4 -> 0.52 on 172 rules)
implementation_authorized: false
```

## 1. Why this card exists (the 001A confound)

001A scout mechanically emitted `route = H_arch` (`downgrade_retrieval_line_or_redesign_architecture`).
**That route is INVALID — confounded by an optimization failure at larger capacity, not an architecture
ceiling.** Evidence from `RUN/FULL_SCOUT/val_curves.jsonl`:

- **C1 (512, 18.9M) and C2 (768, 56.7M) @172 collapsed to chance:** meta ≈ 0.2025 (= 1/K, K=5),
  **identical across all 3 seeds**, with **train loss stuck at ≈ 1.61 = ln(5)** (uniform-prediction CE)
  for **both** lrs {1e-3, 3e-4}. They early-stopped at ~epoch 21-29 (patience 20) because val never left
  chance.
- **Smoking gun:** C2 @ k=8 sat flat at val 0.215 from epoch 1, while **C0 (256, 3.17M) @ k=8 → 0.988.**
  A 18× larger model failing a task the small model solves = the big models **never optimized**.
- A wider/deeper transformer strictly contains the narrow one's function (extra units → 0), so C1/C2 **can
  represent** C0's solution; they did not **find** it ⇒ **optimization, not expressivity/architecture.**

**Root cause (grounded):** `retrieval_model` uses `nn.TransformerEncoderLayer` with the default
`norm_first=False` = **Post-LN**. Post-LN transformers have large gradients near the output at
initialization; a fixed learning rate without **warm-up** destabilizes training, and the effect worsens
with depth (Xiong et al., ICML 2020, arXiv:2002.04745). Combined with (a) an lr grid {1e-3, 3e-4} tuned
for the 256-dim model, and (b) early-stop patience 20 that kills the bigger models during their initial
plateau, C1/C2 are guaranteed to collapse. **The capacity axis was never fairly tested.**

The C0 (256) result stands: consistency control reproduced the banked per-seed meta to ~2e-4; C0 clears
k ≤ 16 and plateaus at 0.52 on 172 rules. **The capacity-vs-architecture question remains OPEN.**

## 2. Goal (unchanged question, fair test this time)

Does **more capacity of the same `retrieval_model` architecture, when actually trained**, clear rung1
seen-rule eligibility at higher rule counts? Fix the training recipe (training only — the frozen model is
NOT edited), add a per-capacity trainability gate, then read the breakpoint. Still rung1-only; NOT rung3 /
transfer / H0 / H1.

## 3. Grounding (how established transformer projects train; consulted per operator request)

- **Warm-up is required for Post-LN** (our case): Xiong et al., *On Layer Normalization in the Transformer
  Architecture*, ICML 2020 — arXiv:2002.04745. (We keep Post-LN to isolate capacity; we do NOT switch to
  Pre-LN, which would change the architecture and confound the question.)
- **Concrete small-transformer recipe (nanoGPT):** AdamW, betas (0.9, 0.95), weight_decay 0.1 (2D params
  only), grad-clip norm 1.0, linear warm-up then cosine decay to a min-lr, peak lr ~3e-4-6e-4.
- **Width-aware lr (μP principle):** optimal lr shifts with width; tune lr per capacity rather than sharing
  one lr across widths (microsoft/mup; μTransfer). We adopt the *principle* pragmatically via a per-capacity
  lr sweep (NOT a full μP reparametrization, which would alter the frozen model).

## 4. Fix = new training recipe (frozen `retrieval_model` untouched; NEW runner only)

Pre-registered and frozen in the canonical design:

- **Optimizer:** AdamW, betas (0.9, 0.95), weight_decay 0.1 applied to 2D weights only, grad-clip global
  norm 1.0.
- **LR schedule:** linear **warm-up** over `warmup_steps` (frozen; e.g. 1000 steps or 10% of the per-run
  step horizon, whichever smaller), then cosine decay to `min_lr = 0.1 × peak_lr`.
- **Per-capacity LR sweep (val-selected):** peak_lr ∈ {3e-4, 1e-4, 3e-5} (drop 1e-3 — it already fails even
  C0; add lower rates that bigger widths need). Selection by best validation balanced accuracy.
- **Relaxed early-stop:** early-stop allowed **only after** `min_epochs = warmup_epochs + patience_margin`
  (frozen), so big models are not killed during their warm-up plateau; keep `max_epochs` high enough to
  converge.
- Everything else (data, splits, world, fair panel, ideal, leakage, ablation, replay, K, N_ADAPT) inherited
  frozen.

## 5. Per-capacity TRAINABILITY positive control (the methodological gate 001A lacked)

Before any capacity's rung1 result is admissible, that capacity must FIRST pass a **trainability control**
under the frozen recipe:

- Control task = trivial seen-rule ID at **k = 2 rules** (24 adapt examples make 2-rule ID near-trivial;
  ideal ≈ 1.0). PASS = meta ≥ 0.90 on ≥ 2/3 seeds.
- **If a capacity FAILS the trainability control → that capacity is marked `TRAINABILITY_FAIL` = INVALID
  (untrained); it is EXCLUDED from the breakpoint map and MUST NOT be read as "architecture-limited."**

This directly prevents the 001A confound (untrained big model → false H_arch).

## 6. Grid

| tag | d_model | layers | heads | ff_mult | params (approx from 001A) |
|-----|---------|--------|-------|---------|----------------------------|
| C0  | 256     | 4      | 4     | 4       | 3.17M |
| C1  | 512     | 6      | 8     | 4       | 18.9M |
| C2  | 768     | 8      | 12    | 4       | 56.7M |

- seeds = first 3 prereg MODEL_SEEDS [20260710, 20260711, 20260712] (scout scale).
- rule_count breakpoint map = {2 (control), 8, 16, 32, 64, 128, 172}.
- clear = meta ≥ ideal − DELTA(0.1) on ≥ 2/3 seeds, admissible only if leakage-clean +
  advantage-destroyed ablation (both modes) + no fair-baseline saturation.

## 7. C0 anchor (consistency, adapted to the new recipe)

The new recipe may change C0 slightly, so the 001A "reproduce 0.52 exactly" gate is replaced by:
- C0 must PASS the trainability control, AND
- C0 new-recipe meta on 172 must be **≥ banked 0.52 − 0.03** (the improved recipe must not regress the
  smallest model). If C0 regresses below that → the recipe is harmful → STOP + report (do not proceed).

## 8. Pre-registered decision rules (gated on trainability)

Let `admissible_caps` = capacities that PASS the trainability control. Read the breakpoint
`bp(cap) = max rule_count cleared` over `admissible_caps` only.

- **H_cap:** `bp` increases with capacity across admissible caps (a larger *trained* capacity clears a rule
  count a smaller one cannot) → route `reopen_rung3_powered_after_powered_rung1_confirm`.
- **H_arch (now legitimate):** all Phase-relevant caps are admissible (they *trained*) AND `bp` is flat/
  non-increasing across them → route `architecture_limited_over_swept_range` (only NOW may downgrade be
  considered).
- **INCONCLUSIVE_optimization:** one or more larger caps FAIL the trainability control even under the fixed
  recipe → route `optimization_unresolved_recipe_or_scale`; **NOT** an architecture-capability claim; next
  step = better recipe (μP reparametrization / more warm-up / lower lr) on a NEW card.

No threshold or recipe change after seeing results. Scout scale (3 seeds) → `route_decision` carries
`inconclusive_underpowered`; a positive H_cap authorizes a POWERED 10-seed rung1 confirm before any rung3.

## 8b. Optional attribution ablation (only if operator wants it)

The recipe bundles warm-up + AdamW + lr-sweep + relaxed early-stop. To attribute the fix to warm-up
specifically, a follow-up may re-run one collapsed 001A cell (e.g., C2@k8) with ONLY warm-up added. Out of
scope for the primary corrective read; note only.

## 9. Baseline / ablation / evidence / anti-hardcoding

- Baselines per cell: ideal, fair panel (lookup / count_table / majority / predict_all / predict_none + real
  graph_cache successor_map), fair_max; report ideal−meta and meta−fair_max.
- Ablation: advantage-destroyed context-ablation (shuffle_adapt + no_adapt) on TEST for any cleared cell.
- Leakage: rule_id / query_e never model input; frozen leakage scan per cell (planted caught, clean not
  flagged) at n_test=200.
- Trace/replay: per-cell trace.jsonl + val_curves.jsonl (LFS); recompute each cell metric from trace within
  1e-9; mismatch = STOP. val_curves MUST include the lr schedule value per step and the warm-up flag so the
  schedule is auditable from trace.
- Anti-hardcoding: recipe + grid + decision rules frozen BEFORE run (canonical sha, recomputed by Claude);
  trainability control is the objective per-capacity gate (no tuning-to-pass); no second logic path; no
  future observations.

## 10. Claim ceiling

Answers ONLY capacity-vs-architecture for rung1 SEEN-rule eligibility, and only among capacities that
demonstrably trained. Does NOT test rung3 / transfer / H0 / H1 / mechanism. A clean H_arch here means
"architecture-limited over the swept, *trained* range" — still bounded, still not a universal wall, and not
a mechanism/agency/self/subjectivity/AGI/EGO/companion/mainline claim.

## 11. Files

**Create (NEW, isolated):**
- `src/tlgp_capability_witness_preflight_001a/rung1_capacity_sweep_002a.py` — new runner: frozen recipe
  (AdamW + warm-up + cosine + grad-clip + relaxed early-stop), per-capacity lr sweep, trainability control,
  breakpoint map; reuse frozen `retrieval_model.build_model(params)`, splits/world/fair/ideal/leakage/
  ablation/replay READ-ONLY. `--validate-only` / `--dry-run` / `--full-run --confirm-full-run <sha>` guards.
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG1_CAPACITY_SWEEP_002A/{FREEZE,RUN}/…`
- `tests/test_rung1_capacity_sweep_002a_001a.py`
- (this card)

**FORBIDDEN to change (STOP if touched):** `retrieval_model.py` (0cba9239 — architecture stays Post-LN,
capacity via params only), `meta_learners.py` (358d2bb2), `world.py`, `splits.py`, `preregistration.py`,
`lower_reference.py`, `leakage.py`, `rung3_graph_cache_baselines.py` (921d4407),
`rung3_single_family_adjudicator.py` (5773f5d1), `rung3_powered_full_run.py` (a0dcea8d),
`rung1_capacity_sweep.py` (863b2b43, the 001A runner — banked evidence), any banked artifact, AGENTS.md,
CLAUDE.md, any frozen design.json.

## 12. Stop / rollback / freeze

- Stops: C0 regresses below banked−0.03; any StopSweep (design sha / prereg / heads|d_model / protected-diff
  / rule-subset overlap / replay mismatch); per-cell wall-clock cap (set by Claude at dry-run review).
- Rollback: isolated new files; no push/tag; revert any protected diff. Failed/collapsed cells preserved as
  evidence (never patched into passes); INVALID capacities recorded as TRAINABILITY_FAIL, not as passes.
- Freeze cadence (same as 001A / rung3): Codex freezes canonical design (recipe + grid + decision rules +
  trainability control), records sha256; Claude independently recomputes the sha (freeze before results),
  reviews the runner + a tiny dry-run (real warm-up schedule wired, trainability control wired, C0 anchor,
  leakage/ablation/replay wired, no frozen-model edit), pins the runner sha BEFORE any full scout.

## 13. What this does NOT prove

Even a clean result proves only a bounded, trained-range capacity-vs-architecture fact for rung1 seen-rule
eligibility on this TLGP world/grid. It does not recover rung3, establish transfer, validate a mechanism,
or support any EGO / agency / self / consciousness claim.
```
