# TRACK1-LEARNING-GENERALIZATION-PREFLIGHT-001A (TLGP-001A)

**STATUS: DRAFT TASK CARD. NOT AUTHORIZED FOR EXECUTION.**
Drafting authorized (user, this session). Forbidden until separate explicit authorization:
implementation code, harness run, `artifacts/` production, schema change, and any
`commit`/`push`/`tag`/remote `anchor`. Execution should run in a fresh, outcome-neutral
session (per `SESSION-HANDOFF-001A`).

Derives method from `docs/research/BENCHMARK-METHODOLOGY-APPLICABILITY-001A.md` (P1 train/test
gap = Procgen; P2 known-latent + ideal-observer = Alchemy; P3 baseline panel = POPGym).
Defends against `docs/research/SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A`
(K1/K3/K4/K6).

## 0. Framing guard
This is **candidate-free**. It does NOT test any learning mechanism. Its only job: prove (or
disprove) that a minimal world + metric can **discriminate latent-structure inference from
lookup/memorization, leak-free, with measured headroom vs an ideal observer**. Route C / the
self-state route died precisely because this step was skipped (obs-baseline underpowered,
metric degenerate → false positive). Pass here only authorizes *drafting* a later candidate
card; it is not a learning result.

## task id
TLGP-001A

## research layer
Engineering implementation + mechanism-hypothesis preflight. NOT subjectivity/consciousness.

## problem definition
Track 1.1 (learning/generalization) is the highest-EV lab axis. Before testing any candidate
learner, we must establish a world where **"infers the latent compositional structure"** is
behaviorally separable from **"memorizes/looks up seen cases"** — on a degeneracy-safe,
held-out metric, with no answer leakage, and with positive headroom between an ideal
(Bayesian) observer and the best non-inference baseline. If that separation does not exist,
no candidate result in this world could mean anything.

## current stage
Pre-implementation, candidate-free. No candidate, no learner exists or is authorized.

## world (minimal, fully-instrumented; Alchemy-flavored)
- **Latent = a compositional rule** `f` drawn per episode from a structured family: an
  outcome is a function of symbol *properties* (e.g. `effect = g(prop_A, prop_B)`), NOT of
  symbol identity. The agent observes properties, tries actions, sees effects → must
  **infer the rule by experimentation**, then predict on new symbols.
- **Held-out generalization split (P1):** the symbol-property combinations (and/or rule
  family members) are partitioned into TRAIN and **HELD-OUT**. A memorizer that learns
  seen property→effect pairs succeeds on TRAIN and **fails on HELD-OUT combinations**; an
  agent that infers the compositional rule generalizes.
- **Latent not single-step decodable (K1):** the rule cannot be read from one observation;
  it requires integrating ≥k interactions. (Verified by the single-step-decoder control.)
- No answer/rule-id appears in any observation (anti-leakage).

## instruments / baselines (all REAL, fitted; no stubs — K4)
- **Ideal observer (P2 ceiling):** Bayesian agent that knows the rule *family* and does
  optimal posterior inference + exploitation. Defines the headroom ceiling. (Probe
  instrument, excluded from any future candidate comparison.)
- **No-inference floor:** fixed/random policy with no adaptation.
- **Fair non-inference baselines (must be real):** training-rule lookup; nearest-neighbor
  over training cases; a fitted classifier (logistic/MLP) on flattened interaction history;
  majority/`predict_all` (hedge).
- **Single-step decoder (K1 control):** a model that tries to decode the latent from ONE
  observation — must score at floor (else latent is obs-decodable → world invalid).

## pre-registered metric (degeneracy-safe — K3; formulas frozen at run)
- **Primary = HELD-OUT generalization score:** balanced accuracy / normalized (1−regret)
  vs ideal observer on HELD-OUT combinations, after a fixed adaptation budget of `k`
  interactions. Balanced (per-rule averaged, chance floor); NOT single-sided; `predict_all`
  must NOT win.
- **Headroom = ideal_observer − max(non-inference baselines)** on HELD-OUT. Must exceed
  pre-registered `margin` or the world cannot discriminate.
- **Generalization gap = held-out − train** for each baseline (memorizers show large gap).
- All numeric constants (symbol/property dims, rule family, `k`, `margin`, seeds, train/
  held-out split) committed to `result.json.preregistration` + sha **before** any run;
  `margin` derived from the triviality battery (`max trivial + δ`, δ fixed in card) — not
  tuned after results.

## triviality probe (RUNS FIRST; gates everything — K3)
Battery {predict_all/hedge, majority, training-rule lookup, nearest-neighbor, no-adaptation,
single-step-decoder} run on HELD-OUT. **If any closes the headroom (scores near the ideal
observer on held-out), the world/metric is degenerate → verdict
`world_cannot_discriminate`, STOP.** (The lookup/NN/predict_all winners are exactly the
Route-C / candidate-free-probe killers; this probe is their pre-registered tripwire.)

