# SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A

Status: DESIGN ARGUMENT (Red / pre-registration governance). Satisfies requirement R4 of
`SAME-AGENT-KERNEL-DISCRIMINABILITY-SPEC-001A` (L-015) against ONE concrete, frozen environment.
On-paper only: NOT mechanism evidence, NOT a kernel authorization, NOT an experiment, NO code, NO
scoring. It is a required input to the future kernel card `SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A`.
It does not close, supersede, or weaken N2/SBMC or the frozen integrated baseline family.

## task id
SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A

## satisfies
`SAME-AGENT-KERNEL-DISCRIMINABILITY-SPEC-001A` requirement R4 (on-paper cache-cannot-match argument),
instantiated on a concrete env. Inherits that spec's formal object, frozen integrated baseline family,
R1-R6, decision table, and honest H_null prior VERBATIM. Adds no threshold, weakens no baseline,
introduces no schema. This card is subordinate to L-015; on any conflict L-015 governs.

## layer
Mechanism-hypothesis + engineering design (route governance). No subjectivity / consciousness layer.

## claim ceiling
Design + pre-registration only. Establishes (a) an on-paper proof that the frozen cache sub-family is
at chance on a specific compositional held-out, and (b) a named, testable sparse/non-stationary regime
where OFFLINE consolidation COULD have headroom over the learning sub-family -- pre-registered as an
OPEN question whose LIKELY empirical outcome (H_null) is baseline equivalence to a drift-aware
continual method. It cannot show mechanism validity, kernel success, learning, that headroom exists,
agency, autonomy, emotion, self-awareness, consciousness, or EGO readiness. Passing R4 authorizes at
most DRAFTING the kernel STEP-A card.

## 1. The concrete environment E* (frozen for this argument)

E* is an action-conditioned factored-relational world instantiating the spec's "candidate concrete
environment" sketch (features x relations; held-out = unseen combinations; sparse per-episode signal).

- Factors. Every entity has two latent factor indices: a row factor r in {1..n} ("type") and a
  column factor k in {1..n} ("context"). Grid is n x n (n large, e.g. n=20); the argument does not
  depend on squareness.
- Latent code. Per-deployment codes a: {1..n} -> Z_L and b: {1..n} -> Z_L drawn i.i.d. uniform over
  Z_L = {0,..,L-1}, with L >= 3 (concrete: L = 5). The codes are LATENT: never observed, never in
  any field.
- Outcome rule (the held-out target). outcome(r,k) = phi(r,k) = ( a(r) + b(k) ) mod L. This is an
  additive Cayley table over Z_L -- a Latin square (each row is a cyclic shift of another). The
  prediction target is y = phi(r,k); chance for L-way prediction = 1/L (concrete: 0.20).
- Formal-object binding (inherits L-015). S = agent latent state; O = o_t reveals (r_t,k_t) as
  value-aware factor indices (NOT a label); A = probe/predicted-response action a_t; outcome_t =
  phi(r_t,k_t); M = (episodic trace E, consolidated store C); update U, prediction P_theta,
  PE_t = d(pred,outcome) as in L-015. Action-conditioning (P_theta(s,a)) is exercised by R2's
  counterfactual-action / corrupted-replay ablations at the kernel card; the R4(a) chance proof
  concerns the outcome-prediction target phi and does not require it.
- Coverage / sparse training (the cross-episode structure). The n x n cell matrix Y[r,k]=phi(r,k) is
  revealed only on a training mask Omega_train subset of [n]x[n]. Held-out queries are drawn from
  Omega_test = complement, under three pre-registered conditions:
  - C1 NOVEL COMBINATION: every test cell (r*,k*) is NOT in Omega_train (cache-void by absence).
  - C2 MARGINAL COVER + BALANCE: every row r* appears in Omega_train paired with >=1 other column,
    and every column k* with >=1 other row (each factor is individually observed -> learnable); AND
    the training partners of r* have b-values whose residues mod L are (near-)uniform, symmetrically
    for k*, so every single-factor marginal of y over Omega_train is (near-)uniform.
  - C3 CONNECTIVITY: the training bipartite graph G_train = (rows U cols, Omega_train edges) is
    connected -> a(.),b(.) are identifiable up to a global additive constant, and since y = a+b is
    invariant to that constant, y[r*,k*] is FULLY identified by solving the connected additive system.
    (C3 is what lets the learning sub-family solve E* in the STATIONARY regime -- and is exactly the
    condition R4(b) must break to create any headroom.)
