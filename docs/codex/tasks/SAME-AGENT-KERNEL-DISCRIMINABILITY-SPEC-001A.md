## task id
SAME-AGENT-KERNEL-DISCRIMINABILITY-SPEC-001A

## layer
Mechanism-hypothesis + engineering design (route-governance). No subjectivity / consciousness layer.

## claim ceiling
Design + pre-registration only. Produces a frozen discriminability specification and an on-paper
gate. It cannot show mechanism validity, kernel success, learning, agency, autonomy, emotion,
self-awareness, consciousness, unified subject, or EGO readiness. Passing this card authorizes at
most the DRAFTING of the kernel STEP-A card — not a build, not a claim.

## problem definition (why this card exists — the reframe)
The lab's recurring failure is not "mechanisms were tested in isolation." It is IDENTIFIABILITY:
the chosen environments did not REQUIRE the mechanism, so an equal-access cheap baseline saturated
the task (LRGG oracle-coupling / active-saturation; ACP-BV/ACOLB parametric saturation; PUM-ENV /
S3d nearest-neighbor dominance; N2 scout lookup-solvability). Composing prediction → action →
prediction-error → state-update → memory-write → replay/consolidation → later-behavior into one
"same-agent kernel" does NOT dissolve this. It RELOCATES the baseline contest one level up: the
fair legal-channel baseline for an integrated loop is an INTEGRATED CACHE (episodic traversal +
count/transition tables + RAG summary + no-update), and that integrated-cache family is precisely
what has been beating the lab's mechanisms. A closed loop only buys ablation SURFACES
(corrupted-replay, counterfactual-action, no-update); it does not buy discrimination. Discrimination
comes from ENVIRONMENT + SCHEMA + compositional held-out structure that the integrated-cache family
provably cannot match. This card forces that to be shown on paper first.

## inherited contracts (this card composes, does not reinvent)
- `DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A` — Saturation STOP-Gate:
  `strongest_fair_legal_channel_baseline < ceiling − equivalence_band` BEFORE candidate authoring.
  Applied here with the INTEGRATED-CACHE FAMILY as the strongest fair legal-channel baseline.
- `LEARNING-SUCCESS-CRITERION-STANDARD-001A` — control vs rival; mandatory control baselines incl.
  the REDUCIBILITY control ("online update must buy something over batch precomputation"); positive
  generality criterion (held-out novelty, few-shot, breadth-over-peak); genuine-learning signature
  (learning curve + forward transfer + ablation-destroys + not-memorization).
- `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` — predict_all/none, saturation, observation-decodable
  controls that INVALIDATE a result.
- `MECHANISM-SIGNATURE-VERDICT-STANDARD-001A` — S1 control-separation is non-negotiable; verdicts
  classified by signature not absolute score.

## bounded formal object (the same-agent kernel under test)
- S: agent persistent latent state s_t (serializable, hashable).
- O: observation o_t.  A: action a_t.  outcome_t: environment return.
- M: memory = (episodic trace E, consolidated store C).
- Prediction: pred_t = P_θ(s_t, a_t)  (action-conditioned, no future info).
- Prediction error: PE_t = d(pred_t, outcome_t).
- Update U: s_{t+1} = U_θ(s_t, o_t, a_t, outcome_t, PE_t); memory_write appends (s_t,o_t,a_t,outcome_t)
  to E; replay/consolidation C ← Consolidate_θ(E, C) and s may be updated by replaying C offline.
- Objective V: performance on HELD-OUT compositional behavior (states that are novel compositions of
  trained factors), not seen-state accuracy.
- boundary: agent-controlled {a_t, s_t, M, θ} vs environment {o_t, outcome_t}. self-boundary =
  posterior over which outcome-variance is action-caused — TESTED LAST, NOT built now, NOT claimed here.

The "same-agent" label is bounded to "one persistent, hash-chained state carried across steps with
causal replay effect." It is NOT a claim of unified subject, self, or agency. A well-plumbed
pipeline is not evidence of an agent; do not let kernel wording upgrade this.

