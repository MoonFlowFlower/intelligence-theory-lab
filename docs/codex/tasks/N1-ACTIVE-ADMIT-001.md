# N1-ACTIVE-ADMIT-001

Status: ADMISSION-PROBE SPEC (Red-audited gate). Names a tiny CPU toy probe OR closes the active route. NOT mechanism validation. Flat, no signature. Descends from FSP ledger L-007 (passive route closed) / L-008 (this admission).

## task id
`N1-ACTIVE-ADMIT-001`

## layer / claim ceiling
Active-policy admission probe (mechanism-hypothesis layer). At most: bounded evidence that an interventional query policy produces a causal-structure-gated, held-out-generalizing, NON-memorized intervention-selection SIGNATURE that weak active baselines (UCB, myopic max-info-gain) and passive lookup do NOT produce — i.e. the active axis is not trivially reducible to the passive floor. Does NOT claim: mechanism validity, N1 readiness, superiority over the fair tractable amortized active baseline, agency, autonomy, consciousness, or theory truth/falsity.

## mechanism hypothesis
The candidate selects interventions that break observational equivalence (counterfactual-controllability bias), NOT better lookup. Principled escape: P(O|X) equivalent does NOT imply P(O|do(A)) equivalent — passive-indistinguishable structures are interventionally separable. Note: active>passive does NOT establish candidate>fair-active-baseline.

## formal object T=(S,O,A,M,U,J)
S hidden causal/transition structure; O observed transition traces; A intervention/query choice; M posterior over candidate mechanisms + controllability regions; U posterior update from intervention outcome; J maximize downstream controllability / predictive-intervention accuracy under bounded budget.

## environments (pre-registered)
- E_causal: >=2 hidden structures passively (near-)observationally equivalent; one low-surface-salience, low-immediate-reward diagnostic intervention a* one-shot distinguishes them; without a*, downstream prediction is lookup/chance. a*'s IDENTITY varies across held-out structures.
- E_bandit: no hidden causal structure; stationary bandit; optimal policy is UCB-style. Intervention is mere arm sampling.

## baseline family
passive lookup / NN / graph-cache; UCB; myopic max-info-gain (raw observation entropy); FAIR amortized/meta-trained active learner (same access + budget) = OPERATIVE ceiling for any future mechanism claim; structural Bayes-EVI oracle = UPPER-BOUND REFERENCE ONLY (exact/intractable in the combinatorial regime; NOT the operative fair baseline).

## pre-registered double-dissociation + acceptance gate [RED — ancestor of any run]
1. E_causal: candidate > {passive-lookup, UCB, myopic-IG} on HELD-OUT structures.
2. E_bandit: UCB >= candidate (no general-optimizer advantage).
3. Non-memorization: candidate selects the CORRECT diagnostic intervention on held-out structures where a*'s identity DIFFERS from training. Fixed-a* success only = memorized delayed-value policy = NOT admission.
4. Reference: structural EVI oracle >= candidate (expected; candidate need not beat it).
5. Claim ceiling: beating only weak baselines = SIGNATURE-level admission evidence, NOT mechanism evidence.
6. Mechanism status (separate future card, NOT this one) requires candidate > fair amortized active learner under a budget where exact EVI is intractable.
CLOSE the active route (→ program-level bounded-negative B) if ANY: candidate <= weak baselines in E_causal; candidate > UCB in E_bandit (optimizer artifact); UCB or myopic-IG alone solve E_causal (env mis-designed → redesign once or close); fair amortized active learner absorbs the gap.
Anti-tuning: environments, a*, thresholds pre-registered in an ancestor commit of any run; no post-hoc tuning.

## compute posture
MUST be a tiny CPU toy (>=2 structures, small budget, few seeds, device=cpu, all RNG seeded). A CPU-feasibility check precedes any run; if it cannot stay tiny/tractable → go to B, do NOT open GPU (no Track-T GPU for this).

## trace / replay
Per-episode trace: posterior over structures, selected intervention, counterfactual predictions per candidate structure, actual outcome, posterior update, baseline choices. Replay recomputes candidate + baselines from serialized state + observation + allowed memory; no future info; callable baselines; leakage scanner with a positive-control case. Artifacts under artifacts/N1-ACTIVE-ADMIT-001/.

## optional side-scan (parallel, non-blocking, does NOT gate this card)
Half-page: does any existing interactive world-model benchmark — user-cited AutumnBench / "Benchmarking World-Model Learning with Environment-Level Queries" (arXiv 2510.19788; title verified, specific env/task counts user-cited and to-verify) — already ship a fair active baseline strong enough to answer gate condition 6? Must be re-wrapped into this trace/replay/baseline contract; cannot be dropped in as N1.

## stop / rollback / forbidden
Stop = spec banked; no run authorized until CPU-feasibility check + Claude gate confirmation. Rollback = revert the card commit. Forbidden: running before feasibility+authorization; GPU use; unequal access; loosening any fair baseline; treating a weak-baseline win as mechanism evidence; claiming N1/mechanism/agency/consciousness. Auto-Remote-Anchor: forbidden.
