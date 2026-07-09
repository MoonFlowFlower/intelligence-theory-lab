# PREREG FREEZE — UNCERTAINTY-VOI-REQUEST-MECHANISM-002A (intelligence-theory-lab)

> Ex-ante pre-registration, **successor to 001A**. Repo: **intelligence-theory-lab** (NOT Ego). 001A was executed (R3 `7be2680`) and ruled `INSTRUMENT_INVALID` by Claude Yellow audit for two coupled prereg-design defects: (1) the primary metric was **blind on information steps** (`regret_t = max_value + cost`, independent of belief ⇒ every non-exploit policy bit-identical ⇒ falsifier/ablation deltas structurally 0.0), and (2) the frozen KG rule (raw EI − cost) **never exploited** (0/4000 actions) ⇒ collapsed to the non-learning floor. 001A artifacts are preserved (no-delete); this file does **not** edit them. All values below are **frozen at the commit that banks this file**, which MUST be an ancestor of the 002A implementation and of any gated run it judges (commit order = ex-ante proof). **No post-hoc tuning.** Operator authorized the redesign and selected task model A (online control / hold-and-observe). The mechanism form and the baseline taxonomy below were validated by a 6-seed pre-freeze probe (mechanism exploits ~56%; controls produce non-zero, correctly-signed deltas; random-active baseline is strong) **before** freezing — the env constants were NOT tuned to manufacture separation.

## Layer / claim ceiling (binding)
Layer 3 mechanism hypothesis. **Claim ceiling:** bounded offline evidence that ONE implemented uncertainty/value-of-information mechanism (myopic knowledge-gradient with exploit pressure), in ONE toy environment, beats BOTH a best-tuned static-threshold rival AND a random-active baseline on a hold-and-observe VOI task, that this advantage collapses under wrong-sign feedback, shuffled feedback, and uncertainty-ablation, with a calibrating uncertainty estimate and held-out generalization. Proves NO general intelligence, real-world adaptation, world-modeling, understanding, self/agency/autonomy, subjectivity, emotion, consciousness, EGO/companion readiness, and specifically NOT that the pet has this mechanism. A PASS = a mechanism-proxy for uncertainty-driven VOI decision-making in a bounded toy.

## Environment (frozen — UNCHANGED from 001A; reuse validated constants)
- `K = 8` arms. Episode horizon `H = 200` steps. Values on [0,1].
- Hidden value `v_i(t)` = Gaussian random walk: `v_i(t+1) = clip(v_i(t) + N(0, τ_i²), 0, 1)`. **Heterogeneous drift**: 4 fast arms `τ_hi = 0.06`, 4 slow arms `τ_lo = 0.005` (assignment fixed per episode from the env-seed). Initial `v_i(0) ~ Uniform(0,1)`.
- Observation noise `σ_obs = 0.10`. Query cost `c_q = 0.02`. Request cost `c_r = 0.08`, returns a lower-noise sample (`σ_obs/3`) for the current top-2 arms by μ.
- Env-seed fixes the value trajectories + all noise draws so every policy is compared on identical worlds (paired).

## Task / reward / regret model (frozen) — **MODEL A: online control, hold-and-observe**
This replaces the 001A metric. It makes the belief load-bearing on **every** step.
- Each step `t`, the agent **automatically holds (realizes the value of) its incumbent arm** `inc(t) = argmax_i μ_i(t)` (ties → lowest index). Independently, it selects **at most one information action** `a_t ∈ {noop, query(i), request}`:
  - `noop`: cost 0, no observation (just hold).
  - `query(i)`: cost `c_q`, observe `v_i(t)+N(0,σ_obs²)`, Kalman-update arm i.
  - `request`: cost `c_r`, observe the top-2 arms by μ with noise `σ_obs/3`, Kalman-update them.
- **Per-step regret**: `regret_t = [ max_j v_j(t) − v_{inc(t)}(t) ] + cost(a_t)`. First term = opportunity regret of holding the current best-guess arm vs the true best (depends on belief through `inc(t)`); second = information cost paid this step.
- **Primary outcome**: cumulative regret `Σ_t regret_t` over H, lower = better. Paired across identical env instances. `oracle` sets `inc(t)=argmax_j v_j(t)`, cost 0 ⇒ regret 0.

