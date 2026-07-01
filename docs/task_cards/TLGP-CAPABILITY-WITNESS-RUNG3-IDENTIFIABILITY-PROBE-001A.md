# TLGP-CAPABILITY-WITNESS-RUNG3-IDENTIFIABILITY-PROBE-001A

**Status: DRAFT — requires operator authorization before implementation.**
This card authorizes NOTHING by itself. Codex must freeze a canonical design
(`*.frozen_design.json`, `_frozen_canonical_sha256` over the underscore-stripped,
sort-keys, compact JSON — same scheme as the POWERED/RERUN cards) and pass the
instrument controls (below) BEFORE reading any real-split result.

## task_id
TLGP-CAPABILITY-WITNESS-RUNG3-IDENTIFIABILITY-PROBE-001A

## research_layer
engineering implementation + mechanism-hypothesis testing. **Candidate-free, NO GPU,
NO training.** This is a *necessary-condition gate* placed BEFORE any powered rung3
learner run.

## problem_definition
Powered rung0 passed (`route_open_capability_witness_feasible`) but rung0 uses SEEN
rules (test rules == the 8 adapt/train rules). The real transfer question is rung3:
**unseen** rules (test rules ⊂ the 125 held-out `TEST_RULES`, disjoint from the 500
`TRAIN_RULES`) + unseen values `[3,4]`. Standing prior negative evidence (the
identifiability ceiling: *equal access ⇒ a fair baseline inherits the same
identifiability*) predicts rung3 may have no learner-exploitable headroom regardless
of the (now-fixed) instrument. Before spending 10-seed GPU on a rung3 learner, test
whether ANY adapt-reading agent can beat equal-access fair baselines on unseen rules.

## the_question_this_probe_answers (and the one it does NOT)
ANSWERS (candidate-free): On unseen rules, does the in-family Bayesian **ideal
observer** (probe ceiling; reads 24 adapt examples, knows the rule *family*
`effect=(Σ wᵢxᵢ + c·a) mod K`, NOT the specific held-out rule) achieve balanced
accuracy materially above the strongest **equal-access fair baseline** — with power?

- `headroom_ideal_vs_fair = ideal_unseen − fair_max_unseen`, per seed, balacc.
- ≤ ε (fair matches the ceiling) ⇒ **identifiability ceiling**: no learner can win ⇒
  close the learnability route at rung3 with NO GPU.
- LCB(headroom) > ε with guards ⇒ headroom exists ⇒ a powered rung3 learner run is
  justified (separate card).

