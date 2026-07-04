# FSP-MASTER-PHASE-PLAN-001A — Program Phases, Gates, and Stage Discipline

- Status: ACTIVE planning document. Stage transitions recorded ONLY in `FSP-STAGE-LEDGER.md` (append-only); this document defines the structure, the ledger holds the state.
- Amendment A2 (2026-07-01, pre-freeze): score–mechanism decoupling principle + candidate-verdict subtypes LOW_SCORE_SIGNATURE_PRESENT / HIGH_SCORE_NO_ATTRIBUTION with anti-backdoor guards (control-separation non-negotiable; signature set frozen at card time; predicted failure geography required; two-track claim separation). See section below.
- Amendment A1 (2026-07-01, pre-freeze): adopted 5 required edits from independent external audit (GPT-5, user-supplied) with 2 corrections — (i) P0.4 preconditions bind to Track-T's own banked TLGP certification, not N0/PUM (cross-track false dependency removed); (ii) gate schemas reference the constitution §10 terminal vocabulary + gap_certificates vector instead of local terminal lists (anti-schema-fragmentation). Edits: P0/P1 exit-mode splits, per-subgate P1 requirements, P0.4 hard preconditions, no-lookahead allowed/prohibited boundary + skeleton horizon, ledger entry-type protocol (v2 in ledger header).
- Date: 2026-07-01
- Claim ceiling (invariant across ALL phases, transitions never raise it): bounded offline mechanism evidence under specified trace/replay/ablation/baseline contracts. The "ultimate goal" reachable by this lab is Phase-3 exit — a composed system whose six mechanism families each carry banked, ablation-attributed, replay-valid, baseline-non-equivalent evidence. Joi is direction, not deliverable. Consciousness/emotion/agency claims are unreachable by construction at every phase.
- Node mapping: contingency-tree node IDs (N0–N4, `FSP-ROADMAP-CONTINGENCY-001A`) remain authoritative for failure routing; phase IDs (P0.x–P3.x) are authoritative for scheduling. Mapping is explicit below; no third numbering may be introduced.

## Two tracks, one foundation

- Track T (TLGP capability-witness): rule-inference axis. Currently owns the trainability question (Post-LN/warmup confound). Its validated training recipe is a shared prerequisite for Track-T rung3 powered rerun AND FSP N3.
- Track F (FSP): user-latent / memory / boundary axes. N0 authorized.
- Rule: one active execution card per track; Codex attention serialized (main thread), GPU jobs may run in background; no mixed commits across tracks.

## Phase 0 — Instruments & Foundations  [WE ARE HERE]

Goal: certified environments + resolved training recipe + governance loop proven end-to-end once.

- P0.1 TLGP rung1 trainability scout (Track T) — RUNNING (Codex). Exit: banked verdict (recipe validated OR bounded negative). Feeds P0.4 and P1.4 gates.
- P0.2 N0 PUM-ENV identifiability certification (Track F) — AUTHORIZED, queued behind P0.1 for Codex attention. Exit: banked verdict + gap_certificates + independent audit. THE first-loop closure.
- P0.3 First-loop retro — process-debt list from P0.2 execution (instrument backlog only; no scope additions). Exit: retro note banked.
- P0.4 (conditional) TLGP rung3 powered learner rerun — lab-side asynchronous GPU execution (assistant cannot monitor without artifact readback), frozen harness. HARD preconditions, all required: (1) P0.1 verdict = recipe validated or bounded interpretable regime; (2) Track-T's own banked environment certification stands (TLGP rung3 identifiability probe — NOT an N0/PUM dependency; cross-track dependencies are forbidden unless declared); (3) power/MDE preregistered; (4) seed bank frozen; (5) baseline battery frozen; (6) zero threshold changes relative to the scout. Exit: banked verdict either way. If P0.1 negative: P0.4 closes unexecuted, banked as blocked-by-trainability.
- P0.5 SBMC-ENV + RIA-drift design cards drafted (design-only; gated on P0.2 verdict so PUM lessons propagate). Exit: cards drafted, NOT authorized.

Phase exit gate — THREE MODES (machine-checkable pointers into artifacts/; mode determines what opens):

- P0-positive-exit: ≥1 env PASS_IDENTIFIABLE + P0.1 banked (either direction) + first-loop retro complete → P1 sub-gates may open per their own requirements (below).
- P0-negative-exit: N0 terminal negative after allowed redesigns + P0.1 banked + retro complete → PUM-dependent P1 cards (P1.1/P1.2/P1.4) blocked; route weights shift to SBMC/RIA/TLGP-ext per contingency tree; P1.3 may still open on its own gate.
- P0-invalid-exit does not exist: unresolved instrument/PC/leakage/oracle/power failures do NOT exit P0 — fix instruments inside P0 (constitution L1); no P1 opens.

