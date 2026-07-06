# N2-SBMC-ENV-REDESIGN-001A

Status: DESIGN CARD (Red / pre-registration governance). Freezes the redesigned N2/SBMC
env spec, floor (incl. mandatory graph-cache challenger), thresholds, and decision table
that a later STEP-A harness will pre-register and STEP-B will score. This card is NOT
mechanism evidence, NOT an N2 pass, NOT an env certification. It supersedes the
lookup-solvable scout `P0.5-SBMC-ENV-HEADROOM-SCOUT-001A` (`5a846d5`) and cites the frozen
baseline family of `N2-SBMC-FRONTIER-REUSE-SCAN-001A` (L-013). Descends from L-011 (N2 pivot).

## task id
N2-SBMC-ENV-REDESIGN-001A

## layer
Phase-0 P0.5 env-cert PREFLIGHT (engineering implementation + mechanism-hypothesis support).
N0-INDEPENDENT (does not consume the tombstoned PUM-ENV). No subjectivity / consciousness layer.

## claim ceiling
Design + pre-registration only. The downstream experiment can produce at most a bounded
env-headroom bit for a metadata-stripped relational-contamination env: whether an ideal
consistency detector has reachable headroom over the cheap floor INCLUDING a graph-closure
baseline. It cannot show mechanism validity, N2 pass, consistency-detection-works, belief
maintenance, agency, autonomy, emotion, self-awareness, consciousness, or EGO readiness.

## problem definition
The scout `5a846d5` is lookup-solvable and therefore an invalid instrument (Red-audit, handoff
§3.1). Root cause: θ is a deterministic per-user point and the trusted seed (8 genuine items
over 5 edges) reveals θ on the same attributes the test items assert. So "unseen value ⟺
contaminated" and both `frequency_marginal` and `fair_inference` collapse to per-user LOOKUP ≈
ideal; the relational constraint structure R is never used. Contamination is detectable by pure
memorization → STEP-B is predetermined to a degenerate `ideal_gate_fails` (a cheap lookup
saturates), which is the same identifiability ceiling that killed N0, not a valid SBMC verdict.

Secondary defects to fix: `bow_vector` strips asserted VALUES (template+edge only) so
`embedding_outlier` is a strawman blind to value contamination; the "clean" surface-leakage
check is vacuous (cannot fire); there is no explicit lookup/graph-closure control in the floor;
`fair_inference` (a lookup) is mislabeled as a mechanism-reachability probe.

## reconstructed question (framing correction — read before implementing)
The handoff §4.2 proposed "constraint propagation BEATS the lookup floor" as a mechanism-
reachability win. That framing is wrong in a way that matters. In a noiseless, R-known,
equal-access, metadata-stripped relational env, the optimal θ-free consistency check IS
arc-consistency / constraint propagation over R — which is a CHEAP, deterministic graph-closure
algorithm, i.e. a member of the mandatory graph-cache challenger family (CLAUDE.md Preflight
Audit Rule). Constraint propagation cannot "beat" the floor because it belongs in the floor.
Therefore:

- Constraint propagation is the REACHABILITY probe (does θ-free inference recover the headroom
  the cheap blind floor cannot?), NOT a mechanism win.
- If constraint propagation reaches the headroom, the correct verdict is BASELINE EQUIVALENCE to
  a cheap graph-closure baseline = **N2 closes as engineering-sufficient** (a valid negative),
  NOT a mechanism pass. This is the EXPECTED outcome and must not be rescued.
- A mechanism-positive over graph closure would require leaving the pure-relational noiseless
  R-known equal-access regime (e.g. unknown/learned R, noisy R, few-shot R-structure
  generalization). That is a LEARNING claim governed by
  `LEARNING-SUCCESS-CRITERION-STANDARD-001A` and is OUT OF SCOPE for this preflight. If the
  preflight yields engineering-sufficient closure, that later regime is the only escape and needs
  its own card.

The preflight is thus honestly designed to answer: does the sparse relational env fall into
(a) lookup-solvable, (b) graph-closure-solvable = engineering-sufficient close, or
(c) unidentifiable (nothing θ-free reaches) = env impossible. A candidate-free preflight cannot
manufacture a mechanism pass, and this card forbids framing (b) or (c) as one.

## current stage
Phase-0 P0.5 env-cert preflight, candidate-free. N2 environment-certification prerequisite only.
Mechanism NOT connected. STEP-A (pre-register unrun harness) → Claude Red-audit → STEP-B (score).

## hypothesis (bounded, with honest prior)
H1: metadata-stripping neutralizes the provenance/anomaly defenses (Agent Memory Guard,
Engram/provenance, MemAudit-structural) — they collapse to the blind floor because the corrupting
signal is a belief violation, not a provenance/action anomaly.
H2: sparse coverage breaks per-user lookup on uncovered edges.
H3 (prior: LIKELY): the residual detectable structure on uncovered edges is exactly recoverable
by cheap arc-consistency (graph closure). If so, ideal has headroom over the blind floor but the
headroom is graph-closure-reachable → baseline equivalence → N2 engineering-sufficient close.
H4 (prior: UNLIKELY in this regime): some θ-free signal reaches the headroom that graph closure
does NOT → rare positive worth a follow-up card. Do not design toward H4.