## Mechanism under test (frozen) — Kalman belief + **exploit-pressure myopic knowledge gradient**
- **Belief**: per-arm `(μ_i, σ_i²)`, Kalman over the walk. Between steps `σ_i² += q` (`q = 0.004`, a single constant; the agent does NOT know per-arm τ). On observing arm i with noise variance `σ_n²` (σ_n = σ_obs for query, σ_obs/3 for request) and sample x: `K = σ_i²/(σ_i²+σ_n²)`, `μ_i += K(x−μ_i)`, `σ_i² *= (1−K)`. Record PE `= |μ_i − x|` (innovation).
- **KG (proper, with exploit pressure)** — the one-step knowledge gradient for independent normal beliefs:
  - predictive std of the update to μ_i from one observation of noise variance σ_n²: `σ̃_i = σ_i² / sqrt(σ_i² + σ_n²)`.
  - gap to the best other arm: `Δ_i = μ_i − max_{j≠i} μ_j`.
  - `KG(query i) = σ̃_i · f( −|Δ_i| / σ̃_i )`, where `f(z) = φ(z) + z·Φ(z)` (φ,Φ = standard normal pdf/cdf), using `σ_n = σ_obs`.
  - `KG(request) = Σ_{i ∈ top-2 by μ} σ̃_i · f( −|Δ_i| / σ̃_i )` using `σ_n = σ_obs/3`.
  - **KG → 0 as σ_i → 0** (well-known arm ⇒ no information value): this is the exploit-pressure property 001A lacked.
- **Decision (exploit pressure)**: `a* = argmax_a [ KG(a) − cost(a) ]` over {query(i) ∀i, request}; **if `max_a [KG(a) − cost(a)] ≤ 0` ⇒ `noop`** (hold, spend nothing). Deterministic function of (μ, σ, cost); no hidden-label access; no fixed PE/age threshold.

## Baselines, controls, floors, ceiling (frozen)
- **RIVALS to beat (the mechanism must beat BOTH, by the MDE):**
  - `static_threshold` (strong, tuned): `noop` unless the oldest-observed arm has `age > θ`, then `query` it; `request` every `request_period` steps (0 ⇒ never). `θ` and `request_period` grid-tuned on the **separate** tuning block 9301–9310 only, then frozen and scored.
  - `random_active`: each step `query` a uniformly random arm (cost `c_q`), Kalman-update, hold incumbent. (Under hold-and-observe this is a **strong active baseline**, not a floor — it tests whether *smart allocation* beats *indiscriminate gathering*.)
- **CONTROLS that must NOT match (matching ⇒ INVALID):** `wrong_sign` (`x' = 2μ_i − x` before update), `shuffled` (per-episode permuted sample pool), `uncertainty_ablation` (σ frozen constant ⇒ no inflation/shrink; KG loses σ→0 exploit pressure and uncertainty prioritization), `value_ablation` (`KG(query i) = σ̃_i`, ignoring Δ_i ⇒ query highest-σ regardless of value).
- **FLOORS (non-learning; used for G6 dominance):** `hold_only` (noop every step; belief never updates), `no_update` (pays to observe but never updates belief).
- **CEILING:** `oracle` (holds argmax `v_i(t)`, pays nothing) ⇒ regret 0.

## Seeds (frozen; assert pairwise disjoint; fail closed)
- Dev probe env-seed `9001` (run first). Rival-tuning `9301–9310` (θ/period only; never scored). Scored `M = 20`, `9101–9120`. Held-out transfer `9201–9210`. Single seeded agent RNG stream; no unseeded RNG.

## Metrics + gates (thresholds frozen; CI/MDE-based)
Primary statistic per rival R: **paired advantage** `A_R = regret(R) − regret(mechanism)` per env-seed. Report mean, 95% bootstrap paired CI, effect size over M=20. **MDE: relative advantage ≥ 10% of the rival's regret.**
- **G1 rival-beat (two sub-gates, BOTH required):** `G1a` mean `A_static > 0`, 95% CI excludes 0, mean relative ≥ 10%; `G1b` same vs `random_active`. (If a sub-gate is underpowered / straddles 0 ⇒ the corresponding *_SUFFICIENT verdict; increase M only via a NEW prereg.)
- **G2 falsifiers:** `A_wrong_sign` and `A_shuffled` each have 95% CI including 0 (advantage collapses), AND `A_clean − A_falsified` CI excludes 0 (collapse significant).
- **G3 ablation:** `A_uncertainty_ablation` CI includes 0 (destroyed); `A_value_ablation` significantly < `A_clean` (value term load-bearing).
- **G4a calibration** (frozen, not fitted): standardized belief residual `z_i(t) = (μ_i(t) − v_i(t))/σ_i(t)` (offline diagnostic; ground truth used only for scoring, like the oracle — not fed to the model). Pass iff `mean(z²) ∈ [0.7, 1.5]`. Report 90%-coverage fraction (target [0.85,0.95]).
- **G4b transfer:** advantage vs the better rival on held-out seeds `A_transfer` CI excludes 0.
- **G5 replay:** fresh-process ×2 bit-exact; AST rng-audit + fail-able positive control; gate-scoped trace + `metric_records` ≤ 25 MiB.
- **G6 floor dominance + info-value (anti-vacuity; frozen anchors):**
  - (a) **floor dominance**: `regret(hold_only) ≥ 2.0 × regret(mechanism)` AND `regret(no_update) ≥ 2.0 × regret(mechanism)` (mechanism is a real active learner, not a non-learning floor).
  - (b) **information has value** (env not trivial): `regret(hold_only) ≥ 2.0 × regret(random_active)` (active gathering meaningfully beats never-gathering; else information is worthless ⇒ no VOI headroom).
