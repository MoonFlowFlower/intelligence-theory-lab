# FSP-TRACK-F-REUSE-GATE-PATCH-001A (DRAFT — UNSIGNED)

> STATUS: DRAFT proposal. NOT authorized. Governance/route patch, not an experiment.
> Requires operator signature (§Sign-off) before any file under `src/`, `tests/`,
> `artifacts/FSP-PUM-ENV-IDPROBE-001A/`, or any frozen governing doc is touched.
> This card changes NOTHING frozen and does NOT interrupt the running S3c-R3 sweep.
> Authored by Claude in the standing independent-auditor role (does not implement).

## task id
FSP-TRACK-F-REUSE-GATE-PATCH-001A

## problem definition
Track F (= `FSP-PUM-ENV-IDPROBE-001A`, the PUM-ENV identifiability probe) was scoped
"build a qualified mechanism testbed." Operator now wants a borrow-first / build-only-on-gap
route to avoid rebuilding what the field already ships. An Import-vs-Build audit (2026-07-05,
web-verified) finds:

1. The field already has bounded, ablatable, self-disclaiming mechanism-indicator assays
   (ReCoN-Ipsundrum arXiv:2602.23232 AAAI-2026; Probing-for-consciousness arXiv:2411.16262;
   synthetic neuro-phenomenology arXiv:2512.19155). ITL does NOT differentiate by "having a testbed."
2. The seven capabilities operator reserved for self-build (adversarial kill-gate; baseline-
   equivalence verdict; mechanism-signature verdict; trace/replay/provenance; leak/RNG/runtime
   sealing; negative-evidence bank; claim-ceiling enforcement) are exactly what NONE of the
   external systems provide and what ITL already has. ITL's differentiation is the ADVERSARIAL
   AUDIT LAYER, not the testbed.
3. Therefore borrow-first, applied honestly, RELOCATES differentiation from "build a testbed"
   to "red-team external positive assays with sealing + a negative bank." Those assays are
   RED-TEAM TARGETS, not bases to build on and not baselines to beat.

Factual corrections to the candidate list (web-verified 2026-07-05): VERSES/Genius defunct
(Friston + COO + CTO resigned 2026-06-27; AI ops ceased; trading halted) — remove as live import
base. pymdp is JAX-first at 1.0.0 — the live occupant of the action-conditioned belief-update class.

## current stage
Track F: S3c-R3 RUNNING (challenger sweep, 30 CPU-h line, 001C contract). S3d/S4/S5/S6 pending.
Repo HEAD at draft time: `2a4502a` (S3d PART0 CPU-time launch preflight). This card patches S5/S6
route planning ONLY; it does not enter the S3c-R3 or S3d evidence path.

## hypothesis (governance-adapted)
Adding a REUSE-GATE + LANDSCAPE-CROSSWALK + EXTERNAL-ASSAY-REDTEAM layer at S5, as a
NON-BLOCKING parallel documentation track, and splitting S6 into a 3-way route, increases Track F's
external relevance and cheapest-validation coverage WITHOUT weakening any gate, changing any
frozen contract, or upgrading the claim ceiling.

## baseline (what this is compared against)
Current plan: S6 is 2-way (testbed qualified → open mechanism card; not qualified → close+bank).
Reuse is deferred to "background consideration at S6." The patch's job is to beat that by making
borrow-first an enforceable gate with a concrete first target, at zero evidence-path cost.

## ablation
Governance card — no mechanism ablation. Sensitivity check instead: if the REUSE-GATE were removed,
Track F could open a mechanism card for a hypothesis class whose strongest existing occupant was
never wired in as a baseline (weak-baseline failure family) — the exact defect this gate prevents.

## trace / replay requirement
Crosswalk provenance: every "strongest existing occupant" claim in the crosswalk cites a
web-verified source (URL + retrieval date) and, where a prior ITL negative lineage applies, the
memory file / artifact id. Red-team outputs follow the standard Evidence Contract
(`artifacts/<redteam_task_id>/` with result/trace/baseline_comparison/replay/failure manifests).

## acceptance gate (the REUSE-GATE itself)
No Track F mechanism card may open until BOTH hold:
(a) the landscape crosswalk names the strongest EXISTING occupant of the candidate mechanism's
    hypothesis class and EITHER wraps it as a battery baseline OR documents, in-contract, why it
    cannot be sealed to the ITL predictor interface; AND
(b) at least one external POSITIVE assay in that class has been red-teamed to a banked
    baseline-equivalence-OR-non-equivalence verdict under the ITL trace-replay-baseline contract.

## claim ceiling (STRICT — unchanged from repo constitution)
Bounded offline mechanism-proxy / testbed evidence under the specified trace-replay-baseline
contract. Red-teaming an external assay yields bounded NEGATIVE evidence about THAT assay's marker
under ITL's contract only. It does NOT prove — and a branch-3 success does NOT upgrade the ceiling
toward — consciousness, subjective experience, emotion, subjectivity, agency, autonomy,
mechanism-validity, or EGO/companion readiness. Falsifying someone else's positive marker is still
bounded negative evidence about their marker, not a positive claim about ITL's own candidate.

## stop condition
- If S3c-R3 or S3d requires ANY change to run this card → STOP (this card is parallel-only).
- If the first red-team target's released artifacts/code cannot be obtained without external
  credentials or a forbidden-layer dependency (LLM integration, external service) → STOP, mark
  that target unavailable, do not substitute scope.
- If drafting the crosswalk surfaces that a candidate class has NO external occupant AND no prior
  ITL negative lineage → that is a genuine build-gap; record it, do not auto-authorize a build.

