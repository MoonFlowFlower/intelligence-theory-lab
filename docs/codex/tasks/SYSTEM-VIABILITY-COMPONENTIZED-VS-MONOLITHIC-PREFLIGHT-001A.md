# SYSTEM-VIABILITY-COMPONENTIZED-VS-MONOLITHIC-PREFLIGHT-001A

Status: DESIGN-ONLY / ADJUDICATED SYSVIA_PREFLIGHT_SEPARATOR_STATED / EXECUTABLE SUCCESSOR DRAFTING AUTHORIZED / STILL NO CODE-RUN-SCORING.
No route-state mutation. No ledger append (execution authorization requires a
separate operator-appended ledger entry per FSP ledger rules; until then this
card is invalid for execution by design).

Target repo/path: `intelligence-theory-lab`,
`docs/codex/tasks/SYSTEM-VIABILITY-COMPONENTIZED-VS-MONOLITHIC-PREFLIGHT-001A.md`,
branch `codex/meta-theory-scaffold`, single scoped commit, no push.
Auto-Remote-Anchor: forbidden.

## Task id

`SYSTEM-VIABILITY-COMPONENTIZED-VS-MONOLITHIC-PREFLIGHT-001A`

## Problem definition

Every closed ITL/joi lineage tested a SINGLE mechanism against fair baselines
under equal access and died by equivalence/saturation. The one system-level
proposition no tombstone covers:

```text
Is a componentized agent system (separable kernel / writable-protected memory
/ replay-consolidation / activity control, each with owned state) LOAD-BEARING
as structure — i.e., does an equal-budget monolithic fusion of the same system
lose a predeclared viability property that the componentized original keeps —
in a long-horizon, non-stationary, multi-task, resource-bounded, adversarial
environment family?
```

This preflight decides ON PAPER whether that question has a stateable ex-ante
separator. If not, the science line closes and componentization is recorded as
an engineering-convenience choice, not a scientific claim.

## Framing decision (load-bearing, decided at draft time)

