# TLGP-001B — Capability-Witness Ladder Redesign — R2-R1 (task card)

> Status: R2-R1 DESIGN-ONLY draft. Bounded revision of `TLGP-001B-R2.md` (preserved, unmodified)
> applying the 4 required revisions from the independent card audit
> (`requires_bounded_card_revision_before_prereg_or_implementation`). NOT authorized to run, NOT
> prereg-frozen, NOT self-approved. Drafter ≠ auditor: this version must be RE-AUDITED before any
> prereg freeze or implementation. No src, no training, no git by this card.
>
> R2 (the audited baseline) is preserved at `docs/task_cards/TLGP-001B-R2.md`. This file changes ONLY
> the 4 audited items + their direct corollary; every accepted R2 element is reproduced verbatim.

## [R2-R1] revision log (exactly what changed vs R2; nothing else weakened)
1. **H0 is no longer `else`.** New INVALID enum `tlgp001b_r2_invalid_discriminativeness_or_ablation`;
   shuffle/context-ablation failure now routes to INVALID, not H0. H0 and H1 are both AFFIRMATIVE.
   Corollary (forced by affirmative H0): added terminal `tlgp001b_r2_invalid_inconclusive_underpowered`
   for the CI-straddles-DELTA region, so the gap NEVER silently downgrades 001A.
2. **Rung-1/Rung-0 are family-level eligibility, not global veto.** Pre-registered PRIMARY adjudicators
   = {in_context_gru, in_context_transformer}; amortized_summary_mlp = DIAGNOSTIC lower learned
   reference (recorded, never gates the global verdict). A weak family can no longer veto the run.
3. **Rung 1 gets a baseline-immunity / overlap scanner** (recorded acceptance items): query↔adapt cell
   overlap, direct-lookup solve rate, count_table/predict_all/majority/no-context-meta vs ceiling,
   ideal_seen1 from seen-rule support (recorded, not assumed 1.0), with a cheap-baseline-saturation flag
   that downgrades the rung-1 claim.
4. **`invalid_no_capability_witness` claim ceiling pinned to "this budget/grid"** + mandatory
   training-curve / early-stop / budget-saturation readback per family.

> Lineage / prior negative evidence (MUST read before audit):
> - TLGP-001A: BANKED candidate-free gap-testbed (prereg sha256 `3fdad0f3…`; audit
>   `artifacts/TLGP-001A-AUDIT-001/` → BANK). 001A LIMITATION #6: the headroom is the value of KNOWING
>   the rule family, NOT proof a learner can acquire it.
> - TLGP-001B-R1: official GPU run → **INVALID**. Independent audit `artifacts/TLGP-001B-INVALID-AUDIT-001/`
>   → **B positive_control_design_flaw_likely__r2_required**: R1's CONTROL test ≡ REAL test on the
>   rule-novelty axis (both test 125 UNSEEN rules), so it cannot witness meta capability; R1 also
>   recorded only REAL predictions (capacity decision not replayable).
> - Reusable standard: `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` (predict_all=oracle,
>   exhaustive-legal-query, obs-decodable, amortized saturation families).

- **task_id:** TLGP-001B-R2 · **card_version:** R2-R1
- **research_layer:** engineering_implementation + mechanism_hypothesis_preflight
- **candidate_free:** TRUE — the cross-episode meta-learner is the strongest FAIR baseline, NOT a
  proposed mechanism. NO candidate is introduced. Every witness rung is a baseline/control.
- **mainline integration:** NONE. No EGO mainline / runtime / admission / bridge / product / agent
  behavior is touched, proposed, or enabled.

## problem definition
R1 cannot adjudicate 001A because its mandatory capacity control is not a valid capability witness: on
the rule-novelty axis CONTROL ≡ REAL (both test 125 unseen rules). R2 replaces it with a graded
capability-witness ladder that isolates "can the meta family learn / amortize at all" (rule-novelty held
OUT) from "can it extrapolate to unseen rules" (the experimental question), and makes every witness
decision replayable. R2 does NOT change the world, metric, DELTA/FLOOR/N_SEEDS, or the capacity grid.

