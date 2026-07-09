# UNCERTAINTY-VOI-REQUEST-MECHANISM-003A

## task_id

`UNCERTAINTY-VOI-REQUEST-MECHANISM-003A`

## problem_definition

002A produced `ATTRIBUTION_FAILURE` under the frozen 002A rule, but the successor
brief identifies that rule as a gate-signature defect: collapse-to-negative under
falsifiers/uncertainty-ablation was mislabeled as survival because G2/G3 required
the falsified advantage CI to include zero. 003A freezes a corrected,
magnitude-free attribution signature and fresh scored/transfer seeds before any
implementation or run.

This R1'' task banks the frozen 003A preregistration and task card as the
ex-ante ancestor of any 003A implementation or gated evidence. It does not run
the 003A experiment.

## current_stage

R1'' preregistration/task-card bank only.

- Source freeze: `PREREG_UNCERTAINTY_VOI_003A_FREEZE.md` supplied to Codex as
  `PREREG~3.MD`.
- Banked freeze path:
  `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/preregistration.md`.
- Banked LF sha256:
  `9964fbce108228cf32cd2df8834ed8b002bb27bc210956c3186c3fd7b96a5b26`.
- Required stop after R1'': report commit hash and prereg hash for Claude Yellow
  post-check before R2''/R3''.

## current_layer

R1'' is Layer 2 engineering implementation/evidence hygiene. The downstream
003A gated run is Layer 3 mechanism-hypothesis testing only.

## mainline_target

Isolated ITL lab artifact and docs paths only:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/preregistration.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/prereg.sha256`
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A.md`

No EGO runtime, UI, companion, LLM/API, AIRI, deployment, pet behavior, or
mainline path.

## enabled_state_requirement

R1'' has no runtime entrypoint and no enabled path. R2''/R3'' may only create
and execute an isolated `runner_003.py` after this R1'' bank remains an ancestor
and the R1'' post-check is complete.

## real_trigger_evidence_requirement

R1'' trigger evidence is limited to:

- operator/Codex instruction
  `CODEX-INSTRUCTION-UNCERTAINTY-VOI-003A-BANK-IMPL-20260709`;
- verified frozen 003A prereg LF hash;
- verified 002A and 001A prereg hashes remain intact;
- verified HEAD is `e54e8e2b93aa56465e037d34f57d0805c9c88a78` or descendant;
- verified clean worktree before R1'' edits.

No 003A experiment trigger exists in R1''.

## hypothesis

With the 002A simulation/mechanism unchanged and with fresh scored seeds
9401-9420 plus transfer seeds 9421-9430, the mechanism can show a bounded VOI
attribution signature: beat both tuned static and random-active rivals; collapse
to parity or negative under wrong-sign, shuffled, and uncertainty-ablation; show
value-ablation sensitivity; and pass replay/headroom/tripwire. Calibration may
fail because `q=0.004` is frozen and not tuned.

## strongest_baseline

The strongest shortcut explanation remains that active sampling in general, a
tuned age/request heuristic, or a random-active same-access sampler can account
for the apparent benefit. If the mechanism fails G1 against either rival, report
`STATIC_SUFFICIENT` or `SIMPLE_ACTIVE_SUFFICIENT`; do not retune or rescue.

## baseline

Frozen rivals/floors/ceiling:

- `static_threshold`, tuned only on 9301-9310;
- `random_active`;
- floors: `hold_only`, `no_update`;
- ceiling: `oracle`.

## ablation

Frozen controls and ablations:

- `wrong_sign`;
- `shuffled`;
- `uncertainty_ablation`;
- `value_ablation`.

003A's corrected collapse predicate for control C is:

- `A_C` 95% CI upper bound `<= 0`; and
- `A_clean - A_C` 95% CI lower bound `> 0`.

G2 requires collapse under both falsifiers. G3 requires uncertainty-ablation
collapse and value-ablation load-bearing.

## trace_replay_requirement

R3'' must produce gate-scoped trace and `metric_records.json` under
`artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/`, keep trace/metric records
at or below 25 MiB, and pass fresh-process x2 bit-exact replay plus AST RNG audit
with a fail-able positive control. Replay must recompute from serialized state
and observations, not only compare stored hashes.

## computed_evidence_provenance_gate

