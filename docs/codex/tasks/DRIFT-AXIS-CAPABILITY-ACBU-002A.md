# DRIFT-AXIS-CAPABILITY-ACBU-002A

Action-Conditioned Belief Update under Non-Stationary Drift — STEP-0 kill-test

Status: DESIGN + PREREGISTRATION BANKING PLAN / RED / NO SCORING IN THIS CARD.
This card supersedes `DRIFT-AXIS-CAPABILITY-ACBU-001A` for STEP-0 framing.
Codex is sole repo writer. Phase 2 execution is gated on an independent Red-audit
CLEAR of the banked preregistration artifact.

Auto-Remote-Anchor: forbidden. The Phase 1 branch push is operator-authorized by
the task's explicit commit discipline; it is not a tag/anchor and does not
upgrade the claim.

## task id

`DRIFT-AXIS-CAPABILITY-ACBU-002A`

## problem definition

ACBU-001A proposed an online-ideal minus amortized-fixed-ideal STEP-0 headroom
test. That framing is rejected for POMDP-like settings because the
Bayes-optimal history-conditioned recurrent meta-policy and explicit
belief-state optimal policy converge to the same optimal object under unbounded
data/compute. The correct kill-test is therefore resource-bounded:

```text
Can a disclosed model-form, action-conditioned structured belief update show
OOD sample-efficiency over an adequately trained recurrent meta-learning
baseline under frozen compute, precision, replay, ablation, and access-rung
constraints?
```

The Phase 1 task is only to bank the patched route card and the frozen STEP-0
preregistration as an ancestor commit of any future run.

## current stage

Phase 1 — preregistration bank, docs-only.

No source code, tests, artifacts, route-state mutation, scoring, calibration, or
STEP-0 run is authorized in Phase 1.

## current layer

Learning/adaptation + mechanism-hypothesis benchmark design, with engineering
implementation hygiene for preregistration and commit-order evidence. It is not
a subjectivity-validation or philosophical-consciousness task.

## mainline target

None. This task does not target EGO mainline, runtime, UI, companion behavior,
LLM/AIRI integration, deployment, API keys, external services, or production
paths.

## enabled-state requirement

Phase 1 output is a committed docs-only preregistration ancestor. Phase 2 remains
disabled until an independent Red-audit, not the designer, records CLEAR of the
banked preregistration.

## real-trigger evidence requirement

Phase 1 may cite only:

- the operator-provided final monolithic preregistration text;
- live repo state;
- route-state readback;
- prior banked negative evidence and standards.

No Phase 2 claim may be made without callable artifacts from the future isolated
implementation path.

## bounded audit before implementation

- Real objective: freeze a kill-test that can fail cheaply before candidate
  implementation or result tuning.
- Strongest baseline explanation: an adequately trained recurrent RL2 baseline
  may amortize the same policy over history under the declared distribution,
  making any structured-prior advantage vanish or reduce to disclosed model-form
  prior rather than active probing.
- Strongest reason the task may be invalid: the candidate has disclosed
  model-form access while the primary claim might be misstated as equal-access;
  the verdict must block any such mismatch.
- Falsifier for the framing: RL2 reaches adequacy and is statistically
  equivalent to the candidate on the primary OOD cell, yielding
  `SATURATED_BASELINE_EQUIVALENCE`.
- Evidence still insufficient: a candidate win without RL2 adequacy, without
  precision adequacy, without probe/belief ablation destruction, without
  replay recomputation, or with access-rung mismatch.
- Mechanism-vs-resemblance classification: this tests a resource-bounded
  disclosed-structure benchmark signature only; it is not evidence of
  subjectivity, agency, autonomy, consciousness, or EGO readiness.
- Hard-coding / leakage checks: hidden `g_t`, true cell hazard, OOD parameters,
  target labels, action answers, seed identity, or fixture ordering must not be
  fed to the candidate except through audit-only ceiling fields.
- Local optimum / weak baseline checks: RL2 adequacy is blocking; weak controls
  are engineering-sufficient only and cannot carry the decisive comparison.
- Zeno / rescue check: no frozen value may change after scores; no broadening,
  weakening, or extra rung may be invented to move a verdict.
- Replay weakness check: future replay must recompute candidate belief
  trajectory from `(b_0,{a_t,o_t})+U`, with two fresh-process recomputes.
- Claim inflation check: even `PROCEED_NARROW` means disclosed-structure,
  resource-bounded, family-bounded offline evidence only.

## collision record

### Candidate 1: minimal implementation first

- Evidence it would produce: quick code and scores for a drift bandit.
- Strongest cheap baseline that could match it: RL2 with enough training, or a
  known-params planner/structured oracle.
- Leakage / hard-coding risk: high; OOD params or `g_t` can accidentally enter
  the candidate through the same code path as ceilings.
- Smallest falsifying test: access-rung mismatch or RL2 equivalence.
- Expected failure mode: high-score/no-attribution or baseline equivalence.

### Candidate 2: preregistration bank first

- Evidence it would produce: commit-order anti-tuning proof and frozen
  verdict/metric/access rules before any run.
- Strongest cheap baseline that could match it: none at Phase 1 because no
  score is produced; the future decisive baseline is RL2.
- Leakage / hard-coding risk: lower; all access, metric, adequacy, ablation, and
  stop conditions are frozen before implementation.