## current stage
Capability-witness redesign of the R1 baseline-completeness extension (pre-candidate).

## design principle (terse rationale, not theory)
A capability witness must be a task the learner passes iff its training/optimization path is functional
and the architecture can represent the target, AND whose passing does NOT require answering the
experimental question. Prior art: in-distribution competence before OOD (Garg et al. 2022,
arXiv:2208.01066); fitting capacity witnessed separately from generalization (Zhang et al. 2017,
arXiv:1611.03530); below a task-diversity threshold an ICL learner is a Bayesian retriever over SEEN
tasks — competent on seen, unable on new (Raventós et al. 2023, arXiv:2306.15063); modular-arithmetic
generalization is learnable but late/sample-hungry, so budget adequacy must be witnessed (grokking,
arXiv:2301.02679).

## hypothesis (pre-registered; neither side is the "hoped" answer)
- **H0 / downgrade:** a capability-established, capacity-saturated PRIMARY meta closes the unseen-rule
  headroom → amortizable structure → downgrade 001A.
- **H1 / bank-within-episode:** capability-established, capacity-saturated PRIMARY metas do NOT close
  it, robustly → genuine residual within-episode headroom → 001A banks as a within-episode gap-testbed.
- **Cannot-adjudicate:** the PRIMARY meta family fails the capability witness (rung 1) → 001A NOT
  adjudicated by this family at this budget; NEITHER H0 nor H1. First-class outcome, not an error.

## inherited frozen constants (copied VERBATIM from R1/001A — NEVER re-chosen for R2)
DELTA = 0.10 · FLOOR = 1/K = 0.20 · N_SEEDS = 10 · close rule ≥ ⌈0.9·N⌉ = 9/10 ·
LCB = mean(headroom) − 2·std/√N_SEEDS · world K=5,D=3,M=5,ACTION_CARD=5,N_ADAPT=24,N_QUERY=30,
TRAIN_VALUES={0,1,2}, HELDOUT_VALUES={3,4}, rule=(Σ wᵢxᵢ + c·a) mod K, 625 rules, split 500/125 ·
training budget (Adam, lr∈{1e-3,3e-4} best-on-val, batch 256, max_epochs 200, patience 20,
steps_max 200000), identical across ALL rungs/conditions · capacity grid = R1 grid UNCHANGED
(GRU hidden{64,128,256}×layers{1,2}; Transformer d_model{64,128,256}×layers{2,4},heads 4,ff 4·d;
MLP hidden{(128,128),(256,256)}; witness = largest point per family).
`headroom_vs_meta := ideal_mean − meta_mean` on held-out balanced accuracy.

## [R2-R1] primary adjudicators vs diagnostic family (NEW — revision 2)
- **PRIMARY adjudicators (gate the global verdict):** `in_context_gru`, `in_context_transformer`.
- **DIAGNOSTIC family (recorded, NEVER gates):** `amortized_summary_mlp` — a weaker lower learned
  reference. Its rung-0/rung-1 pass/fail and rung-3 scores are recorded for context but CANNOT trigger
  any global INVALID/H0/H1. This prevents a weak family from vetoing the run or fabricating a verdict.
- A primary family is **ELIGIBLE** iff it passes rung 0 AND rung 1 (capability established for it).
  Let E = the set of eligible PRIMARY families ⊆ {gru, transformer}.

## NEW R2 parameters (to be FROZEN in the R2 prereg BEFORE any run; chosen WITHOUT seeing R1 scores)
- R0_RULES: a small fixed set (proposed 8) drawn from TRAIN_RULES by a NEW frozen seed; full value
  coverage {0,1,2,3,4} for adapt and query.
- Per-rung reference ceiling = the 001A ideal observer evaluated on THAT rung's test set, RECORDED
  (never assumed 1.0). Pass margins use the INHERITED DELTA (no new thresholds).
- NEW frozen seeds for rung-specific episode draws (disjoint episode-id namespaces per rung).

