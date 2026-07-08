# BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A

Status: DESIGN CARD (Red / pre-registration governance). Design-only. NOT mechanism evidence,
NOT an env certification, NOT a candidate authorization, NO scoring in this card.
Drafted by Claude (red_first_designer) 2026-07-08. Awaits operator authorization + a separate
STEP-A pre-registration bank + independent Red-audit before any scoring run (STEP-B).

## task id
`BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A`

## lineage / merges-into (read before implementing)
- INSTANTIATES: `DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A` (Saturation STOP-Gate + role
  separation). This card does NOT define a new headroom rule; it applies that contract's rule as
  a runnable instrument. On any conflict, the contract governs.
- SUBORDINATE TO / DOES NOT WEAKEN: `N2-SBMC-ENV-REDESIGN-001A` (mandatory graph-cache challenger,
  three-way env verdict, STEP-A→Red-audit→STEP-B pattern) and `SAME-AGENT-KERNEL-R4-CONCRETE-ENV-
  ARGUMENT-001A` (subordinate to L-015 `SAME-AGENT-KERNEL-DISCRIMINABILITY-SPEC-001A`).
- CITES FROZEN BASELINE FAMILY + CONTAMINATION-PRINCIPLE DECISION: `N2-SBMC-FRONTIER-REUSE-SCAN-001A`
  (adopt MINJA-family belief-corruption as PRINCIPLE, provenance-clean reimplementation, NOT drop-in
  code; standing identifiability requirement carried, not dissolved by reuse).
- APPLIES: `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` (19 failure families; predict_all / recall
  saturation, observation-decodable, oracle-coupling, label leakage, threshold tuning).
- This card adds NO threshold to N2/R4, weakens NO baseline, introduces NO second schema.

## layer
Phase-0 env-selection PREFLIGHT (engineering implementation + mechanism-hypothesis support).
Candidate-free. No subjectivity / consciousness / agency layer.

## claim ceiling
Design + pre-registration only. The downstream STEP-B run can produce at most, per environment,
a bounded machine-readable **headroom bit**: whether an ideal/oracle detector has reachable
headroom over the strongest fair-baseline floor (incl. the mandatory graph-cache/lookup family),
PLUS a **probe-instrument-valid bit** (did the probe flag the known-saturated control as saturated
AND the known-headroom control as headroom). It CANNOT show mechanism validity, that any borrowed
env is a valid mechanism testbed, learning, transfer, survival capability, agency, autonomy,
emotion, self-awareness, consciousness, EGO/companion readiness, or that any theory-bot "works".
A headroom bit authorizes at most DRAFTING a downstream candidate/attribution card for that env.

## problem definition
The lab's closed-route audit (2026-07-08) found every major in-repo closure is either (A) fair
equal-access baseline saturation / no-headroom, or (B) invalid instrument (oracle coupling,
non-identifiability, lookup collapse). Zero were unfair product-rival kills. The operative
bottleneck is therefore: **before investing in the expensive attribution layer (trace / replay /
ablation / counterfactual) for ANY environment, does that environment even have headroom above a
fair-baseline floor, and can our headroom instrument be trusted?**

A naive "borrow Alchemy/Crafter/bsuite as the mechanism testbed and score theory-bots on survival"
is REJECTED here, for reasons already established in-repo:
1. Borrowed RL benchmarks reward PERFORMANCE (score / survival / achievements), not mechanism
   attribution. A shared survival leaderboard is a `HIGH_SCORE_NO_ATTRIBUTION` generator (same
   failure the ego-pet audit found: candidate 0.996 ≈ schedule-omniscient oracle 0.996).
2. None ship the mandatory graph-cache/lookup challenger floor the constitution requires; none give
   equal-access provenance-clean observation channels or bit-exact replay. Pixel/physics/real-time
   variants make deterministic replay HARDER (cf. the torch-unseeded nondeterminism incident).
3. `N2-SBMC-FRONTIER-REUSE-SCAN-001A` already decided the correct borrow granularity: borrow the
   task-structure PRINCIPLE and the published BASELINES-as-challengers; build the sim + instrument.

