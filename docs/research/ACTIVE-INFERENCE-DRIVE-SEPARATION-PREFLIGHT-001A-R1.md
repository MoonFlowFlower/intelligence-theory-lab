# ACTIVE-INFERENCE-DRIVE-SEPARATION-PREFLIGHT-001A-R1 (AIDSP-001A-R1)

**STATUS: DRAFT TASK CARD. NOT AUTHORIZED FOR EXECUTION.**
This R1 is the **operative** version and **supersedes 001A for execution** (single source
of truth — 001A retained as drafting history only, to avoid schema fragmentation).

Drafting is authorized (user, this session). The following are each FORBIDDEN until a
separate explicit authorization instruction: writing implementation code, running the
harness, producing `artifacts/`, schema changes, and any `commit` / `push` / `tag` /
remote `anchor`.

Derives vocabulary from `docs/research/ACTIVE-INFERENCE-DRIVE-AFFECT-LINEAGE-001A.md`.

---

## 0. Framing guard (binding, read first)
AIDSP is **not** "we found the correct theory." Active inference / EFE is **one candidate
mechanism family and a design language**, not a foundation and not a result. A pass of
this card means only: *the epistemic-value term produced information-seeking behavior that
a battery of simpler/trivial strategies did not reproduce, in one toy POMDP, under this
contract.* Do not let "active-inference worship" replace "correct-theory worship."

## task id
AIDSP-001A-R1

## research layer
Engineering implementation + mechanism hypothesis. NOT subjectivity / consciousness /
affect-validation / agency.