## capability-witness ladder (monotone difficulty; each rung records per-episode predictions)
Same architecture+budget every rung; the ONLY cross-rung difference is DATA (which rules, which values,
seen vs unseen). Every rung's per-seed per-episode predictions (train-fit where required, and held-out),
for PRIMARY and DIAGNOSTIC families, are written to trace and are replay-recomputable WITHOUT retraining.

**Rung 0 — learnability / overfit floor (capacity; Zhang-style).**
- Construct: train on R0_RULES (8 fixed), full values {0,1,2,3,4}; (0a) fit = train-set balanced
  accuracy; (0b) in-distribution held-out = NEW episodes of the SAME 8 rules, same value range.
- Pass (predeclared, per family): (0a) and (0b) ≥ ideal_R0 − DELTA on ≥9/10 seeds.
- Claim ceiling (rung 0): proves ONLY that the optimizer+architecture can fit/represent a small fixed
  rule set. NOT generalization, NOT mechanism, NOT capability on the full family, NOT H1/H0.

**Rung 1 — seen-rule in-distribution capability control (PRIMARY witness; replaces R1's broken control).**
- Construct: train on TRAIN_RULES (500); test on NEW episodes whose rules ∈ TRAIN_RULES (SEEN rules,
  new instances), values {0,1,2} for BOTH adapt and query (rule-novelty AND value-novelty removed).
  Test episode-ids disjoint from train/val.
- Pass (predeclared, per family): meta_balacc ≥ ideal_seen1 − DELTA on ≥9/10 seeds.
- Purpose: isolate "can amortize/retrieve SEEN rules in-distribution" from "can extrapolate to UNSEEN
  rules." Below the Raventós threshold a competent meta is still a competent seen-rule retriever; failing
  rung 1 means the path is too weak to interpret anything downstream.
- **[R2-R1] baseline-immunity / overlap scanner (NEW — revision 3; mandatory RECORDED acceptance items):**
  for the rung-1 test set, record and write to result.json/trace —
  (a) per-episode fraction of query (x,a) cells that also appear in that episode's adaptation set
      (query↔adapt overlap);
  (b) direct-`lookup` solve rate on rung 1;
  (c) rung-1 balanced accuracy of `count_table`, `predict_all`, `majority`, and a `no_context_meta`
      (meta with adaptation context ablated) — i.e. how close cheap/contextless paths get to ceiling;
  (d) `ideal_seen1` computed from the SEEN-rule support actually used (recorded, NOT assumed 1.0);
  (e) `cheap_baseline_saturation` flag := any of {lookup, count_table, predict_all, majority,
      no_context_meta} ≥ ideal_seen1 − DELTA.
  Interpretation rule (predeclared): rung 1 is a capability witness, NOT required to fully beat
  baselines; BUT if `cheap_baseline_saturation` is set, rung 1 proves ONLY "training path runs" and does
  NOT establish "meta uses context" — in that case the discriminativeness gate (context-ablation
  collapse at rung 1, below) is the load-bearing check that the meta's rung-1 score is context-driven.
- Failure ⇒ contributes to INVALID(no_capability_witness) at the family-eligibility level (see verdict).
- **[R2-R1] mandatory budget/training readback (NEW — revision 4):** per primary family at rung 1 record
  train/val loss curves (or per-epoch val balacc), early-stop epoch, best-checkpoint epoch, whether val
  was still improving at stop, and a per-family budget-saturation summary.
- Claim ceiling (rung 1): proves ONLY in-distribution amortization/retrieval of SEEN rules at THIS
  frozen budget/grid. EXPLICITLY NOT mechanism evidence, NOT generalization, NOT H1, NOT "the meta
  learned the family."

**Rung 2 — seen-rule value extrapolation (diagnostic axis-isolation).**
- Construct: SEEN rules (TRAIN_RULES), adapt {0,1,2}, query {3,4}. NEW disjoint episodes.
- Reported metric (NOT a hard branch): meta_balacc + headroom on seen-rule {3,4}. Localizes whether
  value-extrapolation alone is a wall, to interpret rung 3.
- Claim ceiling (rung 2): bounded to value-extrapolation on SEEN rules; says nothing about unseen rules.

**Rung 3 — REAL unseen-rule + unseen-value (the experiment; identical to R1 REAL).**
- Construct: UNSEEN rules (TEST_RULES, 125), adapt {0,1,2}, query {3,4}.
- Adjudicated for H0/H1 ONLY after integrity + rung0 + rung1 + discriminativeness gates (see verdict).
- Claim ceiling (rung 3): H1 = within-episode headroom survives capability-established PRIMARY metas on
  THIS world + THIS family + this frozen grid. H0 = headroom amortized by such a meta. Nothing broader.

## [R2-R1] exact verdict enum (frozen strings) + precedence (revisions 1 & 2)
Terminal enums (7; each mutually exclusive; each must be uniquely fire-able by a tamper axis):
- `tlgp001b_r2_within_episode_headroom_survives_capable_meta`        (H1 / BANK-WITHIN-EPISODE)
- `tlgp001b_r2_headroom_amortized_by_capable_meta__downgrade_001a`   (H0 / DOWNGRADE)
- `tlgp001b_r2_invalid_leakage_or_replay`                            (INVALID — integrity)
- `tlgp001b_r2_invalid_learnability_floor_failed`                    (INVALID — rung 0 / bucket A)
- `tlgp001b_r2_invalid_no_capability_witness`                        (INVALID — rung 1; cannot adjudicate)
- `tlgp001b_r2_invalid_discriminativeness_or_ablation`               (INVALID — ablation/shuffle invalid) [NEW rev 1]
- `tlgp001b_r2_invalid_inconclusive_underpowered`                    (INVALID — rung-3 CI straddles DELTA) [NEW corollary]

Precedence (PURE function of recorded fields; first matching branch fires; H0/H1 are AFFIRMATIVE — there
is NO `else → H0`). Primary families only; the diagnostic MLP never gates:
1. **INVALID(leakage_or_replay)** iff any planted leak uncaught OR any clean channel falsely flagged OR
   replay not exact for ANY rung's recorded predictions.
2. **INVALID(learnability_floor_failed)** iff NO primary family passes rung 0 (≥9/10) — the optimization
   path itself is broken (route: implementation/budget repair).
3. **INVALID(no_capability_witness)** iff ≥1 primary passes rung 0 but E = ∅ (no primary passes rung 1) —
   path runs but cannot witness seen-rule capability (route: closure or stronger-baseline scan).
4. **INVALID(discriminativeness_or_ablation)** iff, for any ELIGIBLE primary family, context-ablation does
   NOT collapse (rung-1 meta not ≤ FLOOR+DELTA without adaptation context) OR shuffle does NOT collapse
   (meta headroom > DELTA on the non-compositional world). [NEW rev 1 — test-validity, never read as H0]
5. **H0 (downgrade)** iff ∃ family ∈ E that CLOSES rung 3 (headroom_vs_meta ≤ DELTA on ≥9/10 seeds).
6. **H1 (bank)** iff E ⊇ {gru, transformer} (BOTH primary eligible) AND both robustly FAIL to close rung 3
   (LCB(headroom) > DELTA each) AND step 4 passed (valid ablations).
7. **INVALID(inconclusive_underpowered)** otherwise — e.g. only one primary eligible and it does not
   close, or the rung-3 CI straddles DELTA. This region must NOT collapse to H0. [NEW corollary of rev 1]
Required `verdict_detail`: per-rung per-family pass booleans, E, the LCBs and close-counts, the
ablation/shuffle values, the rung-1 scanner outputs, and the branch index that fired — all recomputed by
the pure verdict function from recorded fields.

## trace / replay requirement (FIXES R1's replay gap — load-bearing)
trace.jsonl per rung per TEST episode: rung id, seed, family, adaptation tuples, query (x,a), ground-truth
query_e, ideal_pred, each lower-reference pred+balacc, meta pred+balacc, split/rule-split ids, value-regime,
rule-membership tag (seen/unseen). EVERY rung's predictions are recorded, INCLUDING rung 0 (0a fit + 0b
held-out) and the rung-1 capability witness for EVERY seed and EVERY family (R1 recorded only REAL preds,
so its capacity decision was not replayable). Replay recomputes rung-0/rung-1 pass booleans, E, the
scanner outputs, AND the full verdict from recorded predictions WITHOUT retraining. Retraining
reproducibility is checked separately via frozen seeds. A power/MDE statement is REQUIRED on the fired
verdict (min detectable headroom gap at N_SEEDS=10 + observed std).