- Structural properties used below.
  - P1 MARGINAL BALANCE (from C2): for fixed r, phi(r,.) is uniform over Z_L as the column ranges;
    symmetrically for fixed k. One-factor information is zero information about y.
  - P2 JOINT DETERMINACY: y is exactly determined by the pair (a(r),b(k)); recovering the pair
    (matrix completion of a rank-structured / additive matrix) solves any cell, including held-out.

## 2. R4(a) -- the cache sub-family is provably <= chance (1/L) on Omega_test

Chance = 1/L. By P1 the majority-class predictor is also 1/L (no class is more frequent).

Lemma (cache sufficient-statistic independence). Fix a held-out cell (r*,k*). Every enumerated cache
member's output is a function only of statistics drawn from:
  (i)   the exact cell (r*,k*)                          -- absent by C1 (count 0),
  (ii)  single-factor marginals over Omega_train        -- uniform by P1,
  (iii) single-factor-overlap retrieval neighbours       -- cells sharing exactly one factor with (r*,k*).
Under the uniform-code prior, each of (i)-(iii) is statistically independent of
y[r*,k*] = (a(r*)+b(k*)) mod L. Hence mutual information I(member_output ; y[r*,k*]) = 0, so expected
accuracy = 1/L. Finite-sample deviation is bounded by the pre-registered MDE and self-tested at STEP-A.

Per-member (frozen cache sub-family {episodic_traversal, count_table, transition_table, successor_map,
rag_summary, no_update}):

- no_update -> predicts a fixed prior; global label frequency over Omega_train is uniform (P1) => 1/L.
- count_table -> full-key count N[(r,k)->y]; key (r*,k*) has count 0 (C1); any backoff is to a
  single-factor or global marginal, all uniform (P1) => 1/L. It CANNOT form a(r*)+b(k*) because that
  requires combining two separately-stored marginals via the additive model -- an operation outside a
  count table (that IS the learner; see boundary note).
- transition_table -> (state,action)->next counts; in E* this is the same tuple-keyed lookup, unseen
  held-out key -> backoff -> 1/L. Modelling factor-wise dynamics (r->r or k->k) carries no information
  about the cross term a(r*)+b(k*) => 1/L.
- successor_map -> deterministic key->value cache; novel key (r*,k*); the nearest stored key differs
  in one factor, whose stored value differs from y[r*,k*] by an INDEPENDENT residue (uniform mod L)
  => 1/L in expectation.
- episodic_traversal / nearest-neighbour -> retrieves the most factor-similar stored episode; it
  shares exactly one factor (the other differs, since the exact cell is absent). Its label is
  phi(r*,k_j) or phi(r_i,k*). E[match] = P[b(k_j) == b(k*)] = 1/L (independent uniform codes, k_j != k*).
  Voting over MANY same-row neighbours does not help: their labels are i.i.d. uniform in different
  residue classes -> the vote is uninformative about b(k*) => 1/L.
- rag_summary -> retrieve-a-set + summarize (majority / centroid); the retrieved set shares one factor,
  labels i.i.d. uniform in the target's residue class -> summary uninformative => 1/L.

Boundary statement (why this is a genuine cache-void, not a trick). The ONLY sufficient statistic that
recovers y[r*,k*] is the reconstructed pair (a(r*),b(k*)) obtained by solving the connected additive
system over Omega_train -- i.e. MATRIX COMPLETION of a rank-structured matrix / fitting a factored
(additive) model. This is a LEARNING operation, not a cache operation; no enumerated cache member
performs it. In particular the group identity y[r*,k*] = ( y[r*,k0] + y[r0,k*] - y[r0,k0] ) mod L
(a 2x2 additive minor / 3-point completion) DOES reconstruct the held-out cell from three stored
cells -- but evaluating it is modular additive arithmetic over retrieved labels (label_A + label_B
- label_C mod L), i.e. the additive-model fit itself, which no enumerated cache member performs
(retrieval returns a label or a vote; count returns an argmax; none combine labels additively).
That arithmetic IS the cache/learner boundary. The cache family is confined to lookup (absent), single-factor marginals (uniform), and
one-factor-overlap retrieval (independent residues). Therefore R4(a) HOLDS: every cache member = 1/L.