So this card reframes "borrow an environment" into "**borrow-first env SELECTION via a calibrated
headroom instrument**": run one frozen fair-baseline battery across a candidate env set AND across
already-adjudicated control envs, and emit per-env headroom bits + a probe-validity bit.

## reconstructed question (framing correction)
Not "which borrowed game should our bots live in?" but:
> Which environments — borrowed or bespoke — pass the Saturation STOP-Gate
> (`strongest_fair_legal_channel_baseline < ceiling - equivalence_band`) on a value-aware,
> equal-access, deterministic, replayable interface, using a probe instrument that is itself
> demonstrably fail-able against a known-saturated env and a known-headroom env?
An env that fails the STOP-Gate is NOT admitted for candidate/attribution work — regardless of how
"alive" or rich it looks. This is env selection, not mechanism evidence.

## current stage
Phase-0 env-selection preflight, candidate-free. Mechanism NOT connected. Attribution layer NOT
built. STEP-A (pre-register unrun harness + frozen numbers + controls) → independent Red-audit →
STEP-B (score). This card is the design; STEP-A is a separate bank.

## environment set (v1 — symbolic / deterministic ONLY)
Adapters expose a minimal frozen interface `(observation O, prediction target y, oracle y*)` with
audit/label separation. NO pixels, NO physics, NO real-time loop in v1 (deferred to a later card).

Controls (fix the probe's fail-ability — these are already adjudicated, so the probe's verdict on
them is known ex ante and MUST match, or the instrument is void):
- POS-INTERNAL: `SAME-AGENT-KERNEL-R4` env `E*` (additive Cayley table `y=(a(r)+b(k)) mod L`,
  held-out cells). R4(a) proves the cache sub-family is ≤ chance (1/L) on `Omega_test`. The probe
  MUST report HEADROOM here (ideal solves connected additive system; cache/lookup at chance). This
  certifies that a gap exists for this probe control; it does NOT certify a mechanism-relevant gap.
- POS-EXTERNAL (feasibility-gated): Alchemy symbolic interface (`dm_alchemy` `symbolic_alchemy`,
  verify current API at adapter time). Published as latent-causal-structure resampled per episode,
  lookup-non-amortizable. Probe MUST report HEADROOM. If cheap symbolic wiring is infeasible, DROP
  and rely on POS-INTERNAL only (record the drop in `failure_manifest.json`; do not fabricate).
- NEG: the tombstoned lookup-solvable scout `P0.5-SBMC-ENV-HEADROOM-SCOUT-001A` (`5a846d5`).
  Proven lookup-saturated. The probe MUST report SATURATED here.

Candidate borrowed envs (principle-borrowed / interface-adapted, provenance-clean; NO hidden label
import):
- MiniGrid (procedural held-out levels; transfer axis) — 1–2 configs.
- bsuite targeted subset (`memory_len`, `memory_size`, a generalization env) — methodology cross-
  check; bsuite ships its own baselines, usable as an independent sanity reference.
- (Optional, only if cheap) one Craftax/Crafter symbolic-state slice for the survival/viability axis
  — NOT pixels; if only pixel access exists, DEFER to the later non-symbolic card.

Internal cross-check envs (do not re-adjudicate; just show the probe agrees with prior verdicts):
- The `N2-SBMC-ENV-REDESIGN-001A` redesigned env, if a STEP-A harness exists — expected verdict
  graph-closure-solvable / lookup-solvable per that card's own honest prior (H3). Agreement is a
  consistency check only; disagreement is a BLOCKING probe defect, not an N2 re-verdict.

## baseline / floor family (frozen fair-baseline battery — the STOP-Gate denominator)
Applied identically to EVERY env (equal access, no per-env tuning). Mandatory members:
- `predict_all` / `predict_none` (saturation & metric-degeneracy guard, per baseline-immunity std).
- `per_user_lookup` / `nearest_neighbor` (memorization).
- `count_table` / `frequency_marginal` (marginal statistics).
- `graph_closure` / arc-consistency (the mandatory graph-cache challenger; per N2, constraint
  propagation belongs IN the floor, not above it).
- observation-only decoder (observation-decodability guard).
- `ideal` / oracle detector = the ceiling reference (NOT a candidate; upper bound only).

