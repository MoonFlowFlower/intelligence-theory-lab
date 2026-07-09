# UNCERTAINTY-VOI-REQUEST-MECHANISM-001A

Status: R1 preregistration bank / task-card freeze. R1 is docs/artifact-freeze only.
R2 implementation and R3 gated execution are intentionally downstream and must descend
from the R1 commit. R1 does not authorize a positive mechanism claim.

## task id

UNCERTAINTY-VOI-REQUEST-MECHANISM-001A

## problem definition

Test whether one isolated uncertainty/value-of-information mechanism proxy can
outperform a genuinely tuned static-threshold rival on a restless Gaussian bandit
distribution with costly information, while collapsing under predeclared falsifiers
and ablations. The task must distinguish a belief/VOI mechanism from simpler
threshold, floor, oracle, observation-only, value-only, or leakage explanations.

## current layer

Layer 3 mechanism hypothesis, with Layer 2 engineering evidence hygiene for the
banked preregistration, future isolated implementation, trace/replay, baselines,
and artifacts.

## current stage

R1: ex-ante preregistration and task-card bank only.

Required commit order:

1. R1 banked preregistration + this card.
2. R2 isolated implementation under `src/uncertainty_voi/` with tests.
3. R3 gated run under `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/`.

R2 and R3 must descend from the R1 commit. Any edit to the frozen preregistration
requires a new preregistration that is itself an ancestor of the rerun.

## mainline target

No EGO mainline, runtime, UI, LLM, AIRI, companion, deployment, or external service
target. The only target is an offline ITL lab harness and artifact packet.

## mainline integration status

Not integrated. R1 is a local repo freeze boundary. R2/R3, if later authorized after
review, remain isolated to ITL lab paths.

## enabled-state requirement

R1: no executable path is enabled.

R2/R3, if later authorized, must expose only an isolated local callable implementation
and runner for this task, not a live runtime path.

## real-trigger evidence requirement

R1: the real trigger evidence is the committed banked preregistration body and
`prereg.sha256` matching the frozen LF SHA-256.

R3: the real trigger evidence must be the callable runner invoked on the frozen seed
blocks, beginning with probe env-seed `9001`, with generated machine-readable artifacts.

## hypothesis

The Kalman-belief + myopic KG-VOI request/query mechanism will produce a positive
paired advantage over the tuned `static_threshold` rival on scored seeds, transfer to
held-out seeds, and lose that advantage under wrong-sign feedback, shuffled feedback,
and uncertainty/value ablations. If this does not happen, the correct outcome is a
bounded negative or invalid result, not a patch to force a pass.

## strongest baseline

Primary rival baseline: `static_threshold`, tuned by grid search only on tuning seeds
`9301-9310`, then frozen and evaluated on the scored and transfer seed blocks.

Required floors: `random_query`, `exploit_only`, `no_update`.

Required ceiling: `oracle` with regret `0`, used only as an evaluation reference.

The tuned static rival is not a strawman; if it matches or beats the mechanism under
the frozen rule, the verdict is `STATIC_SUFFICIENT` unless another higher-precedence
invalid/floor verdict applies.

## ablation requirement

Required falsifiers / ablations:

- `wrong_sign`: reflect samples as `x' = 2μ - x`;
- `shuffled`: permute samples by episode before update;
- `uncertainty_ablation`: freeze `σ` to a constant;
- `value_ablation`: make KG ignore `μ`.

The uncertainty ablation must destroy the advantage for a positive mechanism claim.
The value ablation must be significantly below the clean mechanism advantage. If the
advantage survives the falsifiers or uncertainty ablation, the verdict is
`ATTRIBUTION_FAILURE` / `INSTRUMENT_INVALID`, not a VOI pass.

## trace/replay requirement

R3 must emit gate-scoped trace plus `metric_records.json` under the artifact directory
with a fail-closed trace-size assertion of at most 25 MiB. Replay must recompute
candidate behavior from serialized belief state and observation/action records, not
only compare stored hashes. Two fresh-process recomputes must be bit-exact.

## computed-evidence provenance gate

