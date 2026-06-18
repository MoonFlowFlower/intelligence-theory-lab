# GROUNDING-GATE — K1/K2 PREFLIGHT FEASIBILITY (001A)

Status: **candidate-free design-stage feasibility analysis.** NOT a task card. NOT an
experiment. Authorizes no implementation, no candidate, no code run, no schema change, no
commit/push/tag/anchor. This document answers ONE question demanded by
`SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A.md` §4 and by
`SESSION-HANDOFF-001A`: *for the proposed Grounded World-Model / Self-State Intervention
Gate, can K1 (obs-decodability) and K2 (interventional-baseline saturation) be answered?*
Per the catalog: if K1/K2 cannot be answered, the card is not ready to draft — and that is
the **contract-preferred negative answer**, the route closes here.

Research layer: engineering implementation + mechanism hypothesis. **NOT** subjectivity /
consciousness / affect-validation / agency. (Asserting otherwise = K7 violation.)

---

## 0. The proposal, restated precisely

External review (GPT) recommends a latent `L` such that a single **do-intervention**
`do(L=v)` coherently changes three readout channels:
- **prediction** of future observation,
- **report** (structured/discrete; NO LLM),
- **action**,

where `L` is **non-obs-decodable**, **history-integrating**, and **non-enumerable**, in a
**minimal custom world** (not MiniGrid/Crafter). Best-case claim if it ever passed (catalog
ceiling, binding): *"bounded evidence of a non-obs-decodable, interventionally-valid latent
that causally co-binds prediction/report/action against a fair panel, in one minimal
world."* Nothing about self, feeling, emotion, agency, autonomy, subjectivity.

This route is **not new**. It is the lab's ACSB → Route C family. Re-entry must beat the
documented killers point by point.

---

## 1. Prior negative evidence (verified this session, not asserted)

AIDSP-001A-R1 `result.json` read via file API (FUSE-truncation hazard avoided):
- `verdict = baseline_equivalence_or_no_separation`
- `prereg_sha256 = c594f4ae…`, `code_path_hash = 6b8a6b61…`
- `multi_seed_consistent = false`; family A `epistemic_ablation_removes_advantage = false`
  (curiosity term **redundant**; winner = transition-conditioned model-based inference),
  family B `m1_beats_all_fair_by_band = false`.

Standing lineage (from killer catalog §1, anchors carried forward):

| # | Experiment | Killed by |
|---|---|---|
| 1 | ACSB (`d5b4b92`) | **K1** obs-decodability: target = phase XOR action, both in legal obs → obs-only == oracle |
| 2 | ACSB-001B (`347b75b9`) | **K4** fake challengers: "learned" baselines were deterministic, rigged to 0 → gate non-fail-able |
| 3 | ACOLB-A | **K2** fair-baseline saturation: candidate ≡ batch discounted-LS *algebraically*, margin 0.0147 < band |
| 4 | Route C preflight (`726f26d`) | **K1** non-identifiability asserted-not-tested: obs-baseline never read passive values; value-level probe broke it |
| 5 | Candidate-free Route C separation probe | **K3+K2** recall-only metric + missing `predict_all` → add it, separation = 0 |
| 6 | AIDSP-001A-R1 (`6b8a6b61`) | principled term redundant; tie/no-separation (first to *cleanly* defend the killers) |

**Cross-cutting prior (update on this, do not route around it):** every principled mechanism
in this family has collapsed to a simpler fair/observational baseline once the panel and
metric were made honest. The base rate for "new principled latent beats fair panel" in this
lab is **zero**.

---

## 2. K1 — observation-decodability: **ANSWERABLE** (accepted template exists)

Defense construction (buildable on paper):
- World where `obs_t` is a **noisy partial projection** of state; `L` is a history-integrated
  sufficient statistic not recoverable from `obs_t` (nor from a **pre-declared** obs window).
- **Capable obs-baseline:** a *family* of fitted passive predictors (supervised
  regression/classifier, covariance, k-NN, clustering) of each channel from `obs_t` (+
  declared window), at full capacity, scored by **family_max** — never a single weak attacker.
