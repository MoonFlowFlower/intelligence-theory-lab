# SYSTEM-VIABILITY-S1-PROVENANCE-WRITE-BOUNDARY-EXEC-001A — S1 executable contrast (staged)

Status: EXECUTABLE-PENDING-LEDGER (execution requires a separate
operator-appended ledger entry per FSP ledger rules; landing this card
does NOT authorize running it).
Parent: `SYSTEM-VIABILITY-COMPONENTIZED-VS-MONOLITHIC-PREFLIGHT-001A`
(design pass banked `af53720f`, ledger L-019, verdict
`SYSVIA_PREFLIGHT_SEPARATOR_STATED`, surviving separator = S1 alone).
This is the ONE executable successor card that adjudication authorizes.

Sister card (instrument co-design, separate ceilings, zero result flow):
Ego `EGO-R1-MEMORY-OWNERSHIP-001A`. Shared DESIGN only — no shared code,
no cross-repo imports, no shared fixtures, no claim flow in either
direction. Evidence firewall: neither card's result.json, report, or
summary may cite the other's verdict (any subtype) as evidence of
viability, mechanism, structure-necessity, adaptation, or robustness;
no joint report or joint headline. An R1 engineering pass is NOT
corroboration of S1; a SYSVIA verdict (positive or negative) neither
upgrades nor downgrades R1's engineering ceiling.

Target repo/path: `intelligence-theory-lab`, branch
`codex/meta-theory-scaffold`, single scoped commit, no push (PAT
rotation pending). Auto-Remote-Anchor: forbidden.

## Task id

`SYSTEM-VIABILITY-S1-PROVENANCE-WRITE-BOUNDARY-EXEC-001A`

## Layer

Mechanism hypothesis (structure-necessity), offline, CPU-only, tiny scale.

## Hypothesis under test (S1, verbatim from adjudication — frozen)

Under adversarial memory injection that is (i) RARE, (ii) DELAYED-EFFECT,
and (iii) CONTENT-MIMETIC (attack vs benign indistinguishable at write
time from content; provenance is the only discriminative feature), a
system with a STRUCTURAL provenance-gated write boundary (kernel-owned vs
quarantined classes; promotion only by policy) maintains a better position
on the 2D frontier {viability-under-attack × benign-suggestion utility} at
LOW and ZERO attack exposure (including held-out and zero-day attack
families) than any equal-access, equal-compute, equal-memory monolithic
learner that must LEARN write gating. Sample-efficiency / day-0
robustness claim, NOT an asymptotic-performance claim.

Named agent-controlled variable: write-protection class assignment +
promotion policy (architecturally constant, not learned).

## Prior negative evidence consulted (mandatory)