## leakage (per rung)
Dual-target MI detector (planted + RENAMED + clean controls) on EVERY meta input channel, per rung test
set. Meta NEVER receives rule_id or query_e (structural boundary asserted in trace). Leak audit fail-able
(planted/renamed MUST be caught; clean MUST NOT be flagged). Per BASELINE-IMMUNITY-ADMISSION-STANDARD-001A,
assert no leak route through split ids, seed ids, rule-membership tags, or rung labels.

## ablation (discriminativeness — now its OWN INVALID branch, rev 1)
- context ablation: remove adaptation context → meta MUST drop to floor, evaluated AT RUNG 1 (where an
  eligible meta is ABOVE floor, so the collapse is DISCRIMINATIVE; R1's audit flagged that at rung-3 floor
  this check is vacuous). Also reported at rung 3, explicitly marked non-discriminative when rung-3 meta
  is at floor. Failure → INVALID(discriminativeness_or_ablation), NOT H0.
- shuffle structure (reuse 001A non-compositional world): meta headroom MUST collapse. Failure →
  INVALID(discriminativeness_or_ablation), NOT H0.

## tamper / fail-ability (synthetic fixtures; neutral outcome classes, never the enum)
Each of the 7 terminal branches MUST be uniquely fire-able by ≥1 frozen tamper axis. Minimum axes:
(1) inflate a primary baseline/headroom → flip H1↔not-H1; (2) planted leak missed → INVALID(integrity);
(3) break replay_exact → INVALID(integrity); (4) degrade rung 0 below floor → INVALID(learnability);
(5) make E=∅ (degrade rung 1 for all primary) → INVALID(no_capability_witness); (6) break context-ablation
collapse → INVALID(discriminativeness); (7) break shuffle collapse → INVALID(discriminativeness);
(8) set rung-3 to a CI straddling DELTA → INVALID(inconclusive); (9) close rung-3 for one eligible primary
→ H0. Report booleans + neutral classes only.

