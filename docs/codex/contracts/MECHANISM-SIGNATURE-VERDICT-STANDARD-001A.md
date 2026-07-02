# MECHANISM-SIGNATURE-VERDICT-STANDARD-001A

- Status: ACTIVE reusable standard. Mutation: supersede-only once any card cites it as frozen governance (001B/002A with written justification; no in-place relaxation).
- Applies to: candidate-experiment verdicts — FSP P1+ cards, and any ITL candidate card that cites it. Does NOT apply to candidate-free environment certification (N0-class verdicts are governed by FSP-ENV-DESIGN-CONSTRAINTS-001A §10).
- Origin: FSP-MASTER-PHASE-PLAN-001A Amendment A2 (2026-07-01). Empirical anchor: JOI-DEMO-001A banked headline (in-distribution hardcoded beats learner; learning's value appears only under drift) — a real case where a theory-conformant system scores low on the standard distribution while carrying a clean mechanism signature.
- Claim ceiling: nothing in this standard raises any claim above bounded offline mechanism evidence under specified trace/replay/ablation/baseline contracts.

## 1. Principle (dual constraint, both binding)

Do not optimize for benchmark score. Do not excuse absence of mechanism signatures. Absolute score (vs oracle / aspiration level) belongs to the product domain; separation-from-controls belongs to the science domain. Candidate experiments are adjudicated on preregistered signatures, not on scalars.

## 2. Mechanism signature — definition (ALL components, ALL preregistered at card time)

- S1 Control separation (NON-NEGOTIABLE): the candidate strictly separates from EVERY control baseline (lookup / memorization / no-update / obs-decoder / from-scratch / self-amortized / reward-only / scripted, per the card's battery) at the preregistered margin/LCB. Losing to or tying any control voids all signature claims categorically. Rival-vs-control distinction per LEARNING-SUCCESS-CRITERION-STANDARD-001A: a task-specialist rival matching the candidate is not a failure; a control matching it is.
- S2 Directional ablation matrix confirmed: each preregistered cell (destroy / degrade / no-effect) lands as predicted, including declared double dissociations.
- S3 Variant pattern: candidate wins where the theory predicts winning AND loses (or shows no advantage) where the theory predicts losing — should-win/should-lose knob variants and NULL-env silence per the environment constitution.
- S4 Integrity: positive controls pass, leakage self-tests pass, replay reproduces reported metrics from trace, power sufficient (every equivalence statement ships its MDE).
- S5 Failure-mode match: observed failures land inside the theory's predeclared failure geography.

Signature-freeze rule (anti-forking-paths): the signature set — matrix cells, directions, variants, margins — freezes at card time. Signatures discovered after seeing results are exploratory annotations; they cannot support a verdict, upgrade a subtype, or rescue a claim.

## 3. Verdict subtypes

- FULL_PASS: high absolute performance + full signature (S1–S5).
- LOW_SCORE_SIGNATURE_PRESENT: absolute performance below the oracle/aspiration level, but S1–S5 all hold. Allowed claim: "bounded mechanism-signature evidence at low absolute performance." Forbidden claims: product success, mainline readiness, functional-subject language. Downstream: eligible to open follow-on mechanism cards; NOT usable as product-readiness input.
- HIGH_SCORE_NO_ATTRIBUTION: high absolute performance but ablations do not destroy, or a control matches, or the trace cannot attribute the win. Allowed claim: "performance result only." Forbidden: any mechanism evidence. Downstream: attribution hunt per FSP-ROADMAP-CONTINGENCY-001A N1.F4 (this subtype IS N1.F4, named); the performance number may inform the product track but carries zero science weight.
- EQUIVALENCE / NEGATIVE / INVALID: unchanged; governed by BASELINE-IMMUNITY-ADMISSION-STANDARD-001A (admission and invalidation families) and the card's own gates. This standard adds classification on top of admission — it never substitutes for it.

## 4. Guards

- G1 Ablation sensitivity alone is not mechanism evidence — removing parts degrading performance shows the system has parts. Only S1+S2 together carry mechanism weight.
- G2 A low score triggers the PREREGISTERED diagnostic branch of the contingency tree; it never triggers post-hoc metric relitigation, threshold motion, or battery changes.
- G3 Predicted failure geography is mandatory card content: every candidate card must predeclare where its mechanism should lose. A theory that only predicts wins is not yet a mechanism theory and its card is not ready.
- G4 Two-track claim separation: product-track success (e.g. joi-demo Bar-1 life-likeness) and science-track signatures are distinct success functions. Claims never flow from product to mechanism; product decisions are not blocked on mechanism proof.

## 5. Required verdict artifact fields (additions to result.json for cards citing this standard)

verdict; verdict_subtype (one of §3); signature_manifest (S1–S5 status + artifact pointers); score_block {absolute, oracle_bound, control_max, separation_margins_with_LCB}; claim_ceiling.

## 6. Relationship to sibling contracts

- BASELINE-IMMUNITY-ADMISSION-STANDARD-001A — whether a result is admissible at all (control-baseline invalidation families).
- LEARNING-SUCCESS-CRITERION-STANDARD-001A — what counts as learning/generalization success (rival vs control, generality criteria, genuine-learning signature).
- THIS STANDARD — how admitted candidate outcomes are classified when score and signature disagree, and what each classification licenses downstream.

## 7. What this standard does not do

It lowers no gate. It creates no path to mechanism claims while losing to controls. It does not apply to environment certification. It authorizes no claim beyond bounded offline mechanism evidence.
