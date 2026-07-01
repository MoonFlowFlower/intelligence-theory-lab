# TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-001A

```yaml
task_id: TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-001A
status: DRAFT  # awaiting operator authorization + Codex canonical freeze; DO NOT implement yet
layer: mechanism-hypothesis / learning-adaptation measurement (rung1-only diagnostic)
supersedes: nothing
depends_on:
  - bank d00932d9  # powered rung3 stopped at stage1_gate: rung1 eligibility fail 0/10, rung3 gated off
  - bank 7dfb0bde  # powered rung0 SEEN-rule pass ~0.95 (8 rules)
implementation_authorized: false
```

## 1. Problem definition

The banked powered-rung3 run (`d00932d9`) stopped at `stage1_gate`: the validated true-ICL
`retrieval_model` at the **frozen capacity 256/4/4/4** plateaus at rung1 **seen-rule** eligibility
`meta ≈ 0.52` (converged — `val_still_improving_at_stop=False`, early-stop ~epoch 60-80/200; 10/10 seeds)
against `ideal = 1.000`, bar `ideal − DELTA = 0.90`, `fair_max ≈ 0.33`. Ablation is real
(normal 0.52 → no_adapt 0.20), so the model uses context but insufficiently. Banked rung0 (8 rules)
passed ~0.95 at the SAME capacity. rung1 has **172 seen rules**.

**The single open question this card resolves (and nothing more):** is the 172-rule plateau
**capacity-limited** (a larger model clears it) or **architecture/strategy-limited** (adding capacity
does not move the breakpoint)? This — and only this — gates whether rung3 transfer is worth re-attempting.

This is NOT a transfer test. rung3 / unseen rules / H0 / H1 are out of scope.

## 2. Competing hypotheses (pre-registered before any run)

- **H_cap (capacity-limited):** the largest rule-count the model clears (eligibility on ≥2/3 seeds,
  ablation-verified) INCREASES with capacity; a larger capacity clears rung1 at a rule count where
  256/4/4/4 fails.
- **H_arch (architecture/strategy-limited):** the breakpoint does NOT increase with capacity across the
  swept range; adding width/depth does not clear higher rule counts.

rung0=8 passing already proves the architecture is not *fundamentally* incapable of in-context
inference; the question is whether 172 is a **capacity wall** (bigger clears it) or a **strategy wall**
(does not scale regardless).

## 3. Instruments (READ-ONLY; reused unmodified, source-pinned)

- `retrieval_model.build_model(params)` sha `0cba9239…` — accepts an arbitrary
  `{d_model,layers,heads,ff_mult}` dict; **capacity is swept by passing different param dicts only.**
  `heads` MUST divide `d_model` (nn.TransformerEncoderLayer constraint).
- `meta_learners.build_tensors / move_tensors / eval_model / _eval_tensors` sha `358d2bb2…`
- `world.ideal_predictions / make_episode_for_rule`, `splits.rule_split / make_episodes`,
  `preregistration` (DELTA, seeds, budget, TRAIN/HELDOUT values), `lower_reference.evaluate`,
  `rung3_graph_cache_baselines.evaluate` (real successor_map) sha `921d4407…`, `tlgp_001a.leakage`.
- The **advantage-destroyed** `context_ablation_report` logic and the **replay-from-trace** recompute
  from `rung3_powered_full_run.py` (a0dcea8d) may be re-implemented faithfully in the new runner OR
  imported read-only; they must NOT be edited.

## 4. Capacity grid (pre-registered; frozen in canonical design)

| tag | d_model | layers | heads | ff_mult | note |
|-----|---------|--------|-------|---------|------|
| C0  | 256     | 4      | 4     | 4       | banked baseline — MUST reproduce the banked rung1 result |
| C1  | 512     | 6      | 8     | 4       | ~4–5× params |
| C2  | 768     | 8      | 12    | 4       | ~12–15× params |
| C3  | 1024    | 8      | 16    | 4       | optional extreme point |

