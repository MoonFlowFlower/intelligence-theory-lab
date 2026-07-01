# LEARNING-SUCCESS-CRITERION-STANDARD-001A

```yaml
doc_type: reusable_normative_standard
layer: evidence-governance / route-governance (documentation only)
implementation_authorized: false
claim_ceiling: defines what counts as flexible-learning evidence; is not itself mechanism evidence
pairs_with:
  control_side: docs/codex/contracts/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md
  positive_patterns: docs/research/BENCHMARK-METHODOLOGY-APPLICABILITY-001A.md
  killers: docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md
status: new-session entry-point for "what counts as success on the learning axis"
```

## 0. Why this exists (read first)

The lab's default verdict has been "candidate must beat the baseline." That is the
correct bar for a **control** baseline but the **wrong** bar for a **generality /
flexible-learning** claim. A purpose-built specialist will score high on its own
narrow task; a flexible learner that *matches* many specialists across a
distribution — while no single specialist generalizes — is the actual target
("flexible, generalizing, really-learning, usable across situations, like a
biological learner that errs but genuinely learns").

This standard consolidates the **positive success side** of that claim. It does not
replace the two existing docs; it points to them:

- **Control / immunity side** (what *invalidates* a result): `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`.
- **Positive methodology patterns** (P1 generalization gap, P2 latent + ideal-observer,
  P3 one-capability + baseline panel, P4 performance/forgetting/forward-transfer,
  P5 held-out new tasks, P6 strong-methods-must-fail): `BENCHMARK-METHODOLOGY-APPLICABILITY-001A`.

This standard is data/normative text, not an executable checker. A checker needs its
own authorized task card (an unaudited "N tests passed" green is a known false-green
failure mode).

## 1. The load-bearing distinction: rival baseline vs control baseline

Every baseline in a panel is one of two kinds. Conflating them is the error this
standard fixes.

**Rival baseline (a specialist / SOTA you might hope to beat).**
- You do **NOT** need to beat it for a generality/capability claim.
- A specialist matching or beating the candidate **on the specialist's own narrow
  task** is *not* a failure of the candidate.
- Rival baselines are used for a *breadth* comparison (below), not a peak-score duel.

**Control baseline (a trivial explanation you must rule out).**
- You **ALWAYS** must beat it, or the claim "it learned" is indistinguishable from
  "it memorized / decoded / precomputed."
- Mandatory controls for any learning claim (score each in the panel):
  `memorization / lookup`, `nearest-neighbor`, `no-update ablation` (freeze the
  learning mechanism), `observation-only decoder` (K1), `from-scratch learner`
  (no meta-training), `predict_all / predict_none` (metric degeneracy — see immunity
  standard §2), and the candidate's **own rule amortized/batched** (the ACOLB
  reducibility control: online update must buy something over batch precomputation).
- If any control reaches `ceiling − equivalence_band`, the result is **inadmissible**,
  regardless of how "flexible" it looks.

Diagnostic question for any equivalence result: *was the equivalent a rival
specialist (claim survives, re-scope to breadth) or a control (claim fails)?*
Example: ACOLB's equivalent was the candidate's **own** update rule batched (a
control-class reducibility) → genuine no-headroom, not an unfair-specialist artifact.

## 2. Positive success criterion (normative — check a claim against all of these)

A flexible-learning / generality claim is admissible **only if** it states and
measures all of:

1. **One fixed system, many tasks.** A single architecture + single training run is
   evaluated across a **distribution** of tasks (not tuned per task).
2. **Held-out novelty.** Evaluation is on tasks/rules/values **not seen** in
   training (P1 gap; P5 held-out). Seen-task accuracy alone is inadmissible.
3. **Few-shot adaptation.** Success is adaptation from few in-context / few-step
   examples, **faster than a from-scratch learner** on the same task.
4. **Breadth over peak.** The metric is coverage across the distribution, compared to
   a **panel of per-task specialists**: the candidate should approach the per-task
   specialist ceiling **across** tasks while **no single specialist** generalizes
   across the panel. (This is the comparison that makes "don't need to beat the
   specialist" rigorous — you beat the specialists *collectively on breadth*.)
5. **Ideal-observer ceiling.** Where a ground-truth latent exists, report the
   Bayesian/ideal ceiling and the fair no-inference floor; headroom = ceiling − floor
   must be real (P2). Candidate value is measured inside that headroom.
6. **Metric decomposition.** Report performance / forgetting / **forward-transfer**
   separately (P4) rather than a single scalar.

## 3. The "genuine learning" signature (operationalizes "really learns, like biology")

"Makes mistakes but really learns" is admissible only as a **measured signature**,
never as a demo impression:

- **Learning curve:** error decreases with experience (within-episode and/or
  across-episodes). Report the curve, not a single endpoint. Perfection is not required.
- **Forward transfer:** the curve is **steeper on new tasks** than from-scratch
  (evidence of learning-to-learn, not per-task fitting).
- **Ablation-destroys-it:** removing the learning mechanism (no-update / frozen
  latent / shuffled feedback) **collapses** the advantage. If it does not collapse,
  the mechanism was not doing the work.
- **Not-memorization:** held-out performance does not drop to the memorization/lookup
  control; overlap between train and eval is bounded and reported.

## 4. Mandatory falsifier clause

Every success claim must state, in advance, **what result would show it is NOT
genuine learning** — e.g. "no-update ablation does not reduce held-out score by ≥ X,"
or "the memorization control matches within the band," or "no generalization gap."
If a claim cannot name its falsifier, it is inadmissible as "learning" evidence and
is at best a capability demo.

## 5. Claim ceiling (hard)

Passing this standard yields **bounded evidence of a flexible learning / adaptation
mechanism** only. It does **not** upgrade to: mechanism-of-a-subject, causal control,
self/boundary, value/viability, agency, autonomy, real emotion, consciousness,
subjectivity, AGI, or EGO/companion readiness. The biological analogy refers to the
**learning signature** (curve + transfer + non-memorization), **not** to sentience.
Capability ≠ mechanism ≠ subjecthood (per BENCHMARK-METHODOLOGY §0).

## 6. How to use (any learning/generalization card, before authoring a candidate)

1. Classify every panel member as rival or control (§1).
2. State the §2 criterion (1–6) the card will measure.
3. State the §3 signature and the §4 falsifier.
4. Run the immunity standard §2 degeneracy checklist (controls) and the killer
   catalog K1/K2 pre-mortem. Answer K1/K2 or STOP.
5. Keep the §5 claim ceiling verbatim in the result.

## 7. Worked mapping (so this is actionable, not abstract)

TLGP rung3 already satisfies much of §2: one retrieval model, unseen rules (§2.2),
in-context few-shot (§2.3), verified headroom over fair_max with an ideal ceiling
(§2.5), controls including graph-cache/lookup ruled out. What it does **not yet**
provide: a multi-task **distribution** breadth comparison against a specialist panel
(§2.4), an explicit forward-transfer/forgetting decomposition (§2.6), and a reported
learning curve (§3). Those are the concrete additions this standard asks of the next
rung3 result — and they are the difference between "one learner passed one gap test"
and "a flexible learner across a distribution."

## What this does not prove

This standard proves nothing on its own. It is a normative admission criterion. It
does not authorize implementation and does not constitute mechanism, subject, or
readiness evidence for any route.