Each Phase-B borrowed adapter MUST populate the floor key contract with legal observation-derived
values or explicitly declare the member legitimately N/A before scoring:
- `lookup_key` for `per_user_lookup`;
- `cache_key` for `count_table`;
- `relation_pairs` and `asserted_tuple` for `graph_closure` / arc-consistency;
- `frequency_value` for `frequency_marginal`.
If all structural floor members are no-ops / constant because these legal keys are absent or
uninformative, that env's verdict is `VOID_FLOOR_DEGENERATE`, never HEADROOM.

`ceiling` = the ideal/oracle score on held-out (or 1.0 where an exact oracle exists).
`equivalence_band` = pre-registered in STEP-A and frozen as an ancestor commit BEFORE STEP-B
(anti-tuning red line). Suggested default `0.05` absolute, but the STEP-A card sets and freezes the
exact number with its ex-ante rationale; it MUST NOT be changed after seeing STEP-B scores.

Per-env verdict (callable function over computed rows, per `DISTRIBUTION-HEADROOM-PREFLIGHT-
CONTRACT-001A`):
- `VOID_FLOOR_DEGENERATE` if all structural floor members are no-ops / constant on that env.
- `SATURATED_REJECT`  if `strongest_fair_baseline >= ceiling - equivalence_band`.
- `HEADROOM_ADMISSIBLE` if `ideal - strongest_fair_baseline > equivalence_band` AND ideal is
  meaningfully above chance.
- `UNIDENTIFIABLE`     if even the ideal detector is at/near chance (nothing reaches headroom).

## probe-instrument validity (the instrument must be fail-able)
`probe_valid = (verdict(POS-INTERNAL)==HEADROOM) AND (verdict(NEG)==SATURATED)`
(AND `verdict(POS-EXTERNAL)==HEADROOM` when POS-EXTERNAL is wired).
If `probe_valid == false`, ALL candidate-env verdicts in the run are VOID (the ruler is bent);
report a `failure_manifest.json` and STOP. No env-selection conclusion may be drawn from an invalid
probe. This is the single most important guard: it prevents the probe from being a rubber stamp.

## hypothesis (bounded, with honest prior)
- H1 (LIKELY): POS-INTERNAL `E*` shows HEADROOM and NEG `5a846d5` shows SATURATED → probe valid.
- H2 (prior: MIXED): among candidate borrowed envs, several are SATURATED under equal access
  (memorization/lookup closes them) — i.e. the same A-class ceiling recurs. Do not design toward a
  "borrowed env has headroom" result; report saturation honestly if found.
- H3 (prior: PLAUSIBLE for MiniGrid/bsuite-generalization): held-out procedural novelty yields ideal
  headroom over lookup — but that headroom may be graph-closure/planner-reachable = engineering-
  sufficient, NOT a mechanism signal (same distinction N2 draws). Headroom-admissible ≠ mechanism.

## ablation
- Remove `graph_closure` from the floor → any env that flips SATURATED→HEADROOM is exposed as
  graph-closure-reachable (engineering-sufficient), not a mechanism win. Report the flip set.
- Shuffle observation↔target pairing (destroy structure) → every STRUCTURAL fair baseline
  (`per_user_lookup`, `nearest_neighbor`, `count_table`, `frequency_marginal`, `graph_closure`,
  `obs_only_decoder`) must fall to `<= chance + tol`. The privileged `ideal` / oracle is expected
  to track the shuffled target via `y*` and is NOT the target of this leakage criterion. A callable
  `shuffle_leakage_ok(scores_shuffled) -> bool` is a BLOCKING Phase-B verdict input; any structural
  fair baseline staying high under `shuffle_O_y` is leakage and VOIDs candidate verdicts.

## trace / replay requirement
Every score-bearing row records: env id, adapter sha256, baseline id, split id (train mask / held-
out), raw score, seed, and the RNG-seeding record for np / random / any torch use (per the torch-
unseeded-nondeterminism lesson: each framework seeded explicitly; fresh-process recompute ×2 must
match bit-exact before any verdict). Verdicts derived by a callable function from committed rows,
not hand-entered. Replay reconstructs verdicts from `trace.jsonl` with no future/oracle info beyond
the declared ceiling reference.

