# TLGP-001B — Capability-Witness Ladder Redesign — R2 (task card)

> Status: R2 DESIGN-ONLY draft for INDEPENDENT CARD AUDIT, then OPERATOR IMPLEMENTATION
> AUTHORIZATION. NOT authorized to run. No src written, no training, no git by this card.
> Supersedes the *capacity-control design* of R1 only; preserves all R1 evidence.
>
> Lineage / prior negative evidence (MUST read before audit):
> - TLGP-001A: BANKED candidate-free gap-testbed (prereg sha256 `3fdad0f3…`; audit
>   `artifacts/TLGP-001A-AUDIT-001/` → BANK). 001A LIMITATION #6: the headroom is the value of
>   KNOWING the rule family, NOT proof a learner can acquire it.
> - TLGP-001B-R1: official GPU run emitted **INVALID** (`tlgp001b_invalid_capacity_or_leakage_or_replay`).
>   Independent audit `artifacts/TLGP-001B-INVALID-AUDIT-001/` → verdict **B
>   positive_control_design_flaw_likely__r2_required**. Decisive defect: R1's CAPACITY_CONTROL relaxes
>   only value-novelty {3,4} in TRAIN/VAL queries while its **test set is byte-identical to REAL**
>   (held-out values on 125 UNSEEN rules). "Control closes" therefore demands ~the H1 success condition
>   itself, so it cannot witness meta capability. R1's `survives_branch=true` (H1-shaped) was correctly
>   suppressed by INVALID precedence. Secondary defect: R1 recorded only REAL predictions — the
>   capacity decision was NOT replayable from recorded predictions.
> - Reusable standard: `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` (predict_all=oracle,
>   exhaustive-legal-query, obs-decodable, amortized saturation families).

- **task_id:** TLGP-001B-R2
- **research_layer:** engineering_implementation + mechanism_hypothesis_preflight
- **candidate_free:** TRUE — the cross-episode meta-learner remains the strongest FAIR baseline, NOT a
  proposed mechanism. R2 introduces NO candidate. Every witness rung is a baseline/control, never a claim.
- **mainline integration:** NONE. No EGO mainline / runtime / admission / bridge / product / agent
  behavior is touched, proposed, or enabled.

## problem definition
R1 cannot adjudicate 001A because its mandatory capacity control is not a valid capability witness: on
the rule-novelty axis CONTROL ≡ REAL (both test 125 unseen rules), so a 0/10 failure is confounded
between "meta is underpowered" and "the held-out-rule task is intrinsically hard." R2's job is NARROW:
replace the single broken control with a **graded capability-witness ladder** that isolates "can the
meta family learn / amortize at all" (rule-novelty held OUT) from "can it extrapolate to unseen rules"
(the experimental question), and make every witness decision replayable. R2 does NOT change the world,
the metric, DELTA/FLOOR/N_SEEDS, or the capacity grid.

## current stage
Capability-witness redesign of the R1 baseline-completeness extension (pre-candidate). Decides whether
001A can be adjudicated at all by THIS meta family, and if so whether the within-episode headroom
survives (H1) or is amortized (H0).

## design principle (why a ladder; terse rationale, not theory)
A capability witness must be a task the learner passes **iff its training/optimization path is
functional and the architecture can represent the target**, AND whose passing does NOT require
answering the experimental question. Prior art establishes the pattern: establish in-distribution
competence against the optimal estimator before probing OOD (Garg et al. 2022, arXiv:2208.01066);
fitting capacity is witnessed separately from generalization (Zhang et al. 2017, arXiv:1611.03530);
below a task-diversity threshold an in-context learner is a Bayesian *retriever* over SEEN tasks —
competent on seen tasks, unable on new ones (Raventós et al. 2023, arXiv:2306.15063); modular-arithmetic
generalization is learnable but late/sample-hungry, so budget adequacy must be witnessed or "can't
learn" is conflated with "undertrained" (grokking, arXiv:2301.02679). The ladder operationalizes
exactly these as predeclared gates.