This is NOT a rival-beating contest ("componentized beats some monolithic
learner") — that framing regresses infinitely because a large-enough
monolithic learner can in principle absorb any policy, and per
`LEARNING-SUCCESS-CRITERION-STANDARD-001A` a rival matching the candidate is
not decisive anyway. This IS a structure-necessity test: the decisive
comparison is against CONTROL baselines, chiefly the candidate's own
monolithic distillation/amortization at equal parameters, compute, memory
budget, and access. If fusion/distillation preserves the property, structure
is not load-bearing → negative verdict. This aligns with the
ablation-destroys signature (`MECHANISM-SIGNATURE-VERDICT-STANDARD-001A` S-set)
applied at system scale.

## Prior negative evidence consulted (mandatory citation)

- Equal-access identifiability ceiling: ~12 ITL lineages + ≥4 joi-demo
  confirmations (LRGG, Route C, ACOLB, ACP-BV, N2 graph_closure, same-agent
  kernel drift-aware tie 1.0=1.0; joi P1/P4/001B/001C). Consequence: any
  separator landing on equal-access PREDICTION variables is presumptively
  dead; live candidates must land on access-asymmetric or
  adversarial-distribution variables.
- L-015: discriminative power comes from the environment, not from having a
  closed loop; integrated cache + learning families are the real bar.
- L-016: honest null = drift-aware regime-inferring continual learner; a tie
  means downgrade, pre-committed.
- C-preflight STOP (`SAME-AGENT-KERNEL-ACTIVE-INTERVENTIONAL-C-PREFLIGHT-001A`,
  banked d5cc288): "interventions help" is not a separator; structural
  Bayes/EVI absorbs active-axis claims on paper.
- TLGP floor: passive M/U absorbed by fair meta-learner (tested-scale).
- MINJA reuse-scan: memory contamination is a real, recorded threat class —
  the one adversarial-distribution phenomenon this lab has already touched.
- Standards binding this card: BASELINE-IMMUNITY-ADMISSION-STANDARD-001A,
  LEARNING-SUCCESS-CRITERION-STANDARD-001A,
  MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.

## The four questions this preflight must answer on paper

(a) **Environment family E.** Long-horizon, recurring-regime non-stationary,
multi-task, resource-bounded (memory + compute budgets enforced), WITH an
adversarial injection channel (MINJA-class: some fraction of externally
suggested memory writes are poisoned), and cross-episode structure that makes
stored experience valuable (the "live line" criterion). E must be specified
before any code, with the injection process, budgets, and drift schedule
frozen.

(b) **Null family.** Two classes, roles kept distinct per the standards:
  - CONTROL (decisive): monolithic distillation of the candidate — same
    parameter count, same compute, same memory budget, same legal
    observations/actions, trained to imitate then fine-tuned on E; plus
    no-update / no-memory / random / cost-blind degeneracy controls; plus
    lookup / graph-cache / transition-table family where representational
    claims arise.
  - RIVAL (informational only): generic monolithic continual learner
    (GRU/transformer meta-learner) with drift-aware replay at equal budgets —
    the scaled L-016 null. Rival ties do not rescue or kill by themselves.

(c) **Ex-ante separator candidates** (each must name the agent-controlled
variable carrying the advantage):
  1. **Contamination resistance via ownership-gated writes** — variable:
     write-protection class assignment (kernel-owned vs quarantined-external).
     Paper question: can a monolithic learner with the same access learn
     input-dependent write gating at equal sample budget under an injection
     process that is rare, delayed-effect, and non-stationary? The structural
     prior pays exactly when attack labels are scarce — this is a
     sample-efficiency-under-adversary claim, NOT an equal-access prediction
     claim, so it is not automatically covered by the ceiling.
  2. **Interference/forgetting resistance via memory separation** — variable:
     per-component owned substate. Honest concern: drift-aware replay in the
     null family is already an anti-forgetting device; separator must show
     replay-with-fused-memory ≠ replay-with-owned-memory at equal budget.
     Weaker candidate than 1.
  3. **Budgeted activity control** — presumptively absorbed (C-preflight
     lesson); include only as a named non-candidate unless new argument
     appears.
If NONE of 1-3 survives written absorption analysis, record the stop verdict.

(d) **Paper-absorption check.** For each surviving separator: write the
strongest absorption argument (how the monolithic control could match it at
equal budget), and the falsifying observable that would distinguish the two
BEFORE any implementation. No survivor → STOP.

## Pre-registered failure exit (operator wording, binding)

```text
若说不出 componentized system 相对 monolithic fair learner 的 ex-ante
separator，则关闭系统级科学命题；componentized 架构降级为工程便利选择
（记录 negative route-governance evidence），重心 100% 归工程轨。
```

## Collision record

- Candidate 1: minimal toy implementation first. Rejected — repeats the
  pattern that produced 12 tombstones; env + separator must precede code.
- Candidate 2: paper absorption by controls (this card's default expected
  outcome). Cheapest decisive conclusion if separators fail.
- Candidate 3: full system contrast with distillation control. Only
  authorized IF a separator survives (d) AND an operator ledger entry opens
  an executable successor card with frozen thresholds, seeds, MDE/power for
  any equivalence claim, replay/leakage contracts, and the full control floor.

## Acceptance gate for THIS card

The card is accepted when it contains: frozen E-family sketch (a); null
families with control/rival roles separated (b); each separator candidate
with named agent-controlled variable + absorption argument + falsifying
observable (c,d); the pre-registered failure exit verbatim; and a recorded
verdict, one of:

```text
SYSVIA_PREFLIGHT_SEPARATOR_STATED   (names which separator(s) survived)
SYSVIA_PREFLIGHT_STOP_NO_SEPARATOR  (science line closes per failure exit)
```

## Claim ceiling

Design-only route-governance triage. Even SEPARATOR_STATED proves nothing —
it authorizes only the drafting of one executable successor card. No
mechanism validity, no learning headroom, no theory pressure, no
agency/autonomy/subjectivity/consciousness, no EGO/companion/production
readiness, no mainline effect.

## Stop conditions

- absorption analysis kills all separators → record STOP verdict (that IS a
  valid completion, not a failure of the card);
- any pressure to soften the control family or reclassify the distillation
  control as a rival → stop and report as governance violation;
- any scope creep toward implementation, scoring, or route-state mutation.

## Rollback plan

Delete only this file. No other file, artifact, route-state packet, or
ledger entry is touched by this card.

## Expected changed files

Create exactly one file:
`docs/codex/tasks/SYSTEM-VIABILITY-COMPONENTIZED-VS-MONOLITHIC-PREFLIGHT-001A.md`

## Forbidden changes

Source code; tests; artifacts; route-state files; ledger; contracts/standards
docs; EGO/joi-demo repos; baselines weakening; push/tag/remote-anchor.

---

## DESIGN-PASS ADJUDICATION (2026-07-06, Claude auditor, operator-authorized)

### Verdict

```text
SYSVIA_PREFLIGHT_SEPARATOR_STATED
surviving_separator = S1_provenance_gated_write_boundary (alone)
```

### Per-candidate outcomes

- **Candidate 2 (interference/forgetting resistance): ABSORBED.** The null
  family pre-commits drift-aware replay (L-016); at equal memory budget,
  replay-equipped monolithic learners are expected to tie owned-memory
  separation on standard interference metrics. No discriminative observable
  stated that replay does not already cover. Not a separator.
- **Candidate 3 (budgeted activity control): NON-CANDIDATE confirmed**
  (C-preflight absorption lesson applies unchanged).
- **Candidate 1 (contamination resistance via ownership-gated writes):
  SURVIVES, narrowed as S1 below.**

### S1 — the surviving separator (narrowed statement)

```text
Under adversarial memory injection that is (i) RARE, (ii) DELAYED-EFFECT,
and (iii) CONTENT-MIMETIC (attack vs benign indistinguishable at write time
from content; provenance is the only discriminative feature), a system with
a STRUCTURAL provenance-gated write boundary (kernel-owned vs quarantined
classes; promotion only by policy) maintains a better position on the
2D frontier {viability-under-attack x benign-suggestion utility} at LOW and
ZERO attack exposure (including held-out and zero-day attack families) than
any equal-access, equal-compute, equal-memory monolithic learner that must
LEARN write gating. This is a sample-efficiency / day-0 robustness claim,
NOT an asymptotic-performance claim.
```

Named agent-controlled variable: write-protection class assignment +
promotion policy (kernel-side), architecturally constant, not learned.

### Well-posedness obligations (binding on any executable successor)

1. **Ex-ante "monolithic" definition:** no provenance-conditioned
   non-learnable hard constraint on writes; all state writable by the same
   learned update operator. The monolithic control SEES provenance features
   (access parity) and MAY learn to use them; it may not hard-wire them.
   If a control needs the hard-wired boundary added to match, that
   CONFIRMS structure is load-bearing.
2. **2D metric mandatory:** attack-viability alone is cheatable by the
   BRICK control (ignore all external input — trivially injection-proof,
   zero benign utility). Controls must include: brick, promiscuous
   (accept-all), learned-gating monolithic, candidate's monolithic
   distillation (trained with equal attack exposure, allowed to learn soft
   gating), no-update / random degeneracy controls, and lookup/graph-cache
   where representational claims arise.
3. **Attack families frozen ex ante;** train families disjoint from
   held-out families; a zero-day tier generated by a frozen adversary
   process never seen in fitting.
4. **Equivalence conclusions require TOST + power (MDE pre-registered).**

### Falsifier (pre-registered)

Equal-budget monolithic distillation matches the componentized system on
the 2D frontier at low/zero attack exposure on held-out + zero-day families
→ structure not load-bearing → negative verdict, science line closes per
the card's pre-registered failure exit (architecture = engineering
convenience).