## rollback plan
Delete this DRAFT file. No frozen file, no `src/`, no `tests/`, no artifact, no threshold, no
battery membership, and no RNG/runtime scheme is touched by this card, so rollback is file deletion
with zero evidence-path impact.

## proposed Track F diff (for operator decision)
- S3c: UNCHANGED. S3c-R3 continues to completion. Contamination check: this card touches no file
  under the running task_id, no frozen_design.json, no threshold, no battery membership, no RNG
  scheme — so S3c-R3 evidence is uncontaminated and MUST continue. The ONLY action that would
  contaminate it — injecting a pymdp baseline into the RUNNING battery mid-sweep — is explicitly
  forbidden here (pymdp enters as an S4 design-only debt item, wired in only at the NEXT battery
  revision under a signed card).
- S3d: UNCHANGED. Should-win certs are testbed QC; keep in full.
- S4: UNCHANGED + one DESIGN-ONLY debt entry: "pymdp-agent wrapper as the strongest structured
  action-conditioned belief-update baseline, under sealed / prefix-only / prediction-before-action
  access." Spec-only; implementation forbidden until a separate signed card.
- S5: ADD `REUSE-GATE / LANDSCAPE-CROSSWALK / EXTERNAL-ASSAY-REDTEAM` as a NON-BLOCKING parallel
  documentation track. It does NOT gate the certification run. It produces the crosswalk +
  the first red-team card (design-only, unsigned).
- S6: replace 2-way with the operator's 3-way route:
  1. testbed NOT qualified → CLOSE, bank negative evidence, no extension.
  2. testbed qualified but external differentiation does NOT hold → downgrade to
     integration / replication / red-team track.
  3. testbed qualified AND it falsifies a false-positive in an existing external positive assay →
     open a mechanism card.
  Ordering caveat: branch-3's condition is reachable via the S5 red-team BEFORE S6, and is the
  cheapest test of whether the testbed has external bite. Claim caveat: branch-3 still yields only
  bounded negative evidence about the external marker; it does not upgrade ITL's own ceiling.

## first import target (touches the evidence stack)
pymdp (JAX 1.0.0) — wrapped as a battery baseline occupant of the belief-update class. Rationale:
baseline-non-equivalence is only meaningful against the strongest existing occupant of the
candidate's hypothesis class; the hand-rolled sequence/RAG members are weaker occupants of
"principled action-conditioned belief update." Risk: pymdp's generative model = the env's
generative model ⇒ generator access would make it an oracle (LRGG oracle-coupling precedent; the
S2 exact-Bayes ideal observer already IS the generator-access ceiling). Mitigation: pymdp baseline
gets the SAME sealed / prefix-only access as every battery member; passes the planted-leak scan.

## first external positive result to red-team (extends reach, not the evidence stack)
ReCoN-Ipsundrum "qualiaphilia" marker (arXiv:2602.23232; code github.com/xcellect/recips).
Rationale: ships code + fixed-param ablations, and the paper self-admits (a) qualiaphilia is
"value-shaped because scenic vs dull directly changes I_t" = label-in-observation / observation-
decodable, and (b) the lesion result is circular ("persistence is implemented by recurrence") =
tautology. Both map 1:1 onto ITL killer families (obs-decodability K1; tautology/parity —
gate4-cross-family-social precedent). Cheapest high-yield first target.

## first adapter Codex should implement
NONE until a signed card. First adapter to SPEC (design-only, unsigned): pymdp → ITL predictor
interface wrapper (commit prediction_json before action; prefix-only obs; no θ/z access; log to
the ITL trace schema; planted-leak-clean). Implementation forbidden until operator signs a
successor card.

## strongest baseline after import
pymdp active-inference agent under sealed / prefix-only access — occupies the principled
action-conditioned belief-update class, stronger than sequence/RAG members for that class
specifically. Caveat: the S2 exact-Bayes ideal observer remains the CEILING (generator-access
oracle); pymdp sits strictly between the degenerate baselines and the ideal.

## what this still cannot prove
- Nothing here is Track F evidence; S5/S3d are still the first claim-bearing stages.
- Wrapping pymdp does not show ITL's candidate is a mechanism; it only strengthens the baseline
  that a candidate must beat.
- Red-teaming ReCoN-Ipsundrum (or any assay) cannot show anything about consciousness / emotion /
  subjectivity / agency / autonomy — at most that a specific published marker collapses to a
  baseline / is observation-decodable / is tautological under ITL's contract.
- A branch-3 outcome does NOT upgrade ITL's claim ceiling.

## Sign-off (operator — REQUIRED before any implementation)
- [ ] Approve verdict: PATCH (keep / patch / pause / close): ______________________
- [ ] Approve S5 REUSE-GATE as NON-BLOCKING (does not gate S5 certification run): ____
- [ ] Approve S6 3-way route: ______
- [ ] Approve pymdp as first import target (baseline, sealed access), spec-only: ______
- [ ] Approve ReCoN-Ipsundrum as first red-team target: ______
- Operator: __________  Date: __________
```
Retrieval sources (web-verified 2026-07-05):
- pymdp JAX 1.0.0: github.com/infer-actively/pymdp
- VERSES defunct: ad-hoc-news.de reports 2026-06-27 resignations / AI ops ceased
- ReCoN-Ipsundrum: arxiv.org/abs/2602.23232 ; code github.com/xcellect/recips
- Probing for consciousness: arxiv.org/abs/2411.16262
- Synthetic neuro-phenomenology: arxiv.org/abs/2512.19155
- Calibration problem (Koch): arxiv.org/abs/2603.27597
- Butlin & Long indicators (TiCS 2025): cell.com/trends/cognitive-sciences (S1364-6613(25)00286-4)
- Othello-GPT linear world model + causal intervention: arxiv.org/abs/2310.07582
```