## source provenance
delivered_sha256 == executed_sha256 recorded for every R2 src file; R2 prereg canonical sha256 pinned and
embedded in result.json BEFORE any score; FUSE-safe write (author in /tmp, cp to mount, sha256 readback).
The R2 preregistration module LOADS the frozen R2 prereg JSON and raises on sha mismatch (STOP → INVALID).

## baseline / panel (all FAIR; no candidate)
001A lower-reference panel re-applied per rung + primary metas (GRU / Transformer) + diagnostic MLP.
graph-cache family provably dominated by the unseen-value split at rung 3; include `count_table` witness,
expect floor — documented coverage, NOT independent corroboration.

## claim ceiling (global + the two new INVALID terminals)
Bounded offline evidence on whether ONE world's within-episode inference headroom survives a
capability-established cross-episode PRIMARY meta. Candidate-free; tests NO mechanism. NOT
learning-as-mechanism, agency, self, feeling, subjectivity, intelligence, autonomy, AGI,
companion-readiness, or EGO-readiness. Seen-rule rungs (0,1,2) prove only optimization / representation /
amortization capability and are NEVER mechanism evidence or H1.
- **[R2-R1] `invalid_no_capability_witness` ceiling (revision 4):** means THIS family at THIS frozen
  budget/grid failed to provide a capability witness. It does NOT prove the family cannot learn with more
  data / training / task diversity. Must be reported alongside the per-family budget/training-curve readback.
- `invalid_inconclusive_underpowered` means the rung-3 statistic could not robustly distinguish survive vs
  amortize at N_SEEDS=10; it is NOT a downgrade of 001A.

