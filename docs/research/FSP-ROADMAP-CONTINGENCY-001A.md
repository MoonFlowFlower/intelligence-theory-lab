# FSP-ROADMAP-CONTINGENCY-001A — Roadmap with Two-Level Contingency Tree

- Status: DRAFT design memo, companion to FSP-ROUTE-PROGRAM-001A (and its Amendment A). No experiments executed.
- Date: 2026-07-01
- Layer: mechanism hypothesis + task-card planning. Claim ceiling: bounded offline mechanism evidence only.
- Purpose: for every roadmap node, predeclare failure signatures, Plan B (fallback), Plan C (fallback-of-fallback), and the terminal bank. Fallbacks are chosen NOW so that failure-time decisions are lookups, not improvisation (improvised fallbacks are where threshold-tuning and scope-creep historically entered this lab).

## 0. Fallback laws (apply to every node; violations = governance failure)

L1. Instrument failures void results and do NOT consume redesign budget. Fix the instrument, rerun. Only mechanism/environment failures count against the 2-redesign budget. (PC_COPY precedent: instrument confound voided all prior negatives.)
L2. A fallback may change structure, environment, claim target, or route weight. A fallback may NEVER relax a preregistered threshold, add a metric post hoc, remove a baseline, or narrow a battery. If a gate number turns out wrong, that is a new card with a written justification, not a fallback.
L3. Maximum 2 structural redesigns per node (B, then C). After C fails, terminal bank is mandatory. No third redesign under any framing ("001D" renaming included).
L4. Every chain terminates in a bank: a written negative/equivalence verdict + artifacts + memory note + weight reallocation. Silence and abandonment are forbidden outcomes.
L5. Claim-downgrade ladder is predeclared and one-directional: mechanism claim → conditional mechanism claim (budget-/env-restricted) → engineering claim (useful, no mechanism) → banked negative. A result may only move DOWN this ladder, never back up without a new card.
L6. A fallback must be structurally different from what failed (different env family / different claim / different mechanism carrier), not a re-roll of the same dice with new seeds.
L7. Program-death is defined (Section 4) — the program can end honestly; what survives it is also predeclared.

## 1. Roadmap spine

```
                 [YOU ARE HERE]
                       │
  N0  PUM-ENV identifiability probe (card drafted, NOT authorized; CPU)
                       │ pass: env_valid_headroom_certified
                       ▼
  N1  Route-1 loop on PUM-ENV: PE-gated memory + consolidation,
      budget-conditioned, hostile battery + ablation matrix (CPU/API)
                       │ pass: non-equivalence + ablation-destroys + replay
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
  N1.5 EFE selector   N2  SBMC-ENV   (N1 artifacts reused by both)
  vs UCB/curiosity        build + hash-chain vs consistency-
  (double dissociation)   detection separation
          │                    │
          └────────┬───────────┘
                   ▼
  N3  Route-2 trained latent predictor (rung0-analog → rung3-analog)
      [externally gated by TLGP-002A trainability recipe]  (GPU)
                   │
                   ▼
  N4  Cross-env single system + curriculum growth (Route 4/5 phase)
      breadth-over-peak, transfer matrix, module-ablation-only claims
```

Phase mapping: Phase 1 (wk1–4) = N0 + SBMC/RIA specs. Phase 2 (wk5–9) = N1, N1.5, N2-build. Phase 3 (wk10–13) = exactly one of {N2-run, N3, N4-pilot}, chosen by the preregistered rule: largest surviving headroom.

## 2. Contingency tree per node