DOES NOT ANSWER: whether a *learner* reaches the ideal on unseen rules (that is the
prereg's H0/H1 `headroom_vs_meta` question, `ideal − meta`, and needs a trained learner).
This probe is logically PRIOR to H0/H1: it only decides whether rung3 is non-degenerate
enough to be worth a learner run. A "headroom_exists" verdict is NECESSARY, NOT
SUFFICIENT, for rung3 transfer.

## current_stage
Post-powered-rung0 (formal SEEN-rule terminal banked). rung1/rung3 untested.
Instrument (retrieval model) validated on rung0 + positive controls; pooling metas
are confounded and are NOT used here (this probe uses no learner at all).

## hypothesis
H_probe: on unseen rules, `ideal_unseen − fair_max_unseen ≤ DELTA` on ≥ close_fraction_min
seeds (the identifiability ceiling holds; equal-access fair saturates the achievable
gap). The falsifier is a powered, guard-passing `LCB(headroom) > DELTA`.

**AUTHORITATIVE CORRECTION (supersedes the two lines above).** The probe is NEUTRAL and
decides WHICH wall rung3 faces: (a) `ideal ≈ fair` (`headroom ≤ DELTA`) = identifiability
ceiling → close WITHOUT GPU; (b) `ideal ≫ fair` (`LCB(headroom) > DELTA`) = task identifiable
→ the wall is LEARNABILITY → a powered rung3 learner run is REQUIRED (no candidate-free
shortcut). PRIOR ANALYSIS (verify, do NOT assume): the world is deterministic linear-mod-K
with 4 unknowns in Z_K; 24 adapt examples over-identify it and the ideal extrapolates exactly
to unseen rules AND unseen values [3,4] ⇒ branch (b) is the LIKELY outcome, and a real
graph-cache (N1 — holds only seen adapt inputs) stays near floor on the ~96%-novel queries.
The GPU-saving ceiling (a) fires ONLY if 24 adapt fails to identify unseen rules. Probe value =
verify identifiability + force the real graph-cache + record the ideal/fair reference numbers
the powered run needs — NOT a likely GPU-skip.

## system_class (bounded formal object)
- World (read-only import `src/tlgp_001a.world`, frozen): S/effect `y=(Σ_{i<D} wᵢxᵢ + c·a) mod K`,
  K=5, D=3, ACTION_CARD=5, rule_space=625, N_ADAPT=24, N_QUERY=30.
- Observation to every agent: `adapt_x, adapt_a, adapt_e(=adapt answers), query_x, query_a`.
  **Forbidden inputs to every agent: `rule_id`, `query_e`** (structural boundary, asserted in trace).
- Splits (read-only import `src/tlgp_001b_r2/splits.py`, prereg `6e61a831`):
  rung3 test rules ⊂ `TEST_RULES` (125, unseen); assert `TRAIN_RULES ∩ query_rules = ∅`.
  Unseen values `[3,4]`. Use `RUNG3_TEST_EPISODES_SEED` family; MODEL_SEEDS for the 10-seed panel.
- Agents (candidate-free, all equal-access to the SAME adapt):
  - `ideal`: TLGP-001A in-family Bayesian observer (posterior over 625 rules given adapt;
    predict query). READ-ONLY import; MUST NOT peek at rule_id. This is the ceiling; it is
    NOT a member of the fair panel.
  - fair panel (equal access): `lookup`, `count_table`, `majority`, `predict_all`,
    `no_adaptation`, and a **real graph-cache-family challenger** — implement at least one of
    `successor_map` / `transition_table` (equal adapt access). **No aliasing** (see N1 below).
- Statistic: `headroom = ideal − max(fair)` per episode → per-seed mean → 10-seed panel;
  `LCB = mean(headroom) − 2·std/√N_SEEDS`. ε = `DELTA` READ from prereg (0.1); never retuned.

## baseline (the point of the probe — fair must be CAPABLE)
Fair baselines are the challengers, and they must be as strong as possible under equal
access (the Route-C lesson: an underpowered baseline yields a false "headroom" ADMIT).
Report `fair_max` = max over the full panel INCLUDING the real graph-cache challenger.
If `fair_max ≥ ideal − ε`, the verdict is the ceiling (baseline equivalence), reported as such.

## ablation
1. **adapt-size ablation**: recompute ideal headroom at N_ADAPT ∈ {6, 12, 24}. Headroom
   should grow with adapt if the rule is identifiable-from-adapt; if headroom is flat-near-zero
   across adapt sizes, that is the ceiling (structure not recoverable from adapt at any tested size).
2. **no-adaptation ablation**: `no_adaptation` baseline (ignores adapt) must NOT match `ideal`
   (if it does, adapt is irrelevant → degenerate rung → `route_needs_world_rung_redesign`).

## instrument controls (MANDATORY — run and pass BEFORE reading the real rung3 split)
Standing policy: positive control before interpreting negatives.
- **POSITIVE control**: run the identical harness on rung0 SEEN rules (`R0_RULES`, 8). MUST
  report headroom_exists (known: ideal≈1.0, fair_max≈0.226, headroom≈0.77). If it reports
  ceiling here → instrument broken → STOP + failure_manifest.
- **NEGATIVE control**: run on a deliberately unidentifiable split (e.g., N_ADAPT=1, or query
  values never present in adapt). MUST report ceiling/inconclusive. If it reports headroom on a
  no-signal split → false-positive instrument → STOP + failure_manifest.
- **predict_all/majority guard**: `predict_all` and `majority` are in the fair panel; balacc
  (not recall) is the metric — a "separation" that is only recall with no precision must not pass
  (the Route-C separation false positive).

## trace_replay_requirement
`trace.jsonl` per episode: seed, rung/split id, rule_id (LOGGED for audit, NEVER an agent input),
assert_unseen (TRAIN_RULES∩rule=∅), adapt tensors hash, ideal per-query prediction, each fair
baseline per-query prediction, per-episode balacc for ideal + each fair, per-episode headroom.
Replay: reconstruct per-seed headroom, `fair_max`, and the verdict from `trace.jsonl` alone,
with NO future info, NO learner state, NO renderer behavior. `replay_report.json` must match
`result.json` within 1e-9.

## acceptance_gate (verdict from a FROZEN, self-tested adjudicator)
Codex writes `rung3_identifiability_adjudicator.py` (pure fn; reads ε=DELTA/close_fraction_min/
N_SEEDS from prereg `6e61a831`, verifying its canonical sha; trains nothing; imports no candidate).
Self-test must show ALL branches reachable (fail-able). Terminals:
- `route_closed_identifiability_ceiling` — `headroom ≤ ε` on ≥ close_fraction_min/N_SEEDS seeds
  (fair saturates the ceiling; learner-independent close). **This is the predicted outcome.**
- `rung3_headroom_exists_authorize_powered_learner` — `LCB(headroom) > ε` AND controls pass AND
  leakage clean AND `predict_all`/`majority` do not equal `ideal` (no trivial separation).
  Authorizes drafting a SEPARATE powered rung3 learner card. Not transfer evidence.
- `route_needs_world_rung_redesign` — `no_adaptation ≈ ideal` (adapt irrelevant) or degenerate ideal.
- `inconclusive_underpowered` — CI straddles ε at N_SEEDS, or a control did not pass cleanly.
- `invalid_leakage` — leakage detector not clean on an agent input channel.

## leakage
001A dual-target MI detector (planted + renamed + clean controls) on EVERY agent input channel,
per split; standard = `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`. Planted controls MUST be caught
(fail-able) and real channels clean (as in the powered run). `rule_id`/`query_e`/split-ids/seed-ids/
rung-labels asserted clean.

## anti_hardcoding_audit (Codex self-check + Claude re-audit)
- `ideal` is the READ-ONLY TLGP-001A observer; it must not receive/derive `rule_id`.
- unseen split genuinely disjoint (`TRAIN_RULES ∩ query_rules = ∅`), asserted per episode in trace.
- ε read from prereg, not tuned after results (freeze design + canonical sha BEFORE compute).
- graph-cache is a REAL implementation (N1), not `max(lookup,count_table)`.
- verdict is the adjudicator's computed output (clean-room reproducible from `route_decision_input`),
  not a report-header literal.
- no edit to any banked/frozen source (`retrieval_model.py 0cba9239`, `route_decision.py 0dcf3659`,
  `meta_learners.py 358d2bb2`, `src/tlgp_001b_r2/*`, `src/tlgp_001a/*`, prereg, frozen designs).

## evidence_contract
`artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG3_IDENTIFIABILITY_PROBE_001A/`:
`result.json` (incl `claim_ceiling` field), `trace.jsonl` (LFS via `**/*.jsonl`),
`baseline_comparison.json`, `ablation_report.json` (adapt-size + no-adaptation),
`control_report.json` (positive+negative), `leakage_report.json`, `replay_report.json`,
`route_decision_input.json`, `route_decision.json`, `manifest.json`
(source shas, prereg sha, frozen-design sha, split assertions). `failure_manifest.json` if any STOP.

## claim_ceiling
Bounded, candidate-free, no-GPU. Proves ONLY whether an in-family Bayesian ceiling has (or
lacks) headroom over equal-access fair baselines on unseen rules.
- A `ceiling` verdict = a **learner-independent** negative (no learner can beat equal-access fair
  on unseen rules): closes the rung3 *learnability* route without training. Still not consciousness/
  mechanism/agency/self/AGI/EGO evidence.
- A `headroom_exists` verdict = NECESSARY-not-sufficient; authorizes a powered rung3 learner run;
  proves NOTHING about any learner (incl retrieval_model) realizing it, and is not transfer evidence.
- Even a later powered rung3 pass would be no stronger than "bounded rung3 unseen-rule
  capability-witness," never mechanism/subjectivity/transfer-of-mechanism.

## stop_conditions
Positive or negative control fails; leakage planted-not-caught; ideal reads a forbidden input;
graph-cache is an alias; unseen-split assertion fails; ε tuned after results; verdict not from the
frozen self-tested adjudicator; any edit to banked/frozen source. → STOP + `failure_manifest.json`,
do NOT commit, do NOT push, do NOT add audit/review layers.

## rollback_plan
All new isolated files (`src/tlgp_capability_witness_preflight_001a/rung3_identifiability_probe.py`,
`rung3_identifiability_adjudicator.py`, the artifact dir, this card's frozen design). No banked/
frozen file is touched. Rollback = delete the new files/artifacts; nothing else is affected.

## out_of_scope (do NOT do under this card)
No GPU/training; no learner (retrieval_model or metas); no rung1; no EGO/LLM/AIRI/UI; no schema
migration; no push; no rewrite of banked artifacts; no drafting of the powered rung3 learner card
until this probe returns `rung3_headroom_exists_authorize_powered_learner`.