## hypothesis (pre-registered; neither side is the "hoped" answer)
- **H0 / downgrade:** a capability-established, capacity-saturated meta closes the unseen-rule headroom
  → the gap is amortizable structure → downgrade 001A.
- **H1 / bank-within-episode:** a capability-established, capacity-saturated meta does NOT close it,
  robustly → genuine residual within-episode headroom → 001A banks as a within-episode gap-testbed.
- **No-capability / cannot-adjudicate:** the meta family fails the capability witness (rung 1) →
  001A is NOT adjudicated by this family; NEITHER H0 nor H1; route to closure or a stronger learned
  baseline scan. This third outcome is first-class, not an error.

## inherited frozen constants (copied VERBATIM from R1/001A — NEVER re-chosen for R2)
DELTA = 0.10 · FLOOR = 1/K = 0.20 · N_SEEDS = 10 · close rule ≥ ⌈0.9·N⌉ = 9/10 ·
LCB = mean(headroom) − 2·std/√N_SEEDS · world K=5,D=3,M=5,ACTION_CARD=5,N_ADAPT=24,N_QUERY=30,
TRAIN_VALUES={0,1,2}, HELDOUT_VALUES={3,4}, rule=(Σ wᵢxᵢ + c·a) mod K, 625 rules, split 500/125 ·
training budget (Adam, lr∈{1e-3,3e-4} best-on-val, batch 256, max_epochs 200, patience 20,
steps_max 200000), identical across ALL rungs/conditions · capacity grid = R1 grid UNCHANGED
(GRU hidden{64,128,256}×layers{1,2}; Transformer d_model{64,128,256}×layers{2,4},heads 4,ff 4·d;
MLP hidden{(128,128),(256,256)}; witness = largest point per family).
`headroom_vs_meta := ideal_mean − meta_mean` on held-out balanced accuracy.

## NEW R2 parameters (to be FROZEN in the R2 prereg BEFORE any run; chosen WITHOUT seeing R1 scores)
- R0_RULES: a small fixed set (proposed 8) drawn from TRAIN_RULES by a NEW frozen seed; full value
  coverage {0,1,2,3,4} for adapt and query.
- Rung pass margins are the INHERITED DELTA (not new thresholds). Per-rung reference ceiling is the
  001A ideal observer evaluated on THAT rung's test set (recorded, not assumed 1.0).
- NEW frozen seeds for the rung-specific episode draws (disjoint episode-id namespaces per rung).
- These NEW values are predeclared gate parameters, NOT edits of any R1 threshold.

## capability-witness ladder (monotone difficulty; each rung records per-episode predictions)
Each rung trains the SAME architecture+budget; the ONLY differences across rungs live in the DATA
(which rules, which values, seen vs unseen). Every rung's per-seed per-episode predictions (train-fit
where required, and held-out) are written to trace and are replay-recomputable WITHOUT retraining.

**Rung 0 — learnability / overfit floor (capacity; Zhang-style).**
- Construct: train on R0_RULES (8 fixed rules), full values {0,1,2,3,4}; (0a) fit check = train-set
  balanced accuracy; (0b) in-distribution held-out = NEW episodes of the SAME 8 rules, same value range.
- Pass (predeclared): both (0a) and (0b) ≥ ideal_R0 − DELTA on ≥9/10 seeds, per family.
- Failure ⇒ INVALID(learnability_floor) — the path cannot fit even a tiny fixed rule set; this is an
  implementation/budget problem (audit bucket A), NOT evidence about 001A.
- Claim ceiling (rung 0): proves ONLY that the optimizer+architecture can fit/represent a small fixed
  rule set. NOT generalization, NOT mechanism, NOT capability on the full family, NOT H1/H0.