## stop conditions
- rung 0 fails for ALL primary → STOP, INVALID(learnability_floor); route = implementation/budget repair.
- E = ∅ → STOP, INVALID(no_capability_witness); 001A NOT adjudicated by this family at this budget; route
  = close OR pre-candidate stronger-learned-baseline scan; do NOT enlarge capacity to force a pass.
- discriminativeness/ablation invalid → STOP, INVALID; do NOT read as H0.
- inconclusive → STOP, INVALID(inconclusive); do NOT downgrade 001A.
- H0 fires → STOP the special-within-episode route; downgrade 001A; introduce NO candidate.
- H1 fires → bounded bank; do NOT auto-advance to 001C.
- Any capacity enlargement beyond the frozen grid, or any DELTA/FLOOR/N_SEEDS/grid change AFTER seeing
  results → STOP (capacity/threshold tuning); the run is INVALID.

## forbidden (this card / the implementer MUST NOT)
- Enlarge or alter the capacity grid to chase H1, or shrink it to force H0/H1.
- Re-choose DELTA, FLOOR, N_SEEDS, the close fraction, the budget, or the world from R1 results.
- Treat any seen-rule rung (0/1/2) result as mechanism evidence, generalization evidence, or H1.
- Let the diagnostic MLP gate the global verdict.
- Advance to TLGP-001C on ANY R2 outcome without separate operator authorization.
- Edit or reinterpret frozen evidence: `src/tlgp_001a/**`, `artifacts/TLGP-001A/**`,
  `artifacts/TLGP-001A-AUDIT-001/**`, `artifacts/TLGP-001B/**` (R1, preserved as negative governance
  evidence), `artifacts/TLGP-001B-INVALID-AUDIT-001/**`, `docs/task_cards/TLGP-001B-R2.md` (audited
  baseline, preserved). R2 writes ONLY under `src/tlgp_001b_r2/**` and `artifacts/TLGP-001B-R2/**`.
- `scripts/push.*` (hardcoded PAT — BLOCKED) · `CLAUDE.md` · any global config / schema / EGO mainline ·
  LLM / AIRI / external services / credentials. No git operation by the harness.

## out of scope for R2 (preserved reasoning; NOT to be silently pulled in)
A task-diversity sweep (vary #TRAIN_RULES ∈ {8,32,125,500} → chart unseen-rule generalization to locate a
Raventós-style emergence threshold) would turn the binary rung-3 result into a discriminative curve. It is
a SUCCESSOR-card candidate, NOT part of R2, to avoid scope creep and capacity-chasing.

## Auto-Remote-Anchor policy
Default = LOCAL-ONLY. NO automatic remote anchor. Harness performs NO git op. Remote BLOCKED until
`scripts/push.*` hardcoded-PAT is rotated/removed. Any remote anchor is operator-initiated only, scoped
explicit `git add` of named paths — NEVER `git add -A`, NEVER `push.py`. Beware CRLF drift + stuck
`.git/index.lock`; the PAT lives on the user OS, not the sandbox.

## rollback plan
Isolated `src/tlgp_001b_r2/` + `artifacts/TLGP-001B-R2/`. NO edits to 001A, 001B(R1), the audits, or the
R2 baseline card. Rollback = delete the R2 module + R2 artifacts; all prior evidence unaffected.

## authorization gate
DESIGN-ONLY until ALL of: (1) an INDEPENDENT card audit passes THIS R2-R1 card (drafter ≠ auditor;
outcome-neutral); (2) explicit operator "implement TLGP-001B-R2" instruction referencing the frozen R2
prereg sha; (3) a frozen `tlgp_001b_r2` prereg (sha256-hashed) committing the inherited constants
(verbatim), the capacity grid (R1, unchanged), the budget, the rung constructions, R0_RULES, the rung
seeds, the primary/diagnostic family roles, the rung-1 scanner items, and the verdict enum + precedence
BEFORE any training. Until all three exist, NO src, NO run, NO git.
