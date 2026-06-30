# TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A

> Status: DRAFT, revised **R1** (2026-06-29) after external red-team audit
> (blocking C1–C5 accepted). **Two-stage (C5):** this card may be accepted only as
> DESIGN DIRECTION. Implementation requires a SEPARATE authorized card carrying a
> frozen `preflight_plan.json` sha256, a `route_decision.py` sha256, and execution
> environment constraints. This card alone authorizes NO implementation.
> Blocked-by: `TLGP-001B-R2-PROVENANCE-BANK-001A` (the rung0-failure negative must
> be banked and citable first).
> READ-ONLY rule sources: `artifacts/TLGP-001B-R2/prereg.json` (sha `6e61a831…`),
> `verdict.py`, `lower_reference.py`. This card must NOT modify the TLGP protocol,
> trace schema, baseline contract, failure taxonomy, or capacity grid — doing so is
> a blocking governance-self-modification issue.

## R1 revision log (post external red-team)
- **C1 (bar binding)** — the pass bar is bound to the prereg's exact rung/floor
  function + hash, not a natural-language restatement.
- **C2 (pre-result commitment)** — an explicit `preflight_plan.json` (rungs,
  budgets, seeds, learners, baselines, optimizer, early-stop, metric, decision
  function) must be hash-committed BEFORE any result is read.
- **C3 (terminal added)** — new `route_inconclusive_optimization_or_family_limited`;
  `route_closed_identifiability_ceiling` is tightened to require baseline/graph-cache
  saturation or an admissible upper-bound showing no learner advantage.
- **C4 (no administrative route_closed)** — a no-execution stop yields
  `administrative_abandoned_no_computed_evidence` (NOT banked as a negative, NOT in
  `route_decision.json`), never `route_closed`.
- **C5 (two-stage)** — design acceptance vs a separate implementation card (above).

## Why this card exists
TLGP-001B-R2 banked a clean negative: the primary in-context metas (GRU,
Transformer) at the frozen capacity grid memorized train (~0.97) but collapsed to
~0.45–0.55 on held-out queries of the SAME 8 rules — failing rung0 (the capability
witness), so the transfer question (rung3 / H1) was never reachable. The lab's
standing diagnosis (`itl-why-no-qualified-mechanism-testbed-identifiability-ceiling`)
says the ONLY live mechanism thread is "a cross-episode meta-prior beats a fair
meta-baseline" = TLGP's unfinished rung3 — unreachable until SOME admissible learner
establishes a capability witness.

This preflight decides, candidate-free, whether the rung0 failure is (a) a
training-budget/optimization artifact, (b) a fundamental identifiability-ceiling
property, or (c) removable by selecting a rung whose seen-rule value coverage lets a
fair, capacity-bounded learner reach the prereg bar — WITHOUT capacity inflation and
WITHOUT tuning-to-pass.

Pre-conceded likely outcome (W10): under an equal-access regime the most probable
result is baseline parity / no admissible headroom. The value of running is a CHEAP,
pre-committed tombstone of the route, not chasing a pass. If the design cannot beat
that prior cheaply, prefer closing the route on paper over an expensive run.

Task id: TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A

Problem definition: establish a bounded, falsifiable verdict on whether a capability
witness is attainable on the TLGP world under the frozen access/leakage contract,
separating "learner/budget too weak" from "no fair learner has an identifiability
advantage here." Output is a route decision computed by a named function, not a
candidate.

Current stage/layer: mechanism-route feasibility preflight (engineering +
mechanism-hypothesis). Candidate-free. Not a learning/subjectivity claim.

### Bar binding (C1)
The pass bar and close rule are NOT restated here; they are imported/bound:
```text
bar_source       = artifacts/TLGP-001B-R2/prereg.json@6e61a831...
pass_function    = the exact frozen rung_pass computation (DELTA, close_fraction_min,
                   N_SEEDS aggregation, metric key, terminal precedence) from verdict.py
forbidden        = any local recomputation that changes DELTA, close_fraction_min,
                   seed aggregation, metric key, or terminal precedence
artifact outputs = bar_source_hash, pass_function_hash (recorded alongside results)
```
`route_decision` MUST call this same frozen pass computation.

