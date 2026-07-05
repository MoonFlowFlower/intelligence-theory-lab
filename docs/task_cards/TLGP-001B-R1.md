# TLGP-001B — Cross-Episode Meta-Learner Panel Extension — R1 (task card)

> Status: R1 (revised draft) for OPERATOR IMPLEMENTATION AUTHORIZATION. NOT yet authorized to run.
> Lineage: extends TLGP-001A (BANKED candidate-free gap-testbed; prereg sha256 `3fdad0f3…`;
> independent audit `artifacts/TLGP-001A-AUDIT-001/` → BANK). Read TLGP-001A LIMITATIONS #2 first.
> R1 fills the 8 fields flagged at draft review: DELTA, N_SEEDS, capacity grid, training budget,
> split construction, exact verdict enum, forbidden files, Auto-Remote-Anchor policy.

- **task_id:** TLGP-001B
- **research_layer:** engineering_implementation + mechanism_hypothesis_preflight
- **candidate_free:** TRUE — the cross-episode meta-learner is the strongest FAIR baseline, NOT
  the lab's proposed mechanism. No candidate is introduced in 001B.

## problem definition
TLGP-001A's headroom (ideal in-family Bayes = 1.000 vs every per-episode fair baseline ≈ 0.20,
floor) is, by construction (001A LIMITATION #6), the value of KNOWING the rule family. All 001A
baselines are per-episode / cold. Gating question: **does the headroom survive a cross-episode
meta-learner that may amortize the mod-K family across many episodes?**

## current stage
Baseline-completeness extension (pre-candidate). Decides whether 001A banks as a *within-episode*
gap-testbed (H1) or must be downgraded (H0).

## hypothesis (pre-registered, two-sided; neither is the "hoped" answer)
- **H0 / downgrade:** a capacity-saturated meta-learner trained on the withheld regime closes the
  held-out headroom → gap is amortizable structure → downgrade 001A's claim.
- **H1 / bank-stronger:** even the largest-capacity meta-learner does NOT close it, robustly →
  genuine residual within-episode headroom → 001A banks as within-episode gap-testbed; a candidate
  (TLGP-001C) may follow.

## [R1] DELTA
**DELTA = 0.10**, inherited unchanged from the frozen TLGP-001A band (floor = 1/K = 0.20). Reused
verbatim so the bank/downgrade boundary is NOT re-chosen for 001B (anti threshold-tuning).
`headroom_vs_meta := ideal_mean − meta_mean` on the held-out balanced-accuracy metric.

## [R1] N_SEEDS + decision statistic
**N_SEEDS = 10** independent training seeds per (architecture, capacity) point (controls model
init, data order, batch shuffle). Decision uses a one-sided lower confidence bound:
`LCB = mean(headroom_vs_meta) − 2 · std/sqrt(N_SEEDS)`.
- H1 requires **LCB > DELTA** (not a single lucky seed).
- Capacity control must close on **≥ 9/10 seeds** (`headroom_vs_meta ≤ DELTA`).
- A power/MDE statement is REQUIRED on the fired verdict: report the minimum detectable headroom
  gap at N_SEEDS=10 and the observed std.

## [R1] capacity grid (the load-bearing anti-killer; largest point = saturation witness)
- in-context GRU: hidden ∈ {64, 128, 256} × layers ∈ {1, 2}
- in-context Transformer: d_model ∈ {64, 128, 256} × layers ∈ {2, 4}, heads = 4, ff = 4·d_model
- amortized-summary MLP: hidden ∈ {(128,128), (256,256)}
H1 is valid ONLY IF, for each family, the **largest** capacity point (a) closes in the capacity
control AND (b) fails to close in the withheld condition. (If the largest point closes the withheld
gap → H0. If the largest point fails the capacity control → INVALID, capacity-starved.)

## [R1] training budget (FROZEN, identical across both conditions)
- N_TRAIN_EPISODES = 5000, N_VAL_EPISODES = 1000, N_TEST_EPISODES = 200 (matches 001A eval size).
- Optimizer Adam; lr ∈ {1e-3, 3e-4} (best-on-val, selection pre-registered); batch = 256.
- MAX_EPOCHS = 200; early stop patience = 20 on val balanced-accuracy; hard cap STEPS_MAX = 200_000.
- **Budget is identical between the withheld (real) condition and the capacity control.** The ONLY
  permitted difference between the two is the training value regime (below) — never compute.

## [R1] split construction (disjoint on rules × episodes × value-regime)
- **Rule split:** the 625 rules → TRAIN_RULES (500) / TEST_RULES (125), disjoint, by a frozen seed
  permutation. Train/val episodes draw rules from TRAIN_RULES only; test episodes from TEST_RULES
  only (bars rule memorization).
- **Episode split:** train / val / test generated with disjoint frozen seeds; no episode_id reused.
- **Value regime:**
  - REAL (withheld): train + val episodes use TRAIN_VALUES {0,1,2} for BOTH adaptation and queries
    (meta-learner NEVER sees values 3/4). Test = 001A protocol (adapt {0,1,2}, query {3,4}).
  - CAPACITY CONTROL: identical EXCEPT train + val episode QUERIES may also draw {3,4} (adapt still
    {0,1,2}); test identical to REAL. Proves the architecture CAN extrapolate when shown the regime.
- Assertions written to trace: TRAIN_RULES ∩ TEST_RULES = ∅; train/val/test episode_id disjoint.

## [R1] exact verdict enum (frozen strings) + precedence
- `tlgp001b_within_episode_headroom_survives_meta`   (H1 / BANK-WITHIN-EPISODE)
- `tlgp001b_headroom_amortized_by_meta__downgrade_001a` (H0 / DOWNGRADE)
- `tlgp001b_invalid_capacity_or_leakage_or_replay`    (INVALID)
Precedence (computed, fail-able):
1. INVALID iff capacity control does NOT close on ≥9/10 seeds (any family) OR any planted leak
   uncaught OR any clean channel falsely flagged OR replay not exact.
2. else SURVIVES (H1) iff for the largest capacity of every family: `LCB(headroom_vs_meta) > DELTA`
   AND context-ablation collapses (`meta ≤ floor+DELTA` without adaptation context)
   AND shuffle collapses (`meta headroom ≤ DELTA` on the non-compositional world).
3. else DOWNGRADE (H0).

## baseline / panel (all FAIR; no candidate)
Existing 001A panel (lower reference) + NEW in-context sequence learner (GRU / Transformer) +
amortized-summary MLP. graph-cache family (graph_lookup/transition_table/successor_map/count_table/
episodic_traversal) provably dominated by the unseen-value split; include `count_table` as witness,
expect floor (documented coverage, not independent corroboration).

## ablation
- shuffle-structure (reuse 001A world): meta-learner headroom MUST collapse (else exploiting a leak).
- context ablation: remove adaptation context → meta MUST drop to floor (proves context use).

## positive control (capacity / fail-ability — MANDATORY)
`meta_learner_capable`: the SAME architecture+budget trained on the capacity-control regime MUST
close the headroom (≥9/10 seeds). If not → INVALID (underpowered meta-learner; the withheld
condition is uninterpretable). Guards the INVERSE killer — a weak meta-learner falsely preserving
the gap. Leakage: meta-learner NEVER receives rule_id or query_e; reuse the dual-target MI detector
(planted + renamed controls) on every meta-learner input channel.

## trace / replay requirement
trace.jsonl per TEST episode: adaptation tuples, query (x,a), ground-truth query_e, ideal_pred,
each baseline pred+balacc, meta pred+balacc (per seed), split ids, rule-split id. Replay recomputes
ideal + baselines + meta balanced accuracy AND the verdict from recorded predictions vs ground truth
WITHOUT retraining; retraining reproducibility checked separately via frozen seeds + capacity control.
Power/MDE statement required on the fired verdict.

## claim ceiling
Bounded offline evidence on whether ONE world's within-episode inference headroom survives
cross-episode amortization. Candidate-free; tests NO mechanism. NOT learning-as-mechanism, agency,
self, feeling, subjectivity, intelligence, or EGO-readiness evidence. A negative in either direction
is bounded to THIS world + THIS meta-learner family + the pre-registered capacity grid.

## stop condition
- capacity control fails to close → STOP (capacity blocker); do NOT declare H1.
- H0 fires → STOP the "special within-episode inference" route for this world; downgrade 001A; do
  NOT introduce a candidate.
- If you raise capacity AFTER seeing it preserve headroom, or shrink it to force H1 → STOP
  (capacity/threshold tuning).

## [R1] forbidden files (implementer MUST NOT touch)
- `src/tlgp_001a/**` (frozen) · `artifacts/TLGP-001A/**` (banked) ·
  `artifacts/TLGP-001A-AUDIT-001/**` (canonical audit, frozen)
- `scripts/push.*` (hardcoded PAT — BLOCKED) · `CLAUDE.md` · any global config / schema / EGO mainline
- No edits outside `src/tlgp_001b/**`, `artifacts/TLGP-001B/**`, and the new `tlgp_001b`
  preregistration module. No LLM / AIRI / external services / credentials.

## [R1] Auto-Remote-Anchor policy
**Default = LOCAL-ONLY. NO automatic remote anchor.** The harness performs NO git operation
(write artifacts only). Remote anchoring is **BLOCKED** until `scripts/push.*` hardcoded-PAT is
rotated/removed. Any remote anchor is **operator-initiated only**, with **scoped** `git add` of
explicit paths (`artifacts/TLGP-001B/ src/tlgp_001b/ docs/task_cards/TLGP-001B-R1.md`) — **NEVER
`git add -A`, NEVER `push.py`**. Beware CRLF drift + stuck `.git/index.lock`; the PAT lives on the
user OS, not the sandbox. Local commit (if any) via the plumbing-commit recipe only.

## rollback plan
Isolated `src/tlgp_001b/` + `artifacts/TLGP-001B/`. NO edits to 001A or the audit artifact.
Rollback = delete the 001B module + artifacts; 001A and AUDIT-001 unaffected.

## authorization gate
Implementation requires: (1) explicit operator "implement TLGP-001B" instruction, AND (2) a frozen
`tlgp_001b` prereg (sha256-hashed) committing DELTA, N_SEEDS, capacity grid, budget, splits, verdict
enum BEFORE any training. Until both exist, this card is design-only.
