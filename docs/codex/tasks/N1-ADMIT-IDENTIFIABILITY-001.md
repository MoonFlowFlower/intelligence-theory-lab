# N1-ADMIT-IDENTIFIABILITY-001

Status: **ADMISSION CARD (route/admission layer — NOT mechanism validation). Design-only: no code, no experiment, no artifacts. Flat select (solo policy 2026-07-05).**
Auditor-drafted (Claude), 2026-07-05. Decides whether the program has a qualified N1 target after the S3d v0 / PUM-ENV tombstone. Bottoms out in either a named minimal probe or a close — it may **not** spawn another pure-design card.

## task id
`N1-ADMIT-IDENTIFIABILITY-001`

## layer / claim ceiling
Route/admission decision only. May conclude at most: "current S3d/PUM-ENV is not a qualified S4/N1 downstream instrument; the cross-episode reusable-prior class (TLGP-adjacent) is the more reasonable next candidate testbed family, but its learnability is NOT established." May **not** claim: mechanism holds, N1 ready, EGO ready, or any theory true/false.

## why now
- S3d v0 tombstoned (banked `70cdf7e`): ρ dominated by per-user `style_map` privilege; lookup `nearest_neighbor` beats the assigned mechanism 2.16× denominator-free; no assigned member passes any discriminative cell.
- 2nd style_map / equal-access identifiability-ceiling instance (1st = LRGG). Ceiling (bounded inference, not theorem): under equal access, identifiability is a property of the access regime and is handed to the fair baseline; the only class not yet closed is a cross-episode reusable prior that beats a **fair meta-baseline** — and even that is under threat (see admission question).

