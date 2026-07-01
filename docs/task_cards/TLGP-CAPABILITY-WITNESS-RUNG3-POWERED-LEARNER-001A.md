# TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A

**Status: AUTHORIZED by operator (Zhouyu), 2026-06-30. Execute in TWO PHASES: (A) freeze design + implement + tiny smoke → STOP for independent (Claude) audit of the frozen design & harness; (B) only after Phase A clears, launch the full 10-seed GPU run. Do NOT freeze-and-run in one shot (the run is ~28–82h; a design/governance bug caught after is a huge waste).**
This card authorizes NOTHING by itself. Codex must freeze a canonical design
(`*.frozen_design.json`, `_frozen_canonical_sha256` over the underscore-stripped, sort-keys,
compact, ensure_ascii JSON — SAME scheme as the POWERED/RERUN/PROBE cards) and record the sha
BEFORE reading any result. This is the REAL transfer experiment (GPU, expensive).

## task_id
TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A

## research_layer
engineering implementation + mechanism-hypothesis (learning/adaptation). GPU learner run.
NOT subjectivity/consciousness. Claim ceiling enforced (below).

## problem_definition
rung0 (SEEN rules) passed as a formal terminal (banked `7dfb0bde`). The candidate-free rung3
identifiability probe (banked/verified) showed unseen rules are SOLVABLE IN PRINCIPLE
(ideal ≈0.96 ≫ fair_max ≈0.20; headroom ≈0.76) ⇒ the rung3 wall is LEARNABILITY, not
identifiability. The open question this card tests: **can the validated retrieval model LEARN to
do unseen-rule inference — i.e. amortize the Bayesian ideal on rules it never trained on — or
does within-episode headroom survive?** This is the prereg's R1 REAL experiment.

## PRE-DECLARED DEVIATION (governance — read first)
The prereg `6e61a831` names the PRIMARY families as `in_context_gru` + `in_context_transformer`
(the mean-POOLING metas). Positive-control work proved those pool the adapt set and structurally
cannot do in-context retrieval — they are a CONFOUNDED instrument. This card SUBSTITUTES the
validated `retrieval_model` (`0cba9239`, per-example attention, passed rung0 + positive controls)
as the single PRIMARY family. Consequences, all frozen in design.json BEFORE running:
- This is NOT the prereg executed as-written; it is the prereg's world/splits/metric/decision with
  the primary family replaced by the validated instrument. Declare it explicitly; do NOT silently
  reinterpret the prereg.
- The prereg's H1 requires "BOTH primary families eligible." With ONE validated family the
  two-family clause cannot be met; the decision is SCOPED to the retrieval family (single-family
  H0/H1), declared as a deviation. Claim ceiling narrows accordingly.
- Do NOT edit the prereg, verdict.py, route_decision.py, meta_learners.py, retrieval_model.py, or
  any `src/tlgp_001b_r2/*` / `src/tlgp_001a/*`. Substitution is via a NEW runner that IMPORTS the
  frozen model read-only. If a reused adjudicator cannot express single-family scoping without
  editing it, write a NEW frozen adjudicator that implements the prereg decision_statistic verbatim
  (self-tested) — do NOT modify the banked one (governance-self-modification = STOP).

## prerequisites (prereg rung3.adjudicated_only_after — MUST hold before rung3 is adjudicated)
1. integrity pass (source shas, no banked edits).
2. rung0 pass — DONE (`7dfb0bde`), retrieval_model.
3. **rung1 eligibility (E)** — NOT yet established for retrieval_model → Stage 1 of THIS card.
4. discriminativeness pass — rung1_scanner cheap-baseline saturation check + context-ablation.

## hypothesis (prereg decision_statistic, single-family scoped)
- `headroom_vs_meta = ideal_mean − meta_mean` on rung3 test.
- **H0 (amortized / transfer succeeds):** retrieval_model closes to ideal — `headroom ≤ DELTA` on
  ≥ close_fraction_min (9/10) seeds. Bounded capability result: this architecture amortizes
  unseen-rule inference on THIS world+grid.
- **H1 (headroom survives):** retrieval_model robustly fails to close — `LCB(headroom) > DELTA`
  (LCB = mean − 2·std/√N_SEEDS). Bounded: within-episode headroom survives a capability-established
  meta on THIS world+family+grid. NOTHING broader (NOT "recurrence needed", NOT mechanism proof).
- **inconclusive → INVALID(inconclusive):** CI straddles DELTA, or eligibility/discriminativeness
  not cleanly met. NEVER auto-collapse to H0 or H1.

