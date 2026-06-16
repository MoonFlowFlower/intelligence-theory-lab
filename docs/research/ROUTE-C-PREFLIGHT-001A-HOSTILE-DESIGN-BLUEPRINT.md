# ROUTE-C-PREFLIGHT-001A — HOSTILE DESIGN BLUEPRINT

Independent hostile implementation-design blueprint for the Route C surface
(`self-boundary via interventional identifiability under confounding`).

**This document is NOT implementation, NOT a Gate run, NOT mechanism evidence,
NOT a candidate authorization, and NOT remote-anchor authorization.** It is a
design artifact whose only job is to try to kill Route C on paper — to specify a
candidate-free Phase 0 that can falsify the surface before any mechanism code is
written.

- Role: same-agent independent auditor / red-team reviewer (CLAUDE.md Role 001).
- Layer: `mechanism-surface design + preflight design only` (no execution).
- Parent / authorizing record: `docs/research/CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A.md` (§0 "Next action = A").
- Governing closure (read-only rule source): `docs/research/ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A.md` (boundary commit `d5b4b92…`).
- Provenance rule source (read-only): `docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md`.
- Auto-Remote-Anchor: **forbidden.**

> **This design proves no mechanism.** It cannot show that Route C works, that a
> self-boundary mechanism exists, or that any Gate passes. The best outcome this
> blueprint can produce downstream is a *clean preflight admission for candidate
> design* — or, just as acceptable, an early death of Route C at the premise or
> headroom gate.

---

## 1. Current layer / claim ceiling

| Field | Value |
|---|---|
| Current layer | `mechanism-surface design + preflight design only` (engineering-implementation + mechanism-hypothesis *design*, not execution) |
| Mainline integration status | none |
| Enabled status | not enabled; no runtime, no scheduler, no EGO/AIRI/LLM/UI path |
| Real trigger evidence | authorizing route decision `CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A` §0 (`Next action = A`) + the explicit Route C blueprint task instruction |
| Execution performed here | none (no code run, no experiment, no Gate, no git mutation) |
| Claim ceiling | **Route C preflight *design* only.** No mechanism evidence, no Gate pass, no baseline non-equivalence result, no headroom result, no non-identifiability result — those are *future executable outcomes*, not claims of this document. |

**Explicit non-claim.** Nothing in this blueprint constitutes evidence that
observation-only fails, that interventions add headroom, that a candidate beats a
fair interventional baseline, or that self-boundary is a real mechanism. Those
are hypotheses to be *tested* by the Phase 0 implementation this document
specifies. Until that code runs and emits artifacts, every quantity below is a
**design target, not a measured value.**

---

## 2. Prior negative evidence mapping (ACSB family re-entry)