- Smallest falsifying test: prereg text missing frozen numbers, callable verdict
  rules, stop conditions, or access-rung failure.
- Expected failure mode: independent Red-audit rejects the prereg before Phase 2.

### Candidate 3: mechanism-faithful Phase 2 implementation

- Evidence it would produce if later authorized: calibrated cost, env
  admissibility, RL2 adequacy, primary OOD metrics, ablations, trace/replay, and
  callable verdict artifacts.
- Strongest cheap baseline that could match it: adequate RL2 recurrent
  meta-learning over the same history; if it ties, verdict is
  `SATURATED_BASELINE_EQUIVALENCE`.
- Leakage / hard-coding risk: high unless audit-only ceiling fields and model
  form access are strictly separated.
- Smallest falsifying test: `equivalent(total_sep)`, lack of precision
  adequacy, non-destructive ablations, or metric invalidity.
- Expected failure mode: underpowered baseline or baseline equivalence.

### collision selection

Select Candidate 2 for the current task:

```text
Bank the docs-only preregistration as an ancestor commit. Stop after Phase 1.
Do not implement or score until independent Red-audit CLEAR is recorded.
```

## hypothesis

The only possible Phase 2 positive claim is narrow:

```text
Under disclosed MODEL_FORM_ACCESS and frozen compute/precision gates, a
structured action-conditioned belief update may show resource-bounded OOD
sample-efficiency over an adequately trained recurrent meta-learning baseline.
```

## strongest baseline

`C-MetaRecurrent RL2` from the preregistration is the decisive baseline:
GRU hidden 128, A2C, Adam 3e-4, entropy 0.01, discount 0.99, compute ladder
50k/100k/200k, first rung with F_train normalized regret <= 0.15, otherwise
`UNDERPOWERED_BASELINE`.

## ablation requirement

Future Phase 2 must evaluate no-info-gain, random-probe, frozen-belief, and
no-hazard-mix exactly as frozen in the preregistration. Ablations must be
callable reruns, not literal verdict fields.

## trace / replay requirement

Future Phase 2 must log per-step candidate belief summaries, action, q/KG/IG,
prediction, actual reward, prediction error, next belief, audit-only theta, and
per-framework RNG seeding. Replay must reconstruct the candidate belief
trajectory from `(b_0,{a_t,o_t})+U` bit-exact in two fresh processes.

## computed-evidence provenance gate

Future evidence-bearing values must be computed from committed rows by callable
producer paths and must record producer function, input artifacts, run ID,
seed/context/episode IDs, aggregation rule, and code path hash. Literal
verdict dictionaries, unconditional clean reports, and hash-only replay cannot
carry evidence claims.

## acceptance gate for Phase 1

Phase 1 is accepted only if:

- `docs/codex/tasks/DRIFT-AXIS-CAPABILITY-ACBU-002A.md` exists;
- `docs/codex/tasks/DRIFT-AXIS-CAPABILITY-ACBU-002A-STEP-0-PREREG-001A.md`
  exists and contains the frozen final monolithic preregistration;
- no source, tests, artifacts, route-state packet, prior artifact, global schema,
  EGO, LLM/AIRI, UI, deployment, or credential path is changed;
- the staged set contains only the two Phase 1 docs paths;
- the commit message is
  `prereg: freeze drift-axis ACBU-002A STEP-0 kill-test (frozen numbers, verdict callable)`;
- Phase 2 is not run.

## stop condition

Stop after Phase 1 commit and branch push. Do not proceed to Phase 2 until an
independent Red-audit records CLEAR. If the prereg cannot be banked as a
docs-only ancestor commit, report the blocker and do not implement.

## rollback plan

Before commit: remove only the two Phase 1 docs files. After commit: revert the
Phase 1 commit if the operator rejects the preregistration. Do not delete or
rewrite prior artifacts.

## expected changed files

Phase 1:

- `docs/codex/tasks/DRIFT-AXIS-CAPABILITY-ACBU-002A.md`
- `docs/codex/tasks/DRIFT-AXIS-CAPABILITY-ACBU-002A-STEP-0-PREREG-001A.md`

Phase 2, only after independent Red-audit CLEAR and separate execution
authorization:

- `src/drift_capability_acbu/`
- `tests/drift_capability_acbu/`
- `artifacts/DRIFT-AXIS-CAPABILITY-ACBU-002A/`

## forbidden changes

EGO mainline/integration, LLM/AIRI, UI/companion/emotion/affect/proactive
behavior, relationship learning, global schema, any prior artifact,
credentials, external services, pixel/physics envs, `StructuredInferred` at
STEP-0, changing frozen values after seeing scores, weakening RL2/MDE/band,
broadening priors to rescue, Phase 2 run before independent Red-audit CLEAR.

## claim ceiling

Phase 1 proves only that the preregistration was banked locally/remote-branch
published in commit order. It does not prove mechanism validity, learning
headroom, baseline non-equivalence, agency, autonomy, subjectivity,
consciousness, functional subjecthood, EGO/companion readiness, production
readiness, or mainline effect.

## next minimal closed-loop action

Obtain independent Red-audit CLEAR of the banked preregistration artifact. Only
after CLEAR may a separate Phase 2 execution task begin with cost calibration.
