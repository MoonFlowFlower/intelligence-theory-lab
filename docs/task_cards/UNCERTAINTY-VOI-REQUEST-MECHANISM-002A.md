# UNCERTAINTY-VOI-REQUEST-MECHANISM-002A

## task_id

`UNCERTAINTY-VOI-REQUEST-MECHANISM-002A`

## problem_definition

001A produced a preserved negative/invalid result: `INSTRUMENT_INVALID`.
The successor question is whether a frozen hold-and-observe VOI task, a
belief-load-bearing regret metric, and an exploit-pressure KG decision rule
can produce bounded offline evidence that smart uncertainty/value-of-information
allocation beats both a tuned static rival and a random-active rival in one toy.

This R1' card banks the frozen preregistration as an ex-ante ancestor of any
implementation or gated run. It does not execute the experiment.

## current_stage

R1' preregistration/task-card bank only.

- Source freeze: `PREREG_UNCERTAINTY_VOI_002A_FREEZE.md` supplied to Codex as
  `PREREG~2.MD`.
- Banked freeze path:
  `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/preregistration.md`.
- Banked LF sha256:
  `bc087cfc13102a57a624b7bb5d8684b50303db7c9be701bdd08d709bffffdf73`.
- Required stop after R1': report commit hash and prereg hash for Claude Yellow
  post-check before R2'/R3'.

## current_layer

Layer 2 engineering implementation/evidence hygiene for this R1' bank.
The frozen downstream experiment is Layer 3 mechanism hypothesis testing.

## mainline_target

Isolated ITL lab artifacts only:

- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/preregistration.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/prereg.sha256`

No EGO runtime, UI, companion, LLM/API, AIRI, deployment, or mainline path.

## enabled_state_requirement

R1' has no runtime entrypoint and no enabled path. R2'/R3' may only create an
isolated 002A runner and tests after this R1' bank remains an ancestor and the
R1' post-check is complete.

## real_trigger_evidence_requirement

R1' trigger evidence is limited to:

- operator/Codex instruction `CODEX-INSTRUCTION-UNCERTAINTY-VOI-002A-BANK-IMPL-20260709`;
- verified frozen prereg LF hash;
- verified 001A prereg hash remains intact;
- verified clean worktree before R1' edits.

No real experiment trigger exists in R1'.

## hypothesis

In the frozen Model-A hold-and-observe task, a Kalman belief plus exploit-pressure
myopic KG decision rule can reduce cumulative regret relative to both a tuned
`static_threshold` rival and a `random_active` rival, while losing its advantage
under wrong-sign feedback, shuffled feedback, uncertainty ablation, and value
ablation as predeclared.

## strongest_baseline

The strongest cheap explanation is that the task rewards active sampling in
general, so an indiscriminate `random_active` policy or a tuned age/request
heuristic (`static_threshold`) can match the mechanism under equal access.
If either rival matches or beats the mechanism by the frozen MDE/CI rule, report
`SIMPLE_ACTIVE_SUFFICIENT` or `STATIC_SUFFICIENT`; do not retune or rescue.

## baseline

Frozen rivals/floors/ceiling from the preregistration:

- `static_threshold`, tuned only on seeds 9301-9310;
- `random_active`;
- floors: `hold_only`, `no_update`;
- ceiling: `oracle`.

## ablation

Frozen controls:

- `wrong_sign`;
- `shuffled`;
- `uncertainty_ablation`;
- `value_ablation`.

Any surviving advantage under the falsifiers or uncertainty ablation is an
attribution failure / invalid instrument per the preregistered verdict rule.

## trace_replay_requirement

R3' must produce gate-scoped trace and `metric_records.json` under
`artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/`, remain at or below 25 MiB,
and pass fresh-process x2 bit-exact replay plus AST RNG audit with a fail-able
positive control. Replay must recompute from serialized state/observations, not
only compare stored hashes.

## computed_evidence_provenance_gate

All R3' scores, baselines, ablations, falsifiers, calibration, transfer, replay,
headroom, tripwire, and verdict fields must be produced by callable computation
paths. Each score must record producer function, input artifacts, run id,
seed/context/episode ids, aggregation rule, and code path hash. Static verdict
dictionaries, unconditional clean reports, hand-written scores, and tests that
only assert pass are forbidden.

## acceptance_gate

R1' acceptance:

1. `preregistration.md` is byte-identical to the source modulo LF normalization.
2. `prereg.sha256` records the LF sha256
   `bc087cfc13102a57a624b7bb5d8684b50303db7c9be701bdd08d709bffffdf73`.
3. `git show <R1'>:artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/preregistration.md`
   normalized by removing CR bytes hashes to that value.