## system_class (bounded formal object)
- World (read-only `src/tlgp_001a.world` via `src/tlgp_001b_r2.world`): effect `(Σ wᵢxᵢ + c·a) mod K`,
  K=5, D=3, 625 rules, N_ADAPT=24, N_QUERY=30.
- Splits (read-only `src/tlgp_001b_r2/splits.py`; `split_assertions` MUST pass):
  - rung1: train TRAIN_RULES(500) / test TRAIN_RULES SEEN new disjoint episodes; values {0,1,2}.
  - rung3: train TRAIN_RULES(500) withheld-regime values {0,1,2} / test TEST_RULES(125 UNSEEN),
    query values {3,4}; assert `rung3_test_rules_subset_of_test` and disjoint from TRAIN_RULES.
  - rung2 (diagnostic, reuses the rung3 model, trains_model=false): TRAIN_RULES SEEN, query {3,4}.
- Learner: `retrieval_model` (`0cba9239`, READ-ONLY import). Capacity FROZEN d_model256/layers4/
  heads4/ff_mult4 (identical to rung0 — capacity change = STOP). No rule_id/query_e as model input.
- Budget: prereg `training_budget` (identical across rungs; DATA is the ONLY permitted cross-rung
  difference — never compute/capacity/budget). Freeze the exact lr policy (grid {1e-3,3e-4} + val
  selection, per prereg) in design.json. Seeds = prereg MODEL_SEEDS (10).
- Agents for headroom: `ideal` = `world.ideal_predictions` (frozen Bayesian ceiling; per-rung,
  never assumed 1.0); fair panel = `lower_reference` five + the REAL graph-cache from the probe
  (`rung3_graph_cache_baselines.successor_map`, N1, not an alias) for saturation/discriminativeness.

## stages
STAGE 0 — FREEZE design.json (canonical sha) BEFORE any run: capacity (frozen), seeds, budget/lr
policy, family substitution declaration, per-rung pass rules + decision statistic, controls,
claim ceiling. Print + record the sha; never change after results.

STAGE 1 — rung1 eligibility (E):
Train retrieval_model on TRAIN_RULES (values {0,1,2}); eval SEEN-rule disjoint test episodes.
Pass rule: `meta_balacc ≥ (ideal_seen1 − DELTA)` on ≥9/10 seeds. Run `rung1_scanner` cheap-baseline
saturation (lookup/count_table/predict_all/majority/no_context). DISCRIMINATIVENESS: run a
context-ablation (shuffle adapt across episodes AND no-adapt) — meta MUST collapse toward baseline
under ablation, proving it USES adapt context (not just baseline-level performance). If rung1 fails
OR ablation does not collapse → STOP + failure_manifest (retrieval_model not eligible; rung3 not
adjudicable). Record dense val curves.

STAGE 2 — rung3 REAL (only if Stage 1 eligible + discriminativeness pass):
Train retrieval_model withheld-regime (TRAIN_RULES, values {0,1,2}); eval TEST_RULES (125 UNSEEN),
query values {3,4}. Per seed compute ideal_mean, meta_mean, fair panel (incl real graph_cache),
`headroom_vs_meta = ideal − meta`; per-seed → panel; LCB. Leakage detector per rung (planted caught,
real clean; meta never gets rule_id/query_e). Adjudicate via the frozen decision statistic
(reuse `src/tlgp_001b_r2/verdict.py` UNMODIFIED if it expresses single-family H0/H1; else a NEW
self-tested frozen adjudicator implementing the prereg decision_statistic verbatim) → H0 / H1 /
INVALID(inconclusive). STOP at the verdict.

STAGE 3 — rung2 diagnostic (REPORTED, does NOT gate): reuse the Stage-2 rung3 model (trains_model
=false); eval SEEN rules, query {3,4}. Contrast value-extrapolation (rung2) vs rule-novelty (rung3)
holding query {3,4} fixed. Diagnostic only.

## baselines
Per rung: ideal ceiling (excluded from fair panel); fair panel = lower_reference five + real
graph_cache (N1). rung1 cheap-baseline saturation scanner. Context-ablation (shuffle-adapt,
no-adapt) as the discriminativeness control — the decisive guard that the meta uses adapt, not
memorization/amortized-prior. If fair saturates the rung3 bar, report baseline saturation, not H1.

## ablation
1. Context-ablation (adapt shuffled across episodes; adapt removed) — meta must collapse toward
   fair; failure to collapse ⇒ meta not context-using ⇒ discriminativeness FAIL ⇒ STOP.