## discriminability requirements (R1–R6 — the gate; each maps to an inherited standard)
- R1 CACHE-VOID HELD-OUT. The held-out distribution is compositions with no correct entry reachable
  by the cache family over E∪C. Pre-register the property: for every held-out item, the
  nearest-stored / count / traversal answer is provably ≤ chance. (Kills the cache family by
  construction; instantiates BASELINE-IMMUNITY observation-decodable + DISTRIBUTION-HEADROOM saturation.)
- R2 CAUSAL ROUTING + DESTRUCTIVE ABLATION. Held-out gain must be destroyed by BOTH corrupted-replay
  AND no-replay ablations. NECESSARY, NOT SUFFICIENT — the cache passes it too (corrupting its store
  also destroys its effect). R2 only rules out decorative replay; it does not discriminate mechanism
  from cache. (Genuine-learning signature: ablation-destroys.)
- R3 INTEGRATED BASELINE FAMILY — THE REAL BAR. The mechanism must BEAT max over BOTH sub-families
  under equal data/access:
  - cache sub-family (expected to LOSE R1; their job is to prove cache-void): episodic_traversal,
    count_table, transition_table, successor_map, rag_summary, no_update.
  - learning sub-family (the HARD bar): online_no_replay, vanilla_experience_replay,
    standard_continual_replay, from_scratch_per_task, strong_meta_learner (equal data). A tie with
    ANY learning-sub-family member = baseline equivalence = route downgrade (§decision table),
    NOT mechanism evidence. (LEARNING-SUCCESS control side + rival/control distinction.)
- R4 ON-PAPER CACHE-CANNOT-MATCH ARGUMENT (cheapest gate, before any code). A written argument that
  (a) the cache sub-family provably ≤ chance on R1's held-out, AND (b) names the SPECIFIC regime
  (sparse cross-episode signal + non-stationarity / bounded online compute) where OFFLINE
  consolidation could have headroom over the learning sub-family. (b) is pre-registered as an OPEN
  question; the LIKELY empirical outcome is baseline equivalence to a known replay/continual/meta
  method (a valid negative). Route proceeds to build ONLY if (a) holds on paper AND (b) names a
  testable regime; else STOP. (DISTRIBUTION-HEADROOM saturation STOP-gate.)
- R5 SCHEMA ANTI-LEAKAGE. The S/O/A/M schema contains no baked-in answer: no explicit self-label, no
  field encoding the held-out target, no action/observation NAME leaking the label. Audited before
  the kernel plugs in anything. (Anti-hardcoding audit.)
