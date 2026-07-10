# K0-DUAL-TRACK-READY-TRANSITION-001A

Status: EXECUTABLE CONTROL-PLANE TRANSITION / NO CHILD IMPLEMENTATION

Auto-Remote-Anchor: forbidden

## Task identity and problem definition

- Task id: `K0-DUAL-TRACK-READY-TRANSITION-001A`
- Parent route: `K0-DUAL-TRACK-SUPERSESSION-001A`
- Exact transition: `REGISTERED -> READY_TO_IMPLEMENT`
- Current required phase: `CHILD_CARDS_BANKED_READY_TRANSITION_REQUIRED`
- Resulting phase: `FIRST_PAIR_READY_TO_IMPLEMENT`
- Problem: the six ordered cards are banked, but the canonical route still
  authorizes only card banking. Open exactly the first parallel pair without
  opening K0-R, H1, Freeze, Formal, scoring, or any runtime/mainline path.

## Current layer, mainline, enabled state, and real trigger

- Layer: engineering implementation / route-governance evidence hygiene.
- Mainline target: none; no EGO runtime, UI, scheduler, LLM, deployment, or
  product path is changed.
- Enabled-state requirement: only `EGO-K0-FOUNDATION-001A` and
  `ITL-K0-H0-H1-INSTRUMENT-001A:H0` become implementation-authorized.
- Required false children: `EGO-K0-REFERENCE-KERNEL-001A`,
  `ITL-K0-H0-H1-INSTRUMENT-001A:H1`, `K0-IMMUTABLE-FREEZE-001A`, and
  `ITL-K0-FORMAL-EVIDENCE-001A`.
- Real-trigger evidence: callable `routectl validate/status/dashboard` over the
  serialized route packet plus independent `git cat-file`/`git rev-parse`
  readback of all six banked card objects.
- This task performs no Foundation, H0, H1, K0-R, Freeze, or Formal work.

## Frozen source pins and object readback

| Card | Repo commit | Card path | Git blob |
|---|---|---|---|
| `K0-DUAL-TRACK-SUPERSESSION-001A` | `56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92` | `docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md` | `11b0e09025d1064a1eb790f42d79f1db3c690f6d` |
| `EGO-K0-FOUNDATION-001A` | `13bd9268993f74a41b4cc219855761681ab12b66` | `docs/codex/tasks/ego-k0-foundation-001a/STAGE_CARD.md` | `f100d78e48b8d9b21327ed86a5fb35305d11d534` |
| `EGO-K0-REFERENCE-KERNEL-001A` | `0f043254710b47700f2088213232aba777bd3f46` | `docs/codex/tasks/ego-k0-reference-kernel-001a/STAGE_CARD.md` | `55f7ac62bf8aad61b3140c213812d7fb9a166acb` |
| `ITL-K0-H0-H1-INSTRUMENT-001A` | `56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92` | `docs/codex/tasks/ITL-K0-H0-H1-INSTRUMENT-001A.md` | `a642c5734d57af450104b115181a2f7dc18bb646` |
| `K0-IMMUTABLE-FREEZE-001A` | `56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92` | `docs/codex/tasks/K0-IMMUTABLE-FREEZE-001A.md` | `6f01764c2194061fa60c1b84ef6702c7a533cbea` |
| `ITL-K0-FORMAL-EVIDENCE-001A` | `56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92` | `docs/codex/tasks/ITL-K0-FORMAL-EVIDENCE-001A.md` | `c0ce00ff953b389282ba16435ddc884564e2f27e` |

The transition is invalid if any commit, path, blob, task identity, clean
worktree readback, current state, or current phase differs.

## Hypothesis and strongest baseline

Hypothesis: exact source-object pins plus an exact allowlist can open the first
pair while keeping every downstream child and claim path fail-closed.

Strongest baseline/shortcut: hand-edit `current_state` and a prose status file.
That can look complete while silently authorizing a generic implementation
path. Therefore the callable validator must enforce the state, phase, six card
objects, exact two-child allowlist, exact false-child map, ledger event, and
absence of a closure packet.

Strongest invalidity risk: treating generic `READY_TO_IMPLEMENT` as permission
for every child. Falsifier: any extra child or generic experiment/formal/runtime
authorization survives validation. Evidence still insufficient: a passing
control-plane validator does not show that either child is implemented or that
any mechanism proposition is true.

## Collision record

### Candidate 1 - state string only

- Evidence: `READY_TO_IMPLEMENT` appears in JSON.
- Cheap match: manual text edit.
- Leakage/hard-coding risk: high; no authorization boundary.
- Smallest falsifier: set K0-R true and observe no validator failure.
- Expected failure: false broad readiness.

### Candidate 2 - one generic implementation flag

