# BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-STEP-A-PREREG-001A

Status: PHASE A PRE-REGISTRATION FREEZE ONLY. This card freezes the borrow-first
environment-selection/headroom-probe interface and unscored harness contract. It
does not score controls or candidate environments. It does not certify any
borrowed environment. It stops after a scoped commit/push for Claude Red-audit.

## Task id

BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-STEP-A-PREREG-001A

Parent card:
`docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.md`

## Problem definition

Freeze a borrow-first candidate-free headroom probe before selecting or building
a new environment. The probe must first prove that its own controls separate:

- POS-INTERNAL E* from the R4 concrete-env argument must yield HEADROOM.
- NEG `5a846d5` scout must yield SATURATED.

Only after Claude Red-audit may Phase B wire borrowed symbolic environments and
score them. This task exists to prevent post-hoc environment selection,
baseline weakening, band changes, or SATURATED-to-HEADROOM rescue.

## Current layer

Engineering implementation + mechanism-hypothesis support / evidence-governance
only. No subjectivity-validation or philosophical-consciousness layer.

## Current stage

PHASE A: pre-registration freeze, unscored callable harness, exact-scope commit,
branch push, then STOP for Claude Red-audit.

## Mainline target

None. This is an isolated offline script package under
`scripts/env_headroom_probe/`. It must not touch EGO runtime, N2/R4 frozen specs,
`src/` mechanism code, global config, credentials, UI, LLM/AIRI integration, or
deployment.

## Enabled-state requirement

Default CLI mode must emit the frozen contract only. Official control/candidate
scoring is not enabled by default. Any future Phase B scoring must be explicitly
authorized after Claude Red-audit and must write artifacts under
`artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/`.

## Real-trigger evidence requirement

Phase A real-trigger evidence is limited to:

- saved parent card;
- saved STEP-A preregistration card;
- callable script package import/CLI checks;
- focused tests over synthetic unit fixtures and contract metadata;
- no official control or candidate environment result artifacts.

Phase B real-trigger evidence, not authorized here, must include explicit CLI
invocation, two fresh-process recomputes, `probe_valid==true`, trace rows,
baseline comparison, ablation report, replay report, reuse matrix, and a failure
manifest when anything fails.

## Hypothesis

Borrow-first can prevent premature bespoke environment construction if a frozen
adapter interface and baseline floor first classify candidate symbolic
environments as HEADROOM or SATURATED under equal access. The most likely useful
outcome is negative: many borrowed environments will be SATURATED by cheap
lookup/graph/obs-only floors before any mechanism claim is admissible.

## Strongest baseline / shortcut explanation

A candidate environment can look useful because:

- target labels are directly visible in observations;
- per-user lookup or nearest-neighbor solves the split;
- count tables or frequency marginals saturate the oracle;
- graph closure / arc consistency is the real solver;
- obs-only decoder learns fixture names, action names, or schema artifacts;
- ideal/oracle has illegal answer-key access and is mistaken for fair headroom.

The floor must therefore take the maximum over the full frozen family. A tie
within the equivalence band is SATURATED, not near-success.

## Frozen environment set

### Control environments for `probe_valid`

1. `POS_INTERNAL_ESTAR`
   - Source: `docs/codex/tasks/SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A.md`
     and `artifacts/SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A/r4_concrete_env_argument.json`.
   - Interface role: internal positive control for cache-void compositional
     held-out structure.
   - Expected verdict: `HEADROOM`.

2. `NEG_5A846D5_SCOUT`
   - Source commit: `5a846d51e` (`P0.5-SBMC-ENV-HEADROOM-SCOUT-001A STEP-A:
     pre-register relational SBMC headroom scout + unrun harness; no scoring`).
   - Current source readback path: `src/sbmc_headroom_scout_001a/` is unchanged
     from `5a846d5` except later ledger text.
   - Interface role: negative control for lookup / graph-closure saturation.
   - Expected verdict: `SATURATED`.

### Borrowed candidate environments for Phase B only

These are frozen as planned candidates but must not be scored in Phase A.
Adapters may be dropped in Phase B only if unavailable or non-symbolic, with a
failure-manifest entry. Do not fake an adapter.

1. `minigrid:MiniGrid-MemoryS13Random-v0` — symbolic observation adapter only.
2. `minigrid:MiniGrid-KeyCorridorS3R1-v0` — symbolic observation adapter only.
3. `bsuite:memory_len/0` — memory-length probe.
4. `bsuite:memory_size/0` — memory-size probe.
5. `bsuite:umbrella_length/0` — generalization-over-delay probe.
6. `dm_alchemy:symbolic_default` — symbolic only if cheaply feasible; otherwise
   record as dropped in `failure_manifest.json`.