### Pre-result commitment (C2)
Before any result is read, freeze `preflight_plan.json` and record its sha256 in
this card / the implementation card:
```json
{
  "rungs": ["..."],
  "budgets": ["epochs/steps grid — NOT capacity"],
  "seeds": ["..."],
  "learners": ["in_context_gru", "in_context_transformer", "..."],
  "baselines": ["lookup","count_table","predict_all","majority","no_adaptation","graph_cache","ideal"],
  "capacity_grid_source": "prereg@6e61a831...",
  "optimizer": "...",
  "early_stopping": "disabled or exact rule",
  "metric": "balanced_accuracy exact key",
  "decision_function": "route_decision.py:<sha256>"
}
```
Reading results before this is frozen, or editing it after, → STOP.

Hypothesis (falsifiable, bound to the C1 bar): there exists a rung (seen-rule,
value-coverage regime) and an admissible training budget at the FROZEN capacity grid
on which a fair in-context learner PASSES the prereg `pass_function` on the
prereg-required seed fraction. Falsified if, across the frozen `preflight_plan`
budget sweep, no admissible learner passes on any seen-rule rung.

Diagnostic questions (candidate-free; "unknown" allowed):
1. Is the rung0 collapse a TRAIN vs HELD-OUT-VALUE gap (memorize adapt cells, fail
   unseen query values) or a train-fit failure? (budget vs identifiability)
2. Does the ideal observer itself pass the bar at the rung? (If ideal fails, the
   rung/bar is mis-set → `route_needs_world_rung_redesign`; report, never retune.)
3. Do the fair baselines already saturate the attainable bar? If yes →
   identifiability ceiling for THIS rung.
4. Over the frozen budget sweep (epochs/steps only, capacity frozen), does any
   learner pass? Is the budget→balacc curve a sub-bar plateau or a monotone approach?
   (NB C3: a sub-bar plateau alone does NOT prove a ceiling — see terminals.)
5. Is there a seen-rule rung with partial value coverage where a fair learner
   demonstrably interpolates while lookup/graph-cache cannot — a clean witness with
   power-backed headroom over the fair baseline?

Strongest simpler baselines (mandatory, equal access): frozen `lower_reference`
family + ideal observer ceiling. The graph-cache/lookup family MUST be shown unable
to pass wherever a learner is claimed to pass (else the "capability" is lookup).

Pre-clear traps (each checked, and each wired into the named decision function /
machine-readable artifact, not just prose):
- Identifiability ceiling / equal-access parity (`itl-why-no-qualified-mechanism-testbed-identifiability-ceiling`).
- `predict_all == oracle` / majority-as-oracle (BATCH-ENV-HEADROOM-SCOUT-002A).
- Small-data separation evaporation: separation from an asymptotic gap > ε, not a
  small-N artifact; report MDE/power (`itl-discovery-loop-mde-power-curve-001a`).
- Leakage: meta never receives rule_id or query_e; frozen 001A dual-target MI
  detector per channel per rung (`BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`).
- Capacity inflation: grid FROZEN; only training budget sweeps, pre-committed (C2).
- Killer K1 (obs-decodability) / K2 (interventional saturation)
  (`itl-self-boundary-killer-catalog-001a`).

Trace/replay requirement: every preflight number is computed from a fresh
candidate-free run trace under the existing TLGP trace/replay contract; budget-sweep
points are individually replayable; the route verdict is a named-function output
over recorded numbers, never a literal.

Acceptance gate (for the PREFLIGHT, not for any mechanism): `preflight_plan.json`
frozen + sha recorded BEFORE results; sweep executed at frozen grid; ideal +
fair-baseline + learner balacc recorded per rung/seed; leakage detector clean;
MDE/power reported for any claimed separation; `route_decision.json` produced by the
named function with `bar_source_hash` + `pass_function_hash` recorded.