Notation: F = failure signature (observable, specific). B = Plan B. C = Plan C (runs only if B's own failure signature fires). T = terminal bank (mandatory content + weight reallocation).

### N0 — FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A

Pass signal: H1 conjunction (ideal ≥ .80, fair_max ≤ .60, headroom LCB ≥ .10, action-conditioning gap ≥ .10, no saturation, decoder fail-able both directions).

- N0.F1 — No headroom (fair battery ≈ ideal; obs-decodable or saturated).
  - B: bounded structural redesign 001B: deepen camouflage (per-user style maps → per-session), replace linear preference dims with conditional/interaction structure, move more θ mass into probe-only dims, lengthen horizon so windows can't span it. Structural changes only; gates untouched.
  - B-fail signature: same conjunction fails again.
  - C: change the construction method, not the parameters — design-by-proof: pick an interaction channel where the ideal-vs-fair gap is provable analytically before implementation (e.g., discrete-choice user with θ-dims that are theorem-level unidentifiable from passive data — mutually exclusive response mappings only separable under intervention). Implement only after the proof exists (001C).
  - C-fail → T: bank "text/symbolic user-latent identifiability fails under camouflage + budget constraints at this abstraction level" — the social-domain echo of GG-COBIND. Weight reallocation: M1/M3 routes downgrade to engineering-only; program continues on RIA (TLGP-ext) + SBMC axes; Joi-direction narrative explicitly narrowed in a memory note.
- N0.F2 — Integrity failure (PC-IDEAL-SANITY fails, leakage plant not caught, replay mismatch).
  - B (does not consume redesign budget, per L1): fix instrument, rerun. 
  - C: rebuild the instrument on the TLGP probe codebase (known-good lineage: certified probe harness) rather than debugging the new one.
  - C-fail → T: escalate to a harness-infrastructure card; ALL science on this axis pauses until the instrument passes its own PCs. Bank as instrument-debt, not as mechanism evidence of anything.
- N0.F3 — Ideal observer intractable (enumeration blowup).
  - B: shrink/factorize θ so exact inference is tractable (smaller K, conditional independencies).
  - C: particle-filter ideal WITH a convergence certificate: on small configs where enumeration is possible, the filter must match exact inference within preregistered tolerance; only then may it stand in on large configs.
  - Forbidden at every level: a learned "ideal" (that is a candidate smuggled into the oracle slot).
  - C-fail → T: bank "no tractable oracle for this env family"; env family closes on oracle-tractability grounds (a valid, reusable negative about testbed design).

### N1 — Route-1 loop (PE-gated memory + consolidation) on certified PUM-ENV

Pass signal: beats ALL control baselines at budget parity (heldout counterfactual prediction + long-run satisfaction), learning curve, forward transfer, PE-gate and consolidation ablations each cost ≥ preregistered margin, replay reconstructs behavior. Verdict classification per `docs/codex/contracts/MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md`: absolute score is not a gate — control separation is; LOW_SCORE_SIGNATURE_PRESENT is a pass-class outcome.

- N1.F1 — Retrieval equivalence (ties B_rag or B_full-budget).
  - B: raise interference/contradiction density (CLS-motivated: consolidation should matter precisely where raw retrieval retrieves misleading/conflicting episodes); one structural redesign of the task mix, gates untouched.
  - C: downgrade claim target one ladder step (L5): from "beats retrieval" to "matches retrieval at k× smaller memory budget" (selective-write compression claim; preregister k before the rerun). Mechanism claim narrows to the write-gate.
  - C-fail → T: bank "external memory loop adds nothing over retrieval on PUM-ENV under any tested budget" → Route 1 downgraded to memory engineering; weight shifts to N3 (learned latent may capture what explicit schema cannot). The certified env and harness remain assets.
- N1.F2 — Regression equivalence (ties B_prefvec discounted-LS — the ACOLB signature).
  - B: first check the env-control (flat-θ ablation): if LS rises toward ideal there, the env's nonlinearity is real and the CANDIDATE is LS-equivalent → redesign the update rule (structured belief with interaction terms, uncertainty-weighted updates), not the env.
  - C: if the redesigned update rule still ties LS → hand the specific sub-question to N3 ("can a learned latent beat LS where an explicit update rule cannot?") with the failed candidate as a mandatory baseline there.
  - C-fail (N3 also ties LS) → T: bank "user-preference tracking on this env class is LS-complete" — a strong, reusable negative that would say the env's latent structure, though identifiable, is too shallow to separate learners from regression; feeds back into N0-style redesign of FUTURE envs (deeper latents), not this one.
- N1.F3 — Instrument failure (PC-RECALL / PC-UPDATE fail).
  - B (L1): memory plumbing bug — fix, void interpretations, rerun.
  - C: if the schema itself cannot pass PCs after repair, the memory schema is misdesigned → schema-redesign card (this is instrument, not mechanism; does not consume redesign budget but DOES require re-freeze and full rerun).
  - C-fail → T: bank as harness debt; N1 pauses; N1.5/N2 may proceed (they do not depend on the memory schema).
- N1.F4 — Unattributed win (= HIGH_SCORE_NO_ATTRIBUTION per MECHANISM-SIGNATURE-VERDICT-STANDARD-001A; candidate beats battery but ablations do NOT destroy: PE-gate/consolidation removal changes nothing).
  - B: attribution hunt — full single-module ablation sweep to find the actual carrier of the win; redraft the mechanism claim around the real carrier (the claim must name the component whose removal destroys the effect).
  - C: if no component attributes (the win is diffuse LLM-prior/prompt effect) → classify as prompt-performance false positive successfully caught; tighten env (camouflage/renderer) and rerun once.
  - C-fail (win persists, still unattributable) → T: bank "PUM-ENV performance at this level is achievable without any tested mechanism" — env difficulty insufficient for mechanism attribution; env goes back to N0-family redesign; no mechanism claim is ever issued from an unattributed win (L2 protects gates; this protects claims).

### N1.5 — EFE-style epistemic action selection vs UCB / curiosity / greedy

Pass signal: double dissociation — EFE ≥ rivals with fewer probes in probe-required variant; indistinguishable in probe-free variant; count-based-bonus swap degrades.

- N1.5.F1 — Rival equivalence (UCB/curiosity ties EFE in probe-required variant).
  - B: deepen the probe economy: multi-step probe chains where myopic IG and stationary bonuses fail and only planned information seeking works (structural env change).
  - C: coarsen the claim (L5): test "any posterior-aware selector beats posterior-blind selectors" (EFE and Bayes-greedy vs UCB/count-based). If posterior-awareness separates, bank that; the EFE-specific formulation claim closes.
  - C-fail → T: bank objective-equivalence ("epistemic term necessary-or-fungible; formulation irrelevant on this env class"); keep the simplest selector as engineering default; proactivity-as-mechanism closes. Explicitly recorded as a GOOD bounded outcome, not a loss.
- N1.5.F2 — Wrong-direction dissociation (EFE also helps in probe-FREE variant).
  - B: audit for information leak from selector into prediction pathway (implementation bug class); fix, rerun.
  - C: if clean, the epistemic term is acting as a generic regularizer, not an epistemic mechanism → reclassify claim accordingly (regularization effect, no mechanism credit) and bank.
  - C-fail → n/a (C is itself a terminal reclassification).
- N1.5.F3 — Probe spam (cost term not binding).
  - B: this is an env failure, not a candidate failure — trust-dynamics miscalibrated; check trust-cost-off env-control direction; repair env cost structure; rerun.
  - C: if cost structure cannot bind without destroying identifiability (cost so high nothing probes), the probe-economy design is over-constrained → return to N0-family for one redesign of the economy.
  - C-fail → T: bank "no viable probe economy found: identifiability and cost-binding mutually exclusive in this family" — closes the active-probing axis, passive-tracking claims may continue.

### N2 — SBMC-ENV (memory contamination / provenance integrity)

Pass signal: consistency-based detection beats capable baselines in the metadata-stripped condition; balanced macro-F1; low false-rejection; injected-premise action integrity.

- N2.F1 — Hash-chain solves everything (incl. metadata-stripped condition).
  - B: audit the stripped condition — if injections are structurally distinguishable (style, position, timing), they are not really stripped; style-match and re-run once.
  - C: if genuinely solved by cryptographic provenance → bank "engineering sufficient; no mechanism needed for memory integrity at this threat model"; delete boundary-monitor from the hybrid (architecture pruning = success mode); optionally escalate threat model in a NEW card (forged provenance) only if a concrete downstream need exists.
  - C-fail → n/a (C is a terminal bank).
- N2.F2 — Consistency-detection impotent (candidate ≤ embedding-outlier baseline).
  - B: detection quality should track user/world-model quality — couple the detector to N1's consolidated model K (inconsistency = conflict with model predictions, not with raw episodic text); rerun.
  - C: if still ≤ outlier-detector → bank "semantic contamination detection requires model quality unavailable at this scale"; keep provenance-tagging as the engineering deliverable; mechanism claim closes.
  - C-fail → n/a (terminal).
- N2.F3 — Paranoia (false-rejection of genuine memories too high; thresholds frozen so no tuning allowed).
  - B: structural fix that respects L2 — change the ACTION SPACE, not the threshold: detector outputs uncertainty + a verify(memory_k) action instead of binary reject; cost of verification enters J; rerun.
  - C: if verification actions cannot fix the precision/recall tradeoff, the injected/genuine distributions overlap by construction → env redesign (separate the distributions on semantic grounds, keep style matched) — one redesign.
  - C-fail → T: bank "contamination and genuine-memory distributions not separable under style-matching in this family" — a real boundary on what contamination detection can mean here.

### N3 — Route-2 trained latent predictor (gated: N0 pass AND TLGP-002A recipe closed)

Pass signal: rung0-analog (seen users) then rung3-analog (unseen users, few-shot) beat battery with action-conditioning ablation destroying performance.

- N3.F0 — External gate never opens (002A cannot produce trainable capacities).
  - B: run at the largest KNOWN-trainable capacity from the 002A sweep's C0 anchor, accepting a lower ceiling (a conditional-negative regime: results interpretable only within that capacity).
  - C: if no capacity is trainable at all → N3 stays frozen; bank trainability debt; program continues on N1-explicit-state permanently.
  - C-fail → n/a (terminal freeze).
- N3.F1 — rung0-analog fails (cannot fit seen users).
  - B (order fixed): trainability PC first (L1); then env-difficulty check — PUM latents are continuous where TLGP's were discrete: discretize θ / curriculum from 2-user to N-user.
  - C: if discretized rung0 still fails with passing PCs → bank "social-latent learnability wall at this scale" (mirror of the TLGP rung1 verdict, now on the social axis); N3 closes; N1's explicit-state approach becomes the permanent carrier.
  - C-fail → n/a (terminal).
- N3.F2 — rung0 passes, rung3-analog fails (no few-shot transfer to unseen users).
  - B: increase shared structure across the user family (transfer requires shared structure to exist — generator-side change, re-certified through an N0-style probe on the new family).
  - C: bank "within-distribution user adaptation only; no few-shot identification at this scale" — rung0-level evidence stands and is usable; the generalization claim closes.
  - C-fail → n/a (terminal; partial evidence retained).

### N4 — Cross-env single system + curriculum (Routes 4/5)

Pass signal: one system, all certified envs, breadth-over-peak; curriculum shows forward transfer + bounded forgetting; every hybrid module earns its ablation delta.

- N4.F1 — Integration breaks (interfaces, budgets, replay across envs).
  - B: engineering fix; no science claim affected; no redesign budget consumed.
  - C: if integration is not achievable without prompt side channels → hybrid claim reduces to per-env evidence only; bank integration debt.
- N4.F2 — Breadth kills peak (multi-env system degrades on each env).
  - B: interference diagnosis (which env pair conflicts; ablate pairwise) → isolate the conflicting module and split its state per-env if that is honest (declared, not hidden).
  - C: bank "no single-system breadth at this scale"; per-env claims stand as-is; Route 5 narrows to a router, which must be reported as a router, not an architecture.
- N4.F3 — Curriculum yields no transfer.
  - B: one grammar redesign for shared latent structure across stages.
  - C: bank no-transfer negative; Route 4 closes at this scale; single-env evidence unaffected.
- N4.F4 — A hybrid module earns no ablation delta anywhere.
  - B: delete it (architecture pruning is a success mode).
  - C: n/a — deletion is terminal and good.

## 3. Weight reallocation map (where effort goes when a node dies)

| Dead node | Effort flows to | Rationale |
|---|---|---|
| N0 (PUM family closed) | RIA (TLGP-ext) + SBMC | rule/memory axes independent of user-latent identifiability |
| N1 (Route 1 equivalence) | N3 | learned latent is the only remaining carrier for M1 |
| N1.5 (objective equivalence) | nothing (engineering default kept) | question answered, cheaply |
| N2 (engineering-sufficient) | nothing (module deleted) | question answered; prune |
| N3 (learnability wall) | N1 conditional claims + RIA drift | explicit-state becomes permanent carrier |
| N4 (no breadth/transfer) | per-env deepening | claims stay bounded per-env |

## 4. Program-death condition and what survives it

The program ends (honestly) iff ALL of: PUM family closed at N0-C (T fired) AND RIA/TLGP-ext saturated against its battery AND SBMC banked as engineering-sufficient. In that world, no mechanism question in this program survives at toy scale, and the residual statement is itself the deliverable: "at this abstraction level, every FSP mechanism family is either unidentifiable, baseline-equivalent, or engineering-solved." What survives regardless: certified environment generators, the probe/PC/adjudicator harness pattern, the hostile battery implementations, and the negative-evidence corpus — all reusable by any successor program (including a scale-up decision, which would be a NEW program with its own cards).

## 5. Standing constraints (inherited, restated)

All fallbacks operate inside the existing envelope: no EGO-mainline changes, no banked-artifact edits, no threshold motion post-freeze, no LLM-judge primary metrics, graph-cache challengers mandatory for representational claims, instrument PCs before verdicts, artifacts under artifacts/<task_id>/ per the evidence contract, claim ceiling fixed at bounded offline mechanism evidence.