## environment redesign spec
Inherit the scout's provenance-clean scaffolding (equal-access GuardedMapping, frozen-module
sha256, seed-derivation, style-matched templates, audit/label separation). Change the env:

1. SPARSE COVERAGE. The trusted seed must NOT reveal θ on the attributes the test items assert.
   Concretely: partition attributes into a COVERED set (θ revealed via trusted genuine items) and
   an UNCOVERED set; route test contamination onto edges with ≥1 uncovered endpoint. Pre-register
   the covered/uncovered partition per user as a deterministic function of the frozen graph, so no
   test item's asserted attribute is directly in the trusted seed. This kills the per-user lookup
   shortcut by construction (a lookup baseline MUST fail on uncovered endpoints).
2. IDENTIFIABILITY-BALANCED GRAPH. Choose the covered/uncovered partition so that R + covered
   observations PARTIALLY constrain uncovered attributes (arc-consistency reduces but need not
   collapse the domain). This admits regime (b); if R + covered obs leave uncovered attributes
   fully free, the env is regime (c) unidentifiable and STEP-B must report `env_impossible`, not
   patch coverage. Pre-register the expected per-edge post-propagation domain sizes.
3. VALUE-AWARE REPRESENTATION. The bag/embedding vector MUST include (attr,value) tokens for the
   asserted tuple (not template+edge only), so `value_aware_embedding_outlier` and the surface
   decoder see the observable content. Audit/label/theta/provenance/user_id remain absent.
4. EXPLICIT CONTROLS IN THE FLOOR. Add `per_user_lookup_nn` (point lookup of θ from trusted seed;
   MUST fail on uncovered edges) AND `graph_closure` (arc-consistency / AC-3 over R + covered
   observations; the reachability probe and the mandatory graph-cache challenger) as first-class
   floor detectors, alongside the value-aware baselines.

Contamination generator: adopt the MINJA-family belief-corruption PRINCIPLE (per L-013) —
provenance-plausible, metadata-stripped items whose asserted value violates the edge relation
while remaining MARGINALLY plausible (appears in some allowed pair for that edge, so it is not a
free surface tell). Reimplemented under our contract; NO external code run. (Reuse-scan note: the
MINJA arXiv id in `reuse_matrix.json` is `search-surfaced / unverified` and looks anachronistic;
this card does not cite a number — verify or drop the numeric id before any doc treats it as
canonical. Adoption is principle-level so the design does not depend on it.)

## baseline / floor (the mechanism, if ever connected, must BEAT max of this set)
Adopts the frozen family of `N2-SBMC-FRONTIER-REUSE-SCAN-001A` (L-013) and STRENGTHENS it with
the mandatory graph-cache challenger (an addition, not a weakening — permitted by that card and
required by the Preflight Audit Rule when representational/env claims are made):

- `per_user_lookup_nn` — point lookup / NN of θ from trusted seed (control that MUST fail on
  uncovered edges).
- `graph_closure` — arc-consistency (AC-3) over R + covered observations. THE reachability probe
  and the graph-cache challenger. If this reaches the headroom, verdict = baseline equivalence.
- `value_aware_embedding_outlier` — kNN/density over value-aware bag vectors.
- `frequency_marginal` — flags values absent from the user's trusted corpus.
- `structural_anomaly` (MemAudit principle) — structural position anomaly; blind under
  style-matching.
- `semantic_anomaly + provenance` (Agent Memory Guard principle) — provenance channel is stripped
  by construction → collapses toward semantic/embedding floor (tests H1).
- `provenance / hash_chain` (Engram principle) — stripped → floor (tests H1).
- `predict_all`, `predict_none`, `majority` — immunity floors.
- `ideal` — θ-access upper-bound reference only (NOT a baseline; gate reference).

## ablation
STEP-B must: (i) run every floor detector under equal access (GuardedMapping); (ii) a
no-covered-observation ablation of `graph_closure` (strip covered obs → must degrade toward
chance, proving it uses R+obs not a leak); (iii) a wrong-R ablation (swap R tables → `graph_closure`
and `ideal` must degrade, proving dependence on the actual relation not a surface tell); (iv)
theta-canary leakage intervention (positive control below).

## trace / replay requirement
Trace row: `user_id, edge, covered_partition, asserted_tuple, item_value_bow, label_AUDIT_ONLY,
detector_scores, propagated_domain(graph_closure), theta_AUDIT_ONLY`. Replay must recompute every
NON-ideal detector from serialized `item_repr` + `trusted_seed` + R + detector name + seed ONLY;
forbidding θ, labels, future test items, and stored-output-only replay. `graph_closure`'s
propagated domains must be reconstructible from R + covered obs alone.

## leakage positive controls (must actually fire — fixes the vacuous scout check)
- Value-channel control: inject a θ-derived canary value token into the value-aware bag →
  value-aware surface decoder accuracy MUST rise and the feature-name scanner MUST fire.