- **Value-level decode positive control:** inject `L` into the observation *values*; the gate
  MUST flip to `blocked` (obs-baseline becomes ≈ candidate). If a planted leak cannot make the
  obs-baseline win, the obs-baseline is underpowered → Route C preflight failure (#4), STOP.

Status: this is exactly the **accepted** Route-C-preflight obs-baseline repair (`278819a`:
capable attacker family + family_max gate + value-level control; verdict admitted). So K1 has
a known-good, independently-accepted answer.

Residual K1 risk (must be pre-registered, not waved): (a) the obs-window must be declared
(current-only vs windowed) or "non-decodable" is ambiguous; (b) family_max over a genuinely
capable family, or K1 silently reduces to the underpowered-attacker failure again.

**K1 verdict: answerable.**

---

## 3. K2 — interventional-baseline saturation: **the blocking finding**

Required separation (catalog, binding): `separation = candidate − max(fair interventional
panel)`, panel including the `predict_all`-analog per channel **and** a capable **fitted**
interventional baseline.

The decisive fair baseline here is **independent per-channel regressors**: fit three separate
maps `(do(L)=v) → channel_k` on interventional data, one per channel, **no shared latent**. At
test, each head reads the intervened `L` and emits its channel.

Core problem (this is why the route, as posed, fails the gate-to-draft):

> "Intervene on `L` → all three channels change coherently" is, behaviorally, **exactly what
> three independent per-channel regressors fitted on the same `do(L)` distribution produce.**
> The shared-latent ("co-binding") story is **explanatory surplus** over the independent-heads
> baseline. Under access parity (equal data, equal capacity) in a small world, candidate and
> independent-heads **TIE → baseline-equivalence** — the ACOLB-A death (candidate ≡ fair
> estimator), reborn for the latent.

The ONLY axis on which a shared latent can provably beat independent heads is **cross-channel
transfer under channel-imbalanced data**: train with rich prediction data but sparse
report/action data; a shared bottleneck transfers from the data-rich channel to the data-poor
ones, independent heads cannot. This *is* testable and fail-able. But it carries three fatal
consequences for the proposal:

1. **It reframes the gate.** The honest, identifiable question is not "is there a self-state
   latent?" It is **"does a shared bottleneck transfer across channels better than independent
   single-task heads under data imbalance?"** — i.e., textbook multi-task representation
   sharing. A known ML phenomenon, world-dependent, sometimes true and sometimes false. Not
   novel, and not about self.
2. **Its claim ceiling collapses far below the goal.** The most a pass could state is "a shared
   bottleneck transferred across channels in one world." Upgrading that to self / self-state /
   subjectivity = **K7 violation + project forbidden claim**.
3. **Even the transfer pass can saturate.** A fair panel must then also include a
   **shared-low-rank fitted baseline** (one shared feature basis feeding all three heads — a
   fitted, candidate-free model that *also* exploits transfer). The candidate's shared latent
   most likely ties *that* → saturation again, one level up. To avoid silent saturation the
   panel MUST contain this baseline, which is precisely the baseline most likely to tie.

**K2 verdict: technically state-able, but the honest pre-registered expectation is
baseline-equivalence, and the only identifiable residue (transfer) dissolves the proposal's
own claim.** The "self-state co-binding latent" is **non-identifiable** against a fair
independent-heads panel. That is a K2 answer — and it is negative.

---

## 4. K3–K7 (for completeness; none rescues K2)

- **K3 metric degeneracy** — answerable. Reuse AIDSP triviality-probe template: per-channel
  `predict_all` must score low; balanced/exact-set metric or capped `|pred| ≤ K` for ALL agents
  incl. oracle; trivial winner → `invalid_metric_degenerate`.
- **K4 fake challenger panel** — answerable but is the live execution risk: independent-heads,
  shared-low-rank, and fitted estimator must be **real `.fit` models** on the discriminating
  fields, with a capacity/learning check, never stubs rigged to 0 (the ACSB-001B death).
- **K5 non-fail-able self-declared fields** — answerable. Reuse AIDSP `compute_verdict`
  boolean-conjunction + planted positive controls that flip each field. No
  `computed_not_literal=True` literals.
- **K6 semantic leakage + candidate==label-generative** — answerable, with one route-specific
  trap: the **report channel must not be a near-bijection of `L`**, else "report changes when
  `L` changes" is tautological. Report must be a *lossy* discrete channel + an MI-based scanner
  (AIDSP caught a renamed leak at MI ≥ 0.9·H).
- **K7 claim-ceiling leakage** — the highest-temptation failure here. Given §3, a "transfer"
  pass dressed as "self-state grounding" is the exact inflation the contract forbids.
  Buildable ≠ passed; transfer-passed ≠ self.

Extra catalog §3 constraints: report = structured/discrete no-LLM (designable, but see K6);
latent history-integrating + non-enumerable (designable, but **in tension** with the
small-world requirement that lets independent-heads fit cheaply — and the transfer gap depends
entirely on per-channel data budget, a tunable that is itself a threshold-tuning hazard);
minimal custom world (fine).

---

## 5. Verdict (gate-to-draft)

- **K1:** answerable (accepted `278819a` template).
- **K2:** answerable only by reframing "co-binding latent" into "shared-bottleneck transfer vs
  independent heads + shared-low-rank baseline under data imbalance." Under the honest framing,
  (a) the lineage prior predicts a tie, and (b) even a pass evidences representation-sharing,
  **not** the self-state co-binding that motivated the route.

Therefore, **as posed (self-state grounding), the route does NOT clear the gate to draft**: its
central claim is non-identifiable against a fair panel, exactly per the standing lineage. A card
*could* be drafted for the **reframed transfer test**, but that test's best-case claim is far
below the goal and most likely ties — i.e., spending the design budget to most-probably bank
another "principled mechanism ≡ fair baseline" negative.

This is the **contract-preferred negative answer** the handoff anticipated.

---

## 6. Lowest-cost validation step (the cheapest possible kill — requires authorization to run)

A **candidate-free numerical identifiability check** (one isolated file, no candidate, no
mechanism): in a toy `do(L)` world, fit (a) independent per-channel regressors and (b) a
shared-low-rank regressor on equal data; measure whether they reproduce "intervene → all three
channels change coherently."
- **Expected (per §3):** yes → the co-binding claim is **empirically non-identifiable**, route
  closes WITHOUT ever building a candidate. Cheapest negative available.
- **Only if (surprising):** independent-heads + shared-low-rank **cannot** reproduce co-binding,
  AND a planted value-level leak still flips a K1 obs-baseline → only then is there headroom to
  draft the reframed transfer card.

This is an experiment (produces a numeric result), so per CLAUDE.md it needs an explicit
bounded task card + authorization before running. It is named here, not executed.

---

## 7. Recommendation (decision is the user's)

1. **Primary (recommended):** treat this memo as the preflight result and **close the
   self-state-grounding framing** as not-answerable-as-posed (co-binding non-identifiable vs
   independent heads; only transfer is identifiable, and transfer ≠ self). Bank AIDSP's positive
   engineering finding ("goals + world model already produce the exploratory behavior; explicit
   curiosity is redundant") for any "feels-alive" product use **without** a subjectivity claim.
2. **Alternative (only if spending the cheap design budget is wanted):** authorize the §6
   candidate-free identifiability check first; if (and only if) it surprises, authorize drafting
   a candidate-free preflight DESIGN card for the **reframed transfer test**, hard claim-ceilinged
   to representation-transfer. No candidate, no mechanism code, until that design itself survives
   a K1/K2 paper-check.
3. **Do NOT:** build a candidate first; frame any result as self/agency/emotion; reopen a closed
   surface; or draft a "self-state" card on the strength of a transfer result.

---

## 8. What this does NOT prove

- Does NOT prove the route is impossible in every conceivable world — proves that **as posed
  (self-state co-binding)** it is non-identifiable against a fair independent-heads + shared-low-rank
  panel, and that its only identifiable residue (cross-channel transfer) carries a
  sub-subjectivity claim ceiling.
- Makes and refutes **no** claim about consciousness, subjective experience, real emotion, self,
  autonomy, agency, or companion-readiness at the phenomenal level. The felt/phenomenal residue
  is untouched.
- Authorizes nothing. Weakens no prior artifact. Anchors cited are read-only evidence records.

Anchors: AIDSP-001A-R1 `code 6b8a6b61` / `prereg c594f4ae` (verified) · ACSB `d5b4b92` ·
ACSB-001B `347b75b9` · ACOLB-A (saturation) · Route C preflight `726f26d` · obs-baseline repair
`278819a` (accepted K1 template).