Adversarial note (anti-smuggling). A cache member "strengthened" until it fits the additive/log-linear
model (e.g. count_table + additive backoff that solves the marginal system) has LEFT the cache family
and JOINED the learning sub-family. It is then adjudicated by R3/R4(b), not credited as a cache pass.
The R1 self-test at STEP-A asserts each cache member's macro-accuracy on Omega_test <= 1/L + MDE; a
cache member exceeding it is either leakage (R5) or a mislabeled learner -> STOP.

## 3. R4(b) -- the sparse / non-stationary regime G* with possible learning-family headroom

In the STATIONARY connected regime of Section 1, the learning sub-family SOLVES Omega_test
(from_scratch matrix completion; or a meta-learner). So that regime alone yields NO headroom and lands
on H_null / downgrade. To create any headroom for offline consolidation OVER the learning sub-family,
R4(b) must break the conditions (bounded online compute + connectivity within reach of a forward pass)
that let online / replay learners succeed. The named regime:

G* (sparse, RECURRING non-stationarity):
- Sparse disconnected slices. The stream is episodes e=1,2,... Each episode reveals a small slice
  S_e of the current code's cell matrix with |S_e| << n and touching few rows/cols, so G_{S_e} ALONE
  is disconnected/under-determined: no single episode identifies a(.),b(.). Connectivity (C3) holds
  only over the UNION of many episodes' slices -> identifiability REQUIRES cross-episode aggregation.
- Recurring regime switching. The code (a,b) is drawn from a small latent library
  {(a^1,b^1),..,(a^g,b^g)} and SWITCHES between episodes so that regimes RECUR NON-ADJACENTLY
  (e.g. a Markov / interleaved schedule): episodes of the same regime are separated in time by other
  regimes' episodes.
- Bounded online compute. Per-step compute is O(|S_e|); the agent cannot re-solve the full accumulated
  system each step.
- Deployment-resampled library. The regime library is RESAMPLED per deployment (meta-test), so no
  fixed amortized observation->code map transfers; the code must be identified WITHIN the deployment.
- Held-out. Omega_test = novel cells of a regime that has appeared (non-adjacently) enough times that
  the UNION of its slices is connected -> identifiable IN PRINCIPLE only by an agent that both
  (i) segments episodes by regime and (ii) pools same-regime slices; and cache-void per Section 2
  regime-by-regime.

Failure geography (pre-registered -- the discriminative structure):
- cache family: chance (Section 2), holds regime-by-regime.
- online_no_replay: bounded compute + single pass; cannot back-solve a system whose connectivity only
  emerges across non-adjacent episodes; overwrites/forgets prior-regime structure under switching -> fails.
- from_scratch_per_task (task = episode): each slice is disconnected/under-determined -> fails. (task =
  deployment): needs a batch solve = the R6 batch-precompute control AND regime segmentation; see R6.
- vanilla_experience_replay: uniform-random replay POOLS cells across DIFFERENT interleaved regimes
  (replay is regime-blind) -> fits an averaged code wrong for every regime -> chance-to-poor -> fails.
- standard_continual_replay (regime-blind rehearsal): averages across regimes (like vanilla) or, if
  recency-weighted, discards non-adjacent same-regime evidence -> fails UNLESS augmented with regime
  inference (which promotes it to the challenger below).
- strong_meta_learner: the residual threat. Deployment-resampling defeats a meta-learner that
  amortizes the SPECIFIC codes; it can at best amortize the PROCEDURE "segment + pool + solve" -- which,
  if it does, IS the consolidation mechanism realized as an amortized net (baseline equivalence, H_null).
  Headroom survives only if that procedure fails to transfer to meta-test switching statistics.

Residual headroom hypothesis for OFFLINE consolidation (bounded; pre-registered as OPEN). Offline
consolidation = unbounded RETROSPECTIVE re-processing of E that (i) SEGMENTS the stream into regimes
(change-point / clustering over slices), (ii) RETROACTIVELY LINKS non-adjacent episodes of the same
regime, (iii) POOLS their sparse slices into a connected per-regime system and SOLVES it (matrix
completion), (iv) writes a regime-indexed schema (a_hat^j, b_hat^j) into C, reused on held-out cells.
The claimed headroom source is the OFFLINE, GLOBAL, RETROACTIVE linkage (ii)+(iii): a forward-only,
bounded, regime-blind online learner cannot retroactively connect episode 2 and episode 40 of the same
recurring regime; offline re-clustering can.