Note: "P0.1 banked" ≠ "recipe fixed". A trainability-debt verdict satisfies P0 exit but keeps P1.4 locked. Track isolation invariant: P0.1 and P0.2 run in parallel ONLY because they share no mutable thresholds; neither may retro-modify the other's gates or criteria after seeing results.

## Phase 1 — Single-Mechanism Evidence

Goal: first bounded non-equivalence results, one env and one mechanism family at a time.

Per-subgate requirements (a coarse "P0 done" opens NOTHING; each sub-stage has its own gate):

- P1.1 = N1: Route-1 PE-gated memory + consolidation on PUM-ENV, budget-conditioned. Gate: N0 PASS with Gap-1 AND Gap-3 certified + P0.3 retro complete.
- P1.2 = N1.5: epistemic action selection double-dissociation. Gate: N0 Gap-2a certified AND Gap-2b ∈ {certified, one_sided_untested with declared scope cap} + P1.1 posterior infrastructure exists (access parity).
- P1.3 = N2: SBMC build + hash-chain vs consistency separation → run. Gate: P0.5 SBMC design card + SBMC's own environment PCs. Does NOT depend on N0.
- P1.4 = N3: trained latent predictor (rung0-analog → rung3-analog). Gate: N0 PASS AND P0.1 recipe validated (trainability positive controls PASS). A trainability-debt verdict keeps this frozen regardless of P1.1's success — no indirect opening.

Phase exit gate — THREE MODES:

- P1-positive-exit: ≥2 mechanism families with positive or conditionally-positive banked evidence, each through its full ablation/baseline contract → P2 combination allowed.
- P1-mixed-exit: exactly 1 positive survivor + clean negatives elsewhere → only narrow-P2 around that survivor (drift/adaptation extensions); full hybrid (P2.3) stays closed.
- P1-route-evidence-exit: ≥2 banked outcomes but positive survivors < 2 (clean equivalences / engineering-sufficient / negatives) → P2 combination does NOT open; next step is route-weight update / redesign / tombstone decision per contingency tree. Clean negatives are good evidence and insufficient premises for composition — both at once.

## Phase 2 — Composition & Adaptation

Goal: mechanisms together; non-stationarity; deferred families M4/M6.

- P2.1 PUM drift variant + RIA non-stationary extension (M2 adaptation curves, PE-spike→relearn).
- P2.2 Cross-env single system (breadth-over-peak per LEARNING-SUCCESS §2). (= N4 pilot)
- P2.3 Hybrid integration, module-ablation-only claims (Route 5; architecture pruning is success).
- P2.4 M4/M6 conflict battery: persistent-but-updatable objective + rule-conflict explanation traces (design card first; these were deliberately deferred).

Phase exit gate: one system across ≥3 certified envs; every retained module earns its preregistered ablation delta; transfer matrix measured.

## Phase 3 — Developmental Scaling

Goal: growth curves instead of point results.

- P3.1 Task-family growth grammar + per-stage re-certification (fair battery re-run each stage; saturation sentinel per stage). (= N4 full, Route 4)
- P3.2 Forward/backward transfer, forgetting, adaptation-speedup with from-scratch/frozen/specialist controls.
- P3.3 Scale-one-axis decision (model capacity vs env richness vs language rendering) — exactly one, preregistered choice rule: largest surviving headroom.

