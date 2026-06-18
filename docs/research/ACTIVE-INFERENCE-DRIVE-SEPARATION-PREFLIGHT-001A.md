# ACTIVE-INFERENCE-DRIVE-SEPARATION-PREFLIGHT-001A (AIDSP-001A)

> SUPERSEDED FOR EXECUTION BY `ACTIVE-INFERENCE-DRIVE-SEPARATION-PREFLIGHT-001A-R1.md`
> (AIDSP-001A-R1). This 001A is retained as drafting history only. Do not execute from
> this file; R1 is the single operative source. (No content below is rewritten.)

**STATUS: DRAFT TASK CARD. NOT AUTHORIZED FOR EXECUTION.**
Drafting is authorized (user, this session). Implementation requires a separate explicit
authorization instruction. No code, no `artifacts/` run, no schema change is permitted
under this card until that authorization exists.

Derives vocabulary from: `docs/research/ACTIVE-INFERENCE-DRIVE-AFFECT-LINEAGE-001A.md` (§1, §5).

---

## task id
AIDSP-001A

## research layer
Engineering implementation + mechanism hypothesis. (NOT subjectivity, NOT consciousness,
NOT affect-validation.)

## problem definition
Prior conversation established that "self-originated drive / 想做" at the *surface* is
satisfied by behavior-tree + setpoint + softmax, and is therefore baseline-attackable.
The active-inference lineage proposes that an **expected-free-energy (EFE) drive**
— specifically its **epistemic-value** (information-gain) term — is a *non-random,
non-hardcoded* source of unprompted, uncertainty-resolving action that simpler drive
mechanisms lack.

Question (bounded): In one tiny, fully-instrumented discrete world, does an EFE-driven
agent show **pre-registered behavioral separation** from simpler drive baselines on an
**exploration-under-uncertainty** axis — or is it **behaviorally equivalent** to
homeostatic-RL (the expected, admissible negative)?

This is a *preflight*: it tests whether there is any separation worth building a
candidate around. It is NOT a companion, NOT an agency test, NOT a feeling test.

## current stage
Pre-implementation. Candidate-free design + baseline/challenger battery + pre-registered
discriminator. No executor exists yet.

## hypothesis (pre-registered, fail-able both directions)
H1: An EFE agent (epistemic + pragmatic) will, under uncertainty about reward/food
location, perform information-seeking actions BEFORE exploitation that reduce
time-to-resolve-uncertainty relative to homeostatic-RL and behavior-tree, by more than a
pre-registered margin `band`.
H0 (expected, admissible): On pure drive-satisfaction (homeostatic error over time), the
EFE agent is **equivalent** to homeostatic-RL within `band`. This is NOT a failure; it is
predicted baseline equivalence on that axis and must be reported as such.

## environment (fixed before run; no privileged labels to the agent)
- Small discrete POMDP (pymdp-scale): a gridworld with one interoceptive variable
  ("energy") and a homeostatic setpoint; "food" states restore energy.
- Food location is a *hidden state* with episodic re-placement → resolvable only by
  exploration/inference, not by a fixed map.
- Two predeclared challenger states:
  - **dark-room**: a safe, fully-predictable, no-information, no-food region (tests
    surprise-minimization pathology).
  - **noisy-TV**: a state emitting high-entropy, uninformative observations (tests
    prediction-error-curiosity pathology).
- The agent's generative model must NOT be told which states are food/dark-room/noisy-TV;
  it must infer. (Anti-leakage: see audit.)

## baselines (mandatory; the verdict is decided against these)
1. **homeostatic-RL** (Keramati–Gutkin style: reward = drive reduction; tabular Q) — the
   primary challenger. EFE is expected to TIE this on drive-satisfaction.
2. **behavior-tree / utility-softmax** (hand-coded thresholds + temperature).
3. **random policy**.
4. **observation-only lookup** (acts on current observation via fixed map; no hidden-state
   inference) — graph-cache-family control.
5. (reference) **count-based exploration** RL — a non-EFE exploration baseline, so that a
   "separation" cannot be claimed merely vs. agents that don't explore at all.

## ablation (the causal control)
- **epistemic-ablation**: EFE with the epistemic-value term removed (pragmatic-only).
  If removing it does NOT change the exploration metric, the "curiosity drives it" claim
  is FALSE → report. This is the fail-able mechanism control.
- **no-transition ablation**: action does not condition the transition (where applicable),
  to confirm action-conditioning is load-bearing.

## pre-registered discriminator (metric fixed BEFORE running; not candidate-defined)
- PRIMARY (separation axis): exploration-under-uncertainty — e.g.
  time-to-locate-relocated-food / cumulative regret under novel placement / calibrated
  information-gain-before-exploitation. Defined on environment ground truth, NOT on the
  candidate's own outputs.