Every reported score, baseline, ablation, falsifier, calibration, transfer, headroom,
replay, leakage/RNG audit, and verdict must come from callable producer functions.
Each score or gate record must include:

- `producer_function`;
- input artifacts;
- `run_id`;
- seed/context/episode IDs;
- aggregation rule;
- code path hash.

Baselines and ablations must be independent callable implementations. Ablations must
rerun episodes under real interventions. RNG audit must include a fail-able positive
control. Any unseeded RNG, unused frozen seed block, hidden-value leak into the
mechanism, or post-hoc threshold tuning blocks the evidence claim.

## acceptance gate

Frozen gates from the preregistration:

- G1 rival-beat: mean paired advantage over tuned static is positive, bootstrap 95%
  CI excludes zero, and relative advantage is at least 10% of static regret.
- G2 falsifiers: wrong-sign and shuffled advantages collapse to CI including zero,
  and clean-minus-falsified collapse is significant.
- G3 ablation: uncertainty ablation collapses to CI including zero; value ablation
  is significantly below clean.
- G4a calibration: aggregate `mean(z_i(t)^2)` is in `[0.7, 1.5]`; 90% coverage is
  reported.
- G4b transfer: held-out transfer advantage CI excludes zero.
- G5 replay/RNG/trace hygiene: fresh-process replay x2 bit-exact, seeded RNG only,
  positive-control RNG audit, trace under the size cap.
- G6 headroom: floors have at least `2.0x` mechanism regret and tuned static retains
  at least `0.10x` of random-to-oracle regret.

Frozen verdict rule:

- `VOI_MECHANISM_PRESENT` iff G1, G2, G3, G4a, G4b, G5, and G6 all pass.
- `VOI_MECHANISM_PRESENT_UNCALIBRATED` iff G1, G2, G3, G4b, G5, and G6 pass but
  G4a fails.
- `STATIC_SUFFICIENT` iff G1 fails.
- `ATTRIBUTION_FAILURE` iff G1 passes but G2 or G3 fails.
- `INSTRUMENT_INVALID` iff G5 fails, G6 fails, seed-disjointness fails, or attribution
  failure is elevated by the frozen rule.
- `CAPABILITY_ABSENT` iff the mechanism is approximately a floor.

Positive verdicts set `positive_claim: true` and require stopping for Claude FULL
hostile audit before any positive wording beyond the frozen result label.

## claim ceiling

Bounded offline evidence that ONE implemented uncertainty/value-of-information
mechanism, in ONE toy environment, beats the best-tuned static-threshold rival on a
VOI-headroom task distribution, and that this advantage collapses under wrong-sign
feedback, shuffled feedback, and uncertainty-ablation, with a calibrating uncertainty
estimate and held-out generalization. Proves NO general intelligence, real-world
adaptation, world-modeling, understanding, self/agency/autonomy, subjectivity, emotion,
consciousness, EGO/companion readiness, and specifically NOT that the pet has this
mechanism. A PASS = a mechanism-proxy for uncertainty-driven VOI decision-making in a
bounded toy.

## stop condition

- R1 stops after the preregistration and this card are committed and reported for
  Claude Yellow post-check.
- R2 must stop if it requires threshold edits, hidden-label access, unseeded RNG, or
  out-of-scope files.
- R3 must run probe env-seed `9001` first and stop if projected cost exceeds the
  operator-set CPU budget. If the numeric budget source is unavailable at R3 time,
  stop before scoring and request the missing budget boundary rather than proceeding.
- Any seed overlap across probe/tuning/scored/transfer blocks fails closed.
- Any positive verdict stops for Claude FULL hostile audit before promotion language.

## rollback plan