Claim ceiling: bounded feasibility evidence only — whether a capability witness is
attainable on this world under this frozen contract. Proves NOTHING about transfer
(rung3/H1), mechanism, learning-as-mechanism, agency, self, subjectivity, AGI, or
companion/EGO readiness. `route_open` authorizes ONLY drafting a later candidate
card; it is not transfer evidence.

Route outcomes (computed by the named function from executed-sweep numbers):
- `route_open_capability_witness_feasible` — a fair learner PASSES the prereg bar
  with power-backed headroom over the fair baseline AND graph-cache, leakage-clean.
- `route_closed_identifiability_ceiling` — ONLY if the fair baseline / graph-cache
  saturates the attainable bar, OR an admissible upper-bound shows no learner
  advantage. (Not from a learner plateau alone.)
- `route_inconclusive_optimization_or_family_limited` (C3) — ideal PASSES the bar;
  fair baseline does NOT saturate; no learner passes under the declared budget; CI
  does not merely straddle. NOT a ceiling, NOT underpowered-CI.
- `inconclusive_underpowered` — CI straddles the bar at N_SEEDS.
- `route_needs_world_rung_redesign` — ideal fails the bar, or only forbidden
  capacity inflation would pass (requires a new card, NOT a fix here).

Stop condition: STOP + emit `failure_manifest.json` on — any attempt to enlarge the
capacity grid; bar/threshold tuning after seeing results; leakage detected;
`preflight_plan.json` not frozen before results (or edited after); or route verdict
not derivable from the named function. **No-execution stop (C4):** if no sweep is
executed after two critique-only iterations, emit
`administrative_abandoned_no_computed_evidence` with `claim_ceiling = no new
evidence; route status remains unknown / not evaluated`. Do NOT write a scientific
`route_decision.json`, do NOT bank as a negative, do NOT emit `route_closed`.

Rollback plan: candidate-free, additive analysis only; new files under
`src/tlgp_capability_witness_preflight_001a/` and
`artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/`. No edit to TLGP-R2 source,
prereg, verdict, or banked artifacts. Rollback = delete the new module + artifact
dir.

Expected changed files (only when the SEPARATE implementation card authorizes it):
new isolated preflight module + scoped tests + `route_decision.py` + new artifact
dir + frozen `preflight_plan.json` + this card. Nothing in `src/tlgp_001a/**`,
`src/tlgp_001b*/**`, or `artifacts/TLGP-001B*/**`.

Forbidden changes: TLGP prereg / verdict precedence / capacity grid / trace schema /
baseline contract / failure taxonomy (read-only); `AGENTS.md`, `CLAUDE.md`, global
config; `scripts/push.*`; remote anchor; any candidate mechanism (candidate-free).

Auto-Remote-Anchor: forbidden.

## Bounded Audit

Real objective: decide whether the only-live thread (transfer via cross-episode
meta) is even reachable, by testing the rung0 prerequisite cheaply and fairly — not
to manufacture a witness.

Strongest invalidity risk: declaring a "witness" a fair lookup/graph-cache baseline
also passes (ceiling mislabelled as headroom); clearing the bar via capacity
inflation or post-hoc budget/bar tuning; or cherry-picking a rung after seeing
results (mitigated by C2 pre-commitment).

Falsifying result: fair-baseline parity at the witness rung, or no learner passes
across the frozen sweep → route closed/inconclusive **as computed from the executed
sweep** (never administratively).

Mechanism status: none. Feasibility gate on a prerequisite, candidate-free.

What this does not prove: anything about transfer, mechanism, or subjectivity; a
positive only unlocks drafting a candidate card.

## Collision Record

Approach A — jump to a new candidate meta-learner for rung3 transfer: rejected —
rung0 failed in R2; a candidate now would be untestable and likely re-hit the
ceiling.

Approach B — candidate-free capability-witness feasibility preflight with frozen
plan + named decision function (this card): selected — cheaply separates
budget-bound from ceiling-bound from optimization/family-limited failure.

Approach C — make the world easier until something passes: rejected — tuning-to-pass
/ world inflation; only a separate authorized card with a pre-declared difficulty
rationale may touch world rungs.

Selected approach: Approach B.