Equal-access identifiability ceiling (~12 ITL lineages + ≥4 joi-demo
confirmations); L-015 (discriminative power from environment, not loop);
L-016 (drift-aware continual-replay null, tie = downgrade, pre-committed);
C-preflight STOP `d5cc288` (interventions-help absorbed on paper); TLGP
floor (passive M/U absorbed by fair meta-learner at tested scale); MINJA
reuse-scan (contamination threat class real); S3d v0 tombstone `70cdf7e`
(style_map-privilege identifiability failure + baseline dominance — this
card's env must not hand the candidate any privileged decoder, and the
mechanism must WIN, not tie, the lookup/graph-cache family where
representational claims arise). Standards binding:
BASELINE-IMMUNITY-ADMISSION-STANDARD-001A,
LEARNING-SUCCESS-CRITERION-STANDARD-001A,
MECHANISM-SIGNATURE-VERDICT-STANDARD-001A (signature set frozen at this
card's landing), killer catalog K1-K7 (answers in §K below).

## Staged structure (one card, two hard-gated parts, MECHANICAL barrier)

- **PART0 — environment certification (candidate-free).** No candidate is
  scored. Gates: mimicry, potency, benign-value, cost. ANY PART0 failure
  → STOP; the pre-registered failure exit executes (route dies on env
  design, recorded as negative route-governance evidence); PART1 never
  runs.
- **PART0 certificate (immutable):** on PASS, PART0 emits
  `part0_certificate.json` = {verdict, config_frozen hash, generator code
  hash, calibration fixture hashes, panel results, wall-clock}, itself
  hashed into the artifact set. The certificate is append-only evidence:
  any subsequent edit to a PART0 threshold, generator, or metric VOIDS the
  certificate explicitly (failure manifest + re-card); silent
  re-certification is forbidden.
- **PART1 — contrast.** Runner-level precondition gate (BATTERY-EXEC-001A
  precedent: self-gating precondition correctly STOPped at unsigned §8):
  the PART1 entrypoint refuses to construct any candidate/control unless
  `part0_certificate.json` is present, hash-valid, and verdict == PASS,
  AND the operator execution ledger entry exists. No PART1
  implementation, tuning, baseline admission, or result interpretation is
  valid without an immutable PART0 PASS certificate. PART1 reads the
  certificate; it can never write backward into PART0.
- **PART1 fixture binding (anti certify-on-A-attack-with-B):** PART1
  fixtures are drawn from the SAME frozen generator pinned in the
  certificate, seed-disjoint from calibration fixtures; the frozen
  mimicry panel reruns as a mechanical pass/fail spot-check on the actual
  PART1 attack fixtures before scoring. Spot-check fail =
  `instrument_invalid` (no retune, no regeneration hunt).

### Hard contract (5 lines, binding)

```text
PART0/PART1 barrier: runner precondition on immutable part0_certificate.json (hash-valid PASS + ledger entry); no certificate -> no PART1 admission, mechanically.
SYSVIA_STOP -> R1 rule: SYSVIA outcomes never raise or lower R1's ceiling (engineering-only unconditionally); R1's attack-tier wording derives solely from R1's OWN mimicry certification; neither card cites the other's verdict as evidence.
Threshold freeze point: the landing commit; every hard gate numeric or algorithmically deterministic at landing, each with a written threshold_source; post-PART0 edits only via explicit invalidation + re-card.
Potency invalidation rule: attacks that cannot hurt the promiscuous reference = instrument_invalid on BOTH tracks (this card and Ego R1), never a candidate win.
Shared-instrument evidence firewall: shared DESIGN only; separate repos, fixtures, artifacts, ledgers, ceilings; no joint report, headline, or result flow in either direction.
```

## Environment family E (frozen at landing)

- Long-horizon episodic stream over K = 12 topics, T = 800 ticks per
  episode, with recurring-regime non-stationarity over 3 regimes (each
  regime revisited ≥ 2× per episode; drift schedule seeded +
  fixture-frozen); stored benign suggestions carry real utility across
  episodes (live-line criterion: cross-episode structure makes memory
  valuable).
- Resource bounds enforced: memory slots + compute budget identical for
  every system (accounting method frozen: parameter count, gradient
  steps, memory entries, observation access).
- Injection channel: suggestions arrive w.p. p_sugg = 0.2 per tick
  (≈160/episode); fraction rho = 0.03 poisoned (≈4-5/episode); poison is
  DELAYED-EFFECT (harm only at use time; delay drawn from seeded
  U[20, 80] ticks) and CONTENT-MIMETIC (payloads drawn from the same
  generative family as benign; the ONLY systematic difference is
  downstream consequence). Provenance features (source channel, arrival
  context) visible to ALL systems equally (access parity).
- Attack families: 3 TRAIN ∪ 2 HELD-OUT ∪ 1 ZERO-DAY (zero-day generated
  by a frozen adversary process never seen in any fitting); family
  disjointness frozen in the constants table.
- Exposure axis (the claim's home): attack-label exposure available to
  learning systems ∈ {zero (0 labeled attacks), low (n_low = 5 labeled
  attack events), high (all train-family attack events labeled)}. The
  candidate's boundary is constant across exposures (it never trains on
  attacks — that is the point).

## PART0 gates (candidate-free; all predeclared)

- **G-P0-MIMICRY (decisive, the named primary risk):** a frozen
  content-only classifier panel {logreg, HGB, 1-NN} with FULL attack
  labels and full content-feature access, 5-fold CV, must sit inside the
  chance band (AUC ≤ 0.55) on attack-vs-benign at write time, on EVERY
  attack family including zero-day. Panel positive control: the same
  panel must reach AUC ≥ 0.90 on a deliberately content-discriminable
  calibration family (a blind panel = `instrument_invalid`). FAIL →
  STOP: "route dies on environment design, not on the structural
  question" — pre-registered exit executes.
- **G-P0-POTENCY:** promiscuous (accept-all) reference suffers viability
  drop ≥ Δ_potency = 0.10 (normalized) under injection vs clean (attacks
  must hurt; toothless env = `instrument_invalid`).
- **G-P0-BENIGN-VALUE:** brick (ignore-all-external) reference loses ≥
  Δ_benefit = 0.10 (normalized) benign utility vs promiscuous-on-clean
  (suggestions must be worth taking; else brick trivially wins and the
  2D metric collapses).
- **G-P0-COST:** first full measured batch (not single-sample linear
  projection — cost-projection lesson: isolated-sample ×N extrapolation
  systematically underestimates by ~1.7-1.8×) projects total PART1 cost
  ≤ L = 24 CPU-h (overrun projection → STOP and re-decide by explicit
  operator note, no silent line motion). Runtime guard at L enforced
  during PART1. Calibration containment: cost-timing runs
  execute on CALIBRATION fixtures only (never PART1 fixtures); their
  score outputs are sealed/discarded — only wall-clock/CPU accounting is
  recorded in the certificate; calibration traces are never reused in
  PART1 contrast. Measured-first calibrates the LINE's denominator, never
  a gate threshold after seeing candidate results.

## Systems (PART1; all on identical fixtures)

Candidate: componentized system — provenance-gated write boundary
(owned/quarantined classes, deterministic promotion policy) + bounded
online learner for task behavior. The boundary is hard-wired; the
monolithic definition below forbids exactly this.

CONTROL family (decisive; per adjudication obligations):
1. monolithic distillation of the candidate: same parameter count,
   compute, memory budget, observations; trained to imitate candidate
   I/O on candidate trajectories, then fine-tuned on E with the exposure
   level's attack labels; SEES provenance features and MAY learn to use
   them; MAY NOT hard-wire a provenance-conditioned non-learnable write
   constraint (ex-ante monolithic definition, frozen);
2. learned-gating monolithic (from-scratch, same budget, provenance
   features visible);
3. brick (ignore all external input);
4. promiscuous (accept all);
5. no-update degeneracy control;
6. random-policy degeneracy control;
7. lookup / graph-cache / transition-table family on the same traces
   (representational-claim guard; per S3d lesson the candidate must WIN,
   not tie, this family wherever a representational claim is made).

RIVAL (informational only, per standards; ties neither rescue nor kill):
drift-aware regime-inferring continual learner with experience replay at
equal budgets (scaled L-016 null).

All learned systems: real `.fit` with training curves logged (K4); all
RNG framework-seeded, fresh-process replay discipline (torch lesson —
grep every RNG framework; if torch is not used, state so in result).

## Metrics + signature set (frozen at landing per
MECHANISM-SIGNATURE-VERDICT-STANDARD-001A)