## leakage positive controls (scanner must be fail-able — K6)
Plant ≥2 leaks and require detection+block: (i) rule-id wired into an observation channel;
(ii) held-out effect leaked into training observations. A statistical leak detector
(MI between observation channels and the latent rule ≥ frac·H_rule) must flag both,
including a **renamed** channel (caught by statistics, not name). If a planted leak is not
caught → `invalid_due_to_leakage_or_contract_failure`.

## ablation (of the WORLD, not a candidate)
- **shuffle-structure ablation:** replace the compositional rule with a random
  (non-compositional) lookup table → ideal-observer headroom over lookup should **collapse**
  (confirms the headroom comes from *structure*, not artifact). Fail-able control.

## trace / replay requirement
Per-episode `trace.jsonl`: held-out rule id (ground truth, hidden from agents), interaction
sequence, each agent's actions + (ideal observer's) posterior, per-step effects, scores.
Verdict must replay from trace; no hidden future info; no renderer-only behavior.

## acceptance gate (pre-registered, computed, fail-able both ways)
Verdict (computed from booleans, not a header literal):
- `world_discriminates_structure_inference` IFF ALL: headroom > `margin`; every triviality/
  non-inference baseline ≤ floor+`margin` on held-out; single-step decoder ≤ floor;
  leakage positive controls all caught; shuffle-structure ablation collapses headroom;
  replay exact. → authorizes *drafting* a candidate card (NOT running one).
- `world_cannot_discriminate__lookup_or_degenerate`: any lookup/NN/predict_all/single-step
  decoder closes headroom, OR headroom ≤ margin, OR ablation doesn't collapse → STOP,
  banked negative (world too weak — contract-preferred).
- `invalid_due_to_leakage_or_contract_failure`: any planted leak uncaught / parity violation.

## claim ceiling
A pass = "a minimal procedural world that **provably separates** compositional-latent
inference from lookup/memorization on a held-out, balanced, leak-free metric, with measured
headroom vs an ideal observer." NOTHING MORE. It tests **no candidate**, is **not**
generalization-mechanism evidence, and evidences **nothing** about agency, learning-as-
adaptation-mechanism, self, feeling, or subjectivity. A negative = "this world cannot
discriminate," bounded to this world.

## anti-hardcoding audit (predeclared; before AND after)
- [ ] metric on ground-truth/ideal-observer, never a candidate's own output (candidate-free anyway)
- [ ] `margin` derived from triviality battery, δ fixed pre-run, never tuned
- [ ] triviality probe + single-step decoder run and pass BEFORE `world_discriminates` is emittable
- [ ] held-out split real (train-rule lookup fails on held-out)
- [ ] all "baselines" are real fitted models, not deterministic stubs
- [ ] ≥2 leakage positive controls planted AND caught (incl. renamed channel via MI)
- [ ] shuffle-structure ablation is fail-able (collapses headroom)
- [ ] verdict computed from artifacts, not a report-header literal
- [ ] no LLM anywhere; no commit/push/tag/anchor

## stop conditions
- any lookup/NN/predict_all/single-step decoder closes headroom → STOP, `world_cannot_discriminate`.
- headroom ≤ margin → STOP (no discriminating power).
- planted leak uncaught → STOP, invalid.
- shuffle-structure ablation does NOT collapse headroom → STOP (headroom is artifact).
- tooling cannot express the world faithfully → STOP, report (no weaker-world substitution).

## rollback plan
Isolated new files only: `src/tlgp_001a/` (world, rule_family, ideal_observer, baselines,
leakage, metrics, probe, harness), `tests/test_tlgp_001a.py`, `artifacts/TLGP-001A/`.
Rollback = delete those three paths. No edits to existing src/contracts/schemas/prior
artifacts/push scripts.

## evidence contract (artifacts/TLGP-001A/ on a future authorized run)
result.json (preregistration block + sha + computed verdict + claim_ceiling), trace.jsonl,
baseline_comparison.json (incl. headroom + per-baseline held-out/train gaps),
triviality_probe_report.json (gates), ablation_report.json (shuffle-structure),
positive_control_report.json (planted leaks + catches), replay_report.json,
failure_manifest.json if any stop triggers.

## HYGIENE fields (necessary, NOT sufficient)
mainline target: none · enabled: isolated CLI harness only · real-trigger: local→artifacts
only · Auto-Remote-Anchor: forbidden · provenance per score: producer_function/inputs/
run_id/seed/aggregation/code_path_hash · PAT/secret scan of run path before any run.

## pre-implementation plan (future authorized run only)
- files to change: `src/tlgp_001a/*`, `tests/test_tlgp_001a.py`, `artifacts/TLGP-001A/*` (all new)
- forbidden: everything else (existing src, contracts, docs, prior artifacts, schemas, push scripts)
- commands: venv; numpy/scipy (+ scikit-learn for the fitted baselines); `pytest`; run probe→eval→verdict. No git commit/push/tag/anchor.
- rollback: delete the three new paths

## what this does NOT prove
Not a learning mechanism. Not generalization-as-mechanism (that is the *next*, candidate
card, gated on `world_discriminates`). Not agency/feeling/emotion/self/autonomy. Not that any
candidate will beat the baselines. Only: whether this one minimal world can tell
structure-inference apart from lookup.