Phase exit gate (= program's reachable "ultimate goal"): six mechanism families each with banked bounded evidence, composed, with growth curves, all under contracts. Deliverable: program-level evidence dossier. P3 exit is the end of this research program's in-scope ambition, not the beginning of a product claim: P3-exit ≠ Joi, ≠ EGO-ready, ≠ human-facing system, ≠ consciousness/emotion/autonomy/agency evidence. Strongest P3 claim: bounded offline developmental / cross-environment mechanism evidence.

## Phase 4 — Boundary Crossing (OUT OF CURRENT LAB SCOPE — listed to make the boundary visible, not to authorize it)

- P4.1 Language-rendered environments with full re-certification (surface-remap discipline scales here).
- P4.2 Human-in-the-loop calibration studies — requires new ethics/scope governance, not coverable by this lab's contracts.
- P4.3 EGO-mainline integration decision — forbidden under current CLAUDE.md boundary; would be a new program with its own constitution.

Entering any P4 item without a new operator-level charter is a governance violation, whatever the evidence looks like. P4 requires: new charter, new safety model, new consent model, new evaluation protocol, new claim ceiling. No P0–P3 artifact automatically authorizes P4. Explicitly charter-gated regardless of evidence quality: human experiments, live EGO integration, affective rendering, relationship-facing UI, persistent user deployment.

## Stage discipline (how "严格按阶段" is enforced, mechanically)

1. Single source of truth: `FSP-STAGE-LEDGER.md`, append-only. Current stage = last entry. Rewriting or deleting entries is a governance failure.
2. Card admission rule: every new task/execution card MUST carry a header line `stage: Px.y / ledger: L-nnn` proving its stage gate is open. Auditor checks this FIRST; a card citing a closed or future gate is rejected before content review.
3. Gates are artifact pointers, not narrative: a gate is open iff the named banked artifacts exist with the named verdicts. "We're confident" opens nothing.
4. No-lookahead rule — design may lead, execution may not:

   Allowed before a gate opens (within skeleton horizon = current phase + 1 only): conceptual route memos, contingency trees, interface sketches, baseline inventories (membership lists), risk registers, NON-EXECUTABLE card skeletons (task id, problem, stage/gate binding, dependencies, claim ceiling — explicitly marked NON-EXECUTABLE-SKELETON).

   Disallowed before a gate opens: executable task cards, implementation patches, run scripts, threshold-bearing or acceptance-number-bearing card content, artifact-producing candidate runs, claim-bearing report templates. Violation = blocking finding.

   Corollary (anti-tuning): thresholds and acceptance numbers enter a card ONLY at drafting time after its gate opens, and freeze immediately. Pre-writing numbers and "lightly adjusting" them after upstream results arrive is post-hoc tuning by construction and is forbidden — the adjustment's legality is determined by WHAT changes (structure: legal with ledger entry; thresholds/battery/claim: never).
5. One active execution card per track; auditor ≠ implementer at every verdict; failure/instrument-repair loops do not advance stage and do not consume redesign budget (constitution L1).
6. Stage transitions are operator acts: Codex/Claude may PROPOSE a transition with the evidence pointers; only the operator appends the ledger entry.
7. Every phase exit triggers a retro entry (process debt → instrument backlog, never new scope).
8. Claim ceiling audit at every transition: if any banked wording exceeds the program ceiling, transition blocks until the wording is corrected by supersession note (never by rewriting the artifact).

## Score–mechanism decoupling (Amendment A2, 2026-07-01)

Principle (dual constraint, both binding): do not optimize for benchmark score; do not excuse absence of mechanism signatures. Absolute score belongs to the product domain; separation-from-controls belongs to the science domain. What candidate experiments chase is the preregistered separation signature (win-where-predicted, lose-where-predicted, ablation-destroys, NULL-env-silent, controls-separated), not a scalar.

Candidate-experiment verdict subtypes (to be instantiated in P1 card vocabularies when their gates open; NOT ledger entries — the ledger tracks stage transitions, not experiment verdicts):

- LOW_SCORE_SIGNATURE_PRESENT: absolute performance below the oracle/aspiration level, but ALL of: candidate separates from every control baseline (non-negotiable — losing to a control voids this subtype categorically), preregistered ablation matrix confirms directional predictions, positive/negative controls pass, replay reproducible, power sufficient, failure modes match theory. Allowed claim: bounded mechanism-signature evidence at low absolute performance. Forbidden: product success, mainline readiness, any functional-subject language.
- HIGH_SCORE_NO_ATTRIBUTION (= roadmap N1.F4 "unattributed win", named): high absolute performance but ablations do not destroy, or a control matches, or trace cannot attribute the win. Allowed claim: performance result only. Forbidden: mechanism evidence. Routed per N1.F4 (attribution hunt → prompt/prior false-positive classification → env tightening).

Guards:
1. Baseline-separation is a mandatory component of any "signature" — ablation sensitivity without control separation is evidence that the system has parts, not that a mechanism works.
2. Anti-signature-hacking: the signature set (ablation matrix cells + directional predictions + should-win/should-lose variants) freezes at card time. Signatures discovered post hoc are exploratory annotations and cannot support a verdict. A low score triggers the preregistered diagnostic branch of the contingency tree, never post-hoc metric relitigation.
3. Theory correctness includes predicted failure geography: a candidate card must predeclare where its mechanism should LOSE (probe-free variants, no-drift variants, NULL env). A theory that only predicts wins is not yet a mechanism theory.
4. Two-track separation: product-track success (joi-demo, Bar-1-class life-likeness signatures) and science-track success (this program's contracts) are distinct success functions. Claims never flow from product to mechanism, nor are product decisions blocked on mechanism proof. Precedent: JOI-DEMO-001A banked headline — in-distribution hardcoded beats learner; learning's value appears only under drift — is this amendment's empirical anchor.

## Current position (as of 2026-07-01)

Phase 0. P0.1 RUNNING (Codex, Track T). P0.2 AUTHORIZED-QUEUED (Track F). Everything else gated. Nearest decision point: P0.1 verdict → (recipe OK? spawn P0.4 GPU background) → Codex main thread to P0.2 S0 freeze ceremony.