4. Only R1' docs/artifact-bank files are changed.
5. Stop after R1' for Claude Yellow post-check.

R3' acceptance, if later authorized after R1' stop, is exactly the frozen gate
set G1a/G1b/G2/G3/G4a/G4b/G5/G6 plus the tripwire and verdict rule in the
banked preregistration.

## claim_ceiling

R1' claim ceiling: ex-ante preregistration/task-card bank and hash verification
only.

Downstream strongest possible positive claim ceiling: bounded, replayable,
attribution-checked VOI-mechanism-proxy evidence in one toy hold-and-observe
environment. No intelligence, adaptation, world-model, agency, autonomy,
subjectivity, emotion, consciousness, EGO/companion readiness, pet claim, or
mainline effect.

## stop_condition

Stop immediately if:

- the frozen source hash differs from the expected LF/CRLF hashes;
- live repo is not `intelligence-theory-lab` on the expected branch;
- 001A prereg hash is not intact;
- any R1' change would touch 001A artifacts or `src/uncertainty_voi/runner.py`;
- a frozen value must be changed to implement the task;
- a seed block is not disjoint;
- R3' produces a positive claim (requires full hostile audit before positive
  wording);
- R1' commit completes (mandatory stop for Claude Yellow post-check).

## rollback_plan

Before commit, remove only the new 002A R1' files if an R1' precondition fails:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/preregistration.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/prereg.sha256`
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A.md`

After commit, do not rewrite history without explicit operator instruction;
bank a corrective successor instead.

## expected_changed_files