## acceptance gate
STEP-B run is admissible as evidence iff: `probe_valid == true`; `shuffle_leakage_ok == true`;
no env verdict depends on an all-constant / no-op structural floor; all baselines callable &
consumed by the verdict function; ablations callable & consumed; two fresh-process recomputes
bit-exact; no floor member omitted; `equivalence_band`/`ceiling` were frozen as an ancestor commit
of the run. Output = per-env `{SATURATED_REJECT | HEADROOM_ADMISSIBLE | UNIDENTIFIABLE |
VOID_FLOOR_DEGENERATE}` + probe_valid.

## MINJA / borrow caution + anti-leakage (carried, not dissolved)
- Borrow the PRINCIPLE and the published baselines; provenance-clean reimplement adapters. Do NOT
  import a borrowed env's hidden labels, reward internals, or answer keys into any baseline or the
  target channel (label-leakage family). The adapter exposes O and y* through an audit/label
  separation boundary identical across envs.
- No borrowed-code drop-in that carries an env's own agent/optimizer as a "baseline" (that would be
  a non-provenance-clean, potentially contaminated challenger).
- Any borrowed dependency pinned by version + hash; network fetch of env assets recorded, not
  silent.

## anti-tuning / role separation (red lines — preserved from 07-05C + headroom contract)
- STEP-A freezes: env set, adapter interfaces, floor family, `ceiling`, `equivalence_band`, control
  expected-verdicts, verdict function — committed as an ANCESTOR of the STEP-B run (commit order is
  the ex-ante proof). Changing any of these after seeing STEP-B scores VOIDS the run.
- `red_first_designer(Claude) != implementer(Codex) != hostile_auditor(Claude, separate later hat)`.
  Claude does not both design and serve as the final hostile auditor of the same scored run.

## stop condition
Stop and report WITHOUT rescuing the route if any of: probe_valid==false; fresh-process recompute
mismatch; a floor member is uncallable/omitted; a structural fair baseline stays above
`chance + tol` under the shuffle ablation on any env (leakage); all structural floor members are
no-ops / constant on an env (`VOID_FLOOR_DEGENERATE`); POS-EXTERNAL infeasible-and-fabricated
instead of dropped; STEP-B attempted before STEP-A ancestor-commit exists. Preserve all failure
artifacts. Do not patch a SATURATED env into HEADROOM by weakening a baseline or changing the band.

## rollback plan
Design-only card: rollback = do not bank / revert the card file; no src touched. STEP-B rollback =
revert the probe run commit(s); `_v1` failure artifacts are preserved (no-delete). No global config,
schema, or N2/R4 frozen spec is touched by this lineage, so rollback is local and complete.

## expected changed files (STEP-A + STEP-B, by Codex; NONE by Claude)
- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.md` (this card, banked)
- `docs/codex/tasks/...-STEP-A-PREREG-001A.md` (frozen pre-registration)
- `scripts/env_headroom_probe/` (isolated; adapters + battery + verdict function)
- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/` (results)

## forbidden changes
`src/` mechanism code; N2/R4 frozen specs; any threshold in the headroom contract; any prior
artifact; EGO mainline; LLM/AIRI integration; UI/companion; pixel/physics envs (v1); global config;
remote anchor; credentials. No candidate/attribution/mechanism implementation.

## expected artifacts (STEP-B)
`result.json` (per-env verdict + probe_valid), `trace.jsonl`, `baseline_comparison.json`,
`ablation_report.json` (graph_closure-removed flip set + shuffle leakage report), `replay_report.json`,
`reuse_matrix.json` (borrow provenance per env), `failure_manifest.json` if anything fails,
`claim_ceiling.txt`.

## claim ceiling / what this does not prove
Bounded env-selection headroom bits + probe-validity bit only. Does NOT prove: any env is a valid
mechanism testbed; any theory-bot works; learning / transfer / survival capability; that HEADROOM_
ADMISSIBLE == mechanism (it may be graph-closure/planner-reachable = engineering-sufficient); agency,
autonomy, emotion, self-awareness, consciousness, EGO/companion readiness. Godot / rich rendering is
explicitly OUT OF SCOPE and belongs to a later product/demo (capability-conformance) layer, never as
mechanism evidence.