R1 rollback is deletion/reversion of:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/preregistration.md`;
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/prereg.sha256`;
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A.md`.

Future R2/R3 rollback must remain isolated to `src/uncertainty_voi/`,
`tests/uncertainty_voi/` or equivalent isolated test paths, and
`artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/`, without rewriting historical
artifacts.

## collision_record

### Candidate A: minimal implementation

- Evidence it would produce: a small local runner that follows the frozen bandit,
  mechanism, static rival, and artifact schema.
- Strongest cheap baseline that could match it: tuned age/period `static_threshold`
  or exploit-only if the environment is saturated.
- Leakage / hard-coding risk: high if the implementation embeds seed-specific
  trajectories, tuned thresholds, or hidden values.
- Smallest falsifying test: static rival has non-negative advantage over the
  mechanism on scored seeds, or G6 shows no headroom.
- Expected failure mode: `STATIC_SUFFICIENT` or `INSTRUMENT_INVALID`.

### Candidate B: strongest baseline / shortcut explanation

- Evidence it would produce: same-access tuned `static_threshold`, floors, and oracle
  headroom demonstrating whether VOI structure is needed.
- Strongest cheap baseline that could match it: age/period rule or request-period rule
  tuned on the frozen tuning block.
- Leakage / hard-coding risk: tuning on scored seeds or changing the threshold grid
  after seeing results.
- Smallest falsifying test: static threshold closes the paired advantage or headroom
  criterion.
- Expected failure mode: `STATIC_SUFFICIENT`, which is an informative bounded negative.

### Candidate C: mechanism-faithful implementation

- Evidence it would produce: deterministic KG-VOI actions from `(μ, σ, cost)`,
  paired seeded worlds, independent baselines, falsifiers, ablations, calibration,
  transfer, replay, RNG audit, and headroom reports.
- Strongest cheap baseline that could match it: tuned static threshold with same legal
  observations and same seed worlds.
- Leakage / hard-coding risk: hidden `v_i` or per-arm `τ_i` entering the mechanism;
  labels leaking through action names, filenames, fixture names, or seed blocks.
- Smallest falsifying test: wrong-sign/shuffled/uncertainty ablation retains the clean
  advantage, or replay cannot recompute behavior.
- Expected failure mode: `ATTRIBUTION_FAILURE` / `INSTRUMENT_INVALID` if the apparent
  win is not attributable to uncertainty-driven VOI.

Selected approach for downstream R2/R3: Candidate C only after R1 post-check, with
Candidate B retained as the decisive rival/shortcut explanation. If Candidate B matches
under access parity, do not rescue the mechanism; report the frozen negative verdict.

## prior_negative_evidence_cited

- LRGG oracle-coupling (`itl-lrgg-tier0-2-official-run-001a`): G6 oracle/floor
  headroom and the hidden-value access ban prevent answer-key/oracle-only headroom
  from being treated as mechanism evidence; G4a uses `v_i` only as offline scoring.
- LRGG equal-access saturation (`itl-lrgg-tier0-2-001b-r1`): G1 against a genuinely
  tuned same-access `static_threshold` and G6 headroom force `STATIC_SUFFICIENT` or
  `INSTRUMENT_INVALID` if a fair simpler baseline saturates.
- FSP S3d baseline dominance / identifiability ceiling (`fsp-route-program-001a`):
  G6 floor dominance and not-saturated VOI headroom prevent claiming a win on an
  instrument with no fair residual headroom.
- Observation-only / value-only baseline equivalence (Baseline Immunity Standard
  `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`): G3 uncertainty/value ablations,
  floors, falsifiers, and leakage/RNG positive controls block a result explainable
  by observation-only, value-only, lookup, degenerate, or leaked channels.

## expected changed files

R1 expected changed files only:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/preregistration.md`;
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/prereg.sha256`;
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A.md`.

## forbidden changes

No EGO, EgoOperator, EgoDesktop, pet, UI, companion, LLM, AIRI, deployment, API key,
external-service, global schema, old artifact rewrite, post-hoc threshold tuning, hidden
`v_i`/`τ_i` mechanism access, or R2/R3 source/test edits during R1.

## Auto-Remote-Anchor decision

Auto-Remote-Anchor: forbidden. R1 authorizes a local commit only. No push, tag, or
remote anchor is authorized by this card.

## what this card does not prove

This card and R1 preregistration bank do not prove VOI mechanism presence, calibration,
transfer, replay, baseline non-equivalence, learning, adaptation, agency, subjectivity,
consciousness, EGO readiness, companion readiness, runtime readiness, or mainline effect.