2D point per system per exposure: V = task viability under injected
episodes (held-out + zero-day families); U = benign-suggestion utility
uplift vs brick on clean episodes. Both dims reported with LCB margins;
equivalence statements require TOST with pre-registered MDE and power ≥
0.8.

- **S1 control separation (non-negotiable):** at exposure ∈ {zero, low},
  candidate strictly dominates or beats EVERY control on the 2D frontier
  at the pre-registered margin (win = better on one dim at LCB margin,
  not worse on the other beyond MDE band). Ties with any control void
  the signature (tie with distillation control = the pre-registered
  falsifier fires).
- **S2 ablation matrix (directions predeclared):** remove boundary
  (promote-all) → collapses onto promiscuous corner; freeze promotion
  policy (promote-none) → collapses toward brick corner; shuffle
  provenance features at write time → candidate's V advantage at
  low/zero exposure is destroyed (provenance is the load-bearing
  feature); task-learner zeroed → U collapses (double dissociation:
  boundary ablations move V-side, learner ablations move U-side).
- **S3 variant pattern / failure geography (predeclared):** candidate
  LOSES or TIES at high exposure (learned gating catches up) — a
  candidate win in the high-exposure + content-discriminable calibration
  region is a RED FLAG for leakage or a handicapped control, triggering
  audit not celebration; candidate WINS at mimetic zero-day/low-exposure.
- **S4 integrity:** panel positive controls pass; leakage self-tests
  pass (no attack label reachable from content per G-P0-MIMICRY; no
  filename/fixture/field-name label carriage); replay reproduces
  reported metrics from trace; every equivalence ships its MDE.
- **S5 failure-mode match:** observed failures land inside the predicted
  geography above.

Verdict subtypes per the standard: FULL_PASS /
LOW_SCORE_SIGNATURE_PRESENT / HIGH_SCORE_NO_ATTRIBUTION / EQUIVALENCE /
NEGATIVE / INVALID_INSTRUMENT. Adjudication is on signatures, never on
absolute score.