- Evidence: route can report that implementation is enabled.
- Cheap match: every child inherits the same flag.
- Leakage/hard-coding risk: high; phase boundaries collapse.
- Smallest falsifier: Formal becomes reachable without Freeze.
- Expected failure: DAG bypass.

### Candidate 3 - exact child allowlist plus negative controls (selected)

- Evidence: callable validation of the two true and four false child states,
  exact object pins, current phase, and append-only transition record.
- Cheap match: a manually consistent report; blocked because validation is
  recomputed from serialized artifacts and negative-control tests mutate pins
  and authorizations.
- Leakage/hard-coding risk: stale pins or an unvalidated second field.
- Smallest falsifier: change one blob/pin or one false child to true.
- Expected failure: fail-closed validation with a specific error code.

## Frozen transition contract

The route packet must contain:

```text
current_state = READY_TO_IMPLEMENT
phase = FIRST_PAIR_READY_TO_IMPLEMENT
implementation_authorized = true
authorized_implementation_targets =
  - EGO-K0-FOUNDATION-001A
  - ITL-K0-H0-H1-INSTRUMENT-001A:H0
```

The child authorization map must contain exactly those two `true` values and
the four downstream `false` values named above. Generic experiment execution,
scoring, formal run, freeze, runtime, mainline, theory/mechanism claims, remote
anchor, agency, autonomy, subjectivity, and consciousness remain false.

Allowed next actions are exactly:

- `implement_EGO-K0-FOUNDATION-001A`
- `bank_ITL-K0-H0-H1-INSTRUMENT-001A_H0`
- `run_route_state_machine_validation`

## Ablation, trace/replay, and computed-evidence provenance

- Ablation/negative controls: tests must change each required-false child to
  true, remove one authorized child, alter a pinned commit/blob, or use the
  wrong phase; each intervention must fail callable validation.
- Trace/replay: append one `first_pair_ready_to_implement` event and append one
  ledger entry. Revalidation from serialized JSON/event/ledger state is the
  governance replay. No mechanism replay is claimed or run.
- Computed-evidence provenance gate: `validation_report.json` must be generated
  by `build_validation_report` and record input artifacts, run id, aggregation
  rule, code-path hash, zero errors, zero warnings, and `pass`.

## Acceptance gate

1. Both ITL and Ego worktrees were clean before transition work.
2. All six cards read from the named Git object stores at the frozen commits and
   match their paths/blobs/task identities.
3. Current route is `REGISTERED` with phase
   `CHILD_CARDS_BANKED_READY_TRANSITION_REQUIRED` before mutation.
4. Callable route validation passes before and after the change.
5. Resulting state/phase and the exact two-child allowlist match this card.
6. K0-R, H1, Freeze, Formal, experiment, scoring, runtime/mainline, claim, and
   publication authorizations remain false.
7. No Foundation, H0, H1, K0-R, Freeze, or Formal implementation/artifact path
   is created or modified.
8. Route-state tests, `routectl status`, and `routectl dashboard` pass.
9. Exact-path staging and `git diff --cached --check` pass; local commit only.

## Claim ceiling

Local control-plane authorization for the first two implementation cards only.
No implementation, integration, instrument validity, headroom, formal evidence,
learning, memory/replay/transfer contribution, mechanism validity, theory
pressure, agency, autonomy, subjectivity, consciousness, EGO readiness,
companion readiness, product benefit, or mainline effect.

## Stop condition

Stop without repair-by-reframing if a pin/blob/task identity, clean-worktree
precondition, callable pre-transition validator, current state/phase, append-only
ledger, or exact allowlist cannot be verified; if any downstream authorization
would become true; if a child implementation path must be touched; or if push,
tag, or remote anchor is required.

## Rollback plan

Before commit, revert only the exact files below to their pre-task object-store
bytes. After commit, preserve the event and ledger append; corrections require
an additive bounded transition card/event. Never rewrite a banked card or prior
negative evidence.

## Expected changed files

- `docs/codex/tasks/K0-DUAL-TRACK-READY-TRANSITION-001A.md`
- `docs/research/FSP-STAGE-LEDGER.md` (append-only `L-021`)
- `src/route_state_machine_001a/state_machine.py`
- `src/route_state_machine_001a/validator.py`
- `tests/route_state_machine_001a/test_validator.py`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/events.jsonl` (append-only)
- `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json` (callable output)

## Forbidden changes

Every other path, especially Foundation/H0/K0-R/H1/Freeze/Formal implementation
or evidence paths, EGO files, old route packets, closure packets, metrics,
thresholds, baselines, runtime/UI/LLM/deployment paths, push, tag, and remote
publication.

## Local commit authorization

One exact-scope local commit is authorized after all gates pass. Push, tag, and
remote anchor are forbidden.

## What this does not prove

This transition proves only that the local control plane exposes the first two
bounded work cards under exact pins. It does not prove that either work item has
started, passed, integrated, or produced mechanism evidence.