**Rung 1 — seen-rule in-distribution capability control (PRIMARY witness; replaces R1's broken control).**
- Construct: train on TRAIN_RULES (500); test on NEW episodes whose rules are drawn from TRAIN_RULES
  (SEEN rules, new instances), values {0,1,2} for BOTH adapt and query (rule-novelty AND value-novelty
  both removed). Test episode-ids disjoint from train/val.
- Pass (predeclared): meta_balacc ≥ ideal_seen1 − DELTA on ≥9/10 seeds, per family.
- This is the MANDATORY capability gate. It isolates "can amortize/retrieve SEEN rules in-distribution"
  from "can extrapolate to UNSEEN rules." Below the Raventós task-diversity threshold a competent meta
  is still a competent seen-rule retriever, so failing rung 1 means the path is too weak to interpret
  anything downstream.
- Failure ⇒ INVALID(no_capability_witness) — cannot adjudicate 001A with this family; route to closure
  or a stronger learned-baseline scan; do NOT enlarge capacity to force a pass; do NOT read as H0/H1.
- Claim ceiling (rung 1): proves ONLY in-distribution amortization/retrieval of SEEN rules. This is
  EXPLICITLY NOT mechanism evidence, NOT generalization, NOT H1, NOT "the meta learned the family."

**Rung 2 — seen-rule value extrapolation (diagnostic axis-isolation).**
- Construct: SEEN rules (TRAIN_RULES), adapt {0,1,2}, query {3,4} (value extrapolation on rules the
  meta has seen). NEW disjoint episodes.
- Reported metric (NOT a hard branch): meta_balacc and headroom on seen-rule {3,4}. Localizes whether
  value-extrapolation alone is a wall, separately from rule-novelty, to interpret rung 3.
- Claim ceiling (rung 2): bounded to value-extrapolation on SEEN rules; says nothing about unseen rules.

**Rung 3 — REAL unseen-rule + unseen-value (the experiment; identical to R1 REAL).**
- Construct: UNSEEN rules (TEST_RULES, 125), adapt {0,1,2}, query {3,4}.
- Adjudicated for H1/H0 ONLY IF rung 0 AND rung 1 passed (capability established) AND integrity gates
  pass. H1 = LCB(headroom_vs_meta) > DELTA at the largest capacity of EVERY family AND context-ablation
  collapse (at rung 1, see ablation) AND shuffle collapse. H0 = meta closes (headroom ≤ DELTA on ≥9/10).
- Claim ceiling (rung 3): H1 = within-episode headroom survives a CAPABILITY-ESTABLISHED meta on THIS
  world + THIS family + this frozen grid. H0 = headroom amortized by such a meta. Nothing broader.

## exact verdict enum (frozen strings) + precedence (computed, fail-able both ways)
- `tlgp001b_r2_within_episode_headroom_survives_capable_meta`            (H1 / BANK-WITHIN-EPISODE)
- `tlgp001b_r2_headroom_amortized_by_capable_meta__downgrade_001a`       (H0 / DOWNGRADE)
- `tlgp001b_r2_invalid_leakage_or_replay`                               (INVALID — integrity)
- `tlgp001b_r2_invalid_learnability_floor_failed`                       (INVALID — rung 0 / bucket A)
- `tlgp001b_r2_invalid_no_capability_witness`                          (INVALID — rung 1; cannot adjudicate)

Precedence (first matching branch fires; each branch must be independently fail-able by a tamper probe):
1. INVALID(leakage_or_replay) iff any planted leak uncaught OR any clean channel falsely flagged OR
   replay not exact for ANY rung's recorded predictions.
2. else INVALID(learnability_floor_failed) iff rung 0 does not pass on ≥9/10 seeds for any family.
3. else INVALID(no_capability_witness) iff rung 1 does not pass on ≥9/10 seeds for any family.
4. else H1 iff at the largest capacity of EVERY family: LCB(rung-3 headroom_vs_meta) > DELTA AND
   context-ablation collapse (rung 1 meta → ≤ FLOOR+DELTA without adaptation context) AND shuffle
   collapse (meta headroom ≤ DELTA on the non-compositional world).
5. else H0.
Required `verdict_detail`: per-rung per-family pass booleans, the LCBs, ablation/shuffle values, and
the branch index that fired — all recomputed by the pure verdict function from recorded fields.

## trace / replay requirement (FIXES R1's replay gap — load-bearing)
trace.jsonl per rung per TEST episode: rung id, seed, adaptation tuples, query (x,a), ground-truth
query_e, ideal_pred, each lower-reference pred+balacc, meta pred+balacc, split/rule-split ids,
value-regime, rule-membership tag (seen/unseen). **EVERY rung's predictions are recorded, INCLUDING
rung 0 (0a fit + 0b held-out) and the rung-1 capability witness for EVERY seed** — R1 recorded only
REAL preds, so its capacity decision was not replayable; R2 MUST record control/witness predictions and
recompute rung-0/rung-1 pass booleans AND the full verdict from recorded predictions WITHOUT retraining.
Retraining reproducibility is checked separately via frozen seeds. A power/MDE statement is REQUIRED on
the fired verdict (min detectable headroom gap at N_SEEDS=10 + observed std).

## leakage (per rung)
Dual-target MI detector (planted + RENAMED + clean controls) on EVERY meta input channel, run on each
rung's test set. The meta NEVER receives rule_id or query_e (structural boundary asserted in trace).
Leak audit must remain fail-able (a planted/renamed leak MUST be caught; a clean channel MUST NOT be
flagged). Per BASELINE-IMMUNITY-ADMISSION-STANDARD-001A, additionally assert no leak route through
split ids, seed ids, rule-membership tags, or rung labels.

## ablation (discriminativeness fixed vs R1)
- context ablation: remove adaptation context → meta MUST drop to floor. Evaluated AT RUNG 1, where a
  capable meta is ABOVE floor, so the collapse is DISCRIMINATIVE (R1's audit flagged that at rung-3
  floor the meta is at chance anyway, making context-ablation vacuous). Also reported at rung 3 for
  completeness, explicitly marked non-discriminative when the rung-3 meta is at floor.
- shuffle structure (reuse 001A non-compositional world): meta headroom MUST collapse (else a leak is
  being exploited).

## tamper / fail-ability (≥7 frozen axes; synthetic fixtures; neutral outcome classes, never the enum)
Each axis MUST flip the computed verdict equivalence class: (1) inflate a fair baseline → not-H1;
(2) planted leak missed → INVALID(integrity); (3) break shuffle collapse → not-H1; (4) break
replay_exact → INVALID(integrity); (5) degrade rung-3 capacity-witness → not-H1; **(6) degrade rung 0
below floor → INVALID(learnability_floor); (7) degrade rung 1 below capability → INVALID(no_capability_witness).**
Axes 6–7 are NEW and guard the two new INVALID branches.

## source provenance
delivered_sha256 == executed_sha256 recorded for every R2 src file; R2 prereg canonical sha256 pinned
and embedded in result.json BEFORE any score; FUSE-safe write (author in /tmp, cp to mount, sha256
readback). The R2 preregistration module LOADS the frozen R2 prereg JSON and raises on sha mismatch
(STOP → INVALID), mirroring R1.

## baseline / panel (all FAIR; no candidate)
001A lower-reference panel re-applied per rung + the R1 meta families (GRU / Transformer /
amortized-summary MLP). graph-cache family (graph_lookup / transition_table / successor_map /
count_table / episodic_traversal) is provably dominated by the unseen-value split at rung 3; include
`count_table` witness, expect floor — documented coverage, NOT independent corroboration.

## claim ceiling (global)
Bounded offline evidence on whether ONE world's within-episode inference headroom survives a
capability-established cross-episode meta. Candidate-free; tests NO mechanism. NOT learning-as-mechanism,
agency, self, feeling, subjectivity, intelligence, autonomy, AGI, companion-readiness, or EGO-readiness
evidence. Seen-rule rungs (0,1,2) prove only optimization/representation/amortization capability and are
NEVER mechanism evidence or H1. Any negative is bounded to THIS world + THIS meta family + this frozen
capacity grid.

## stop conditions
- rung 0 fails → STOP, INVALID(learnability_floor); route = implementation/budget repair card; do NOT
  emit H0/H1.
- rung 1 fails → STOP, INVALID(no_capability_witness); 001A NOT adjudicated by this family; route =
  close the route OR pre-candidate scan for a stronger learned baseline; do NOT enlarge capacity to
  force a pass; do NOT read as H0/H1.
- H0 fires → STOP the special-within-episode route for this world; downgrade 001A; introduce NO candidate.
- H1 fires → bounded bank (within-episode headroom survives a capable meta); do NOT auto-advance to 001C.
- Any capacity enlargement beyond the frozen grid, or any DELTA/FLOOR/N_SEEDS/grid change AFTER seeing
  results → STOP (capacity/threshold tuning); the run is INVALID.

## forbidden (this card / the implementer MUST NOT)
- Enlarge or alter the capacity grid to chase H1, or shrink it to force H0/H1.
- Re-choose DELTA, FLOOR, N_SEEDS, the close fraction, the budget, or the world from R1 results.
- Treat any seen-rule rung (0/1/2) result as mechanism evidence, generalization evidence, or H1.
- Advance to TLGP-001C on ANY R2 outcome without separate operator authorization.
- Edit or reinterpret frozen evidence: `src/tlgp_001a/**`, `artifacts/TLGP-001A/**`,
  `artifacts/TLGP-001A-AUDIT-001/**`, `artifacts/TLGP-001B/**` (R1, preserved as negative governance
  evidence), `artifacts/TLGP-001B-INVALID-AUDIT-001/**`. R2 writes ONLY under `src/tlgp_001b_r2/**` and
  `artifacts/TLGP-001B-R2/**`.
- `scripts/push.*` (hardcoded PAT — BLOCKED) · `CLAUDE.md` · any global config / schema / EGO mainline ·
  LLM / AIRI / external services / credentials.
- No git operation by the harness (write artifacts only).

## out of scope for R2 (preserved reasoning; NOT to be silently pulled in)
A task-diversity sweep (vary #TRAIN_RULES ∈ {8,32,125,500} and chart unseen-rule generalization to
locate a Raventós-style emergence threshold) would convert a binary rung-3 result into a discriminative
curve. It is a candidate for a SUCCESSOR card, NOT part of R2, to avoid scope creep and capacity-chasing.

## Auto-Remote-Anchor policy
Default = LOCAL-ONLY. NO automatic remote anchor. Harness performs NO git op. Remote BLOCKED until
`scripts/push.*` hardcoded-PAT is rotated/removed. Any remote anchor is operator-initiated only, scoped
explicit `git add` of named paths — NEVER `git add -A`, NEVER `push.py`. Beware CRLF drift + stuck
`.git/index.lock`; the PAT lives on the user OS, not the sandbox.

## rollback plan
Isolated `src/tlgp_001b_r2/` + `artifacts/TLGP-001B-R2/`. NO edits to 001A, 001B(R1), or any audit
artifact. Rollback = delete the R2 module + R2 artifacts; all prior evidence unaffected.

## authorization gate
DESIGN-ONLY until ALL of: (1) an INDEPENDENT card audit passes this card (drafter ≠ auditor;
outcome-neutral); (2) explicit operator "implement TLGP-001B-R2" instruction referencing the frozen R2
prereg sha; (3) a frozen `tlgp_001b_r2` prereg (sha256-hashed) committing DELTA/FLOOR/N_SEEDS (inherited
verbatim), the capacity grid (R1, unchanged), the budget, the rung constructions, R0_RULES, the rung
seeds, and the verdict enum + precedence BEFORE any training. Until all three exist, NO src, NO run, NO git.