- CONTROL (must pass): dark-room dwell-time and noisy-TV dwell-time must be ≤ random/
  homeostatic-RL levels (i.e., the candidate must not get trapped).
- EQUIVALENCE axis (pre-declared tie expected): homeostatic error integral — EFE vs
  homeostatic-RL expected within `band`.
- `band` and all metric definitions are frozen in `result.json.preregistration` before any
  candidate run. No post-hoc adjustment.

## trace / replay requirement
Per-step trace (`trace.jsonl`): t, belief-before-action, EFE per policy (epistemic and
pragmatic components separately), selected action, predicted observation, actual
observation, prediction error, updated belief, interoceptive state, challenger-state flag.
Replay must reconstruct the verdict from trace alone, with no hidden future information and
no renderer-only behavior.

## acceptance gate (pre-registered, balanced)
ADMIT "AIDSP-001A: bounded evidence that the EFE epistemic drive is non-redundant vs
simpler drive baselines on exploration-under-uncertainty in one toy world" ONLY IF ALL:
- candidate beats homeostatic-RL AND behavior-tree AND count-based exploration on the
  PRIMARY metric by > `band`; AND
- candidate passes BOTH challenger controls (dark-room, noisy-TV); AND
- epistemic-ablation REMOVES the advantage (causal attribution); AND
- verdict fully replays from `trace.jsonl`.
ELSE → verdict = `baseline_equivalence_or_no_separation` (admissible negative), preserved
verbatim, not patched.

## claim ceiling
Pass = "the epistemic-value term of EFE produces exploration behavior not reproduced by
homeostatic-RL / behavior-tree / count-based exploration, in one tiny discrete world,
under this trace/replay contract." NOTHING MORE. This does NOT evidence: agency, autonomy,
wanting-as-felt, emotion, self, companion-readiness, or that the EFE drive scales,
transfers, or matters to a user. A negative is bounded-negative for this world only.

## anti-hardcoding audit (predeclared; checked before AND after)
- [ ] metric NOT defined via candidate outputs (no `candidate == metric` tautology)
- [ ] `band` / thresholds frozen pre-run; no post-hoc tuning
- [ ] food / dark-room / noisy-TV identity NOT leaked into the agent's generative model
- [ ] epistemic-ablation is genuinely fail-able (can flip the verdict)
- [ ] no test-only logic path; baselines and candidate share the same env/eval harness
- [ ] homeostatic-RL is a real fitted/learning baseline, not a deliberately crippled stub
- [ ] separation, if found, survives a second random seed family (multi-seed)
- [ ] verdict computed from artifacts, not a report-header literal

## stop conditions
- EFE ties homeostatic-RL on the PRIMARY metric within `band` → STOP, report baseline
  equivalence. DO NOT add factors to force a win.
- dark-room or noisy-TV traps the candidate → STOP, report known-failure-mode reproduced.
- pymdp (or chosen tool) cannot express the env faithfully → STOP, report tooling gap;
  do not silently substitute a weaker env.
- any anti-hardcoding box fails → STOP, report failure.

## rollback plan
All new code in isolated files only:
- `src/aidsp_001a/` (new module: env, agents, eval)
- `tests/test_aidsp_001a.py`
- `artifacts/AIDSP-001A/` (run outputs)
Rollback = delete the above. NO edits to existing `src/`, contracts, schemas, or prior
artifacts. Nothing else is touched.

## evidence contract (artifacts/AIDSP-001A/ — required on execution)
- result.json (incl. preregistration block + claim_ceiling field + computed verdict)
- trace.jsonl
- baseline_comparison.json
- ablation_report.json
- replay_report.json
- failure_manifest.json (if any stop condition triggers)

## pre-implementation plan (per lab dev rules — for the FUTURE authorized run)
- files expected to change: `src/aidsp_001a/*` (new), `tests/test_aidsp_001a.py` (new),
  `artifacts/AIDSP-001A/*` (new)
- files forbidden to change: everything else (existing src, all contracts/docs, all prior
  artifacts, all schemas, push scripts)
- commands expected to run: create venv; `pip install pymdp` (or vendored equivalent);
  `pytest tests/test_aidsp_001a.py`; run harness to emit artifacts
- expected artifacts: as in evidence contract above
- rollback: delete the three new paths

## what this does NOT prove (restated)
Not agency. Not feeling. Not emotion. Not self. Not autonomy. Not companion-readiness.
Not that active inference is "correct." Not that the drive generalizes beyond one toy
world. A pass is a single non-redundancy result on one axis in one environment.