- **Tripwire (fail-closed, evaluated before verdict):** if the mechanism's scored **exploit(noop)-fraction ∉ (0.02, 0.98)** (it must both noop and query), OR **any** falsifier/ablation `A_clean − A_control` is exactly 0.0 across all M seeds (a control with literally zero effect ⇒ mechanism not wired to it), the run is `INSTRUMENT_INVALID` subtype `MECHANISM_INERT` — do not emit a mechanism verdict.

## Verdict rule (frozen)
- `VOI_MECHANISM_PRESENT` iff G1a ∧ G1b ∧ G2 ∧ G3 ∧ G4a ∧ G4b ∧ G5 ∧ G6 ∧ tripwire-clear.
- `VOI_MECHANISM_PRESENT_UNCALIBRATED` iff all of the above except G4a (calibration) fail — positive-but-weaker, drops the "calibrating uncertainty estimate" clause; `positive_claim: true` ⇒ same STOP + FULL hostile audit.
- `SIMPLE_ACTIVE_SUFFICIENT` iff G1b fails (mechanism does not beat `random_active` by the MDE) — bounded negative: smart VOI allocation is not shown superior to indiscriminate active gathering on this env.
- `STATIC_SUFFICIENT` iff G1a fails but G1b passes (a tuned age heuristic matches the mechanism).
- `ATTRIBUTION_FAILURE` (⇒ INSTRUMENT_INVALID) iff G1a ∧ G1b pass but the advantage survives a falsifier (G2 fails) or uncertainty-ablation (G3 fails) — the win is not VOI.
- `INSTRUMENT_INVALID` iff G5 fails, G6 fails (floor/info-value), the tripwire fires, or seed-disjointness fails.
- `CAPABILITY_ABSENT` iff mechanism ≈ non-learning floors (hold_only/no_update).

## Predeclared failure geography
Advantage MUST be absent (CI∋0) under wrong-sign, shuffled, and uncertainty-ablation; present only for the full mechanism vs both rivals and on held-out transfer. Any advantage under falsifier/ablation ⇒ INSTRUMENT_INVALID. The mechanism MUST both noop and query (exploit pressure real). Expected-hard baseline: `random_active` is close under hold-and-observe; a `SIMPLE_ACTIVE_SUFFICIENT` outcome is a legitimate, informative negative, not a bug.

## Anti-rigging + anti-hardcoding (frozen)
Tuned (not strawman) static rival on a separate block; random-active and non-learning floors both present; oracle regret-0 + G6; `q` a single constant (no per-arm-drift access); KG computed from belief only; thresholds pre-registered (MDE 10%; G4a [0.7,1.5]; G6 2.0× floor + 2.0× info-value; tripwire (0.02,0.98)); env constants unchanged from 001A and NOT tuned for separation; replayable from trace; no hidden `v_i`/τ leaked into observations, action names, filenames, or fixtures; no future observations in prediction; probe-first CPU budget STOP.

## Artifacts (ITL convention)
Under `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/`: `result.json` (verdict + subtype + per-rival/per-condition A tables + CIs + exploit-fraction + claim_ceiling + config_shas incl. this prereg), gate-scoped `trace.jsonl` + `metric_records.json`, `baseline_comparison.json`, `ablation_report.json`, `falsifier_report.json`, `calibration_transfer_report.json`, `replay_report.json`, `headroom_report.json` (G6 floor + info-value ratios), `tripwire_report.json` (exploit-fraction + control-delta liveness), `failure_manifest.json` if any fail, `claim_ceiling.txt`. Card at `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A.md`; code isolated under `src/uncertainty_voi/` (new module, e.g. `runner_002.py`; do NOT edit the 001A runner); tests under `tests/`.