- R6 REDUCIBILITY / NON-EXPERIENCE-REPLAY-COLLAPSE. The consolidation effect must (i) beat vanilla
  experience replay specifically, and (ii) beat batch-precomputation on the same data ("online/replay
  must buy something over batch"). If the effect equals experience replay → report "re-derived
  experience replay," downgrade. Plus a non-memorization control: held-out items not ε-close to any
  trained item. (LEARNING-SUCCESS reducibility control + not-memorization signature.)

## hypothesis (bounded, with honest prior)
H_null (LIKELY): in most compositional-held-out regimes a strong learning-sub-family member
(continual-replay / meta-learner) matches the kernel → baseline equivalence → valid negative
(no headroom over known methods). H_target (UNLIKELY): a specific sparse / non-stationary regime
where offline consolidation extracts a transferable schema that online + vanilla-replay + cache all
miss. Design to DETECT which holds, NOT toward H_target.

## candidate concrete environment (sketch only — instantiated + argued at kernel STEP-A, not frozen here)
A factored relational world (features × relations) where held-out = unseen feature/relation
COMBINATIONS (cache-void by R1); per-episode signal is sparse, forcing cross-episode aggregation;
optional non-stationarity forces consolidation-vs-forgetting. The kernel STEP-A card must instantiate
one such env, freeze its generator, and supply the R4 argument against THIS env; this card only fixes
the requirements it must meet.

## decision table (pre-registered)
1. R4(a) fails on paper (cache family CAN match held-out) → env not cache-void → STOP / redesign env;
   do NOT build the kernel.
2. R4(a) holds, R4(b) names no testable learning-family-headroom regime → route DOWNGRADE to
   "auditable engineering demo of a closed loop"; claim ceiling = infrastructure only, NOT mechanism
   evidence; do not claim mechanism.
3. R4(a) holds AND R4(b) names a testable regime → PROCEED to draft
   `SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A` STEP-A (minimal kernel + env instantiation +
   pre-registration), which must then empirically satisfy R2 / R3 / R6.
4. At kernel STEP-B, tie with any learning-sub-family member → baseline equivalence → valid negative,
   route closes as "no headroom over known replay/meta method" (the expected H_null outcome).

There is no row that yields a mechanism pass from THIS card. Correct — it is a paper gate.

## acceptance gate (for THIS spec card)
Formal object + R1–R6 written and internally consistent; integrated baseline family (both
sub-families) enumerated and FROZEN; the on-paper R4 argument drafted and FALSIFIABLE by the future
STEP-B; honest H_null prior recorded; inherited contracts cited; NO code, NO env scored, NO result.json.

## known limitation (do not hide)
Under the 2026-07-05C solo protocol, Claude is BOTH the red-first designer of this discriminability
argument AND its hostile auditor — a relaxation of the `DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT`
role separation (`red_first_designer != hostile_auditor`). Compensating controls: (i) the R4
argument is FALSIFIABLE by the empirical STEP-B (an argument that survives paper but fails the run is
caught); (ii) this card is pre-registered as an ancestor commit before any kernel run (commit-order
anti-tuning). This does not fully substitute for an independent designer; treat the R4 argument as a
hypothesis to be broken at STEP-B, not as settled.

## trace / replay requirement (deferred to the kernel card)
The kernel must emit a per-step loop trace (s_t hash, o_t, a_t, pred_t, outcome_t, PE_t, memory_write,
consolidation event, s_{t+1} hash) and be replayable from serialized state + observations only, no
future info, no stored-output-only replay. Specified here as a standing requirement; instantiated at
the kernel card.

## stop conditions
R4(a) fails on paper; any schema leakage (R5); the baseline family is narrowed below the frozen set;
"same-agent/self/agency" language upgraded beyond the bounded label; any attempt to build code under
this card; any move to score an environment here.

## rollback plan
Revert this card + its spec artifact + the ledger append. No code exists to revert. Preserve the
pre-existing dirty S3d files and the `273137f` preserve debt untouched.

## prior negative evidence cited
- Identifiability ceiling ×2 (LRGG + PUM-ENV/S3d): equal-access baselines saturate; the standing
  lesson this card operationalizes.
- N2 scout `5a846d5` lookup-solvable; N2 redesign L-014 (graph-closure equivalence = engineering
  sufficient) — same "cache reaches it" pattern at the component level.
- `DISTRIBUTION-HEADROOM-PREFLIGHT-CONTRACT-001A`, `LEARNING-SUCCESS-CRITERION-STANDARD-001A`,
  `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`, `MECHANISM-SIGNATURE-VERDICT-STANDARD-001A`.

## forbidden changes (this card scope)
Writing kernel/env/mechanism code; scoring; GPU frameworks; touching src/, dirty S3d files, contracts,
frozen plans, N1/N2 packages; weakening the frozen baseline family; claiming agency/self/consciousness;
auto remote-anchor of a result.

## what this does not prove
Nothing about kernel success, mechanism validity, learning, belief maintenance, agency, autonomy,
subjectivity, emotion, self-awareness, consciousness, stable user benefit, or EGO readiness. It only
fixes a paper gate whose most probable downstream outcome is a bounded baseline-equivalence negative.

## feeds
`SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A` STEP-A must cite this id, satisfy R1–R6, and carry the R4
argument for its concrete environment before any build.