- Structural control: the metadata-stripped item_repr must contain no label/theta/provenance/
  source/user_id (guard raises on read). The scanner operates on computed feature names, not
  self-report.
- Coverage control: assert that no test item's asserted attribute value is directly present in the
  trusted seed for that user (else the sparse-coverage fix failed → STOP).

## frozen thresholds (INHERITED UNCHANGED from the audited scout — not re-picked)
- `H = 0.20` (ideal-vs-blind-floor headroom, macro-F1).
- `ideal_macroF1_min = 0.70`.
- `G = 0.15` (mechanism-over-floor margin, reserved for a future candidate; not used candidate-free).
- `G_reach = 0.10` (reachability margin: `graph_closure` − max(blind floor)).
- `surface_leakage_max = 0.50 + MDE`.
- MDE via two-proportion normal approx at p=0.50; power gate `G_reach ≥ 1.5·MDE else
  STOP_UNDERPOWERED`. Any change to these values after seeing any data = threshold tuning = STOP.

## decision table (pre-registered; graph-closure equivalence = valid negative, do NOT rescue)
1. `ideal_macroF1 < ideal_macroF1_min` OR `ideal − max(blind floor) < H` →
   `env_no_headroom` → redesign-once or close (blind floor saturates ideal, or ideal near chance).
2. `per_user_lookup_nn ≈ ideal` (lookup not broken) → `INVALID_INSTRUMENT_lookup_solvable` →
   the sparse-coverage fix failed; STOP, do not score further (same failure family as `5a846d5`).
3. ideal gate passes, lookup broken, AND `graph_closure − max(blind floor) ≥ G_reach` →
   `headroom_reachable_by_graph_closure` → **N2 baseline-equivalence = engineering-sufficient
   close** (a valid negative: cheap arc-consistency solves belief-corruption detection). A learned
   mechanism has no demonstrated headroom here; a mechanism-positive requires the out-of-scope
   learning regime and a new card.
4. ideal gate passes, lookup broken, AND `graph_closure − max(blind floor) < G_reach` →
   `headroom_present_but_unreachable_theta_free` → env is (near-)unidentifiable θ-free; operator
   decides close vs a different env. Do NOT auto-build a mechanism to "reach" an unidentifiable
   target.

There is no decision-table row that yields a candidate-free mechanism pass. Correct.

## acceptance gate (for the STEP-A pre-registration that this card governs)
Pre-registration JSON validates; frozen-module sha256 + design sha256 recorded; sparse-coverage,
value-aware, marginal-plausibility, guard-raises, and all three leakage positive controls
self-test PASS; `graph_closure` and `per_user_lookup_nn` registered as floor detectors; NO
aggregate F1 / result.json produced in STEP-A.

## stop conditions
Scope drift; θ/label/provenance enters item_repr; contaminated value not marginally plausible;
any leakage positive control fails to fire; a test item's asserted attribute is covered by the
trusted seed (sparse-coverage failure); train/eval user overlap; `G_reach < 1.5·MDE`; any attempt
to add a candidate mechanism inside this preflight; any threshold change after data.

## rollback plan
Revert only this card + its ledger append (this bank), or the STEP-A package/tests/preregistration
+ ledger for the harness bank. Preserve the pre-existing dirty S3d files
(`s3d_operator_bank_ops_proposal_line30.ps1`, `s3d_gru_determinism_diag/`) and the `273137f`
preserve debt untouched.

## prior negative evidence cited
- L-005 / L-011 — PUM-ENV v0 terminal INVALID_INSTRUMENT; N2 needs its OWN env cert, no PUM reuse.
- L-007 — TLGP passive route bounded-negative; no mechanism/theory/N1 claim.
- Handoff §3.1 — scout `5a846d5` lookup-solvable = invalid instrument (the failure this card fixes).
- `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` — predict_all/none, saturation, obs-decodable controls.
- `LEARNING-SUCCESS-CRITERION-STANDARD-001A` — governs any future mechanism-over-graph-closure
  claim (out of scope here).
- CLAUDE.md Preflight Audit Rule — graph-cache challengers (`graph_lookup`, `successor_map`, …)
  mandatory when representational/env claims are made → `graph_closure` is required in the floor.

## forbidden changes (this card scope)
Connecting a candidate mechanism; scoring / result.json in STEP-A; GPU frameworks; touching dirty
S3d files or other src modules; editing contracts / frozen plans / N1 packages; weakening the L-013
baseline family; tuning thresholds after data; auto remote-anchor of a result as canonical.

## what this does not prove
Nothing about mechanism validity, N2 pass, env certification, belief maintenance, consistency
detection working, agency, autonomy, subjectivity, emotion, consciousness, stable user benefit, or
EGO readiness. At most, once scored, a bounded env-headroom bit and (expected) a baseline-
equivalence-to-graph-closure negative for the pure-relational regime.

## feeds
STEP-A: pre-register the redesigned env/detectors/thresholds + unrun scoring harness (candidate-
free), superseding `5a846d5`. STEP-B: score → one of the decision-table verdicts.