Pixel renderers, physics-state adapters, and environment-specific mechanism
code are forbidden.

## Frozen adapter interface

Every adapter must emit a deterministic list of records:

```json
{
  "record_id": "string",
  "split": "train|eval",
  "group_id": "string",
  "O": {
    "schema_version": "env_headroom_probe.observation.v1",
    "legal_observation_fields_only": true
  },
  "y": ["target_label"],
  "y_star": ["oracle_target_label"]
}
```

Definitions:

- `O`: legal observation available to fair baselines. It must not contain audit
  labels, hidden answer maps, future observations, file-name hints, fixture-name
  labels, or candidate-authored ground truth.
- `y`: evaluation target. It is never readable by fair baselines at prediction
  time.
- `y*`: ideal/oracle reference target. It is callable only by the ideal/oracle
  ceiling function and is not a fair baseline input.
- `split`: `train` may be used to fit legal baselines; `eval` is scored.
- `group_id`: user/env/episode grouping for lookup and nearest-neighbor controls.

## Frozen fair-baseline floor family

The Phase B floor is the maximum fair score over:

1. `predict_all`
2. `predict_none`
3. `per_user_lookup`
4. `nearest_neighbor`
5. `count_table`
6. `frequency_marginal`
7. `graph_closure`
8. `obs_only_decoder`

Reference only:

9. `ideal_oracle` — ceiling reference, not a fair baseline.

No member may read `y`, `y*`, hidden labels, answer keys, audit fields, future
observations, or filenames. If an adapter requires a baseline stronger than this
family, Phase B must add it before scoring or VOID the environment; it must not
score first and then repair the floor.

## Ceiling definition

`ceiling_score = ideal_oracle_score`, computed by comparing `ideal_oracle(O,
y*)` predictions with `y` on eval records. A candidate environment has
measurable headroom only when:

```text
ceiling_score - max(fair_baseline_scores) > equivalence_band
```

If the strongest fair baseline is within the band of the ceiling, the verdict is
`SATURATED`.

## Equivalence band

`equivalence_band = 0.05`

Ex-ante rationale: this is a deliberately non-hairline band for heterogeneous
borrowed symbolic environments and macro-F1 / set-F1 style metrics. It is larger
than deterministic arithmetic noise and therefore makes HEADROOM harder, not
easier, to claim. The two controls are expected to show large margins
(`POS_INTERNAL_ESTAR` should separate far above cheap floors; `NEG_5A846D5_SCOUT`
should be closed by graph/lookup floors), so 0.05 should not decide either
control by tuning. Changing this band after any Phase B score is a stop
condition.

## Control expected verdicts

`probe_valid == true` only if both hold:

- `POS_INTERNAL_ESTAR` verdict is exactly `HEADROOM`;
- `NEG_5A846D5_SCOUT` verdict is exactly `SATURATED`.

If either control differs, all candidate environment verdicts are VOID and
Phase B must write `failure_manifest.json` and stop.

## Ablation requirement

Phase B must rerun the battery under both interventions:

1. `drop_graph_closure`: remove `graph_closure` from the fair floor. This tests
   whether SATURATED verdicts are specifically graph-closure driven.
2. `shuffle_O_y`: seeded permutation of eval targets across unchanged
   observations. Fair baselines must not preserve headroom under broken
   observation-target alignment. If they do, suspect leakage or direct target
   encoding.

Phase A only implements these callable interventions and synthetic unit tests;
it does not execute official control/candidate ablations.

## Trace/replay requirement

Phase B must serialize:

- adapter id and source pin;
- record ids, split, group id, `O` hash, `y` hash, `y*` hash;
- each baseline prediction;
- run id, seed, aggregation rule, code path hash;
- ablation mode and replay mode.

Replay must recompute predictions from serialized `O` plus allowed train split
state. Stored-output-only replay is invalid.

## Computed-evidence provenance gate

Every future score must record:

- `producer_function`;
- input artifact paths or adapter source pins;
- `run_id`;
- seed and eval record ids;
- aggregation rule;
- `code_path_hash`;
- baseline invocation list;
- ablation invocation list;
- fresh-process recompute digests.

No literal verdict dictionaries, hand-written scores, or unconditional clean
reports may support a claim.

## Collision record

### Candidate A — minimal implementation