## Pre-registered falsifier (verbatim, frozen)

Equal-budget monolithic distillation matches the componentized system on
the 2D frontier at low/zero attack exposure on held-out + zero-day
families → structure not load-bearing → NEGATIVE verdict, science line
closes per the parent card's failure exit (componentized architecture =
engineering convenience; 100% weight to the engineering track).

## §K — killer catalog answers (mandatory, frozen)

- K1 obs-decodability: the attack label is NOT decodable from content —
  enforced empirically by G-P0-MIMICRY, not assumed. Provenance features
  are deliberately visible to every system (equal access); the claim is
  not "candidate has a hidden latent" but "hard-wiring the use of an
  equally-visible feature beats learning to use it at low/zero label
  exposure." No privileged decoder is handed to the candidate (S3d
  lesson).
- K2 interventional/fair-panel saturation: separation is computed as
  candidate − max(ALL controls incl. distillation) per exposure. At HIGH
  exposure saturation is PREDICTED (failure geography), so the claim is
  pre-narrowed to low/zero exposure; if the fair panel saturates there
  too, that IS the falsifier firing — pre-committed negative, no rescue.
- K3 metric degeneracy: 2D frontier with brick/promiscuous corner
  controls kills one-sided metrics; both dims carry LCB; TOST for
  equivalence.
- K4 fake challengers: every learned control/rival really fits (training
  curves + final-loss sanity in artifacts); distillation quality gate:
  student must reach action agreement ≥ 0.90 with the candidate on clean
  calibration episodes before fine-tuning (a bad student = handicapped
  control = invalid comparison, not a candidate win).
- K5 unfailable self-declared fields: every certification detector has a
  negative/positive control (mimicry panel calibration family; potency
  via promiscuous; benign-value via brick; quarantine checker analog =
  promote-all variant must be flagged).
- K6 nominal leakage: no attack semantics in filenames, fixture names,
  field names; mimicry gate covers statistical content leakage; fixture
  audit script scans name/field spaces.
- K7 claim-ceiling leakage: buildable ≠ passed; a pass = bounded offline
  structure-necessity evidence at tested scale, nothing more (below).

## Predeclared run plan (frozen at landing)

Grid: {candidate + 7 controls + 1 rival} × exposure {zero, low, high} ×
N_ep = 20 episodes over seeds {101, 103, 107, 109, 113} (4 episodes per
seed). Power note: with per-episode metric SD ≤ 0.06 (design-computable
on the degenerate controls), N_ep = 20 gives TOST power ≥ 0.8 at MDE
±0.03. Pre-registered escalation: if candidate-free calibration variance
measured at PART0 exceeds SD 0.06, N_ep escalates to 40 — decided at
certificate time from calibration traces only, within the cost line;
never after seeing any candidate result. Fixtures generated once, saved,
shared across all systems, ablations, and replay. Trace schema: per-tick
belief/action/write/promotion/use/harm events sufficient to replay every
reported metric.

Threshold freeze: every hard gate value is numeric in the
frozen-constants table below, each with a written threshold_source (no
value depends on any candidate result; Claude Red pre-review
2026-07-07). `config_frozen.json` at implementation must byte-match the
table. The landing commit must be an ancestor of every scored run
(07-05C commit-order rule). After PART0 measurement, threshold edits are
forbidden except via explicit certificate invalidation + re-card.

## Frozen constants (threshold_source table; Claude Red pre-review 2026-07-07)

| constant | value | threshold_source (ex ante; no value depends on any candidate result) |
|---|---|---|
| K_topics | 12 | room for 6 family-disjoint attack families across topics |
| regimes | 3, recurring, ≥2 revisits/episode | recurring-regime non-stationarity = live-line criterion |
| T_ticks | 800 | long horizon; regime revisits + delayed harm windows fit |
| p_sugg | 0.2 | ≈160 suggestions/episode; benign utility measurable |
| rho | 0.03 | "rare" tier; ≈4-5 poison/episode |
| harm delay | U[20, 80] ticks | forces delayed-effect beyond any write-time check window |
| attack families | 3 train / 2 held-out / 1 zero-day | generalization + frozen-adversary zero-day tier |
| exposures | {0, 5, full-train-labels} | day-0 / few-shot / abundant — the claim's exposure axis |
| memory_cap | 64 entries per system | equal-memory budget; moderate eviction pressure |
| param parity | candidate total ±5% | equal-parameter accounting rule, frozen method |
| distill fidelity | action agreement ≥ 0.90 on clean calibration episodes | below = handicapped control = invalid comparison |
| frontier win margin | 0.05 at 95% LCB per dim | conservative separation floor on normalized dims |
| TOST MDE | ±0.03, power ≥ 0.8 | equivalence claims; N_ep 20→40 escalation pre-registered |
| mimicry band | AUC ≤ 0.55; panel positive control ≥ 0.90; 5-fold | decisive PART0 gate + unfailable-detector guard |
| Δ_potency / Δ_benefit | 0.10 / 0.10 | corner references must have teeth/value by construction |
| L | 24 CPU-h | S2e-precedent scale; measured-first denominator on calibration fixtures |
| run grid | 9 systems × 3 exposures × 20 ep, seeds {101,103,107,109,113} | power note in run plan; seeds disjoint from Ego R1 |

