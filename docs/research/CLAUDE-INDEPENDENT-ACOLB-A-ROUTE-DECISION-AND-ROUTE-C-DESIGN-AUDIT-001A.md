# CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A

Independent route decision + next-surface design audit.
This record is **not** implementation, **not** a Gate run, **not** mechanism-validity
evidence, **not** remote-anchor authorization, and **not** a Codex implementation card.

Role: same-agent independent auditor / red-team reviewer (CLAUDE.md Role 001).
Layer: `route-governance + mechanism-surface design only`.

---

## 0. Verdict (headline)

**Next action = A: close the current ACOLB-A surface and draft a Route C *hostile design blueprint* — conditioned on Route C being treated as the ACSB-family re-entry card the prior closure already demands, with the ACSB re-entry gates bound as mandatory preflight STOP gates.**

- ACOLB-A: **close current surface, preserve as bounded local negative (fair-baseline / amortization saturation) evidence, stop A repair, no remote anchor.**
- Route C: **a structurally stronger separation principle than ACOLB-A, but unproven, and it re-enters a surface family (ACSB) with a documented multi-round collapse history. It earns the right to implement only by passing a hostile preflight first. The blueprint's job is to try to kill Route C on paper before any code.**

No positive mechanism evidence is claimed. No claim that Route C will work.

---

## 1. Inherited state readback (grounded in artifacts, not self-report)

Read directly from `artifacts/acolb_001a/` and `src/acolb_001a/` (not from the handoff summary):

| Fact | Value | Source |
|---|---|---|
| verdict | `saturated_close` | `result.json`, `failure_manifest.json` |
| mechanism_claim_admitted | `false` | `result.json` |
| stop condition | `blocked_by_saturated_distribution` | `failure_manifest.json` |
| candidate OOD | 0.9445271267992709 | `headroom_preflight.json` |
| fair amortized OOD (decay 0.35) | 0.9298601357421954 | `headroom_preflight.json`, `baseline_comparison.json` |
| margin | 0.014666991057075474 < OOD_BAND 0.05 | `headroom_preflight.json` |
| headroom | 0.07013986425780461 ≤ EQUIV_BAND 0.08 | `headroom_preflight.json` |
| OOD seeds (N) | `[5001, 5002, 5003]` → **N = 3** | `config.py SEED_FAMILIES` |
| drift family | single deterministic linear `(0.16·t, −0.11·t)`, `ood` regime only | `generator.py _drift` |
| claim ceiling (recorded) | "bounded local mechanism-discrimination evidence on this constructed generator/seeds/thresholds only…" | `claim_ceiling.txt` |

Two structural facts the handoff summary did **not** state, but which the artifacts make decisive:

**(1.a) The candidate and the fair baseline are the same estimator.**
`candidate.py` is an online recursive Bayesian/Kalman update with a forgetting factor (covariance inflation `cov/decay` each step), O(d²) state, action-conditioned prediction-error correction. `amortized_seq.py` is a batch weighted-least-squares fit with `decay**age` weighting over the same probe sequence. On a fixed 10-probe, 2-D linear-Gaussian episode these are **algebraically the same discounted-least-squares estimator**. The online recursion buys no information the batch reweighting lacks. The equivalence is structural, not a sampling coincidence.

**(1.b) Equivalence is robust across the whole legal decay grid, not a knife-edge.**
`fair_baseline_sensitivity.json` already swept every legal decay. `baseline_equivalent: true` at all five, and the margin *shrinks off the candidate's own operating point*:

| decay | amortized OOD | candidate OOD | margin | baseline_equivalent |
|---|---|---|---|---|
| 0.35 | 0.92986 | 0.94453 | **0.01467** | true |
| 0.55 | 0.91565 | 0.92470 | 0.00906 | true |
| 0.75 | 0.87049 | 0.87520 | 0.00471 | true |
| 0.90 | 0.81970 | 0.82176 | 0.00207 | true |
| 1.00 | 0.78576 | 0.78659 | 0.00083 | true |