All `heads | d_model`. `parameter_count(build_model(cap))` recorded per cell.

## 5. Two-phase, conditional design (cost-bounded; scout scale = 3 seeds)

**Built-in consistency control (mandatory, runs first):** train C0 on the exact banked rung1 task
(172 rules, `n_train=5000/n_val=1000/n_test=200`, `lr∈{1e-3,3e-4}`+val-select, `max_epochs=200`,
early-stop, seeds = first 3 prereg MODEL_SEEDS). **Gate:** C0 `meta` must reproduce the banked
`≈0.52 ± 0.05` on ≥2/3 seeds. If C0 does NOT reproduce → the new runner is broken/confounded → STOP,
`failure_manifest`, do not interpret any larger-capacity cell. (Positive-control-before-interpretation.)

**Phase 1 — capacity at the failing point (cheapest; decides the POSITIVE case).**
Fix rule_count = 172 (the exact banked rung1). Sweep C0, C1, C2 (and C3 if authorized). 3 seeds each.
- Pre-registered read: a cell **CLEARS** iff `meta ≥ ideal − DELTA(0.1)` on ≥2/3 seeds AND
  leakage `detector_valid=True` AND context-ablation is **advantage-destroyed**
  (`ablated ≤ fair_max + EPSILON`, both shuffle_adapt + no_adapt) on the rung1 TEST set.
- If ANY capacity CLEARS 172 → **H_cap supported at 172**; STOP; route =
  `reopen_rung3_powered_at_cleared_capacity` (new powered 10-seed rung1 confirm → then rung3 card).
- If NONE clears 172 → proceed to Phase 2.

**Phase 2 — breakpoint map (conditional; only if Phase 1 all-fail).**
rule_count ∈ {8, 16, 32, 64, 128} × capacity {C0, C1, C2}, 3 seeds. rule_count < 172 uses a
deterministic subsample of `k` rules drawn from the **train** rule pool (seed
`RUNG1_SWEEP_SUBSET_SEED`, disjoint from the 125 TEST rules), evaluated on **held-out episodes** of
those `k` seen rules (seen-rule eligibility, identical construction to rung1 via
`world.make_episode_for_rule`). ideal / fair / leakage recomputed per k-rule set.
Record `breakpoint(capacity) = max k cleared`.
- Pre-registered read: if `breakpoint(C2) > breakpoint(C0)` → **H_cap** (capacity moves the wall);
  route = `scale_up` (larger powered card). If breakpoint FLAT across C0..C2 → **H_arch supported**;
  route = `downgrade_retrieval_line_or_redesign_architecture`.

## 6. Baseline / ablation / evidence

- **Baselines (per cell):** ideal (Bayes, per rule set), fair panel (lookup / count_table / majority /
  predict_all / predict_none + real graph_cache successor_map), `fair_max`. Report `ideal − meta` and
  `meta − fair_max`. A "clear" is inadmissible if a fair baseline saturates (`fair_max ≥ ideal − DELTA`).
- **Ablation:** context_ablation (shuffle_adapt + no_adapt) on the TEST set of any cleared cell,
  advantage-destroyed criterion. A cell counts as CLEAR only if its advantage is context-driven
  (ablation collapses) — guards a bigger model "clearing" via non-context degeneracy.
- **Anti-leakage:** `rule_id` and `query_e` never enter the model (reuse `build_tensors`); run the
  frozen leakage scan (planted must be caught, clean must not false-flag) per cell at `n_test=200`.
- **Trace/replay:** emit `trace.jsonl` (per-episode rung1 rows: seed, capacity, rule_count, meta/ideal/
  fair/headroom, mode) + `val_curves.jsonl` (dense) → LFS. Recompute each cell's eligibility from the
  trace within `1e-9` (replay-from-trace); mismatch = STOP.

