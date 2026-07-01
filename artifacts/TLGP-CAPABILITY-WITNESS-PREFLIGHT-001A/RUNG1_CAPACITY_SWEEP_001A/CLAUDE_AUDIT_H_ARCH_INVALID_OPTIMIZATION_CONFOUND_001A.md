# CLAUDE INDEPENDENT AUDIT — rung1 capacity sweep 001A route H_arch is INVALID (optimization confound)

```yaml
audit_of: TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-001A
run_id: tlgp-rung1-capacity-sweep-full-20260701-040418-2d37ed06
runner_sha256: 863b2b439f2fe147d9728aab0b4cd63010822806e5ea3b71fc2e6b008c8779cd
design_canonical_sha256: 79e51bb4c2f4af89e330ea81e5f9a636a75be3bdb862754e8851164b6f48c21f
run_from_head: d00932d934e81abcfa5bd9e8689d61959f94bb01
verdict: INVALID_optimization_confound
route_in_result_json: H_arch   # preserved as-recorded; NOT accepted as a valid conclusion
role: independent auditor (verify-don't-trust; recomputed from raw val_curves.jsonl)
```

## Verdict

The runner mechanically emitted `route_decision = H_arch`
(`downgrade_retrieval_line_or_redesign_architecture`) by its pre-registered rule (breakpoint flat/
non-increasing: C0:16, C1:16, C2:0). **That route is NOT accepted.** The larger-capacity cells did not
fail because capacity/architecture is insufficient — they **failed to optimize at all** (collapsed to
chance). The capacity-vs-architecture question is therefore **UNRESOLVED**, not answered.

## Evidence (recomputed from `RUN/FULL_SCOUT/val_curves.jsonl`, not the summary)

- **C1 (512, 18.9M) and C2 (768, 56.7M) @ 172:** meta ≈ 0.2025 = 1/K (K=5), **identical on all 3 seeds**;
  train loss stuck at **≈ 1.61 = ln(5)** (uniform-prediction cross-entropy) for **both** lrs {1e-3, 3e-4};
  early-stopped at ~epoch 21-29 (patience 20) because validation never left chance.
- **Smoking gun:** C2 @ k=8 sat flat at val 0.215 from epoch 1, while **C0 (256, 3.17M) @ k=8 → 0.988.**
  A model with 18× the parameters cannot fail a task the small model solves unless it never trained.
- **Expressivity argument:** a wider/deeper transformer strictly contains the narrow model's function
  (extra units → 0), so C1/C2 **can represent** C0's solution; they did not **find** it ⇒ this is an
  optimization failure, not an expressivity/architecture ceiling.

## Root cause (grounded)

`retrieval_model` uses `nn.TransformerEncoderLayer` with default `norm_first=False` = **Post-LN**. Post-LN
transformers have large output-layer gradients at initialization; a fixed learning rate without **warm-up**
is unstable, worsening with depth (Xiong et al., *On Layer Normalization in the Transformer Architecture*,
ICML 2020, arXiv:2002.04745). Fixed lr {1e-3, 3e-4} (tuned for the 256-dim model) + no warm-up + early-stop
patience 20 guarantees the deeper C1/C2 collapse during their initial plateau.

## What IS valid (do not discard)

- **C0 (256) result stands:** the C0 consistency control reproduced the banked per-seed rung1 meta to ~2e-4
  (0.519/0.504/0.51); C0 clears k ≤ 16 and plateaus at 0.52 on 172 rules. This is a real, bounded C0 fact.
- Leakage clean (detector_valid true, all 18 cells, planted caught, no clean false flags); replay exact
  (max_abs_diff 0.0, 32400 rows); consistency-control gate_pass true. The instrument is sound; the
  **larger-capacity cells are TRAINABILITY-invalid (untrained), not architecture evidence.**

## Disposition

- The C1/C2 cells must be read as `TRAINABILITY_FAIL` (untrained), NOT as "failed to clear" / architecture-
  limited. `result.json`'s `route=H_arch` is preserved byte-as-recorded (evidence integrity) but is
  overridden by this audit and must not be cited as a conclusion.
- Corrective card: `docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A.md` — fix training
  only (warm-up + AdamW + per-capacity lr sweep + relaxed early-stop) and add a **per-capacity trainability
  positive control** (each capacity must clear a trivial k=2 task or be marked INVALID before its result is
  read). The frozen `retrieval_model` architecture is NOT edited (keeps the capacity question clean).

## Claim ceiling

Bounded offline audit of one rung1-only scout. Establishes only that the 001A H_arch route is confounded by
an optimization failure at larger capacity, and that the C0 result reproduces the banked negative. Proves
nothing about rung3 / transfer / H0 / H1 / mechanism / agency / self / AGI / EGO / mainline. The capacity-
vs-architecture question remains open pending 002A.
```
