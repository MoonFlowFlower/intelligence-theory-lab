# BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A — Phase B-ii-R1 adapter fairness repair

Status: bounded implementation card. Operator authorized Phase B-ii-R1 on 2026-07-08.
No scoring. No candidate verdicts. Stop for Claude re-audit.

## task id
`BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-PHASE-BII-R1-ADAPTER-FAIRNESS-REPAIR`

## problem definition
The Phase B-ii borrowed adapters can be unfair if `y` is sourced from private env
state that is absent from legal observation `O`, or if a sequence/history env is
trivially decoded from `O` but the trivial legal decoder is not represented as a
floor/void guard. Repair the adapter admission boundary before any borrowed-env
scoring.

## current layer
Engineering implementation layer with mechanism-hypothesis support only.

## mainline target
None. Isolated `scripts/env_headroom_probe/` adapter admission hygiene and
adapter artifacts only.

## enabled-state requirement
No scoring path is enabled for borrowed adapters. `BORROWED_ADAPTERS` remains
separate from official scored `ADAPTERS`.

## real-trigger evidence requirement
Adapter-level tests and manifest readback only: each surviving borrowed adapter
must expose an `oracle_from_O` admission report computed from legal `O` only.
MiniGrid reset-only adapters must be dropped unless redesigned to make `y`
O-determined. bsuite sequence/history adapters must be marked trivially legally
decodable / saturated by an O-only decoder, not admissible as headroom.

## bounded audit / collision record

### candidate A — minimal implementation
Add `oracle_from_O` admission helpers, drop MiniGrid reset-only adapters, mark
bsuite adapters with `VOID_TRIVIALLY_DECODABLE` guard, and update tests/artifacts.
- Evidence: adapter admission reports and falsifier tests.
- Strongest cheap baseline: read the target directly from legal observation
  history.
- Leakage/hard-coding risk: using private `_context`, `_query`, `_need_umbrella`
  in the decoder. Mitigation: decoder receives only `O`.
- Smallest falsifying test: random target independent of `O` must be invalid.
- Expected failure mode: a future adapter could set uninformative keys and still
  vary; re-audit must inspect legal key semantics.

### candidate B — keep MiniGrid by full episode-history redesign
Run legal episode rollouts until target-relevant cues are observed, expose full
history, and add O-only decoders.
- Evidence: more adapters survive.
- Strongest cheap baseline: planner/history parser may solve from legal history.
- Leakage/hard-coding risk: action policy/trajectory could import target-specific
  behavior or private env fields.
- Smallest falsifying test: target not recoverable from serialized history.
- Expected failure mode: accidental scoring/selection pressure before Red audit.

### candidate C — mechanism-faithful future redesign
Create a new symbolic task interface where target, affordances, and legal
observations are designed together, then rerun Phase B-ii under a new card.
- Evidence: cleaner later adapter boundary.
- Strongest cheap baseline: explicit symbolic parser.
- Leakage/hard-coding risk: lower, but broader scope.
- Smallest falsifying test: parser baseline saturates.
- Expected failure mode: route expansion without increasing current audit value.

Selected approach: candidate A. It is the minimal reversible repair that blocks
unfair private-state targets and preserves the no-scoring boundary.

## hypothesis
MiniGrid reset-only adapters are not O-determined and must be dropped. bsuite
memory/umbrella adapters are O-determined from legal observation history and
therefore require a `VOID_TRIVIALLY_DECODABLE` / saturated-by-legal-decoder guard
before any future scoring.

## strongest baseline
An O-only legal decoder that reads the target from serialized observation
history or an explicit legal observation field.

## ablation requirement
No scoring ablations in this phase. Falsifier tests substitute for scoring:
random target independent of `O` must fail admission; trivial target encoded in
`O` must trigger the trivial-decoder guard.

## trace/replay requirement
No score trace. Adapter manifest must record producer function, record digests,
admission result, dropped adapters, and no-scoring flags.

## computed-evidence provenance gate
Admission reports must be produced by callable functions over generated adapter
records, not by static verdict dictionaries. The callable decoder must receive
only `record.O`.

## acceptance gate
- No control/candidate scoring command is run.
- No borrowed candidate verdict or `probe_valid` is computed.
- MiniGrid reset-only adapters are dropped or redesigned to be O-determined.
- bsuite adapters include O-only admission reports and `VOID_TRIVIALLY_DECODABLE`
  guard / saturated-by-legal-decoder future-floor effect.
- Falsifier tests pass.
- Scoped commit descends from `470f4490`.

## claim ceiling
Borrowed-adapter fairness hygiene only. No headroom, no borrowed-env verdict,
no probe-validity result, no mechanism evidence, no learning, no mainline effect.

## stop condition
Stop if any test requires scoring, any adapter uses private env state inside
`oracle_from_O`, any band/control/expected verdict threshold changes, or any
candidate verdict is emitted.

## rollback plan
Revert this card, adapter/test changes, and updated B-ii manifest artifacts.
No global config, frozen control contract, N2/R4 specs, or mechanism code are
touched.

## expected changed files
- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-PHASE-BII-R1-ADAPTER-FAIRNESS-REPAIR.md`
- `scripts/env_headroom_probe/adapters.py`
- `tests/env_headroom_probe/test_phase_bii_borrowed_adapters.py`
- `tests/env_headroom_probe/test_phase_bii_r1_adapter_fairness.py`
- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/borrowed_adapter_manifest.json`
- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/failure_manifest.json`

## forbidden changes
Scoring; candidate verdicts; probe-valid computation; band/control/expected
verdict edits; pixel/physics adapters; `src/` mechanism code; N2/R4 frozen
specs; remote anchor; credentials.

## Auto-Remote-Anchor decision
Forbidden.