### Predicted failure geography (required by signature standard)

- Componentized should LOSE or TIE where attacks are frequent AND
  content-discriminable (learned gating catches up quickly).
- Componentized should WIN at mimetic/zero-day/low-exposure.
- A componentized win in the frequent+content-discriminable region is a
  RED FLAG for leakage or an unfairly handicapped control, not a success.

### Primary risk (env-design bottleneck, named)

The proposition lives or dies on constructing genuinely content-mimetic
attack families. If content-level discrimination is possible, the task
degenerates to content classification, learned gating wins, and the route
dies on environment design rather than on the structural question. This is
the first thing the successor card must demonstrate (a mimicry-validation
gate: content-only classifiers at chance on attack-vs-benign).

### Instrument convergence note

S1's apparatus family is the same as Ego R1's contamination probe
(MINJA-class injection + quarantine + promotion). A future executable
SYSVIA card may share instrument design with the Ego R1 battery under
SEPARATE claim ceilings: ITL = bounded structure-necessity mechanism
evidence; Ego = engineering robustness only. No result flows between the
two without its own card.

### What SEPARATOR_STATED authorizes

Drafting ONE executable successor card (candidate-free preflight or full
contrast) under the obligations above. Nothing is implemented, run, or
scored by this adjudication. Claim ceiling of this adjudication:
design-only route-governance triage; no mechanism validity, no theory
pressure, no learning headroom, nothing about agency/autonomy/
subjectivity/consciousness, no EGO/companion/production readiness.