## problem definition
Test, in one tiny fully-instrumented POMDP, whether the EFE **epistemic-value** term is a
**non-redundant, causally-attributable** source of information-seeking action versus a
battery that now explicitly includes **trivial coverage strategies** (the degeneracy that
001A's `time-to-locate` metric was vulnerable to). The metric is redesigned so that brute
coverage cannot win; a **metric triviality probe runs first** and gates everything.

## current stage
Pre-implementation card repair (R1). No executor exists.

## hypothesis (pre-registered, fail-able both directions)
H1: Under uncertainty about food location resolvable by *informative cues*, the EFE agent
achieves higher **unit-cost posterior-entropy reduction (M1)** and higher **interventional
cue-usage (M2)** than every fair baseline — including exhaustive-sweep and
systematic-coverage — by margin ≥ `band`, and this advantage is **removed** by the
epistemic-ablation.
H0 (admissible negative, expected-plausible): the EFE agent ties one or more fair baselines
within `band`, OR the ablation does not change the metric. Reported as baseline
equivalence; not patched.

## environment (R1 — revised so no fixed heuristic is optimal)
Discrete POMDP gridworld, pymdp-scale:
- Hidden state: food location, **relocated each episode**.
- **Informative cues**: observations are a *noisy function of the hidden state* (e.g., a
  noisy distance/direction signal), NOT the hidden state itself. An agent that *integrates
  cues over time* (inference) can localize faster **per cost** than blind coverage. Cues
  must be partial and noisy (anti-leakage: never a direct food label).
- Interoceptive variable "energy" with setpoint; food restores energy.
- Challenger states: **dark-room** (predictable, no-info, no-food) and **noisy-TV**
  (high-entropy, uninformative observations).
- REQUIREMENT: the world must be constructed so that **no fixed cue-following or coverage
  heuristic is optimal** (e.g., multiple cues of differing reliability, or an
  explore-vs-exploit tension). This requirement is **verified by the triviality probe
  (§ metric triviality probe)** — if the probe cannot be passed, the world is too weak →
  STOP (`invalid_metric_degenerate`).

## baselines (mandatory; verdict decided against these)
1. **homeostatic-RL** (Keramati–Gutkin: reward = drive reduction; tabular Q) — primary
   drive challenger; expected to TIE on drive-satisfaction.
2. **behavior-tree / utility-softmax** (hand-coded thresholds + temperature).
3. **random policy**.
4. **observation-only lookup** (fixed map on current obs; no hidden-state inference).
5. **count-based exploration** RL.
6. **exhaustive-sweep** (deterministic full-coverage traversal). *(R1 addition)*
7. **systematic-coverage** (lawnmower / spiral heuristic, cue-ignoring). *(R1 addition)*

Architectural differences between agents (model-based vs model-free) are LEGITIMATE and
declared; they are NOT access-parity violations (see access parity).

## access parity (R1 addition — binding)
Candidate and ALL baselines share, byte-for-byte: identical environment instances,
identical observation interface (same cue access, same noise), identical action space,
identical per-episode step budget, identical seed set, and **no privileged labels** (none
receives food / dark-room / noisy-TV identity). Parity is over **observations / actions /
budget / seeds**, not over internal architecture. Any asymmetry must be explicitly logged
and justified in `baseline_comparison.json`; an unlogged asymmetry → `invalid`.

## primary metric (R1 — degeneracy-safe; formulas FROZEN here)
Computed on environment ground truth / an **independent** posterior estimator, never on the
candidate's own outputs (anti-tautology).

- **M1 — unit-cost posterior-entropy reduction.**
  `M1 = Σ_t [ H(p_t(food)) − H(p_{t+1}(food)) ] / cost_t`, where `H` is Shannon entropy of
  the (independent estimator's) posterior over food location given observations up to `t`,
  and `cost_t` is the per-step action cost. Rewards *targeted* information acquisition;
  brute sweep reduces `H` only at high cumulative cost → low M1.
- **M2 — interventional cue-usage.**
  Run each agent twice on matched seeds: cue-present vs **cue-ablated** (cue replaced by
  noise). `M2 = divergence(π_present , π_ablated)` over the trajectory/action distribution
  (e.g., mean per-state action-distribution KL, or normalized trajectory edit distance).
  A blind/coverage agent is invariant to cue ablation → M2 ≈ 0; an inference agent's
  behavior shifts → M2 > 0. (Interventional — Route C lesson: decode ≠ use.)
- Numeric constants (grid dims, cue noise, step budget, seed family, `band`, ablation
  margin `δ`) are committed in `result.json.preregistration` BEFORE the first candidate
  run and are immutable thereafter.

## metric triviality probe (R1 — RUNS FIRST; gates everything)
Before ANY candidate evaluation, run a trivial-strategy battery on M1 and M2:
{ exhaustive-sweep, systematic-coverage, random-walk, cue-ignoring-greedy,
posterior-uniform / predict-all-locations }.
- **`band` is DERIVED, not tuned:** `band := max(M1 over trivial battery) + δ`, with `δ`
  fixed in this card. The candidate must beat the *best trivial strategy* by `δ`. This
  removes post-hoc threshold tuning.
- If any trivial strategy attains high M1 or non-trivial M2 (i.e., the metric is gameable
  by brute coverage), the metric/world is **degenerate** → verdict
  `invalid_metric_degenerate`, STOP, redesign. Do NOT proceed to candidate claims.

## ablation (causal control)
- **epistemic-ablation**: EFE with the epistemic-value term removed (pragmatic-only). If
  removing it does NOT reduce M1/M2, the "curiosity drives it" claim is FALSE → report.
- **no-transition ablation**: action does not condition the transition, to confirm
  action-conditioning is load-bearing.

## challenger controls (must pass)
dark-room dwell-time and noisy-TV dwell-time must be ≤ random/homeostatic-RL levels. Being
trapped → `known_failure_mode_reproduced`.

## trace / replay requirement
`trace.jsonl` per step: t, belief-before-action, EFE per policy (epistemic and pragmatic
components separately), selected action, predicted obs, actual obs, prediction error,
updated belief, interoceptive state, cue value, challenger-state flag, cost. Verdict must
replay from trace alone — no hidden future info, no renderer-only behavior.

## verdict set (R1 — weak_admit CLOSED)
- `admit_non_redundant`: beats ALL fair baselines (1–7) on M1 by ≥ `band` AND shows M2 ≥
  pre-registered cue-usage threshold AND passes both challenger controls AND
  epistemic-ablation removes the advantage AND replays.
- `baseline_equivalence_or_no_separation`: ties any fair baseline within `band`, or
  ablation does not matter. (admissible negative)
- `known_failure_mode_reproduced`: dark-room or noisy-TV traps the candidate.
- `invalid_metric_degenerate`: triviality probe fails (a trivial strategy wins).
- `invalid_due_to_leakage_or_contract_failure`: positive control not caught, parity
  violation unlogged, provenance missing, or secret present.

**`weak_admit`: CLOSED / DEFERRED in R1.** It is NOT in the active verdict set, to prevent
gate fragmentation (a "ties count-based but principled" bucket would become a face-saving
escape hatch — especially dangerous combined with any residual metric degeneracy). It may
be opened only by a future card that hard-defines it with a fail-able boundary AND only
after `invalid_metric_degenerate` has been cleared. Until then, tie = baseline equivalence.

## leakage positive controls (R1 — the scanner must be fail-able)
Plant ≥ 2 deliberate leaks and require the harness to CATCH and BLOCK each:
(i) a food-location oracle wired into the candidate's observation;
(ii) a privileged dark-room/noisy-TV label.
If the leakage scanner does NOT flag a planted leak → the scanner is non-fail-able →
`invalid_due_to_leakage_or_contract_failure`, STOP. (Closes the lab's recurring
"leakage scanner not fail-able" family.)

## PAT / secret stop condition (R1 — standing BLOCK)
Before any run/commit, scan the run code path for hardcoded secrets/tokens (notably
`scripts/push.*` PAT). If any secret is present → STOP, BLOCK; no run, no commit, no push,
no tag, no anchor until the secret is rotated/removed. This is a hard stop, not a field.

## claim ceiling (unchanged)
A pass = "the EFE epistemic-value term produced information-seeking behavior (higher M1 and
interventional M2) not reproduced by random / behavior-tree / homeostatic-RL / count-based
/ observation-only / exhaustive-sweep / systematic-coverage, in one toy POMDP, with the
advantage causally removed by epistemic-ablation, fully replayable." NOTHING MORE. Does NOT
evidence agency, autonomy, wanting-as-felt, emotion, self, companion-readiness, that EFE is
"correct", or that the drive scales/transfers. A negative is bounded-negative for this
world only.

## anti-hardcoding audit (predeclared; checked before AND after)
- [ ] M1/M2 computed on ground truth / independent estimator, never candidate outputs
- [ ] `band` derived from triviality probe (`max trivial + δ`), δ fixed pre-run, never tuned
- [ ] triviality probe run and passed BEFORE any candidate claim
- [ ] food / dark-room / noisy-TV / cue-mapping identity NOT leaked into any agent's model
- [ ] epistemic-ablation is genuinely fail-able (can flip the verdict)
- [ ] access parity holds (obs/action/budget/seed identical; asymmetries logged)
- [ ] homeostatic-RL is a real fitted/learning baseline, not a crippled stub
- [ ] separation survives a second seed family (multi-seed)
- [ ] ≥2 leakage positive controls planted AND caught
- [ ] verdict computed from artifacts, not a report-header literal

## stop conditions (consolidated)
- triviality probe fails → `invalid_metric_degenerate`, STOP.
- candidate ties any fair baseline within `band` on M1 → STOP, baseline equivalence (do
  NOT add factors to force a win).
- dark-room / noisy-TV traps candidate → STOP, known failure reproduced.
- any planted leak not caught → STOP, invalid.
- secret present in run path → STOP, BLOCK.
- pymdp cannot express the env faithfully → STOP, tooling gap (no weaker-env substitution).
- any anti-hardcoding box fails → STOP, report.

## rollback plan
All new code isolated:
- `src/aidsp_001a_r1/` (new), `tests/test_aidsp_001a_r1.py` (new),
  `artifacts/AIDSP-001A-R1/` (new).
Rollback = delete those three paths. NO edits to existing src, contracts, schemas, prior
artifacts, or push scripts.

## evidence contract (artifacts/AIDSP-001A-R1/ — on a future authorized run)
- result.json (preregistration block w/ frozen numeric constants + claim_ceiling + computed
  verdict)
- trace.jsonl
- baseline_comparison.json (incl. logged architectural asymmetries)
- ablation_report.json
- triviality_probe_report.json *(gates the run)*
- positive_control_report.json *(planted leaks + catches)*
- replay_report.json
- failure_manifest.json (if any stop triggers)

## HYGIENE fields (necessary, NOT sufficient — completing these does NOT establish validity)
Per prior lab evidence, "complete fields" with a degenerate metric / unfair baseline is the
historical false-pass route. These are anti-fabrication hygiene only; the binding safety is
the triviality probe + parity + positive controls above.
- mainline target: none
- enabled requirement: isolated CLI harness only
- real-trigger requirement: local run → artifacts only; no runtime / mainline trigger
- Auto-Remote-Anchor: forbidden
- provenance: each score records `producer_function`, `inputs`, `run_id`,
  `seed/episode_id`, `aggregation`, `code_path_hash`

## pre-implementation plan (for the FUTURE authorized run only)
- files expected to change: `src/aidsp_001a_r1/*`, `tests/test_aidsp_001a_r1.py`,
  `artifacts/AIDSP-001A-R1/*` (all new)
- files forbidden to change: everything else (existing src, all contracts/docs, all prior
  artifacts, all schemas, push scripts)
- commands expected to run: create venv; `pip install pymdp` (or vendored); run triviality
  probe; `pytest`; run harness to emit artifacts. **No** git commit/push/tag/anchor.
- rollback: delete the three new paths

## what this does NOT prove (restated)
Not agency. Not feeling. Not emotion. Not self. Not autonomy. Not companion-readiness. Not
that active inference is "correct." Not that the drive generalizes beyond one toy world. A
pass is a single non-redundancy result on one information-seeking axis in one environment.