R1' only:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/preregistration.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A/prereg.sha256`
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-002A.md`

Potential later R2'/R3' files are isolated to a new 002A module/tests/artifacts
and must not edit the 001A runner or 001A artifacts.

## forbidden_changes

- No Ego/EgoOperator/EgoDesktop/pet files.
- No LLM, UI, runtime, API key, AIRI, deployment, or external-service path.
- No edit/delete/rewrite of any 001A artifact.
- No edit to `src/uncertainty_voi/runner.py`.
- No post-hoc threshold tuning or seed substitution.
- No hidden `v_i`/tau leak into model observations/action names/fixture names.
- No schema change that hides a failure.
- No push, tag, or remote anchor.

## Auto-Remote-Anchor decision

forbidden

## bounded_audit

- Real objective: freeze the redesigned 002A experiment before any code/run so
  later evidence has an ex-ante ancestor and cannot silently retune after seeing
  results.
- Strongest baseline explanation: a simpler active sampler (`random_active`) or
  tuned static heuristic may achieve the same regret reduction.
- Strongest invalidity reason: the hold-and-observe toy may still lack
  discriminative headroom or may reward sampling frequency rather than KG value
  allocation.
- Falsifies the framing: frozen R3' gate result where `random_active`,
  `static_threshold`, floors, or controls match the mechanism under the
  predeclared rules.
- Still insufficient evidence: a green local test, a single favorable seed,
  a report-only summary, or a pass that lacks callable baseline/ablation/replay
  provenance.
- Mechanism-vs-resemblance classification: only a bounded mechanism-hypothesis
  proxy test; no subjectivity or agency validation.
- Claim ceiling: R1' bank only now; downstream claim ceiling remains toy VOI
  mechanism-proxy only.
- Minimal validation: hash-pin prereg, task card, scoped diff, local commit, and
  no 001A/runner modification.
- Stop condition: R1' commit completed.
- Acceptance signal: committed R1' ancestor with verified banked prereg hash and
  scoped files only.

## collision_record

### Candidate A: minimal implementation

- Evidence produced: a small isolated runner and tests for Model-A regret.
- Strongest cheap baseline that could match it: `random_active` or a tuned age
  heuristic can reduce regret by querying often.
- Leakage / hard-coding risk: high if tests only check fixed outputs or if
  thresholds are adjusted after probe results.
- Smallest falsifying test: random-active CI overlaps or exceeds mechanism under
  paired seeds.
- Expected failure mode: `SIMPLE_ACTIVE_SUFFICIENT` or invalid attribution.

### Candidate B: strongest baseline / shortcut explanation

- Evidence produced: same-access tuned `static_threshold` and `random_active`
  comparisons with floors and oracle.
- Strongest cheap baseline that could match it: this candidate is the baseline
  challenge itself.
- Leakage / hard-coding risk: under-tuning or strawman rival would inflate the
  mechanism; tuning must be restricted to 9301-9310.
- Smallest falsifying test: rival beats or ties the mechanism by frozen MDE/CI.
- Expected failure mode: `STATIC_SUFFICIENT` or `SIMPLE_ACTIVE_SUFFICIENT`.

### Candidate C: mechanism-faithful implementation

- Evidence produced: Kalman belief plus exploit-pressure KG, controls,
  ablations, calibration, transfer, replay, and tripwire under the frozen
  contract.
- Strongest cheap baseline that could match it: indiscriminate active sampling
  if smart allocation adds no value.
- Leakage / hard-coding risk: hidden true values/tau in the policy, unseeded
  RNG, future observation leakage, or a second logic path for tests.
- Smallest falsifying test: exact-zero control deltas, exploit fraction outside
  `(0.02, 0.98)`, or any control/ablation preserving the clean advantage.
- Expected failure mode: `INSTRUMENT_INVALID`, `ATTRIBUTION_FAILURE`, or
  `SIMPLE_ACTIVE_SUFFICIENT`.

Selected downstream approach: Candidate C, with Candidate B as decisive rival.
For R1' only, no implementation is selected/executed; the freeze is banked and
then stopped for post-check.

## prior_negative_evidence_cited

- 001A `INSTRUMENT_INVALID`: the frozen 001A info-step metric at
  `src/uncertainty_voi/runner.py:427` used `regret_t = max_value + cost`, making
  information-step regret blind to belief/incumbent quality. 002A neutralizes
  this with Model-A regret where every step holds `argmax mu` and regret depends
  on belief through the incumbent.
- 001A never-exploiting KG: the 001A rule collapsed to the non-learning floor
  and the Claude Yellow audit recorded 0/4000 exploit/noop actions. 002A
  neutralizes this with exploit-pressure KG and a tripwire requiring both noop
  and query behavior.
- 001A floor-taxonomy error: treating indiscriminate sampling as a weak floor
  would overclaim. 002A reclassifies `random_active` as a strong rival with its
  own G1b/MDE gate.
- LRGG oracle-coupling: oracle or answer-key access can create fake headroom.
  002A restricts the policy to belief/cost inputs, reserves hidden `v_i` for
  offline scoring/oracle only, and forbids true-value/tau leaks.
- LRGG equal-access saturation: equal-access cheap baselines can saturate the
  task. 002A includes tuned static and random-active rivals and converts their
  success into `STATIC_SUFFICIENT` / `SIMPLE_ACTIVE_SUFFICIENT` rather than a
  mechanism claim.
- FSP S3d baseline dominance: baseline dominance / identifiability ceilings
  invalidate apparent discriminability. 002A includes G6 floor/info-value
  anchors and preserves invalid/negative verdicts rather than patching around
  baseline dominance.
- Tripwire lesson from inert mechanisms: exact-zero control deltas or no exploit
  behavior indicate an unwired/inert mechanism. 002A evaluates the tripwire
  before any positive verdict and maps failure to `INSTRUMENT_INVALID` subtype
  `MECHANISM_INERT`.