## the admission question (hard form)
Does any candidate N1 target admit a mechanism whose advantage **cannot be captured by the strongest fair baseline**, where for the cross-episode class the strongest fair baseline is a **fair amortized meta-learner / Bayes-optimal meta-estimator / fair active-exploration policy** — NOT a weak per-episode extrapolator? (TLGP-001A's 0.80 headroom was vs the weak extrapolator; that bar is void here.)

Three sub-gates — ALL must pass to admit:
1. **Not single-episode lookup-reducible.** Not solvable by episode-only lookup / NN / graph-cache.
2. **No unequal-access privilege.** Candidate and baselines share the same information + intervention set (the S3d failure: oracle handed `style_map`, members not).
3. **Named controllable-variable advantage.** The candidate must declare WHICH agent-controlled variable in `T=(S,O,A,M,U,J)` carries the claimed advantage, and why a fair baseline with the same controllable set does not trivially capture it:
   - advantage in `M/U` (passive cross-episode prior) → a fair amortized meta-learner gets the same prior → **presumed ceiling-blocked**; admission requires a specific reason the fair meta-baseline cannot form it (e.g., held-out-novel families with a sample budget below the meta-baseline's floor).
   - advantage in `A` (active intervention / query policy) → potentially non-tautological, but the fair baseline must be a fair active-exploration policy (UCB / max-info-gain) and admission requires a pre-declared **discriminating prediction** where candidate and fair policy diverge (double-dissociation), not "candidate beats random exploration."

## candidates evaluated
- **A. PUM-ENV / S3d-R2 (style-invariant redesign).** Already closed by the P0 route-decision (`INVALID_INSTRUMENT`). Recorded only: fails sub-gate 3 — residual signal is `style_map` / retrieval recovery, and denominator-free it loses to `nearest_neighbor`. → `INVALID_FOR_N1` unless it drops the style/retrieval dependency AND names a non-lookup advantage (currently cannot).
- **B. TLGP-R2 (cross-episode learnability).** TLGP-001A validated environment headroom (0.80) but **only vs a weak per-episode extrapolator**; TLGP-001B failed (learnability floor + positive-control defect: control ≡ real). Sub-gate 3 UNRESOLVED — whether a candidate beats a fair meta-baseline is the open empirical question. → admit only to a **minimal learnability probe**, not to a mechanism experiment.
- **C. No qualified N1 target.** If neither can state an ex-ante advantage over the strongest fair baseline → close the "build an identifiability instrument" route; downgrade to a benchmark-method scan (e.g., AutumnBench equal-access saturation check) or accept a program-level bounded-negative.

## pre-registered decision (no 4th path)
- Sub-gate 3 unmet for all candidates → `NO_QUALIFIED_N1_TARGET`.
- TLGP-R2 states a controllable-variable advantage (active-policy divergence, or a specific meta-baseline-floor argument) and PUM-ENV cannot → `ADMIT_TO_MINIMAL_PROBE(target=TLGP-R2)` — admits to a diagnostic, NOT to N1 mechanism.
- Genuinely undecidable on paper in one pass → `NEEDS_ONE_MINIMAL_PROBE` naming the cheapest discriminating experiment.
- **This card may not spawn a second pure-design card** — it must name a probe or close (anti-stagnation).
- Forbidden output: "maybe threshold / strength tuning would pass." Baseline-immunity (equal-access, lookup/NN/graph-cache, fair meta-baseline) is non-negotiable.

## preconditions to verify before any downstream probe
- **Compute posture:** TLGP-001B was GPU; the FSP side is CPU-only (spec §6). Declare and authorize the diagnostic's compute posture (CPU-feasible small scale, or explicit Track-T GPU authorization) BEFORE committing — do not assume.
- **Positive-control fix:** the downstream probe must not repeat the 001B defect (control ≡ real test); its fair baseline must be a strong meta-learner, and it must carry a leakage / permutation control.

## if ADMIT_TO_MINIMAL_PROBE(TLGP-R2): the next (execution) card
`TLGP-LEARNABILITY-FLOOR-DIAG-001` — decide whether TLGP-001B's failure was a real learnability floor or a positive-control design defect. Design-only spec here; execution is a separate authorized card.
- Formal object `T=(S,O,A,M,U,J)`; nuisance = surface label / episode id / memorized-instance identity.
- Mandatory baselines: random/majority, episode-only lookup, NN / graph-cache, amortized learner, **fair cross-episode meta-learner**, oracle rule-family upper bound, ablated-memory candidate, shuffled-family / label-permuted leakage control.
- Accept only: candidate > **strongest fair meta-baseline** on held-out families AND held-out episodes AND under memory-ablation AND trace-replay. Beating random/majority alone = not evidence. Oracle-only headroom = not evidence. Fair meta-baseline erases the gap = close/redesign.

## stop / rollback
Design record; triggers no compute. Superseded when a decision enum is recorded + ledger transition appended. Rollback = revert the doc commit.

## forbidden
Recommending S4 on S3d v0; disguising `style_map`/renderer recovery as latent-mechanism evidence; loosening any fair baseline (equal-access, lookup/NN/graph-cache, fair meta-baseline) to admit a target; spawning a further pure-design card instead of naming a probe or closing.

## §operator selection (flat — no signature)
Decision: [ ] NO_QUALIFIED_N1_TARGET   [ ] ADMIT_TO_MINIMAL_PROBE(TLGP-R2)   [x] NEEDS_ONE_MINIMAL_PROBE: `TLGP-LEARNABILITY-FLOOR-DIAG-001` (spec in the "if ADMIT..." section above)   —   Operator: Zhouyu (delegated to auditor; authorized 2026-07-05)  Date: 2026-07-05
Controllable-variable advantage stated: NOT yet stateable on paper — this is why NEEDS_PROBE, not ADMIT. Passive prior (`M/U`) is presumed captured by a fair amortized meta-learner (ceiling); the only candidate escape axis is the active query/intervention policy (`A`) vs a fair UCB / max-info-gain policy (double-dissociation). The diagnostic must FIRST establish whether there is any headroom vs a fair meta-baseline (i.e. whether TLGP-001B's failure was a real learnability floor or a positive-control defect) before any mechanism-advantage claim is admissible.
Authorization scope (explicit): records the route/admission decision only (~0 compute). Does NOT authorize the diagnostic run — that requires its own execution card with compute posture (CPU-feasible vs Track-T GPU authorization) resolved + budget + stop condition.