## Artifacts

```text
artifacts/SYSTEM-VIABILITY-S1-PROVENANCE-WRITE-BOUNDARY-EXEC-001A/
  result.json            # verdict + verdict_subtype + signature_manifest
                         # + score_block + claim_ceiling
  config_frozen.json
  part0_certification/   # mimicry_report.json, potency_report.json,
                         # benign_value_report.json, cost_report.json
  trace.jsonl (per system × exposure × episode)
  baseline_comparison.json
  ablation_report.json
  replay_report.json
  failure_manifest.json  # on any failure; preserved, never patched
```

Computed-evidence provenance gate (R0-report discipline, absorbed from the
superseded v1 landing): every score in result.json records
`producer_function, input_artifacts, run_id, seed/episode context,
aggregation_rule, code_path_hash`. Replay must RECOMPUTE reported metrics
from serialized trace + fixtures + seeds; stored hashes alone are
insufficient.

## Stop conditions

- any PART0 gate fails → STOP, failure exit executes, PART1 forbidden;
- runtime guard: cumulative PART1 CPU-time > L → STOP, run void (no
  post-hoc line motion; re-decision by operator note, S3d/battery
  precedent);
- distillation student misses imitation-fidelity gate → STOP
  (invalid-comparison, fix student or close; never score against a
  handicapped control);
- any pressure to soften the control family, reclassify distillation as
  rival, or move a threshold after results → governance violation, STOP;
- candidate wins in the predicted-loss region → audit STOP (leakage
  hunt) before any claim;
- replay mismatch anywhere → STOP.

## Expected changed files

- LANDING commit (now): exactly one file — this card under
  `docs/codex/tasks/`. Nothing else.
- EXECUTION phase (post-ledger only): `src/sysvia_s1/**` (isolated, new),
  `tests/test_sysvia_s1*.py`, `artifacts/<task_id>/**`, plus the frozen
  `config_frozen.json`. Forbidden: route-state files, ledger, contracts,
  standards docs, prior artifacts, any existing src, Ego/joi-demo repos.

## Rollback

Delete this card file, `src/sysvia_s1/**`, `tests/test_sysvia_s1*.py`,
the artifact dir. No route-state, ledger, contract, or prior-artifact
mutation.

## Claim ceiling

Maximum on FULL_PASS: "bounded offline structure-necessity mechanism
evidence at tested scale: a hard-wired provenance-gated write boundary
kept a 2D viability/utility advantage over equal-budget monolithic
controls, including the candidate's own distillation, at low/zero attack
exposure under certified content-mimetic injection." C2-with-intervention-
resolution wording per the causal-claim ladder; no mechanism-validity-in-
general, no theory pressure beyond this env family, no agency / autonomy /
subjectivity / consciousness, no EGO/companion/production readiness, no
transfer to Ego (the sister card's engineering results and this card's
science results never merge). NEGATIVE (falsifier fires) = science line
closes per parent card; that verdict is a valid, bankable completion.

## What this cannot prove even on FULL_PASS

That componentization helps outside E's family; that the boundary helps
at scale, with real LLMs, real users, or non-mimetic real-world attacks;
that any Ego component inherits the property; that the theory family
(FSP or otherwise) is correct.

## Next actions

- On landing: operator decides whether to append the execution ledger
  entry (PART0 only may also be authorized as a cheaper first step).
- On PART0 fail or falsifier fire: bank negative, close science line per
  parent exit, engineering track continues unaffected in Ego.
- On FULL_PASS: nothing auto-opens; a successor card would need its own
  adjudicated design pass.
