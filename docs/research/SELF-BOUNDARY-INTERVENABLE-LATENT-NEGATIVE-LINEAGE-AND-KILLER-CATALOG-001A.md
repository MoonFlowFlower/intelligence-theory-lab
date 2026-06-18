# SELF-BOUNDARY / INTERVENABLE-LATENT — NEGATIVE LINEAGE + KILLER CATALOG (001A)

Status: prior-negative-evidence record (research synthesis). NOT a task card. Authorizes
no implementation. Required reading before drafting any "grounded latent / self-state
intervention / grounding gate" card.

Why this exists: CLAUDE.md operating contract — "Every successor task must search and cite
relevant prior negative evidence before proposing a new gate, bridge, or implementation."
An external review (GPT) re-derived the next route as a **"Grounded World-Model / Self-State
Intervention Gate"**: an *intervenable latent state that simultaneously constrains
prediction, report, and action*. That route is **NOT new** — it is this lab's **ACSB
(action-conditioned self-boundary) → Route C** family, which has a standing negative
lineage. Re-entry requires beating the documented killers below, point by point.

---

## 1. The lineage (what was tried, what killed it)

| # | Experiment (anchor) | Verdict | What killed it |
|---|---|---|---|
| 1 | ACSB family (sealed @ `d5b4b92`) | downgraded+sealed | **obs-decodability**: `_target_from_observation = phase_bit XOR action_bit`, both bits live in the legal observation → obs-only baseline == oracle (1.0/1.0/0.0 artifact) |
| 2 | ACSB-001B learned-baseline challenge (@ `347b75b9`) | blocks_on_learned_baseline_invalidity | **fake challenger panel**: the 3 "learned" baselines were deterministic heuristics (no `.fit`, no ML), engineered to score 0.0 → gate non-fail-able (reference=1.0 *by construction*) |
| 3 | ACOLB-A online-vs-amortized | saturated_close (negative) | **fair-baseline saturation**: candidate (online Kalman w/ forgetting) ≡ fair amortized (batch discounted-LS) — the *same* discounted-least-squares estimator → saturation **algebraic**, margin 0.0147 < band 0.05 |
| 4 | Route C preflight 001A (@ `726f26d`) | blocked_by_observation_baseline_underpowered | **non-identifiability asserted not tested**: shipped obs-only baseline never read the passive values (only planted answer-maps); a value-level decode probe broke it (mean-attacker=1.0 vs shipped 0.3854, gate still ADMIT) |
| 5 | Candidate-free Route C separation probe 001A | reject_as_false_positive_or_weakened_baseline | **metric degeneracy + incomplete panel**: recall-only metric (predict-more = win) + missing `predict_all` fair baseline (predict all 12 legal → recall 1.0 == oracle); add it → separation vanishes, delta=0 |
| 6 | AIDSP-001A-R1 drive variant (this session; code `6b8a6b61`, prereg `c594f4ae`) | baseline_equivalence_or_no_separation | EFE epistemic term **redundant**; winner = transition-conditioned model-based pragmatic inference. (Different mechanism — drive, not latent — but first run to *cleanly defend* against killers below) |

Cross-cutting standing fact: **every principled mechanism in this family has collapsed to a
simpler fair/observational baseline once the panel and metric were made honest.** That is
the prior a successor must update on, not route around.

---

## 2. The killer catalog (a grounding gate MUST pre-register a defense for each)

**K1 — Observation-decodability (the ACSB killer).**
If the latent is decodable from the *current legal observation*, an obs-only baseline ==
oracle and the gate measures "you read the answer from the input." Defense required: a
non-identifiability premise that is **tested, not asserted** — the obs-only baseline must
be a *capable* passive predictor (allowed covariance/clustering/supervised fit on the
actual values), AND a **value-level decode positive control** (inject the latent into the
observation values) must be able to flip the gate to *blocked*. If a planted leak cannot
make the obs-baseline win, the obs-baseline is underpowered (Route C preflight failure).