2. rung2 value-extrapolation contrast (SEEN rules, query {3,4}) vs rung3 rule-novelty.
3. (optional, reported) capacity is FROZEN — no capacity sweep; any capacity change is a STOP.

## trace_replay_requirement
`trace.jsonl` per episode per rung: seed, rung/split, rule_id (LOGGED for audit, NEVER a model
input), adapt tensor hash, meta per-query prediction, ideal per-query prediction, each fair
prediction, per-episode meta/ideal/fair balacc, per-episode headroom_vs_meta; plus dense per-seed
val curves (`val_curves.jsonl`, LFS). Replay reconstructs per-seed headroom + the verdict from
trace alone (no future info, no learner state beyond recorded preds), matching result within 1e-9.

## acceptance_gate
Eligibility (Stage 1) MUST pass before Stage 2 is adjudicated. rung3 verdict = frozen self-tested
adjudicator output over the recorded per-seed headroom (H0 / H1 / INVALID). Clean-room reproducible
from route_decision_input.json. Verdict is COMPUTED, never a report literal.

## anti_hardcoding_audit
- retrieval_model imported READ-ONLY; capacity/budget frozen; no rule_id/query_e model input.
- unseen split asserted via `splits.split_assertions` (rung3 test ⊂ TEST_RULES, disjoint from
  TRAIN_RULES); logged per rung.
- ideal = frozen `world.ideal_predictions`; graph_cache = real successor_map (not alias).
- DELTA/close_fraction_min/N_SEEDS read from prereg (canonical sha verified); not tuned after results.
- family substitution frozen + declared (not a silent prereg reinterpretation).
- decision from frozen adjudicator (verdict.py unmodified, or a new self-tested one); all terminals
  reachable (self-test). No edit to any banked/frozen source (governance-self-mod = STOP).
- context-ablation present and decisive (guards amortized-prior / memorization false positives).

## evidence_contract
`artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG3_POWERED_LEARNER_001A/`:
`result.json` (+claim_ceiling field), `trace.jsonl` (LFS), `val_curves.jsonl` (LFS),
`baseline_comparison.json` (per rung, incl real graph_cache), `ablation_report.json`
(context-ablation + rung2), `eligibility_report.json` (rung1 + scanner + discriminativeness),
`leakage_report.json` (per rung), `replay_report.json`, `route_decision_input.json`,
`route_decision.json`, `manifest.json` (source shas, prereg sha, frozen-design sha, capacity,
split assertions, GPU env, family-substitution declaration). `failure_manifest.json` on any STOP.

## claim_ceiling
Bounded rung3 transfer evidence for the retrieval_model on THIS world+grid ONLY.
- H0 = this architecture AMORTIZES unseen-rule inference on this testbed (a bounded capability/
  transfer result). H1 = it does NOT; within-episode headroom survives a capability-established meta
  on THIS world+family+grid. Single validated family → decision scoped to the retrieval family.
- Proves NOTHING about: mechanism validity, agency, self, subjectivity, real autonomy, AGI, EGO/
  companion readiness, or the correctness of Bio-CMBC/CVPSM/VCCO/CMBC/R-G. H1 is NOT evidence that
  "recurrence/consciousness is required" — only that this feedforward meta did not amortize this
  grid.

## stop_conditions
rung1 not eligible; context-ablation does not collapse (meta not context-using); leakage
planted-not-caught; capacity/budget changed; ideal reads a forbidden input; graph_cache is an alias;
split-disjoint assertion fails; DELTA/thresholds tuned after results; verdict not from the frozen
self-tested adjudicator; any edit to banked/frozen source or the prereg (governance-self-mod).
→ STOP + failure_manifest.json; do NOT commit, push, or add audit/review layers.

## rollback_plan
New isolated files only (`src/tlgp_capability_witness_preflight_001a/rung3_powered_learner.py`, a
new frozen adjudicator if verdict.py cannot be reused unmodified, the artifact dir, this card's
frozen design). No banked/frozen file touched. Rollback = delete the new files/artifacts.

## out_of_scope
No capacity/budget change; no pooling metas; no EGO/LLM/AIRI/UI; no schema migration to the prereg/
verdict/route_decision; no push/PR; no rewrite of banked artifacts; no broadening the claim beyond
the single-family, this-world bounded transfer statement. Emit artifacts and STOP for independent
(Claude) re-audit.

## compute_note
GPU (operator machine, via Codex). rung1 + rung3 × 10 seeds × full budget is a long run (prior TLGP
full runs ran ~28–82h). Early-stop is allowed per the prereg budget. Emit artifacts, STOP at the
verdict, no commit/push — leave everything for independent re-audit.