The largest margin (0.0147) is at the candidate's hand-picked decay and is still < ⅓ of OOD_BAND. The fair amortized decay was selected on a disjoint `validation` family (`2001–2003`) by a drift-aware rule — fair, no OOD-test oracle.

**(1.c) The candidate already beats the entire graph-cache / lookup / memory challenger family decisively.**
`baseline_comparison.json` panel OOD scores: graph_lookup 0.568, transition_table 0.561, successor_map 0.246, count_table 0.561, fsm_planner 0.563, episodic_traversal 0.571, NN 0.568, factorized_lookup 0.731, exact_key_memory 0.543, no_update 0.543, parametric_frozen 0.571, partial_key_memory 0.568, sequence_imitation 0.465 — all ≪ amortized_seq 0.930. So the candidate is **not** a disguised lookup/graph-cache. Its *only* equivalent is the fair amortized sequential estimator.

Precise diagnosis: the candidate's marginal value **over precomputation** is null. It is not equivalent to memory baselines; it is equivalent to *amortizing its own update rule*.

Git note: in-sandbox `git` plumbing is in the known-broken FUSE state (empty output). The inherited HEAD `bb65008…` was not independently re-verified from the object store; the artifact files above corroborate the inherited result and are sufficient for a **design** decision. This is a non-blocking limitation explicitly recorded.

---

## 2. Output 1 — ACOLB-A route decision (attack the closure first)

### 2.1 The strongest objection (steel-manned)

> ACOLB-A used only N = 3 seeds and one drift family. A larger seed set, or a different drift strength/shape, might push the candidate past the band and show non-equivalence. Closing now risks discarding a mechanism that the test was simply too weak to detect.

This is the correct objection to lead with, and the N = 3 part is *literally* true: with three OOD seeds you cannot put a meaningful confidence interval on a 0.0147 margin. Taken alone, the result is "no separation detected at N = 3," not "proven equivalent." That distinction is real and must constrain the claim (§2.3).

### 2.2 Why the objection does **not** justify more ACOLB-A work

Three independent reasons, in decreasing order of strength:

**(a) The saturation is algebraic, not statistical.** Per §1.a, candidate ≈ discounted batch least squares. No N and no drift *strength* changes that identity. More seeds tighten the CI around a margin that is structurally near-zero — they make equivalence *more* likely to be confirmed, not less. N = 3 is therefore not the load-bearing weakness; it is a side issue relative to the structural fact.

**(b) Drift *strength* is already absorbed by fair decay selection.** The drift is deterministic-linear, the friendliest possible case for a fixed forgetting factor. Scaling the drift up just makes both estimators pick a smaller decay; the fair baseline is *allowed* drift-aware decay selection (on the disjoint validation family), so it re-tracks any drift magnitude the candidate can. The decay-grid sweep (§1.b) already shows equivalence holds across the full legal operating range. Stronger drift moves both curves down together; it does not open a gap.