**K2 — Interventional / fair-baseline saturation (the ACOLB/A killer).**
Separation MUST be measured as `candidate − max(fair INTERVENTIONAL baseline panel)`, NOT
`interventional − observational`. The panel MUST include the strongest fair non-privileged
estimators: the `predict_all`-analog AND a capable **fitted** interventional baseline
(CI-test / do-regression / contingency table / nearest-neighbor / FSM). Tie within band
with any of them = baseline-equivalence STOP. (A died because candidate == discounted-LS
algebraically; do not let the latent gate die the same way silently.)

**K3 — Metric degeneracy / single-sided (the separation-probe killer).**
No recall-only / unbounded-prediction-set metric. Use precision-aware/balanced (exact-set,
F1, Jaccard) or cap `|pred| ≤ K` for ALL agents incl. oracle. A **triviality probe**
(predict_all, exhaustive, uniform, history-cache) must score low; any trivial winner →
`invalid_metric_degenerate` STOP. (AIDSP-001A-R1's triviality probe is the working template:
predict_all scored 0.0, trivials < oracle.)

**K4 — Fake/crippled challenger panel (the ACSB-001B killer).**
Every "learned"/"capacity-matched" baseline must be a **real fitted model** (actual `.fit`
on the legal inputs *including* the discriminating fields), never a deterministic heuristic
rigged to score 0. If a competent challenger cannot make the gate fail, the gate is
non-fail-able. (AIDSP-001A-R1 used real tabular-Q learners trained on disjoint seeds.)

**K5 — Non-fail-able self-declared fields (recurring across the lineage).**
No `computed_not_literal=True` / `threshold_frozen=True` / `failure_path_available=True` as
asserted constants. Each needs a positive control that flips it. (AIDSP-001A-R1: verdict
shown computed via `compute_verdict` boolean conjunction; `scanner_failable` proven by
planted leaks.)

**K6 — Name/label leakage + candidate==label-generative.**
The leakage scanner must catch **semantic** leakage (statistical mutual information), not
just name substrings; the candidate/metric must not trivially reproduce the label.
(AIDSP-001A-R1 caught a renamed leak `aux_sensor_7` by MI 3.19 ≥ 0.9·H_food, name_flag=false.)

**K7 — Claim-ceiling leakage / re-authorization.**
A preflight that shows a gate is *buildable* must NOT emit authorization to claim self/agency
or to re-open a closed surface. **Buildable ≠ passed; passed ≠ evidence of self/feeling.**

---

## 3. Extra constraints specific to GPT's grounding-gate proposal

- **"report" channel must be structured/discrete, NOT free-text from an LLM.** Free-text
  report pulls in an LLM (forbidden by the project contract) and reintroduces fluent
  confabulation — the exact "looks alive" failure the whole lab exists to reject.
- **Latent must integrate history and be non-enumerable**, else a hardcoded `need`/`pref`
  scalar read by report+action+prediction passes "intervene → all three change" trivially
  (the apple-test trap). Non-obs-decodable (K1) + non-enumerable + history-dependent are the
  three conditions that separate a *real latent* from a *fancy behavior tree*.
- **Do not migrate to MiniGrid/MiniHack/Crafter for this gate.** Intervention + 3-channel
  readout need a *minimal, fully-instrumented* world; richer environments add confounds and
  breed false passes. Right structure (latent ⟂ observation, intervention hooks), not size.

---

## 4. Gate to even DRAFT

A grounding-gate card may be drafted **only if** it states, point by point, how it beats
**K1–K7** — in particular K1 (capable obs-baseline + value-level decode positive control)
and K2 (separation vs max fair interventional panel incl. predict_all-analog + fitted
estimator). **If the card cannot state defenses for K1 and K2, it is not ready to draft —
and that is itself the contract-preferred negative answer.**

## Claim ceiling

Negative-lineage record only. Authorizes nothing, claims no route will work, weakens no
prior negative. The strongest a future grounding gate could ever claim is: "bounded
evidence of a non-obs-decodable, interventionally-valid latent that causally co-binds
prediction/report/action against a fair panel, in one minimal world." NOT self, feeling,
emotion, agency, autonomy, or subjectivity.

Anchors: ACSB `d5b4b92` · ACSB-001B `347b75b9` · Route C preflight `726f26d` ·
AIDSP-001A-R1 code `6b8a6b61` / prereg `c594f4ae`.