## 7. Acceptance gate (pre-registered decision — set BEFORE results)

- Phase 1 clears 172 (admissible: leakage-clean + ablation-destroyed + no fair saturation) → **H_cap**,
  route reopen-rung3.
- Phase 1 all-fail + Phase 2 breakpoint monotically increasing with capacity → **H_cap**, route scale-up.
- Phase 1 all-fail + Phase 2 breakpoint FLAT across capacities → **H_arch**, route downgrade/redesign.
- Any C0 consistency-control miss, leakage positive, replay mismatch, or fair saturation on a claimed
  "clear" → that cell/result INADMISSIBLE (not a pass); do not tune to rescue.

## 8. Claim ceiling

This sweep answers ONLY capacity-vs-architecture for rung1 **SEEN-rule** eligibility. It does NOT test
rung3 / transfer / H0 / H1 / mechanism. Even if a capacity clears rung1-172, that only **reopens** rung3
— it does not establish transfer. Scout scale (3 seeds) → `route_decision = inconclusive_underpowered`
by design; a positive result authorizes a POWERED (10-seed) rung1 confirm before any rung3, not a
transfer claim. No consciousness / subjectivity / real emotion / self / autonomy / agency / AGI / EGO /
companion / mainline claim.

## 9. Stop conditions

- C0 consistency control fails to reproduce banked ~0.52 → STOP (runner broken).
- Phase 1 clears 172 → STOP Phase 2 (positive; go reopen rung3).
- Per-cell wall-clock exceeds the pre-declared cap `[CAP_HOURS]` → cap that cell, record `steps_run`
  and `val_still_improving_at_stop`, do NOT extend budget to force a pass.
- Any anti-hardcoding trip (threshold change after results, leakage, saturation, ablation non-collapse
  on a claimed clear, second logic path, future-observation use) → STOP + report.

## 10. Files

**Create (NEW, isolated):**
- `src/tlgp_capability_witness_preflight_001a/rung1_capacity_sweep.py` — sweep runner: calls
  `retrieval_model.build_model(cap_params)` per grid cell, reuses frozen splits/world/fair/ideal/
  leakage/context-ablation/replay, trains rung1-only, emits the contract. `--validate-only`,
  `--dry-run`, `--full-run --confirm-full-run <canonical_sha>` guards mirroring the rung3 executor.
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG1_CAPACITY_SWEEP_001A/{FREEZE,DRY_RUN,RUN}/…`
- `tests/test_rung1_capacity_sweep_001a.py` — wiring/guards only.
- (this card)

**FORBIDDEN to change (STOP if touched):** `retrieval_model.py` (0cba9239), `meta_learners.py`
(358d2bb2), `world.py`, `splits.py`, `preregistration.py`, `lower_reference.py`, `leakage.py`,
`rung3_graph_cache_baselines.py` (921d4407), `rung3_single_family_adjudicator.py` (5773f5d1),
`rung3_powered_full_run.py` (a0dcea8d, banked), any banked artifact, `AGENTS.md`, `CLAUDE.md`,
`PHASE_B_FREEZE_REVIEW/design.json`.

## 11. Rollback plan

All new files isolated under new paths; new artifacts under a new dir. No push, no tag. If any protected
file shows a diff → `git checkout --` it and STOP. Negative/failed cells are preserved (evidence), never
patched into passes.

## 12. Pre-implementation freeze requirement

Before implementation: Codex freezes a canonical design JSON (grid, seeds, budget inherited from prereg,
DELTA/EPSILON inherited, clear-threshold, decision rules, per-cell cap) and records its canonical sha256.
Claude reviews + independently recomputes the canonical sha (anti-tuning: freeze before results), reviews
the runner + a tiny dry-run (real training loop, correct eval sets, C0 consistency control wired,
leakage/ablation/replay wired, no banked edits) and pins the runner sha BEFORE any full run — same
freeze≠executor cadence as the rung3 executor.
```