**(c) The only thing that could open a gap is a *different separation principle*, i.e. a different surface — not more A.** To make online updating beat amortization you need information that is *not amortizable*: an environment where the optimal answer depends on something a precomputed schedule structurally cannot capture (e.g. drift whose *rate* is itself non-stationary and unlearnable from validation, or — more cleanly — where the agent's own actions change which data it can obtain). Constructing such a generator *after* seeing the null, and searching drift shapes until the margin crosses 0.05, is precisely the forbidden post-hoc generator/threshold tuning. It is garden-of-forking-paths p-hacking, not robustness.

So the objection, even granting its true premise (N = 3 is weak), points **away** from A, not toward it: the productive response to "amortization saturates the candidate" is a surface where amortization is *structurally impossible*, which is a new surface (Route C), not a bigger A sweep.

### 2.3 What the objection *does* legitimately buy

A claim-ceiling limiter, which I adopt: the ACOLB-A negative is **"no detectable mechanism advantage over a fair amortized baseline on this constructed generator, seeds, and thresholds at N = 3,"** *not* "proven equivalent in general." The existing `claim_ceiling.txt` already says exactly this; no strengthening is warranted, and (per contract) none is permitted.

### 2.4 The one legitimate "more-A" action — considered and rejected

There exists a non-p-hacking version of "one more probe": a *single, pre-registered, higher-N equivalence-confirmation* run with **frozen** generator, drift, decay grid, and thresholds, whose only possible outcomes are "equivalence confirmed tighter" or "we were wrong." That is not pass-seeking. I still reject it, because: (i) it tightens a CI on a result already structurally inside the band (low information), (ii) the task forbids further A repair and post-result tuning, and the spirit is to stop poking A, and (iii) opportunity cost — the same effort spent on Route C design has far higher expected value. I record it only to show the line between legitimate confirmation and p-hacking was drawn deliberately, not by reflex.

### 2.5 ACOLB-A decision

- **Close** the current ACOLB-A surface.
- **Preserve** `bb65008…` + `artifacts/acolb_001a/` as bounded local negative (fair-baseline / amortization saturation) evidence. Do not rewrite, do not patch the null into a pass.
- **Stop** A repair. No generator/drift/threshold tuning.
- **No remote anchor** (consistent with prior ACP-BV / ACOLB local-only decisions; no stable-boundary argument is made here, so none is authorized).
- Add a one-line decision-log entry mirroring the ACP-BV closure format.

This matches the inherited verdict `accept_for_local_commit_as_negative_acolb_fair_baseline_saturation_evidence`; the audit confirms it and supplies the structural reason (1.a) the handoff omitted.

---

## 3. Prior negative evidence that governs Route C (required citation)

Per the operating contract ("every successor task must search and cite relevant prior negative evidence before proposing a new gate/bridge/implementation"), Route C cannot be treated as a fresh idea. **Route C = "self-boundary via interventional identifiability under confounding" is a re-entry into the `action_conditioned_self_boundary` (ACSB) surface family**, which is already downgraded and sealed.

Governing record: `docs/research/ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A.md`
(verdict `preserve_acsb_current_route_downgrade_closure_001a_pass`; boundary commit `d5b4b92…`).

Key inherited facts:

- **Collapse mode (decisive):** ACSB 001D collapsed into an *oracle-minus-oracle constructive identity artifact*. `full_reference`, `fair_capacity_disabled_reference`, the "learned" MLP, and the observation-only probe all reduced to the same target path `_target_from_observation = phase_bit XOR action_bit`, where **both bits are present in `legal_observation`**. Because the target was computable from same-step legal observation, observation-only = oracle, everything tied `1.0 / 1.0 / 0.0`, and the "negative evidence" was an artifact, not a falsification.
- **Status:** ACSB is **downgraded, not mechanism-falsified.** "A clean ACSB harness might or might not show a positive margin." 001B/001C/001D are preserved as *invalid-harness / hygiene lessons*, not mechanism-negative evidence.
- **Anti-Zeno warning:** "The current route has repeatedly collapsed into oracle, lookup, boundary-inert, or non-causal surfaces. Continuing immediate ACSB repairs would likely produce more governance artifacts rather than discriminative mechanism evidence."
- **Re-entry boundary (predeclared contract):** future re-entry requires "a separate route-decision card for a **materially different surface**… [that] make[s] hard preflight gates explicit before any implementation." The closure lists those gates (target not computable from same-step legal observation; target-generator unreachable by call-graph/AST; a no-boundary learner that genuinely consumes train data; empty-train + label-shuffle positive controls; reference output causally depends on boundary memory; boundary-memory mutation changes behavior; capacity-disabled intervention causes behavior difference or blocks; replay recomputes from serialized boundary state not same-step observation; provenance proves non-oracle call graph; strongest fair baseline independent and not feature-impoverished; positive controls prove scanners fire).

**Implication for this audit:** Route C's blueprint *is* the "separate route-decision card for a materially different surface" the closure requires. Its preflight (§6) must bind those re-entry gates. Drafting Route C as if ACSB never happened would itself violate the contract.

Wider lab context (meta-signal, stated as inference not fact): the lab's recent surfaces — Gate1 `graph_cache_collapse`, RESIDUE-001A, ACSB 001B/C/D, ACP-BV 001A/001B baseline saturation, ACOLB-A amortization saturation — have all ended in saturation or oracle/leakage collapse. That is a run of closures. It does **not** prove the paradigm cannot yield a positive (each is a bounded negative on a specific constructed surface), but it raises the prior that the fair-baseline panel will saturate any *amortizable* constructed surface. Route C is interesting precisely because its separation principle is non-amortizable in a way the prior surfaces were not. This meta-signal also argues for a hard pre-registered stop on Route C (§7) so it does not become the next entry in the run.

---

## 4. Output 2 — Route C evaluation

Route C candidate mechanism: the agent must use **its own interventions** to infer which observation channels are action-coupled / self-controlled under confounding. Observation-only baselines should fail by **non-identifiability**; the interventional candidate can break the confound.

### 4.1 Separation principle: causal non-identifiability vs OOD drift

- ACOLB-A's intended separation source was **OOD drift** — online adaptation vs a precomputed schedule. Failure mode: **amortization** (a fixed schedule matches the online learner because the drift was learnable/precomputable). Confirmed saturated.
- Route C's separation source is **interventional identifiability under confounding** — an *information-theoretic* gap, not a learning-rate gap. Under genuine confounding, observational data is provably insufficient to recover the causal structure (do-calculus: `P(Y|X) ≠ P(Y|do(X))`). The agent's own do-operations carry information that is **absent from any observational dataset, at any N**.

### 4.2 Why this is structurally stronger than ACOLB-A

The amortization attack that killed A does not directly transfer. You cannot precompute your way out of non-identifiability from observational data, because the missing information is interventional *by construction*. An amortized observational baseline — however large its training set or however clever its schedule — still faces a non-identifiable problem. So the "fair baseline catches up" mechanism that saturated A is, in principle, blocked. **This is the single strongest point in Route C's favor.**

### 4.3 Why Route C is the correct *structural response to the ACSB collapse*

ACSB died because the self/non-self target was **decodable from same-step observation** (`phase_bit XOR action_bit`). Route C's entire premise — "observation-only must fail by non-identifiability" — is the direct structural negation of that failure mode. If the confounding is genuine, observation-only *cannot* be an oracle, so the `1.0/1.0/0.0` constructive-identity artifact is structurally prevented. Route C is therefore not a re-skin of ACSB repair; it changes the *reason* observation-only fails from "we hope the scanner catches leakage" to "the information is provably not there." That is a materially different surface in the sense the closure demands.

### 4.4 The dominant caveats (where Route C dies if undisciplined)

Two prior failure modes reappear, fused:

- **Interventional-baseline saturation (the A failure mode, reborn).** The candidate's claimed advantage is "uses its own interventions." But a *non-candidate* baseline that also receives interventional data — a CI test, a do-regression, a contingency table over interventional samples — may identify the self-set just as well. If observation-only fails but *any* fair interventional method succeeds, the candidate's "self-boundary mechanism" collapses to "interventional data + standard causal discovery," and you are back at baseline equivalence — exactly ACOLB-A, one layer up. **Showing `interventional > observational` proves causal discovery works; it does NOT prove the candidate mechanism is non-trivial.** The separation that matters is `candidate − max(fair interventional baseline)`, not `interventional − observational`.
- **Observation-decodability (the ACSB failure mode, reborn).** If the confounding is cosmetic — any same-step legal-observation path leaks the self-set — observation-only becomes an oracle again and the whole surface is the `phase_bit XOR action_bit` artifact in new clothes.

### 4.5 Verdict on "more promising"

**Conditionally yes, on the separation *principle*; unproven as a *result*.** Route C's non-identifiability framing is structurally stronger than ACOLB-A's drift framing (amortization-resistant) and is the correct structural answer to the ACSB collapse. But it inherits the full ITL collapse-family risk set, with two dominant, *fused* risks (4.4) that have each already killed a surface in this lab. Net: Route C is a **more promising surface to design**, not a more promising outcome. The promise is real **only if** the preflight forces `candidate vs fair-interventional` separation *and* proves genuine non-identifiability — both *before* implementation. Per forbidden list: no claim that Route C will work.

---

## 5. Output 3 — Strongest risks for Route C

Each with the concrete failure manifestation and the detection that must be wired as a positive control. (Required ten, plus four ITL-canon additions.)

1. **Schema alias leakage through channel identity.** Self channels identifiable by index/name/dtype/range/position without intervention. *Manifests:* candidate (or a name/index-only attacker) succeeds with interventions disabled. *Detect:* schema-only attacker panel must score ≤ ceiling.
2. **Hidden self-set leakage.** Ground-truth self-set readable via observation vector structure, intervention-API return shape, or replay state. *Manifests:* candidate ≈ oracle; no-intervention ablation does not hurt. *Detect:* input-contract audit + oracle-injection positive control that proves the channel *would* be exploitable, then confirm it is closed on the real path.
3. **Intervention labels leaking through names/ordering.** The do-action targeting a self channel is named/ordered so its target is inferable without observing effects. *Manifests:* candidate maps action→channel by label, not by effect. *Detect:* action/channel names randomized per episode; label-only attacker ≤ ceiling.
4. **Observation-only baseline accidentally getting interventional data.** The "observational" dataset was collected under an intervening policy and carries do-information. *Manifests:* obs-only baseline > ceiling → non-identifiability premise void → whole surface void. *Detect:* premise gate (§6.1); audit data-collection policy is purely passive.
5. **Interventional baseline saturating the candidate.** A fair interventional baseline matches the candidate. *Manifests:* `candidate − max(fair interventional baseline) < band` → baseline equivalence (the A outcome). *Detect:* mandatory fair interventional panel (§6.3); this is the predicted null and an honest STOP, not a repair target.
6. **Candidate hardcoding channel IDs.** Baked-in "channel k is self." *Manifests:* candidate fails under per-episode channel permutation. *Detect:* permutation mandatory; hardcode probe.
7. **Generator making self-boundary too directly observable.** No real confounding; observational correlation recovers the self-set. *Manifests:* obs-only > ceiling (same as #4, generator-side). *Detect:* confounder-strength premise gate + obs-only ceiling control. Confounder strength must be *pre-registered*, never tuned to make obs fail.
8. **Fake intervention effects from deterministic schema.** Interventions produce fixed, memorizable effects. *Manifests:* a lookup/memorization baseline matches the candidate; candidate succeeds without inference. *Detect:* per-episode remapping + stochastic effects; lookup baseline in the panel must not reach candidate.
9. **Replay becoming a stored hash.** "Replay" re-emits a stored result rather than recomputing behavior from serialized self-boundary belief. *Manifests:* replay passes even when the serialized belief is corrupted/zeroed. *Detect:* replay must recompute *and* must change under belief corruption (anti-stored-hash control).
10. **Ablations not rerun.** Ablation reports stale/literal/copied. *Manifests:* `ablation_report.json` identical across runs; no-intervention ablation reported as collapsing without being executed. *Detect:* freshly recomputed ablations with run-stamped provenance; CI asserts non-identical, freshly produced values.

ITL-canon additions (each has already bitten a prior surface):

11. **Non-fail-able gate fields.** The success metric is tautological (e.g. `candidate == label-generating expression`, as in the ACSB `1.0` artifact and ACP-BV cross-family `candidate==label`). *Detect:* every gate must ship a demonstrated negative control that actually returns *fail*; a gate that cannot logically fail is void.
12. **Parity violation.** Candidate and the fair interventional baseline given *different information access*, so any "win" is access asymmetry, not mechanism (ACP-BV social: same-access faithful baseline tied at 1.0 → parity violation). *Detect:* pre-registered access-parity contract; candidate and the strongest fair baseline must have identical interventional access budgets.
13. **Post-hoc confounder/threshold tuning.** Confounder strength, ceiling, band, or oracle-margin adjusted after seeing results to manufacture obs-failure or candidate-pass. *Detect:* `THRESHOLDS_FROZEN_BEFORE_RUN` recorded in the card with hashes; any change voids the run.
14. **Provenance / source-hash gap.** No cryptographic link between the recorded run and the real candidate/generator source (this is how prior bypasses — const+echo, stub-fed harness — were caught). *Detect:* source-hash of candidate, generator, baselines, evaluator embedded in artifacts and checked.

---

## 6. Output 4 — Required preflight STOP gates for Route C

Minimum gates before *any* Codex implementation. Each is a hard STOP (fail ⇒ Route C does not get implemented; that is an acceptable, contract-preferred outcome). Bracketed tags map to the ACSB re-entry boundary conditions this gate discharges.

**6.1 Non-identifiability premise gate.** Observation-only baseline must be **at or below a pre-registered ceiling** (e.g. chance = 1/C for C channels, or a defined low bound) on the confounded generator. If obs-only > ceiling ⇒ generator does not instantiate non-identifiability ⇒ STOP (surface void). *[discharges: "target not computable from same-step legal observation alone" — the exact ACSB killer.]*

**6.2 Interventional headroom gate.** A full-access interventional **oracle** must beat obs-only by margin > band. If oracle ≈ obs-only ⇒ interventions add nothing on this generator ⇒ STOP (no headroom for any mechanism to exist).

**6.3 Fair interventional baseline panel (load-bearing anti-saturation gate).** Pre-declare the panel: CI-test causal discovery, do-regression, contingency/count table over interventional samples, nearest-neighbor on intervention-effect vectors, FSM/lookup over (action, channel) effects. Candidate must beat **the best** of these by > band. If `candidate ≤ max(fair interventional baseline)` ⇒ **baseline equivalence**, recorded as the predicted null and an honest STOP — **not** a repair target. *[discharges: "strongest fair baseline independent and not feature-impoverished."]* This gate is what ACOLB-A taught: the comparison must be candidate-vs-fair-interventional, never interventional-vs-observational.

**6.4 Candidate input-contract gate (no hidden self-set).** Pre-declare the candidate's inputs: observations + its own intervention API + intervention outcomes — **not** the ground-truth self-set, **not** confounder values. Ship an oracle-injection positive control proving the self-set channel *would* be exploitable if present, then confirm the real path has it closed. *[discharges: "no-boundary learner must not call target generator / oracle / evaluator-only fields / answer alias."]*

**6.5 Channel name/order randomization gate.** Mandatory per-episode permutation of channel indices and any names; candidate sees only permuted handles. Name-only / order-only attacker must score ≤ ceiling. *[discharges: schema-alias + label-leakage re-entry conditions.]*

**6.6 Schema-alias leakage positive-control battery.** A panel of attackers using *only* schema features (dtype, range, index, name, position) with interventions disabled — all must fail (≤ ceiling). Any pass ⇒ leakage ⇒ STOP. *[discharges: "positive controls must prove scanners fire."]*

**6.7 No-intervention ablation must collapse.** Candidate with the intervention channel disabled (observations only) must drop to the obs-only ceiling. If it still succeeds ⇒ it is not using interventions ⇒ mechanism void ⇒ STOP. Must be **freshly rerun**, artifact `ablation_report.json`. *[discharges: "capacity-disabled intervention must cause behavior difference or block."]*

**6.8 Shuffled action→channel mapping must collapse.** Permute which action affects which channel (break true coupling) while keeping intervention machinery active. Candidate must collapse to ceiling. Survival ⇒ it reads the answer elsewhere (leakage) ⇒ STOP. This is the causal-faithfulness gate. *[discharges: "reference output causally depends on boundary memory; boundary mutation changes behavior."]*

**6.9 Replay-from-serialized-belief gate.** Serialize the candidate's self-boundary belief, reload, recompute downstream behavior; must match within tolerance **and** must change when the serialized belief is corrupted (anti-stored-hash control). Replay passing on corrupted belief ⇒ stored hash ⇒ STOP. *[discharges: "replay must recompute from serialized boundary state, not same-step legal observation."]*

**6.10 Governance gates (mandatory, not deferrable — these recur as defects across the lab).**
- **Fail-able fields:** every gate ships a demonstrated failing negative control (closes the recurring "non-fail-able field").
- **Access parity:** pre-registered identical interventional access budget for candidate and strongest fair baseline (closes parity violations).
- **Frozen thresholds:** ceiling/band/oracle-margin/confounder-strength fixed and hashed before any candidate run; `THRESHOLDS_FROZEN_BEFORE_RUN=true` recorded.
- **Source-hash provenance:** candidate/generator/baseline/evaluator source hashes embedded in artifacts and checked (closes the const+echo / stub-fed-harness bypass class).
- **Truth isolation:** ground-truth self-set seeds disjoint from any seed the candidate/baselines observe (mirrors ACOLB drift_val ⟂ ood_test).

**Preflight admission rule:** Codex implementation may begin **only** if 6.1, 6.2, 6.3 are constructible (premise holds, headroom exists, a fair panel is defined and beatable in principle) **and** 6.4–6.10 are specified with demonstrated failing negative controls. If 6.1 or 6.2 cannot be met, Route C **dies at design** — and that is a clean, contract-preferred negative, not a failure to be repaired.

---

## 7. Output 5 — Next action decision

Using the decision structure:

**Conclusion.** **A — Close ACOLB-A; draft the Route C hostile design blueprint as the ACSB re-entry card, with §6 bound as mandatory preflight STOP gates.** Not B, not C-as-primary.

**Why.**
- *Reject B (one more bounded ACOLB-A probe):* mostly the forbidden p-hacking; the only legitimate version (frozen higher-N equivalence confirmation) is low-information against a structurally algebraic saturation and has worse opportunity cost than Route C design (§2.2, §2.4).
- *Reject C-as-primary (stop mechanism dev, repair governance/tooling):* the recurring defects (non-fail-able fields, whitelist escape, provenance gaps) are real and *systemic*, but they are non-blocking for *design* and are better discharged **inside** Route C's preflight (§6.10) as first-class STOP gates than as a separate governance sprint that produces no new mechanism evidence. A pure governance pivot now would itself be an anti-Zeno move (more governance artifacts, no surface progress).
- *Choose A, conditioned:* Route C is the strongest available separation principle (amortization-resistant, §4.2) and the correct structural answer to the ACSB collapse (§4.3). The blueprint is the contractually-required re-entry card. Drafting a *hostile* blueprint is pure design work, produces no mechanism claim, and its honest success criterion is "can Route C even be constructed to pass §6 on paper?" If it cannot, A terminates Route C cheaply at design — the best possible outcome short of a positive.

**Key unknowns.** (i) Whether a generator can instantiate *genuine* non-identifiability (6.1) without leaking the self-set through same-step observation. (ii) Whether, once non-identifiability holds, a fair interventional baseline (6.3) saturates the candidate anyway — i.e. whether the candidate adds anything over standard interventional causal discovery. These two are the crux; both are currently **unknown**.

**Best solution inside the current framing.** A, as scoped: blueprint + §6 preflight gates, no implementation until the gates are themselves reviewed.

**Better framing outside the current framing.** The lab's run of saturation/collapse closures (§3) suggests the deciding question is not "which surface" but **"is the fair-baseline-discrimination paradigm able to ever certify a *non-amortizable* mechanism, or will the fair panel saturate everything constructible?"** Route C is the cleanest test of that meta-question precisely because non-identifiability is the one regime where a fair baseline *provably* lacks the information. So Route C doubles as a probe of the paradigm itself. If Route C also saturates under a genuinely fair interventional panel, that is strong evidence to reconsider the paradigm (escalate weight on C) rather than design surface #N+1.

**Lowest-cost validation step.** Before writing any candidate, build only the **generator + obs-only baseline + interventional oracle** and check gates 6.1–6.2 (premise + headroom). This is a few hundred lines, no candidate, no mechanism claim, and it can kill Route C before any mechanism design — the cheapest possible falsification.

**Stop-loss / rollback.** Route C stops immediately if: 6.1 fails (no non-identifiability), 6.2 fails (no headroom), or 6.3 returns `candidate ≤ fair interventional baseline` (saturation = the A outcome). Rollback for ACOLB-A: none needed — close is preservation only; `bb65008…` and artifacts untouched, no remote anchor, no tag.

**Acceptance signals (for the blueprint task, not for mechanism validity).** Blueprint is acceptable iff: every §6 gate has a written pass/fail + required artifact + a *demonstrated failing* negative control; the fair interventional panel (6.3) is concrete and access-parity-bound; the ACSB re-entry conditions are each mapped to a gate; and the claim ceiling is restated. No mechanism evidence is an acceptance signal here.

**What this does not prove.** See §8.

---

## 8. Claim ceiling / what this does not prove / remaining unknowns

**Claim ceiling:** route decision + mechanism-surface design only. No positive mechanism evidence, no Gate pass, no mainline effect, no live path, no agency, no autonomy, no consciousness, no emotion, no subjectivity, no stable user benefit, no EGO/companion readiness, no proof of Bio-CMBC/CVPSM/VCCO/CMBC/R-G.

**What this does not prove:**
- Does not prove ACOLB-A's candidate is invalid *in general* — only that it shows no detectable advantage over a fair amortized baseline on this generator/seeds/thresholds at N = 3 (amortization saturation).
- Does not prove Route C will work, is identifiable, or is implementable. Route C may die at preflight 6.1/6.2/6.3.
- Does not authorize Codex implementation, a Gate run, remote anchor, tagging, or any mainline/EGO/LLM/AIRI/UI path.
- Does not convert any prior ACSB artifact into valid mechanism-negative evidence (they remain invalid-harness/hygiene lessons per the closure).
- Does not establish that the lab's measurement paradigm can certify any positive mechanism.

**Remaining unknowns:** whether genuine interventional non-identifiability is constructible without observation leakage (6.1); whether a fair interventional baseline saturates the Route C candidate (6.3); whether the recurring non-fail-able-field / whitelist-escape defect class can be structurally closed rather than scanner-patched.

---

## 9. Final report block

- **Verdict:** ACOLB-A → close + preserve as bounded local negative (amortization-saturation) evidence, stop A repair, no remote anchor. Next action → **A** (draft Route C hostile design blueprint as ACSB re-entry card; §6 gates mandatory; no implementation yet).
- **Layer:** route-governance + mechanism-surface design.
- **Files changed:** this audit doc only (`docs/research/CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A.md`). No `src/`, `tests/`, or `artifacts/` modified. (Optional follow-up: one-line `docs/decision_log.md` entry — not yet written.)
- **Commands run:** read-only inspection of `artifacts/acolb_001a/*`, `src/acolb_001a/*`, `config.py`, `generator.py`, `candidate.py`, `amortized_seq.py`, and `docs/research/ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A.md`. No experiment executed, no test run, no git mutation.
- **Artifacts generated:** none (design audit; the document is the deliverable). No `artifacts/` writes — consistent with "not a Gate run."
- **Baseline results (inherited, re-read):** fair `amortized_seq` OOD 0.92986 vs candidate 0.94453, margin 0.01467 < OOD_BAND 0.05; baseline-equivalent across the full legal decay grid; candidate decisively beats all 13 graph-cache/lookup/memory baselines.
- **Ablation results:** n/a (no new run). ACOLB-A inherited ablations preserved untouched.
- **Replay result:** n/a (no new run).
- **Stop conditions triggered:** ACOLB-A `blocked_by_saturated_distribution` (inherited, confirmed). Route C STOP conditions pre-registered (6.1/6.2/6.3) but not yet evaluated.
- **Claim ceiling:** as §8.
- **What this does not prove:** as §8.