Per the operating contract ("every successor task must search and cite relevant
prior negative evidence before proposing a new gate/bridge/implementation"),
Route C is treated as a **re-entry into the `action_conditioned_self_boundary`
(ACSB) surface family**, which is downgraded and sealed
(`ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A`, verdict
`preserve_acsb_current_route_downgrade_closure_001a_pass`; boundary `d5b4b92…`).
This blueprint *is* the "separate route-decision card for a materially different
surface" that closure requires; drafting it as if ACSB never happened would
itself violate the contract.

The decisive ACSB collapse: `full_reference`, `fair_capacity_disabled_reference`,
the "learned" MLP, and the observation-only probe **all reduced to the same
target path** `_target_from_observation = phase_bit XOR action_bit`, where *both
bits live in `legal_observation`*. Target computable from same-step legal
observation ⇒ observation-only = oracle ⇒ everything tied `1.0 / 1.0 / 0.0` ⇒ the
"negative evidence" was an **oracle-minus-oracle constructive identity artifact**,
not a falsification.

For each prior ACSB failure mode, the Route C gate that structurally prevents it:

| # | Prior ACSB / ITL failure mode | Concrete manifestation | Route C gate that prevents it |
|---|---|---|---|
| F1 | **Same-step observation target decoding** (the decisive ACSB killer: `phase_bit XOR action_bit` both in obs) | obs-only = oracle; `1.0/1.0/0.0` constructive identity | **§6.1 non-identifiability premise gate** — `S` is provably absent from passive `P(X)` (§3); obs-only baseline must score ≤ frozen chance ceiling, *tested not assumed*. If obs decodes `S` ⇒ `blocked_by_observation_decodable_self_set`. |
| F2 | **Schema alias leakage** (self channels identifiable by dtype/range/index/name/position) | a schema-only attacker succeeds with interventions disabled | **§6.5 + §6.6** per-episode channel permutation + schema-alias attacker battery, all must score ≤ ceiling ⇒ else `blocked_by_schema_alias_leakage` |
| F3 | **Action/channel identity leakage** (do-action named/ordered so its target is inferable without observing effects) | candidate maps action→channel by label, not by measured effect | **§6.5** action/channel handles randomized per episode; label-only attacker ≤ ceiling ⇒ else `blocked_by_action_label_leakage` |
| F4 | **Oracle-minus-oracle constructive identity** (the metric is tautological: `candidate == label-generating expression`) | all arms tie at the label; "negative" is an artifact | **§6.10 fail-able-fields rule** + **§3 separation by information, not by formula**: obs-only and oracle consume *different information sets* (passive vs interventional), so they cannot be the same expression; every gate ships a demonstrated failing negative control |
| F5 | **Non-fail-able controls** (a gate that cannot logically return `fail`) | leakage/ablation "checks" that pass unconditionally | **§6.10 + §7**: every gate and every leakage scanner ships an *injected* positive control that MUST flip the verdict to fail; a control that does not fire is itself a terminal blocker (`blocked_by_non_fail_able_control`) |
| F6 | **Baseline equivalence / saturation** (the ACOLB-A killer: fair baseline matches candidate) | `candidate − max(fair baseline) < band` ⇒ mechanism collapses to "standard method + the same data" | **§6.3 fair *interventional* baseline panel** (deferred to candidate task, specified here): key comparison is `candidate − max(fair interventional baseline)`, **never** `interventional − observational`. Predicted-null saturation is an honest STOP, not a repair target. |

Inherited limiter (do not strengthen): ACSB is **downgraded, not
mechanism-falsified.** `001B/001C/001D` and `fe5aa85` remain
invalid-harness/hygiene lessons, never mechanism-negative evidence. Route C does
not convert any of them into evidence.

Meta-signal (inference, not fact): the lab's recent surfaces — Gate1
`graph_cache_collapse`, RESIDUE-001A, ACSB 001B/C/D, ACP-BV 001A/001B, ACOLB-A —
have all ended in saturation or oracle/leakage collapse. This raises the prior
that *any amortizable constructed surface* will be saturated by the fair panel.
Route C is interesting only because non-identifiability is the one regime where a
fair observational baseline *provably* lacks the information. That same prior
demands a hard pre-registered STOP (§14) so Route C does not become the next
entry in the run.

---

## 3. Causal graph and non-identifiability premise

The premise gate (§6.1) is the load-bearing structural fix for the ACSB killer.
It must be **proven by construction**, not hoped for. This section gives the
minimal toy causal model and the exact argument.

### 3.1 Variables

Per episode (one hidden self-set, fixed for the episode):

| Symbol | Meaning | Visibility |
|---|---|---|
| `C` | number of observation channels (e.g. 8) | legal (public constant) |
| `k` | size of the hidden self-set, `1 ≤ k < C` (e.g. 3) | legal (public constant) |
| `S ⊆ {0..C-1}`, `|S| = k` | **hidden self-set**: channels the agent's actions causally control | **hidden / oracle-only** |
| `U_t ∈ R^m` | latent confounder vector (e.g. `m = 2`), `U_t ~ N(0, I_m)` iid per step | **hidden / oracle-only** |
| `W ∈ R^{C×m}`, rows `w_i` | channel loadings on the confounder; `w_i ~ N(0, I_m)` iid, **drawn from the same distribution for `i ∈ S` and `i ∉ S`** | **hidden / oracle-only** |
| `g > 0` | action-coupling gain (frozen scalar) | structural; its magnitude is what §6.2 tests |
| `σ` | per-channel observation noise sd (frozen) | structural |
| `a_t` | agent action: either `∅` (passive) or `do(channel=j, value=v)` with `v ⟂ U,ε` | legal *in interventional dataset only* |
| `π` | the channel permutation applied per episode (original index → public handle) | **hidden**; only permuted handles are legal |

### 3.2 Structural equations

Passive regime (no action, `a_t = ∅`), for every channel `i`:

```
X_{t,i} = w_i · U_t + ε_{t,i},   ε_{t,i} ~ N(0, σ²)         (PASSIVE)
```

Interventional regime, randomized `do(channel = j, value = v)`, `v ⟂ U, ε`:

```
X'_{t,i} = w_i · U_t + ε_{t,i} + g · v · 1[ i = j  AND  j ∈ S ]   (INTERVENED)
```

In words: the agent's do-action shifts the targeted channel `j` by `g·v` **iff
that channel is in the self-set**; non-self channels never respond to the agent's
action. Self and non-self channels are otherwise generated identically.

### 3.3 Non-identifiability from passive observation (proof, exact)

The passive law is

```
X_t ~ N(0,  W Wᵀ + σ² I_C ).
```

This distribution is a function of `(W, σ)` **only**. The self-set `S` does not
appear anywhere in the passive structural equations. Therefore:

> For any two self-sets `S, S'` with the *same* `W`, the passive observational
> distributions are **identical**: `P_S(X) = P_{S'}(X)`. No estimator — at any
> sample size `N`, with any compute — can distinguish `S` from `S'` from passive
> data better than the prior.

The Bayes-optimal passive predictor of `S` given any amount of passive `X` is
therefore the **uniform prior over k-subsets**, whose expected set-F1 is exactly
`k / C` (chance). This is *exact, finite-sample* non-identifiability, not an
asymptotic claim. It is the information-theoretic negation of the ACSB
`phase_bit XOR action_bit` killer: there, `S` was a deterministic function of
same-step observation; here, `S` is provably *not a function of the passive
observation distribution at all.*

This yields a constructive falsification test (§12): the generator can emit a
**twin pair** `(episode_A, episode_B)` sharing `W, σ, U-stream` but with disjoint
`S_A ≠ S_B`; their passive observation streams are drawn from the identical law.
Any "observation-only" method that scores above chance on telling them apart is
by definition reading a leak, not signal ⇒ premise gate fails.

### 3.4 Identifiability from intervention (proof)

Under randomized `do(j, v)` with `v ⟂ U, ε`, the average causal effect on the
targeted channel is

```
E[ X'_{·,j} − X_{·,j} | do(j, v) ] = g · v · 1[ j ∈ S ].
```

So the do-effect of acting on channel `j` is `g·v` if `j ∈ S` and `0` otherwise.
With enough randomized interventions per channel, the effect estimate
concentrates and recovers `S` exactly (up to `O(σ/√n_int)` noise). Hence `S` is
**identifiable from interventional data** though non-identifiable from passive
data — the do-information is absent from every observational dataset *by
construction*. This is the headroom the §6.2 oracle must demonstrate (and which a
zero-gain ablation, `g → 0`, must destroy — the gate's fail-able control).

### 3.5 Role of the confounder (why this is "under confounding", not "no signal")

`U` is essential and is what makes naive methods fail in *both* regimes:

- **Passive:** `Cov(X_i, X_j) = w_i · w_j` — strong cross-channel correlation
  driven entirely by shared `U`, completely **S-independent**. A correlational /
  observational causal-discovery method sees rich structure that has *nothing* to
  do with `S`; it is actively misled, not merely uninformed. This is genuine
  confounding, not absence of signal.
- **Interventional, if the do-policy is itself confounded:** if intervention
  assignment is correlated with `U` (the agent tends to act on channel `j` when
  `U` is large), then a naive contingency/regression over interventional samples
  re-absorbs the confound and reports spurious effects on non-self channels.
  **Randomized** interventions (`v, j ⟂ U`) break this — which is exactly why the
  §6.2 *oracle* uses randomized do-operations to establish that headroom *exists*,
  while the §6.3 *fair interventional panel* (candidate phase) is what tests
  whether a non-candidate method can also exploit it. The gap between "randomized
  interventions identify `S`" and "the candidate's specific update rule is needed"
  is the saturation risk F6 — the thing that killed ACOLB-A, here reborn one layer
  up, and the reason the candidate is **deferred** until the panel is built.

Pre-registration rule: `C, k, m, g, σ`, the confounder-strength, the do-policy
randomization, and all gate thresholds are **frozen and hashed before any run**
(§6.10). Confounder strength may **never** be tuned after seeing whether obs-only
fails — that would be the forbidden post-hoc generator tuning (risk #13).

---

## 4. Generator specification

All randomness flows from a single seeded `rng`; the generator is a pure
function of `(seed, config)`. Truth (`S`, `U`, `W`, `π`) is emitted **only** into
an `oracle` side-channel that legal consumers cannot import (enforced by call-graph/AST
scan, §7). Legal consumers receive only the `LegalObservation` view (§5).

```python
@dataclass(frozen=True)
class Config:
    n_channels: int          # C, frozen (e.g. 8)
    k_self: int              # |S|, frozen (e.g. 3)
    m_confounder: int        # U dim, frozen (e.g. 2)
    gain: float              # g, frozen; >0 for headroom, 0.0 for the no-headroom control
    noise_sd: float          # σ, frozen
    n_passive: int           # passive samples per episode (obs-only train/query)
    n_intervention_budget: int   # do-operations available (parity-shared, §6.10)
    do_policy: str           # "randomized" (Phase 0 oracle) | "confounded" (candidate-phase panel)
    confounder_strength: float   # scales W; frozen, NEVER tuned post-hoc
    permute_channels: bool   # per-episode π; MUST be True on the real path

def sample_episode(seed: int, config: Config) -> "HiddenEpisode":
    """Pure (seed, config) -> HiddenEpisode. Draws S, U-stream, W, π; builds the
    legal view lazily. No global state. Re-running with the same (seed, config)
    is byte-identical (test T1)."""

def sample_hidden_self_set(rng, n_channels: int, k_self: int) -> set[int]:
    """Uniform k-subset of original channel indices. ORACLE-ONLY output."""

def sample_confounder(rng, n_channels: int, m: int, strength: float) -> "ConfounderState":
    """Draw W (C×m) ~ N(0, strength·I) and the per-step U stream ~ N(0, I_m).
    Loadings for i in S and i not in S come from the SAME distribution (no
    membership signal in W). ORACLE-ONLY output."""

def generate_passive_observations(hidden: "HiddenEpisode", n: int) -> list["PassiveObs"]:
    """Apply PASSIVE eq (§3.2): X_i = w_i·U_t + ε. NO action applied, ever.
    This is the only data obs-only baselines may consume. Returns LEGAL rows
    (channel values under permuted handles); S/U/W not included."""

def apply_intervention(hidden: "HiddenEpisode", action: "InterventionAction") -> "InterventionResult":
    """Apply INTERVENED eq (§3.2): shift channel j by g·v iff j in S. Returns
    POST-intervention legal observation + the (permuted) acted-on handle + value.
    MUST NOT return which channels are self, the original index of j, U, or the
    effect label. do-value/target sampling obeys config.do_policy."""

def make_queries(hidden: "HiddenEpisode") -> list["Query"]:
    """Emit the prediction task: 'which channels (by permuted handle) are self?'
    Query carries NO answer. The truth self-set is held in oracle-only space and
    handed only to score_self_set_prediction()."""

def score_self_set_prediction(predicted: set[int], truth: set[int]) -> "Score":
    """Set-F1 over channel membership. With |pred| = |truth| = k,
    F1 = |pred ∩ truth| / k. Chance (uniform k-subset) = k / C. Pure, oracle-side."""
```

What is hidden / legal / oracle-only:

| Quantity | Class |
|---|---|
| channel values `X` under **permuted** handles, in the regime's dataset | **legal** (candidate- and baseline-legal) |
| acted-on **permuted** handle + do-value, in interventional rows | **legal** (interventional access only; parity-shared budget) |
| `C, k, m` (public constants), regime tag (`passive` / `interventional`) | **legal** |
| `S`, `U_t`, `W`/loadings, `g`, original channel indices, `π` | **hidden / oracle-only** |
| the truth self-set used by `score_self_set_prediction` | **oracle-only**, never in any legal row |

Channel-name / order randomization: every episode draws an independent
permutation `π`; the public handle of a channel is its post-`π` position, plus an
opaque random string id (no dtype/range/name correlated with membership). The
original index is never exposed. Two episodes with the same `S` (original
indices) look unrelated to a legal consumer (defeats hardcoding + cross-episode
memorization, risks #3/#6/#8).

How confounding prevents passive decoding: per §3.3, `S ∉ P(X)`; passive
cross-channel correlation is pure-`U` and S-independent, so the passive dataset
carries no S-signal at any `N`.

How interventions reveal coupling without leaking `S`: the only legal
interventional signal is *the post-intervention channel values themselves*. The
API returns no "this channel is self" flag and no effect label; the learner must
*estimate* the effect from noisy `X'` across its budget. A single sample does not
cleanly reveal `S` (noise `σ` + confounder `U` movement mask it); aggregation
over randomized interventions is required — which obs-only structurally cannot do
because it has no interventional rows.

---

## 5. Legal observation schema

Legality tags per field: **CL** = candidate-legal, **BL** = baseline-legal (fair
baselines), **H** = hidden, **OO** = oracle-only, **AB** = answer-bearing
(must never be CL/BL), **D** = derived-legal (computed from legal fields only).

```python
@dataclass(frozen=True)
class HiddenEpisode:        # the full episode; NOT a legal object
    config: Config                       # CL/BL (public constants subset only via .public())
    self_set_original: frozenset[int]    # OO/AB  -- the answer
    confounder: ConfounderState          # OO  (W, U-stream)
    permutation: tuple[int, ...]         # H   (π: original index -> handle)
    gain: float                          # OO  (structural)
    seed: int                            # OO  (truth-stream seed; see §6.10 truth isolation)

@dataclass(frozen=True)
class ConfounderState:
    W: "ndarray[C,m]"                    # OO
    U_stream: "ndarray[T,m]"             # OO

@dataclass(frozen=True)
class PassiveObs:           # one passive timestep (obs-only train/query)
    handle_values: dict[Handle, float]   # CL/BL  -- X_i under permuted handles
    regime: str                          # CL/BL  == "passive" (constant)
    # NO action, NO self flag, NO U, NO original index.

@dataclass(frozen=True)
class InterventionAction:   # a do-request issued by a learner with interventional access
    target_handle: Handle                # CL/BL  -- permuted handle to act on
    value: float                         # CL/BL  -- do-value v

@dataclass(frozen=True)
class InterventionResult:   # what the API returns for one do-operation
    post_handle_values: dict[Handle, float]  # CL/BL  -- X'_i under permuted handles
    target_handle: Handle                    # CL/BL  -- echo of the acted handle
    value: float                             # CL/BL  -- echo of v
    regime: str                              # CL/BL  == "interventional"
    # HARD: no responded-channel flag, no effect size, no original index, no S, no U.

@dataclass(frozen=True)
class LegalObservation:     # the ONLY object candidate/fair-baselines may read
    passive_rows: list[PassiveObs]           # CL/BL
    intervention_log: list[InterventionResult]   # CL/BL  (empty for obs-only baseline)
    public_config: dict                      # CL/BL  -- {n_channels, k_self, regime budgets}
    handles: list[Handle]                    # CL/BL  -- permuted handle list (opaque ids)

@dataclass(frozen=True)
class Query:
    handles: list[Handle]                    # CL/BL  -- "label each handle self / not-self"
    k_self: int                              # CL/BL  -- public constant
    # NO truth, NO membership.

@dataclass(frozen=True)
class SelfBoundaryBelief:   # candidate state (candidate phase only)
    logits: dict[Handle, float]              # CL (candidate-internal)

@dataclass(frozen=True)
class PredictionRecord:
    predicted_self: set[Handle]              # D  -- argmax/threshold over belief
    producer: str                            # provenance: producer_function name
    run_id: str; seed: int; episode_id: str

@dataclass(frozen=True)
class ScoreRecord:
    value: float                             # D  -- F1 from score_self_set_prediction
    producer_function: str; inputs: dict; run_id: str
    seed: int; episode_ids: list[str]; aggregation: str
    code_path_hash: str; threshold_used: float
    threshold_frozen_before_run: bool; computed_not_literal: bool
    failure_path_available: bool
```

**Hard rule (enforced by §7 scanners + §12 tests).** Candidate and fair baselines
may read `LegalObservation` / `Query` / their own `SelfBoundaryBelief` only. They
must **never** see: `S` (`self_set_original`), confounder `W`/`U`, original
channel indices, `π`, the do-effect/oracle map, the gain `g`, or any unpermuted
channel identity. The obs-only baseline additionally receives an
`intervention_log` that is **empty by contract** (§6.1).

---

## 6. Phase 0 preflight gates

Thresholds are **frozen and hashed before any run** (§6.10). `ceiling = k/C +
PREMISE_BAND`; `PREMISE_BAND`, `HEADROOM_BAND`, `SAT_BAND` are predeclared
constants. Every gate returns a `GateVerdict {verdict: str, value: float,
threshold: float, passed: bool, failure_path_available: True}` and is constructed
so that a specific input makes it return `fail` (the fail-able control). **Phase 0
implements 6.1 and 6.2 (+ the §7 controls). 6.3 is specified here but NOT
implemented in Phase 0 (no candidate exists yet).**

### 6.1 Non-identifiability premise gate

```python
def obs_only_baseline(train: list[LegalObservation], queries: list[Query]) -> Prediction:
    """Best passive predictor. Sees passive_rows only; intervention_log MUST be
    empty (asserted). May use any observational structure (covariance, clustering,
    supervised fit on passive features). Per §3.3 its ceiling is chance = k/C."""

def schema_only_attacker(schema_rows: list[LegalObservation]) -> Prediction:
    """Predicts S from SCHEMA features ONLY (handle ids, position, dtype, value
    range/order) with all channel VALUES zeroed. Must not exceed chance unless
    schema leaks membership."""

def name_order_attacker(legal_rows: list[LegalObservation]) -> Prediction:
    """Predicts S from handle ordering / string ids ONLY. Must not exceed chance
    unless permutation π leaked or handles correlate with original index."""

def non_identifiability_premise_gate(results: BaselinePanelResult,
                                     ceiling: float, band: float) -> GateVerdict:
    obs   = results.obs_only_score
    schem = results.schema_only_score
    nameo = results.name_order_score
    if schem > ceiling + band or nameo > ceiling + band:
        return GateVerdict("blocked_by_schema_alias_leakage", max(schem, nameo),
                           ceiling + band, passed=False)
    if obs > ceiling + band:
        return GateVerdict("blocked_by_observation_decodable_self_set", obs,
                           ceiling + band, passed=False)
    return GateVerdict("non_identifiability_present", obs, ceiling + band, passed=True)
```

Required verdicts: `non_identifiability_present` |
`blocked_by_observation_decodable_self_set` | `blocked_by_schema_alias_leakage`.

**Fail-able control (mandatory, §7-L1):** run the gate on a generator variant
that injects `S` as a legal field (`inject_hidden_self_set_as_legal_field`).
`obs_only` must jump to ≈1.0 and the gate MUST return
`blocked_by_observation_decodable_self_set`. If it does not flip ⇒
`blocked_by_non_fail_able_control` (the premise gate is void). This is what proves
the gate can actually fail — the exact defect that made the ACSB `1.0/1.0/0.0`
"negative" an artifact.

### 6.2 Interventional headroom gate

```python
def interventional_oracle(hidden: HiddenEpisode, budget: int) -> Prediction:
    """CEILING ONLY, not a fair baseline, not the candidate. Issues `budget`
    RANDOMIZED do-operations (v, j ⟂ U) per channel, estimates per-channel ACE
    Ê[X'_j − X_j | do(j,v)], predicts top-k channels by |effect| as self.
    Allowed to use the clean randomized do-API; NOT allowed to read S directly
    (it still must estimate, so a g→0 world collapses it — see control)."""

def interventional_headroom_gate(obs_score: float, oracle_score: float,
                                 band: float) -> GateVerdict:
    if (oracle_score - obs_score) > band:
        return GateVerdict("interventional_headroom_present",
                           oracle_score - obs_score, band, passed=True)
    return GateVerdict("blocked_by_no_interventional_headroom",
                       oracle_score - obs_score, band, passed=False)
```

Required verdicts: `interventional_headroom_present` |
`blocked_by_no_interventional_headroom`.

**Fail-able control (mandatory):** run on the `gain = 0.0` generator variant.
Interventions then carry no information, `oracle_score → chance ≈ obs_score`, and
the gate MUST return `blocked_by_no_interventional_headroom`. If the oracle still
"succeeds" with `g = 0` ⇒ it is reading `S` through a leak, not estimating
effects ⇒ `blocked_by_non_fail_able_control`. Headroom is **tested, never
assumed.**

### 6.3 Fair interventional baseline panel gate (specified; **deferred — not in Phase 0**)

This is the load-bearing anti-saturation gate and the lesson of ACOLB-A. It is
**defined but not implemented in Phase 0** because it only has meaning once a
candidate exists. The key comparison is **`candidate − max(fair interventional
baseline)`**, *never* `interventional − observational` (proving the latter only
shows causal discovery works, not that the candidate is non-trivial — risk F6).

```python
def ci_test_baseline(legal_interventions, queries) -> Prediction:
    """Conditional-independence causal discovery over interventional samples."""
def do_regression_baseline(legal_interventions, queries) -> Prediction:
    """Regress ΔX on do-indicators; top-k coefficients -> self."""
def contingency_baseline(legal_interventions, queries) -> Prediction:
    """Count/contingency table of (acted handle -> observed shift) over samples."""
def intervention_effect_nn_baseline(legal_interventions, queries) -> Prediction:
    """Nearest-neighbor over per-channel intervention-effect vectors."""
def fsm_lookup_baseline(legal_interventions, queries) -> Prediction:
    """Lookup/FSM over (action, channel) effect pairs."""
def random_intervention_baseline(legal_interventions, queries) -> Prediction:
    """Random k-subset using the same budget (floor control)."""

def select_strongest_fair_interventional_baseline(results: list[BaselineResult]) -> BaselineResult:
    return max(results, key=lambda r: r.score)        # argmax by number, no hand-pick

def fair_interventional_saturation_gate(candidate_score: float,
                                        strongest_fair_score: float,
                                        band: float) -> GateVerdict:
    if (candidate_score - strongest_fair_score) > band:
        return GateVerdict("fair_interventional_separation_present",
                           candidate_score - strongest_fair_score, band, passed=True)
    return GateVerdict("blocked_by_fair_interventional_saturation",
                       candidate_score - strongest_fair_score, band, passed=False)
```

Hard rule: **candidate vs `max(fair interventional baseline)`**; the oracle is a
ceiling only and is never the comparison target. Access parity is mandatory
(§6.10): candidate and every fair baseline get the **identical** interventional
budget and the **same** (possibly confounded) `do_policy`. `blocked_by_fair_
interventional_saturation` is the **predicted null** and an honest STOP — it is
**not** a repair target and must not be patched (this is the ACOLB-A discipline).

### 6.4–6.10 (inherited from the authorizing route decision, bound here)

These map 1:1 to `CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION…-001A` §6.4–6.10 and
are restated as binding obligations; 6.4/6.5/6.6 ship as Phase 0 §7 controls,
6.7/6.8/6.9 are candidate-phase ablations/replay (§9/§10):

- **6.4 Candidate input-contract** (no hidden `S`): inputs = legal obs + own do-API + outcomes; never `S`/confounder. Oracle-injection positive control proves the channel *would* be exploitable, then confirms the real path closed it.
- **6.5 Channel name/order randomization**: per-episode `π`; name-only/order-only attacker ≤ ceiling.
- **6.6 Schema-alias positive-control battery** (§7).
- **6.7 No-intervention ablation must collapse** (§9, candidate phase).
- **6.8 Shuffled action→channel mapping must collapse** (§9, candidate phase) — the causal-faithfulness gate.
- **6.9 Replay-from-serialized-belief**, anti-stored-hash (§10, candidate phase).
- **6.10 Governance gates (non-deferrable):** fail-able fields; access parity; frozen+hashed thresholds (`THRESHOLDS_FROZEN_BEFORE_RUN=true`); source-hash provenance; truth isolation (truth-stream seeds disjoint from any seed the learner observes).

**Preflight admission rule.** Codex Phase 0 may emit
`preflight_admitted_for_candidate_design` **only if** 6.1 returns
`non_identifiability_present`, 6.2 returns `interventional_headroom_present`, 6.3
is *defined and beatable-in-principle* (panel specified, parity contract written),
and 6.4–6.10 are specified with demonstrated failing negative controls. If 6.1 or
6.2 fails, **Route C dies at design — a clean, contract-preferred negative, not a
defect to repair.**

---

## 7. Leakage / alias positive controls

Each control has: **clean case** (real path), **injected case** (deliberately
broken generator/bundle), **expected scanner result**, **expected score change**,
and a **terminal blocker** that fires if the scanner does *not* react. A scanner
that cannot be made to fire is itself a blocker (`blocked_by_non_fail_able_control`).
This battery is what makes every Phase 0 gate fail-able and is the structural
answer to the ACSB non-fail-able-field collapse (F4/F5).

```python
def inject_hidden_self_set_as_legal_field(bundle): ...      # L1: add membership flag to LegalObservation
def inject_unpermuted_channel_ids(bundle): ...              # L2: expose original index as handle
def inject_action_label_alias(bundle): ...                  # L3: name do-action after its target channel
def inject_query_label(bundle): ...                         # L4: put truth into Query
def inject_confounder_label(bundle): ...                    # L5: expose U / W in legal rows
def inject_intervention_return_shape_leak(bundle): ...      # L6: API returns responded-channel flag/effect size
def schema_only_attack(bundle): ...                         # L7: run schema_only_attacker on real bundle
def import_oracle_formula(bundle): ...                      # L8: call-graph/AST scan for target-generator reachability
def run_leakage_scanner(clean_or_injected_bundle) -> LeakageReport: ...
```

| ID | Control | Clean case | Injected case | Expected scanner | Expected score change | Terminal blocker if it does not fire |
|---|---|---|---|---|---|---|
| L1 | hidden self-set injected as legal field | scanner silent; obs-only ≈ chance | `S` membership readable in `LegalObservation` | **fires: self-set-in-legal** | obs-only → ≈1.0; 6.1 → `blocked_by_observation_decodable_self_set` | `blocked_by_hidden_self_set_leakage` |
| L2 | unpermuted channel index leak | silent; handles opaque | original index recoverable from handle | **fires: identity-not-permuted** | name/order attacker → ≈1.0 | `blocked_by_schema_alias_leakage` |
| L3 | action label alias | silent | do-action named/ordered after target | **fires: action-label-alias** | label-only attacker → ≈1.0 | `blocked_by_action_label_leakage` |
| L4 | query label leak | silent; Query answer-free | truth embedded in `Query` | **fires: answer-in-query** | any reader → 1.0 | `blocked_by_non_fail_able_control` |
| L5 | confounder label leak | silent; `U,W` oracle-only | `U`/`W` in legal rows | **fires: confounder-in-legal** | obs-only → high (de-confounds passively) | `blocked_by_observation_decodable_self_set` |
| L6 | intervention API return-shape leak | silent; API returns values only | API returns responded-channel/effect flag | **fires: api-effect-label** | oracle/any-int reader → 1.0 even at `g=0` | `blocked_by_intervention_api_leakage` |
| L7 | schema-only attack on real bundle | attacker ≤ ceiling | (n/a — run on real path) | silent on clean | none (≤ ceiling) | `blocked_by_schema_alias_leakage` if attacker > ceiling on real path |
| L8 | oracle-formula import (AST/call-graph) | no legal module reaches `S`/`U`/`g`/target-generator | a legal module imports the oracle path | **fires: oracle-reachable** | candidate/baseline → 1.0 | `blocked_by_provenance_gap` |

The clean run of all L1–L8 plus 6.1/6.2 passing is the only route to
`preflight_admitted_for_candidate_design`. Every injected run must be archived in
`leakage_positive_controls.json` showing the verdict flipped (proof of
fail-ability), so an auditor can confirm scanners fire rather than trusting a
clean report.

---

## 8. Candidate design placeholder (NOT authorized in Phase 0)

A bounded sketch for a *later* candidate task only. **Phase 0 implements none of
this.** A candidate is admissible only after `preflight_admitted_for_candidate_
design` and a separate candidate task card.

```python
def init_belief(n_channels: int) -> SelfBoundaryBelief:
    """Uniform logits over handles (prior). No channel identity, no S."""

def update_belief_from_intervention(belief, action: InterventionAction,
                                    result: InterventionResult) -> SelfBoundaryBelief:
    """Bayesian/online update from the OBSERVED post-intervention values only.
    Reads result.post_handle_values + which handle it acted on. MUST NOT read S,
    U, gain, original index, or any effect label. Increments belief for handles
    whose post-do shift is large relative to passive baseline."""

def predict_self_set(belief, threshold: float) -> set[int]:
    """Top-k handles by belief (k public). Returns permuted handles."""

def serialize_belief(belief) -> dict:
    """Round-trippable; the object §10 replay reloads and recomputes from."""
```

**Hard rule.** The candidate may use only legal observations, its own
intervention API, and intervention outcomes. It may **not** use channel identity
(original index), hidden `S`, confounder `U`/`W`, query truth, gain `g`, or
original channel order. Violations are caught by §7-L8 (AST/call-graph) and the
§6.4 input-contract control. The candidate's claim is adjudicated **only** by
§6.3 (`candidate − max fair interventional baseline`), never by beating
observation-only.

---

## 9. Required ablations for later candidate task (defined; deferred)

Each is a **fresh rerun** (no stale/literal reports, risk #10), artifact
`ablation_report.json`, run-stamped provenance.

| Ablation | Manipulation | Expected collapse | Blocker if it does NOT collapse |
|---|---|---|---|
| `no_intervention` | candidate sees passive rows only (empty `intervention_log`) | → obs-only chance ceiling | `blocked_by_non_load_bearing_update` (it wasn't using interventions) |
| `shuffled_action_channel` | permute which action affects which channel; machinery still "active" | → ceiling (true coupling broken) | leakage: it reads the answer elsewhere → `blocked_by_*_leakage` |
| `randomized_intervention_effects` | replace do-effects with noise | → ceiling | `blocked_by_non_fail_able_control` |
| `frozen_belief` | disable `update_belief_from_intervention` | → prior/chance | `blocked_by_non_load_bearing_update` |
| `no_causal_update` | accumulate samples but never condition on do-target | → ceiling | `blocked_by_non_load_bearing_update` |
| `schema_only_candidate` | candidate restricted to schema features | ≤ ceiling | `blocked_by_schema_alias_leakage` |
| `observation_only_candidate` | candidate = obs-only path | ≤ ceiling (= 6.1) | `blocked_by_observation_decodable_self_set` |

A candidate that survives `no_intervention` or `shuffled_action_channel` is, by
construction, not using interventions causally ⇒ mechanism void.

---

## 10. Replay requirement (defined; deferred to candidate task)

```python
def replay_from_serialized_belief(serialized_belief, legal_intervention_log,
                                  queries) -> ReplayResult:
    """Reload belief, RECOMPUTE predict_self_set + downstream behavior from the
    deserialized state and the legal intervention log. Must match the live run
    within tolerance. Recomputation, NOT a hash/string compare."""

def corrupt_serialized_belief(serialized_belief) -> dict:
    """Zero / shuffle / perturb the serialized logits."""
```

Anti-stored-hash control: replay on a `corrupt_serialized_belief` output **must
change** the recomputed behavior. If replay still "passes" on corrupted belief ⇒
it is comparing a stored hash, not recomputing ⇒ `blocked_by_replay_hash_only`.
Replay must depend on the serialized boundary state, **not** on same-step legal
observation (the ACSB re-entry condition).

---

## 11. Artifact schema (Phase 0)

All under `artifacts/route_c_preflight_001a/`. **No artifact = no evidence**
(contract). On any STOP, downstream artifacts are emitted as
`{skipped: true, reason: <stop>, stop_conditions: [...]}` (the ACOLB-A pattern),
never silently omitted.

```
artifacts/route_c_preflight_001a/
├── route_c_preflight_result.json     # top-level verdict, mechanism_claim_admitted=false, claim_ceiling
├── non_identifiability_report.json   # 6.1: obs/schema/name-order scores, ceiling, verdict
├── interventional_headroom_report.json  # 6.2: obs vs oracle, band, verdict
├── obs_only_baseline_report.json     # per-episode obs-only F1 + provenance
├── schema_attack_report.json         # schema/name-order attacker scores + provenance
├── leakage_positive_controls.json    # L1..L8 clean vs injected, verdict-flip proof
├── trace.jsonl                       # per-episode: seed, regime, predicted/truth, F1, gate inputs
├── claim_ceiling.txt                 # frozen ceiling text (design-only)
└── failure_manifest.json             # iff any gate STOPs: stop_conditions[], verdict
```

Every score (`ScoreRecord`, §5) MUST carry, and the §12 provenance test asserts:

```
producer_function          # callable that computed it (cf. ACOLB headroom_preflight producer_function)
inputs                     # refs/hashes of the frozen inputs consumed
run_id                     # this run
seed / episode_ids         # which seeds/episodes
aggregation                # e.g. "mean_episode_score"
code_path_hash             # source hash of candidate/generator/baseline/evaluator (provenance contract)
threshold_used             # the frozen threshold compared against
threshold_frozen_before_run = true     # else blocked_by_threshold_tuning
computed_not_literal = true            # else blocked_by_provenance_gap  (no constants/static dicts)
failure_path_available = true          # the gate CAN return fail (else non_fail_able)
```

`route_c_preflight_result.json` (admit case) shape:

```json
{
  "verdict": "preflight_admitted_for_candidate_design",
  "mechanism_claim_admitted": false,
  "non_identifiability": "non_identifiability_present",
  "interventional_headroom": "interventional_headroom_present",
  "leakage_controls": "all_fired_on_injection",
  "thresholds_frozen_before_run": true,
  "claim_ceiling": "Route C preflight design admission only; no mechanism, no Gate, no candidate result"
}
```

---

## 12. Test plan (Phase 0 pytest)

`tests/route_c_preflight_001a/`. Each test maps to a falsification obligation;
several are **expected-fail-on-injection** to prove gates are fail-able.

| Test | Asserts |
|---|---|
| `test_generator_determinism` | same `(seed, config)` → byte-identical episodes (T1) |
| `test_passive_cannot_decode_self_set` | obs-only F1 ≤ chance+band on clean generator; **twin-pair** (§3.3) indistinguishable |
| `test_schema_only_attacker_fails` | schema-only attacker ≤ ceiling on real path |
| `test_name_order_attacker_fails` | name/order attacker ≤ ceiling; permutation actually applied |
| `test_interventional_oracle_beats_obs` | oracle − obs-only > HEADROOM_BAND on clean generator |
| `test_hidden_self_set_injection_is_caught` | L1 injected → 6.1 returns `blocked_by_observation_decodable_self_set` (fail-able proof) |
| `test_zero_gain_kills_headroom` | `gain=0` → 6.2 returns `blocked_by_no_interventional_headroom` (fail-able proof) |
| `test_channel_permutation_changes_identities` | same `S` (original) → unrelated handles across episodes |
| `test_train_test_seed_disjoint` | truth-stream seeds ⟂ learner-observed seeds (truth isolation) |
| `test_obs_only_intervention_contamination_fails` | if `intervention_log` non-empty for obs-only → hard error (no accidental do-data) |
| `test_failure_manifest_emitted_on_block` | any STOP writes `failure_manifest.json` + skipped downstream artifacts |
| `test_strongest_baseline_is_argmax` | `select_strongest_*` returns argmax-by-number, not hand-pick |
| `test_provenance_rejects_literal_scores` | a score lacking `computed_not_literal`/`code_path_hash`, or a static-constant score, is rejected → `blocked_by_provenance_gap` |
| `test_leakage_controls_all_fire` | each of L1–L8 injected flips the verdict; a non-firing control → `blocked_by_non_fail_able_control` |

---

## 13. Codex Phase 0 implementation card

```yaml
task_id: ROUTE-C-PREFLIGHT-001A
parent_blueprint: ROUTE-C-PREFLIGHT-001A-HOSTILE-DESIGN-BLUEPRINT   # this document, read-only
task_type: bounded preflight implementation (generator + baselines + oracle + controls + gates)
layer: engineering implementation + mechanism-hypothesis preflight   # NOT subjectivity/consciousness
role: implementer   # NOT designer, NOT hostile auditor (role separation, contract)

problem_definition: >
  Implement ONLY the Route C Phase 0 falsification harness: generator (§4),
  observation-only baseline + schema/name-order attackers (§6.1), interventional
  oracle (§6.2), leakage/schema positive controls L1-L8 (§7), and Phase 0 gates
  6.1 + 6.2. Determine whether the surface even instantiates non-identifiability
  with interventional headroom, BEFORE any candidate exists. A blocked result is
  the contract-preferred outcome and must be preserved, not patched.

current_stage: pre-implementation (no src/tests/artifacts for route_c_preflight_001a exist)

hypothesis: >
  On the confounded generator (§3), observation-only is at chance (k/C) by
  construction while a randomized-intervention oracle exceeds it beyond
  HEADROOM_BAND. Honest-null outcomes are equally acceptable: obs decodes S
  (premise void) or oracle ties obs (no headroom) -> Route C dies at design.

baseline: obs_only_baseline; schema_only_attacker; name_order_attacker (§6.1). Oracle = ceiling only (§6.2).
ablation: NONE in Phase 0 (candidate-phase, §9). Fail-able controls: gain=0 (kills 6.2), L1 inject (kills 6.1).
trace_replay_requirement: trace.jsonl per §11; replay deferred (no candidate/belief to serialize yet).

candidate_implementation: FORBIDDEN in this task (Phase 0 is candidate-free).
fair_interventional_panel: SPECIFIED ONLY (§6.3), not implemented here.

acceptance_gate: >
  Emit preflight_admitted_for_candidate_design IFF 6.1=non_identifiability_present
  AND 6.2=interventional_headroom_present AND all L1-L8 fire on injection AND
  thresholds_frozen_before_run AND no forbidden path touched. Otherwise emit the
  matching blocked_* verdict + failure_manifest.json.

claim_ceiling: >
  Route C preflight evidence only (does non-identifiability + headroom hold on
  this constructed generator/seeds/thresholds). No mechanism, no candidate result,
  no Gate, no mainline, no agency/autonomy/consciousness/emotion, no stable user
  benefit, no EGO/companion readiness, no proof of any total theory.

allowed_paths:
  - src/route_c_preflight_001a/**
  - tests/route_c_preflight_001a/**
  - artifacts/route_c_preflight_001a/**

forbidden_paths:
  - any candidate implementation or Route C mechanism claim
  - any Gate run (Gate0-5), bridge, tournament, runtime, scheduler, admission
  - src/acsb_*, src/action_conditioned_self_boundary_*  (ACSB files, read-only history)
  - src/acolb_*  (ACOLB files, read-only history)
  - src/acp_bv_*  (ACP-BV files, read-only history)
  - ego_mainline/*, companion/product/LLM/RAG/AIRI/UI, global schemas
  - docs/** rule sources (this blueprint, the route decision, the ACSB closure,
    the provenance contract) -> read-only
  - any push / tag / remote-anchor script

allowed_outcomes:
  - preflight_admitted_for_candidate_design
  - blocked_by_observation_decodable_self_set
  - blocked_by_no_interventional_headroom
  - blocked_by_schema_alias_leakage
  - blocked_by_non_fail_able_control
  - blocked_by_provenance_gap

hard_blockers (any -> STOP + failure_manifest.json, no mechanism claim, preserve artifacts):
  - blocked_by_observation_decodable_self_set
  - blocked_by_no_interventional_headroom
  - blocked_by_schema_alias_leakage
  - blocked_by_action_label_leakage
  - blocked_by_hidden_self_set_leakage
  - blocked_by_intervention_api_leakage
  - blocked_by_non_fail_able_control
  - blocked_by_provenance_gap
  - blocked_by_forbidden_path
  - blocked_by_codex_success_redefinition

prohibitions:
  - do NOT implement a candidate or the fair interventional panel (defer)
  - do NOT tune confounder_strength / gain / ceiling / bands after seeing results
  - do NOT add interventional data to the obs-only baseline
  - do NOT redefine a blocked_* outcome as success; do NOT patch a STOP into a pass
  - do NOT edit ACSB/ACOLB/ACP-BV files, this blueprint, or any docs rule source
  - Auto-Remote-Anchor: FORBIDDEN (no push, no tag, no remote anchor)

stop_condition: emit failure_manifest.json on first hard blocker; preserve all artifacts; stop.
rollback_plan: >
  All work confined to the three allowed paths. Rollback = delete
  src/route_c_preflight_001a, tests/route_c_preflight_001a,
  artifacts/route_c_preflight_001a. No global/schema change, no remote state.

required_final_report (implementer):
  verdict, layer, files_changed, commands_run, tests_run, artifacts_generated,
  obs_only_result, oracle_result, headroom_verdict, non_identifiability_verdict,
  leakage_control_results (L1-L8 fired?), thresholds_frozen_before_run,
  stop_conditions_triggered, claim_ceiling, what_this_does_not_prove, remaining_unknowns

next_role_after_implementation: hostile auditor (separate pass) re-runs + tampers vs this frozen blueprint.
```

A `blocked_*` result is **acceptable and must not be patched.** Codex
redefining a blocked outcome as success is itself the terminal blocker
`blocked_by_codex_success_redefinition`.

---

## 14. Stop conditions (terminal)

Any of the following is a hard STOP: write `failure_manifest.json`, emit skipped
downstream artifacts, preserve everything, do **not** repair or patch into a pass.

- `blocked_by_observation_decodable_self_set` — 6.1 obs-only > ceiling (premise void; the ACSB killer reappeared)
- `blocked_by_no_interventional_headroom` — 6.2 oracle ≈ obs-only (no room for any mechanism)
- `blocked_by_schema_alias_leakage` — schema/name/order attacker > ceiling
- `blocked_by_action_label_leakage` — action/channel label decodes target without effects
- `blocked_by_hidden_self_set_leakage` — `S` reachable from a legal field
- `blocked_by_intervention_api_leakage` — do-API return shape leaks responded channel/effect
- `blocked_by_non_fail_able_control` — a gate/scanner cannot be made to return fail
- `blocked_by_provenance_gap` — a reported value is literal/static or lacks source-hash/computed-not-literal
- `blocked_by_forbidden_path` — any write outside the three allowed paths
- `blocked_by_codex_success_redefinition` — a blocked outcome relabeled as success

`blocked_by_fair_interventional_saturation` (6.3) is a candidate-phase terminal
STOP, not reachable in Phase 0 (no candidate), listed for lineage continuity.

---

## 15. Claim ceiling

This blueprint supports **Route C preflight design only.** It does **not** prove:
Route C works; self-boundary is a real mechanism; non-identifiability or headroom
actually hold (those are future *executable* outcomes, untested here); any Gate
pass; any mainline/EGO/companion effect; agency; autonomy; consciousness;
emotion; subjectivity; stable user benefit; or the correctness of Bio-CMBC /
CVPSM / VCCO / CMBC / R-G. It does not convert any prior ACSB artifact into valid
mechanism-negative evidence (they remain invalid-harness/hygiene lessons). It does
not authorize Codex implementation, a Gate run, tagging, or remote anchoring —
the §13 card is a *draft authorization template*, activated only by an explicit
separate instruction. **Auto-Remote-Anchor: forbidden.**

---

## 16. Acceptance self-audit (this Claude task vs its own gate)

Accept-criteria (all required):

| Criterion | Where satisfied |
|---|---|
| every §6 gate has function-level pseudocode | §6.1 (`obs_only_baseline`, `schema_only_attacker`, `name_order_attacker`, `non_identifiability_premise_gate`), §6.2 (`interventional_oracle`, `interventional_headroom_gate`), §6.3 (panel + `select_strongest…`, `fair_interventional_saturation_gate`) |
| Phase 0 is candidate-free | §8 marked NOT authorized; §13 `candidate_implementation: FORBIDDEN`, `ablation: NONE in Phase 0` |
| generator + legal schemas explicit | §4 signatures + §3.2 equations; §5 dataclasses with CL/BL/H/OO/AB/D tags |
| observation-only failure tested, not assumed | §6.1 fail-able control (L1 must flip verdict) + §12 `test_passive_cannot_decode_self_set` + twin-pair test; §3.3 proves it but §12 still measures it |
| interventional oracle headroom tested | §6.2 + §12 `test_interventional_oracle_beats_obs`; gain=0 fail-able control |
| schema/identity leakage controls concrete | §7 L1–L8 table (clean/injected/scanner/score-change/terminal blocker) |
| fair interventional baselines specified for later candidate comparison | §6.3 full panel + access-parity + argmax selection + `candidate − max fair` rule |
| Codex Phase 0 card included | §13 |
| stop conditions terminal | §14 (terminal, no-patch) + §13 `hard_blockers` |
| no mechanism claim | §1 explicit non-claim, §15 ceiling, `mechanism_claim_admitted=false` in artifacts |

Reject-criteria (all avoided):

| Reject if… | Avoided by |
|---|---|
| jumps straight to candidate | §8 deferred; Phase 0 candidate-free (§13) |
| only proves intervention beats observation | §6.3 makes the load-bearing comparison `candidate − max fair interventional baseline`; §2 F6 + §3.5 call out `interventional−observational` as insufficient |
| lacks fair interventional baseline plan | §6.3 panel specified |
| ignores ACSB prior collapse | §2 maps F1–F6 to gates; §3.3 is the structural negation of `phase_bit XOR action_bit` |
| channel-identity leakage underspecified | §4 per-episode `π` + opaque handles; §5 hidden original index; §7 L2/L3; §12 permutation test |
| Codex free to tune confounding after results | §3.5 + §6.10 frozen+hashed thresholds; §13 prohibits post-hoc tuning; `blocked_by_threshold_tuning` |
| pass-shaped reports without failure controls | §7 every control ships an injected verdict-flip; §6.1/6.2 ship fail-able negative controls; §12 `test_leakage_controls_all_fire`, `test_provenance_rejects_literal_scores` |

---

## 17. Final report block

- **Verdict:** Route C hostile design blueprint produced; Phase 0 specified as candidate-free falsification harness; §6 gates bound to ACSB re-entry conditions; Codex card `ROUTE-C-PREFLIGHT-001A` drafted (not authorized). No implementation, no Gate, no mechanism claim.
- **Layer:** mechanism-surface design + preflight design only.
- **Files changed:** none in repo (blueprint delivered as a standalone document; recommended repo home `docs/research/ROUTE-C-PREFLIGHT-001A-HOSTILE-DESIGN-BLUEPRINT.md`, to be placed by the user). No `src/`, `tests/`, `artifacts/` touched.
- **Commands run:** read-only inspection of the authorizing route decision, the ACSB downgrade closure, the ACOLB Codex card + artifacts, and the provenance contract. No experiment, no test, no git mutation.
- **Artifacts generated:** none (design document is the deliverable; consistent with "not a Gate run").
- **Baseline / ablation / replay results:** n/a (no run; all are *future executable* obligations specified in §6/§9/§10).
- **Stop conditions triggered:** none (design task). Route C STOP conditions pre-registered (§14) but unevaluated.
- **Claim ceiling:** §15.
- **What this does not prove:** §15 — no mechanism, no non-identifiability/headroom result, no Gate, no mainline effect, no agency/autonomy/consciousness/emotion/subjectivity, no EGO/companion readiness.
- **Remaining unknowns:** (i) whether a generator can instantiate genuine non-identifiability without same-step observation leakage (6.1, untested); (ii) whether a fair interventional baseline saturates the candidate once it exists (6.3, untested); (iii) whether the recurring non-fail-able-field defect class is structurally closed by the §7 injected-control battery or merely scanner-patched.