All 003A scores, baselines, ablations, falsifiers, calibration, transfer,
replay, headroom, tripwire, collapse/survive determinations, and verdict fields
must be produced by callable computation paths. Each score must record producer
function, input artifacts, run id, seed/context/episode ids, aggregation rule,
and code path hash. Static verdict dictionaries, unconditional clean reports,
hand-written scores, and tests that only assert pass are forbidden.

## acceptance_gate

R1'' acceptance:

1. `preregistration.md` is byte-identical to the provided freeze modulo LF
   normalization.
2. `prereg.sha256` records LF sha256
   `9964fbce108228cf32cd2df8834ed8b002bb27bc210956c3186c3fd7b96a5b26`.
3. `git show <R1''>:artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/preregistration.md`
   normalized by removing CR bytes hashes to the expected LF hash.
4. Only R1'' docs/artifact-bank files are changed.
5. Stop after R1'' for Claude Yellow post-check.

R3'' acceptance, if later authorized after R1'' stop, is exactly the frozen gate
set G1a/G1b/G2/G3/G4a/G4b/G5/G6 plus tripwire and verdict rule in the banked
003A preregistration.

## claim_ceiling

R1'' claim ceiling: ex-ante preregistration/task-card bank and hash verification
only.

Downstream strongest possible positive claim ceiling: bounded, replayable,
attribution-checked VOI-mechanism-proxy evidence in one toy hold-and-observe
environment. If the verdict is `VOI_MECHANISM_PRESENT_UNCALIBRATED`, calibration
is not claimed. No intelligence, real-world adaptation, world-modeling, agency,
autonomy, subjectivity, emotion, consciousness, EGO/companion readiness, pet
claim, or mainline effect.

## stop_condition

Stop immediately if:

- the frozen source hash differs from the expected LF/CRLF hashes;
- live repo is not `intelligence-theory-lab` on the expected branch;
- HEAD is not `e54e8e2b93aa56465e037d34f57d0805c9c88a78` or descendant;
- 002A or 001A prereg hash is not intact;
- any R1'' change would touch 001A/002A artifacts, `runner.py`, or `runner_002.py`;
- a frozen value would need to change to implement 003A;
- seed blocks are not disjoint;
- R3'' produces a positive claim, which requires full hostile audit before any
  positive wording;
- R1'' commit completes, because the instruction mandates STOP for Claude
  Yellow post-check.

## rollback_plan

Before commit, remove only the new 003A R1'' files if an R1'' precondition fails:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/preregistration.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/prereg.sha256`
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A.md`

After commit, do not rewrite history without explicit operator instruction; bank
a corrective successor instead.

## expected_changed_files

R1'' only:

- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/preregistration.md`
- `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/prereg.sha256`
- `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A.md`

Potential later R2''/R3'' files are isolated to new 003A module/tests/artifacts
and must not edit the 001A/002A runners or artifacts.

## forbidden_changes

- No Ego/EgoOperator/EgoDesktop/pet files.
- No LLM, UI, runtime, API key, AIRI, deployment, or external-service path.
- No edit/delete/rewrite of any 001A or 002A artifact.
- No edit to `src/uncertainty_voi/runner.py` or `src/uncertainty_voi/runner_002.py`.
- No post-hoc threshold tuning, q tuning, or seed substitution.
- No hidden `v_i`/tau leak into model observations/action names/fixture names.
- No schema change that hides a failure.
- No push, tag, or remote anchor.

## Auto-Remote-Anchor decision

forbidden

## bounded_audit

- Real objective: freeze the corrected 003A gate before implementation/run so
  later evidence is ex-ante and not a post-hoc reinterpretation of 002A.
- Strongest baseline explanation: tuned static or random-active rivals may still
  match the mechanism on fresh seeds.
- Strongest invalidity reason: the gate correction is motivated by a prior run
  and could still be an overfit interpretive repair if fresh seeds do not repeat
  the signature.
- Falsifies the framing: fresh 9401-9420 R3'' result where rivals match, controls
  survive significantly positive, replay/provenance fails, or tripwire/headroom
  fails.
- Still insufficient evidence: re-labeling 002A, rerunning only old seeds, local
  test pass without official artifacts, or a positive result without hostile
  audit.
- Mechanism-vs-resemblance classification: bounded mechanism-hypothesis proxy
  only; no subjectivity/agency validation.
- Claim ceiling: R1'' bank only now; downstream claim ceiling remains toy VOI
  mechanism-proxy only.
- Minimal validation: hash-pin prereg, task card, scoped diff, local commit, and
  no 001A/002A mutation.
- Stop condition: R1'' commit completed.
- Acceptance signal: committed R1'' ancestor with verified banked prereg hash and
  scoped files only.

## collision_record

### Candidate A: minimal gate relabel

- Evidence produced: a corrected verdict layer over existing 002A outputs.
- Strongest cheap baseline that could match it: prior numbers could be
  overinterpreted after seeing them.
- Leakage / hard-coding risk: high, because re-scoring old evidence would look
  like patching failure into pass.
- Smallest falsifying test: fresh seeds do not reproduce rival-beat and collapse
  signature.
- Expected failure mode: overfit gate repair; blocked if it rewrites 002A.

### Candidate B: strongest baseline / shortcut explanation

- Evidence produced: same-access tuned `static_threshold`, `random_active`,
  floors, oracle, and control/ablation comparisons on fresh seeds.
- Strongest cheap baseline that could match it: random-active or static rival
  matches the mechanism by CI/MDE.
- Leakage / hard-coding risk: under-tuning or stale-seed tuning would inflate the
  mechanism; tuning remains 9301-9310 only.
- Smallest falsifying test: `G1a` or `G1b` fails on 9401-9420.
- Expected failure mode: `STATIC_SUFFICIENT` or `SIMPLE_ACTIVE_SUFFICIENT`.

### Candidate C: mechanism-faithful 003A implementation

- Evidence produced: unchanged 002A simulation/mechanism with corrected
  G2/G3/verdict logic and fresh 9401-9430 evidence.
- Strongest cheap baseline that could match it: indiscriminate active sampling
  or tuned age/request heuristics.
- Leakage / hard-coding risk: editing `runner_002.py`, hidden value/tau access,
  seeded-block drift, or schema changes that hide failed gates.
- Smallest falsifying test: controls/uncertainty-ablation survive significantly
  positive or no fresh transfer advantage.
- Expected failure mode: `ATTRIBUTION_FAILURE`, `STATIC_SUFFICIENT`,
  `SIMPLE_ACTIVE_SUFFICIENT`, or `INSTRUMENT_INVALID`.

Selected downstream approach: Candidate C, with Candidate B retained as the
decisive rival/shortcut explanation. For R1'' only, no implementation or run is
selected/executed; the freeze is banked and then stopped for post-check.

## prior_negative_evidence_cited

- 002A `ATTRIBUTION_FAILURE`: the frozen 002A G2/G3 signature mislabeled
  collapse-to-negative as survival. 003A neutralizes this by freezing the
  corrected collapse predicate (`A_C` CI upper `<= 0` and clean-minus-control CI
  lower `> 0`) before any fresh scored run.
- 002A post-hoc risk: the correction is motivated by prior evidence. 003A
  neutralizes this with fresh scored seeds 9401-9420 and fresh transfer seeds
  9421-9430, while preserving 002A artifacts unchanged.
- 001A `INSTRUMENT_INVALID` metric blindness: the 001A information-step regret
  did not load belief/incumbent quality. 003A preserves 002A Model-A
  hold-and-observe regret where regret depends on `argmax mu` every step.
- 001A never-exploiting KG: the 001A mechanism collapsed to a non-learning floor.
  003A preserves exploit-pressure KG and tripwire enforcement that requires both
  noop and query behavior.
- LRGG oracle-coupling: oracle/answer-key access can create fake headroom. 003A
  keeps hidden values/tau out of the policy and uses them only for offline
  scoring/oracle diagnostics.
- LRGG equal-access saturation: same-access cheap baselines can saturate the
  task. 003A keeps tuned static and random-active rivals as G1 gates, with
  `STATIC_SUFFICIENT` / `SIMPLE_ACTIVE_SUFFICIENT` outcomes preserved as
  legitimate negatives.
- FSP S3d baseline dominance: baseline dominance / identifiability ceilings
  invalidate apparent discriminability. 003A keeps floor/info-value anchors,
  replay/provenance, and negative/invalid verdict preservation rather than
  patching around baseline dominance.