- Evidence it would produce: a small CLI and two adapters.
- Strongest cheap baseline that could match it: obs-only decoder or
  graph-closure if the adapter leaks the target structure.
- Leakage / hard-coding risk: high if expected verdicts are encoded as static
  constants instead of computed by the verdict path.
- Smallest falsifying test: swap synthetic metrics so the verdict changes; a
  static expected-verdict map must fail this test.
- Expected failure mode: fake-green Phase A where `probe_valid` is shape-only.

### Candidate B — strongest baseline / shortcut-first implementation

- Evidence it would produce: robust floor before adapters.
- Strongest cheap baseline that could match it: graph closure, lookup, and
  count-table floors.
- Leakage / hard-coding risk: medium if baseline members are just names and not
  callable.
- Smallest falsifying test: remove graph closure and show verdict changes on a
  graph-solvable synthetic case.
- Expected failure mode: floor becomes the whole task and adapter interface
  remains underspecified.

### Candidate C — mechanism-faithful borrow-first harness

- Evidence it would produce: frozen interface, callable floor, verdict function,
  probe-valid gate, ablations, and fresh-process recompute mode before candidate
  scoring.
- Strongest cheap baseline that could match it: if legal-channel graph/lookup
  baselines saturate, the environment is SATURATED by design.
- Leakage / hard-coding risk: lower if official verdicts come only from computed
  scores and controls are not scored in Phase A.
- Smallest falsifying test: synthetic score bundle flips HEADROOM/SATURATED
  according to the band; `probe_valid` fails on either wrong control.
- Expected failure mode: Phase B finds no borrowed env headroom; preserve as
  negative environment-selection evidence.

Selected approach: Candidate C, with Candidate B's floor family frozen as the
first-class adversary.

## Acceptance gate

Phase A is acceptable only if:

- parent card exists;
- this STEP-A prereg card exists and freezes env set / interface / floor / band;
- isolated script package exists under `scripts/env_headroom_probe/`;
- focused tests pass without writing official result artifacts;
- no candidate borrowed environments are scored;
- `git diff --cached --check` passes before commit;
- staged files are exactly the Phase A docs/scripts/tests allowlist;
- commit is pushed to the current branch as the ex-ante ancestor;
- no tag or remote anchor is created.

## Claim ceiling

Phase A proves only that a local pre-registration card and isolated unscored
script harness exist and were committed before scoring. It does not prove
borrowed-env headroom, probe validity, mechanism validity, learning, agency,
autonomy, subjectivity, consciousness, EGO readiness, production readiness, user
benefit, or mainline effect.

## Stop conditions

Stop if:

- the parent card cannot be banked;
- official control or candidate scores are produced in Phase A;
- a result artifact is written under `artifacts/BORROW-FIRST-.../`;
- the equivalence band is changed after any scoring;
- a fair baseline reads `y`, `y*`, labels, hidden state, future observations, or
  filenames;
- `src/` mechanism code, N2/R4 frozen specs, global config, credentials, or
  runtime files are modified;
- a borrowed env requires pixel/physics state;
- staged paths widen beyond the explicit Phase A allowlist;
- push would require rebase, reset-hard, amend, or conflict repair.

## Rollback plan

Before commit: revert only the new Phase A docs/scripts/tests files. After
commit: `git revert <phase-a-commit>` if Claude Red-audit rejects the
pre-registration. Do not rewrite or delete historical artifacts. Do not touch
N2/R4 frozen specs or `src/`.

## Expected changed files

- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.md`
- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-STEP-A-PREREG-001A.md`
- `scripts/env_headroom_probe/__init__.py`
- `scripts/env_headroom_probe/adapters.py`
- `scripts/env_headroom_probe/battery.py`
- `scripts/env_headroom_probe/contract.py`
- `scripts/env_headroom_probe/runner.py`
- `tests/env_headroom_probe/test_phase_a_contract.py`

## Forbidden changes

- `src/` mechanism code;
- N2/R4 frozen specs;
- pixel/physics env adapters;
- global configuration;
- candidate, attribution, or mechanism code;
- EGO mainline/runtime files;
- credentials or API keys;
- tags or remote anchors.

## Auto-Remote-Anchor decision

Auto-Remote-Anchor: forbidden. The user explicitly authorized a branch push for
the Phase A commit; that branch push must not create tags or remote-anchor
claims.

## What this does not prove

This does not prove `probe_valid`, candidate-env headroom, baseline
non-equivalence, mechanism validity, learning/adaptation evidence, runtime
integration, agency, autonomy, subjectivity, consciousness, EGO readiness,
production readiness, or stable user benefit.