Strongest challenger inside the FROZEN learning sub-family -- the one to beat (H_null: expected TIE).
`standard_continual_replay` instantiated as a DRIFT-AWARE / REGIME-INFERRING continual learner: online
change-point detection + a regime-indexed replay buffer + per-regime online additive/low-rank
completion. This is still a learning-sub-family member (replay + online updates, no offline global
re-solve). Honest prior: this challenger MATCHES the consolidation kernel in G*, because "segment by
regime and pool same-regime slices" can be done online-incrementally as well as offline-retroactively.
If it does -> baseline equivalence -> route downgrade. This restates the N2 precedent: the moment you
specify WHAT consolidation does, it may already be a continual-replay member (cf. "constraint
propagation cannot beat the floor because it belongs in the floor").

Where genuine headroom could survive (the narrow, testable cracks -- each a STEP-B contrast):
- Retroactive re-segmentation. Early episodes mis-assigned by an ONLINE change-point detector (before
  enough evidence accrues) are corrected by OFFLINE global clustering; the online learner has committed
  to wrong assignments and cannot un-mix. Headroom = held-out accuracy on regimes that were ambiguous
  early. Falsifier: give the online challenger a look-back re-labeling buffer; if it closes the gap,
  no headroom.
- Bounded-resource asymmetry (NOT batch-precompute). Offline consolidation re-solves during "sleep"
  under the SAME data budget and a MEMORY/COMPUTE BUDGET where batch is inadmissible (batch needs all
  cells resident at once; the bounded kernel does not). The only defensible headroom is
  RESOURCE-BOUNDED. Falsifier: at unbounded budget a batch additive-fit + change-point segmentation
  matches it -> R6 downgrades to "offline == batch precompute."

Honest narrowing (carry into any future claim). E*/G* make the kernel's BEST-CASE positive a
RESOURCE-BOUNDED headroom over {online_no_replay, vanilla_experience_replay, regime-blind
standard_continual_replay} in G* -- NOT headroom over an unbounded batch solver and NOT over a
drift-aware regime-inferring continual learner unless the two cracks above empirically hold. The prior
that they do not (H_null) is LIKELY.

## 4. R1-R6 mapping for E* / G*
- R1 cache-void held-out: SATISFIED by construction (Section 2 proof; STEP-A self-test asserts each
  cache member <= 1/L + MDE on Omega_test).
- R2 causal routing + destructive ablation: DEFERRED to kernel STEP-B; both corrupted-replay and
  no-replay must destroy held-out gain. Necessary-not-sufficient: the drift-aware challenger collapses
  under the same ablations, so R2 does not discriminate mechanism from it.
- R3 integrated baseline family (the real bar): frozen family applies unchanged; in G* the DECISIVE
  member is the drift-aware regime-inferring continual learner. Tie with it = baseline equivalence.
- R5 schema anti-leakage: O carries factor INDICES + outcomes only; no field encodes a(.),b(.), the
  held-out target, or the regime id (regime id is LATENT and must be INFERRED, not read). Action /
  observation names carry no label. Exposing regime id in O would leak the segmentation -> forbidden.
- R6 reducibility / non-experience-replay-collapse: consolidation must beat (i) vanilla experience
  replay (fails in G* by regime-mixing) AND (ii) batch-precompute on the same data. (ii) is a HARD
  threat here: a batch additive-fit + segmentation likely matches; hence the only escape is the
  bounded-memory/compute constraint that makes batch INADMISSIBLE (Section 3 narrowing). Plus
  non-memorization: held-out cells not epsilon-close to any trained cell (C1 guarantees this in cell
  space).

## 5. Decision (per L-015 pre-registered decision table)
- R4(a): HOLDS on paper -- cache sub-family = chance (1/L) on Omega_test of E* (additive Latin-square +
  P1 marginal balance + C1 novelty). NOT row-1 STOP.
- R4(b): NAMES a testable regime G* (sparse-disconnected per-episode slices + recurring non-adjacent
  non-stationarity + bounded online compute + deployment-resampled library) AND its decisive challenger.
=> Gate outcome = decision-table ROW 3 (PROCEED to draft kernel STEP-A), QUALIFIED. The qualification,
pre-registered: R4(b) does NOT establish headroom on paper; it locates the single contrast on which the
route lives or dies -- kernel vs drift-aware regime-inferring continual replay in G*, equal data, under
a stated resource budget -- with honest prior H_null = TIE = downgrade to "re-derived a known
drift-aware continual method."

Cheapest validation step (binds kernel STEP-A). Do NOT build the full kernel first. Scope STEP-A's
FIRST experiment to exactly that decisive contrast as a tiny CPU toy (small n, L=5, g in {2,3}, sparse
slices, resampled library). If the drift-aware continual baseline ties the offline consolidator there
(within the equivalence band), STOP / downgrade before any kernel plumbing. Only if consolidation beats
it -- AND survives R2 ablations, R3 max-over-family, R6 batch + vanilla-replay controls, and
non-memorization -- does the route earn a bounded, resource-qualified positive.

## 6. Falsifiers (how STEP-B breaks this argument)
- F1 (breaks R4(a)): any cache member scores > 1/L + MDE on Omega_test -> either R5 leakage or a
  mislabeled learner in the cache slot -> STOP, do not credit.
- F2 (breaks R4(b) headroom): the drift-aware regime-inferring continual learner matches the
  consolidator in G* (equal data + budget) -> baseline equivalence -> downgrade (expected H_null).
- F3 (batch dominates): batch-precompute (additive fit + segmentation) matches the consolidator at the
  kernel's budget -> "offline == batch precompute" -> R6 downgrade.
- F4 (env too easy): if G_train stays connected within a single episode, or the library is not
  resampled, the whole learning sub-family solves it -> no headroom, redesign or close.
- F5 (env impossible): if same-regime slices never union to connected, Omega_test is unidentifiable
  theta-free -> report env_impossible, do NOT auto-build a mechanism to "reach" an unidentifiable target.

## 7. Known limitation (do not hide)
Under the 2026-07-05C solo protocol, Claude is BOTH red-first designer of this argument AND its hostile
auditor (relaxes the DISTRIBUTION-HEADROOM role separation), as already recorded in L-015. Compensating
controls: (i) every claim here is falsifiable by the STEP-B contrasts F1-F5; (ii) this card is
pre-registered as an ANCESTOR commit before any kernel run (commit-order anti-tuning). Treat R4(b) as a
hypothesis to be broken at STEP-B, not as settled. This argument's function is to make the route's most
probable outcome (baseline equivalence to a drift-aware continual method) CHEAP to reach and hard to
rescue.

## 8. What this does not prove
Nothing about kernel success, mechanism validity, learning, that headroom exists, belief maintenance,
agency, autonomy, subjectivity, emotion, self-awareness, consciousness, stable user benefit, or EGO
readiness. It fixes one concrete env for which the cache family is provably at chance, and names one
testable regime whose most probable STEP-B outcome is a bounded baseline-equivalence negative.

## stop conditions
Any cache member > chance on paper or at STEP-A (R4(a) fails, F1); the frozen baseline family narrowed
below L-015's set; regime id or code exposed in O/A (R5); "same-agent/self/agency" language upgraded
beyond L-015's bounded label; any attempt to build kernel/env code under THIS card; any move to score.

## rollback plan
Revert this card + its JSON artifact + the ledger/decision-log append. No code exists to revert.
Preserve the pre-existing dirty S3d files and the 273137f preserve debt untouched.

## prior negative evidence cited
- Identifiability ceiling x2 (LRGG oracle-coupling / active-saturation; PUM-ENV / S3d nearest-neighbour
  dominance) -- equal-access cheap baselines saturate; the lesson E* operationalizes.
- N2 scout 5a846d5 lookup-solvable; N2-SBMC-ENV-REDESIGN-001A (L-014) "constraint propagation belongs
  in the floor" -- the exact structure restated as "drift-aware replay belongs in the learning family."
- `DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A`, `LEARNING-SUCCESS-CRITERION-STANDARD-001A`,
  `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`, `MECHANISM-SIGNATURE-VERDICT-STANDARD-001A`,
  `SAME-AGENT-KERNEL-DISCRIMINABILITY-SPEC-001A` (L-015).

## feeds
`SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A` STEP-A must cite this id and L-015, instantiate E*/G* (or a
declared variant), freeze its generator, run the Section 5 decisive contrast FIRST, and satisfy
R1/R2/R3/R5/R6 empirically before any build beyond the toy.
