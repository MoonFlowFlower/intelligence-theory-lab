# ITL-K0-H0-CODE-FIRST-PREBANK-PRECONDITION-CLOSURE-001A

Status: executable additive governance-closure task card
Auto-Remote-Anchor: forbidden

## 1. Problem definition and current boundary

- Task id: `ITL-K0-H0-CODE-FIRST-PREBANK-PRECONDITION-CLOSURE-001A`.
- Problem definition: the frozen Phase-C raw-byte precondition for
  `ITL-K0-H0-CODE-FIRST-PREBANK-001A` is internally unsatisfied. Callable
  recomputation from commit `381cc5f28b597325efba9abda055507b58c2133f`
  finds four manifest mismatches among sixteen frozen paths before Phase D or
  the official CLI was invoked.
- Real objective: consume the live code-first prebank authorization and close
  only the H0 admission-science child branch while retaining the independently
  authorized `EGO-K0-FOUNDATION-001A` product/shared-kernel path.
- Required classification:
  - `failure_class=IMPLEMENTATION_DEFECT`
  - `subtype=PORTABLE_BYTE_FREEZE_PRECONDITION_INVALID`
  - `instrument_validity=NOT_TESTED`
  - `mechanism_evidence=NOT_TESTED`
  - `official_run_invoked=false`
- Forbidden classifications: `H0_FAILED`, `INSTRUMENT_INVALID`,
  `MECHANISM_ABSENT`, `THEORY_FALSIFIED`, and
  `CODE_FIRST_PREBANK_FAILED`.
- Current layer: engineering implementation plus mechanism-hypothesis
  instrument governance.
- Current stage: pre-run governance closure after Phase C and before Phase D.
- Mainline target: the ITL repo-local route control plane only.
- Mainline integration status: none; this laboratory is offline and no EGO
  runtime or product mainline is changed.

## 2. Enabled state and real trigger

- Enabled-state requirement before mutation: route
  `READY_TO_IMPLEMENT`, phase `CODE_FIRST_H0_PREBANK_AUTHORIZED`, with
  Foundation true and H0/H1/K0-R/Freeze/Formal false.
- Enabled-state requirement after mutation: route remains
  `READY_TO_IMPLEMENT` solely because Foundation remains available; bounded
  code-first prebank, H0, H1, K0-R, Freeze, Formal, scoring, experiment,
  runtime, and remote authorizations are false.
- Authorized implementation targets after closure: exactly
  `EGO-K0-FOUNDATION-001A`.
- Real-trigger evidence requirement: callable raw-byte SHA-256 recomputation
  must read the Phase-C Git object version of `freeze_manifest.json` and every
  path in its `frozen_file_hashes`, return exactly sixteen checked paths and
  the four preregistered mismatches, while Phase-D outputs remain absent.
- Real trigger observed during live preflight: the callable recomputation
  returned exactly the required four mismatches; the official prebank trigger
  was not invoked and Phase D never began.

## 3. Hypothesis, baseline, and bounded audit

### Hypothesis

An additive route closure can preserve the raw-byte precondition failure as a
bounded packaging/implementation defect, consume only the affected prebank
authorization, and leave Foundation independently available without
reinterpreting the defect as H0 or mechanism evidence.

### Strongest baseline explanation

The four manifest mismatches are harmless newline-representation differences:
five working freeze files differ from their Phase-C Git blobs only by CRLF/LF
representation.

That explanation does not pass the frozen card. The card preregistered raw
commit-object equality and no newline-normalization exception. Newline
equivalence may explain the defect but cannot retroactively satisfy the
acceptance condition.

### Strongest invalidity risk and falsifier

- Strongest reason the task may be invalid: the prior handoff could have
  misreported the Phase-C object bytes or mismatch set.
- Framing falsifier: callable Phase-C object recomputation returns anything
  other than sixteen checked paths and the exact four-path mismatch set. If
  so, stop without banking or mutating route state.
- Evidence still insufficient: this closure cannot adjudicate H0, instrument
  validity, headroom, learning, memory, replay, transfer, mechanism
  contribution, or EGO mainline effect.
- Test classification: route/evidence-governance enforcement only. It tests no
  mechanism and no behavioral resemblance.

### Anti-hardcoding and anti-Zeno audit

- Hard-coding: the validator must recompute Phase-C Git-object hashes and may
  not accept a literal clean verdict or static mismatch report.
- Local optimum: newline equivalence is explanatory only and may not be used
  as a passing rule.
- Zeno trap: no `.gitattributes`, CLI, manifest, freeze, equality-definition,
  or follow-on overlay repair is permitted.
- Evidence leakage: Phase-C objects are addressed by immutable commit and path;
  working-tree normalization cannot substitute for object-byte readback.
- Weak baseline: the harmless-newline explanation is retained explicitly but
  cannot override the frozen raw-byte contract.
- Schema split/second path: the route validator enforces pins, recomputation,
  state, and preservation only; it must not implement H0 semantics.
- Replay weakness: no mechanism replay claim is made; the required readback is
  a fresh SHA-256 recomputation from immutable Git objects.
- Claim inflation: route-validation pass is not instrument or mechanism pass.

## 4. Collision-before-collapse record

### A. Ignore newline differences and run the CLI - rejected

- Evidence produced: a Phase-D report from a working tree treated as
  newline-equivalent.
- Strongest cheap baseline that could match: normalize CRLF/LF before hashing
  and declare the frozen package valid.
- Leakage/hard-coding risk: critical; it bypasses the preregistered raw-byte
  condition and lets the executor redefine its own input boundary.
- Smallest falsifying test: compare the same paths as raw Phase-C Git-object
  bytes; the four mismatches remain.
- Expected failure mode: an official-looking run whose source freeze never met
  its own declared precondition.
- Rejection reason: the existing CLI checks working-byte hashes against the
  manifest but does not establish raw equality with Phase-C Git objects.

### B. Add `.gitattributes`, patch the CLI, regenerate freeze, or redefine equality - rejected

- Evidence produced: a repaired packaging contract or a newly regenerated
  freeze.
- Strongest cheap baseline that could match: post hoc newline normalization.
- Leakage/hard-coding risk: high; a post-freeze rule change rescues the
  instrument after inspecting the failing bytes.
- Smallest falsifying test: read the original Phase-C manifest and object bytes;
  the original raw-byte precondition is still unsatisfied.
- Expected failure mode: another governance overlay without stronger
  discriminative mechanism evidence.
- Rejection reason: this violates the final-replacement and anti-Zeno
  boundary.

### C. Additive closure of the failed child branch while retaining Foundation - selected

- Evidence produced: bounded packaging/precondition failure, honest
  authorization consumption, and route-state convergence.
- Strongest cheap baseline that could match: the mismatch is harmless newline
  representation only.
- Leakage/hard-coding risk: bounded by live Git-object recomputation and
  fail-closed mutation tests; no mechanism classification is inferred.
- Smallest falsifying test: callable recomputation does not yield the exact
  four-path mismatch set among sixteen paths.
- Expected failure mode: drift in pins, counts, paths, ledger/event uniqueness,
  or authorization state blocks closure.
- Selection rationale: this preserves the frozen acceptance rule and negative
  evidence without consuming another repair cycle. Foundation remains
  independently authorized.

## 5. Governance mutation and ablation requirements

The only permitted intervention is the exact route-governance transition. It
must:

1. retain `current_state=READY_TO_IMPLEMENT` because Foundation remains true;
2. set phase to
   `CODE_FIRST_H0_PREBANK_PRECONDITION_FAILED_SCIENCE_BRANCH_CLOSED`;
3. make all authorizations false except `foundation_implementation=true`;
4. set authorized targets exactly to `EGO-K0-FOUNDATION-001A`;
5. set allowed actions exactly to `implement_EGO-K0-FOUNDATION-001A`,
   `operator_route_decision`, and `run_route_state_machine_validation`;
6. preserve the original task-card and Phase-C pins as immutable historical
   provenance, not live authority;
7. add the committed-object pin for this closure card;
8. append exactly one L-026 entry and exactly one
   `h0_code_first_prebank_precondition_failed_science_branch_closed` event;
9. preserve L-020 through L-025 and all prior event bytes; and
10. add the structured precondition-failure record without producing a Phase-D
    evidence artifact.

Governance ablations are fail-closed mutation tests. Tests must reject at
least: `official_run_invoked=true`; wrong mismatch count or path set; wrong
Phase-C pin; missing/duplicate L-026; missing/duplicate closure event; missing
closure-card pin; code-first authorization true; H0 or downstream
authorization true; rerun/correction action present; Phase-D output present;
classification `INSTRUMENT_INVALID`; and classification changed to a mechanism
failure.

## 6. Trace/recompute and computed-evidence provenance gate

- Producer: a callable route-validator path must read the Phase-C
  `freeze_manifest.json` with `git show`, read each frozen path from the same
  commit object, compute SHA-256, and compare it with the recorded value.
- Inputs: Phase-C commit, manifest path, all sixteen frozen object paths,
  closure-card committed object, route/program state, ledger, and event log.
- Required computed result:
  - `checked_path_count=16`
  - `mismatch_count=4`
  - exact mismatches:
    - `artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/baseline_ablation_contract.json`
    - `artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/claim_ceiling.txt`
    - `artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/normative_field_manifest.json`
    - `artifacts/ITL-K0-H0-CODE-FIRST-PREBANK-001A/transformation_catalog.json`
  - `freeze_manifest_self_hash_covered=false`
  - `official_run_invoked=false`
  - `phase_d_artifacts_present=false`
  - `source_test_blob_drift=false`
  - `phase_c_source_test_freeze_modified_by_closure=false`
- Provenance gate: validation output must identify `producer_function`, input
  artifacts, run id, aggregation rule, and code-path hash. A literal/static
  report is insufficient.
- Trace/replay requirement: there is no mechanism trace or replay. The relevant
  replay analogue is fresh object-byte recomputation from immutable Phase-C
  state; comparing only stored hashes without rereading the objects is
  insufficient.

## 7. Acceptance gate and claim ceiling

Acceptance requires all of the following:

1. Phase-C source/test/freeze blobs are unchanged.
2. The official CLI was not run.
3. No Phase-D result or failure artifact exists.
4. Callable recomputation returns the exact four mismatches among sixteen
   paths.
5. Route phase, actions, targets, and authorizations are exact.
6. Foundation remains true; Prebank, H0, H1, K0-R, Freeze, Formal, scoring,
   experiment, runtime, and remote remain false.
7. L-026 and the closure event each occur exactly once while historical bytes
   remain preserved.
8. Mutation tests fail closed.
9. Focused tests and `routectl validate/status/dashboard` pass with zero errors
   and zero warnings.
10. Final worktree/index is clean and no push, tag, or remote anchor occurs.

Acceptance verdict label:
`H0_PREBANK_SCIENCE_BRANCH_CLOSED_PRE_RUN_IMPLEMENTATION_DEFECT`.

Claim ceiling: pre-run implementation-defect closure and route-governance
enforcement only.

## 8. Stop condition and rollback plan

Stop on any drift in repo identity, branch, HEAD, worktree/index,
ahead/behind, source pins, route state, authorization state, Phase-D absence,
callable mismatch counts/paths, or required historical preservation. Also stop
if closure would require a Phase-C byte change, `.gitattributes`, CLI or freeze
repair, equality redefinition, official output, EGO repo modification, remote
action, H0/downstream authorization, another rescue overlay, unexpected user
work, or history rewrite.

Before the Phase-A commit, rollback may remove only this newly added,
uncommitted card. After either commit, preserve the result additively. Reset,
stash, rebase, amend, squash, checkout-based discard, and historical rewrite
are forbidden.

## 9. Expected changed files

### Phase A - add and bank this card only

- `docs/codex/tasks/ITL-K0-H0-CODE-FIRST-PREBANK-PRECONDITION-CLOSURE-001A.md`

Commit exactly: `docs: bank code-first H0 precondition closure`.

### Phase B - exact route transition only

- `docs/research/FSP-STAGE-LEDGER.md`
- `src/route_state_machine_001a/state_machine.py`
- `src/route_state_machine_001a/validator.py`
- `tests/route_state_machine_001a/test_validator.py`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/events.jsonl`
- `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`

Commit exactly: `governance: close code-first H0 prebank science branch`.

## 10. Forbidden changes and actions

- Any Phase-C source, test, freeze, or catalog byte.
- `.gitattributes`, the prebank CLI, freeze regeneration, or equality changes.
- Any Phase-D output, including `result.json` or `failure_manifest.json`.
- H0 semantics, resolver/oracle calls, atomic-spec scoring, or mechanism
  interpretation inside route validation.
- EGO repo/runtime, H1, K0-R, immutable freeze, formal evidence, deployment,
  external services, or external writes.
- Rescue, correction, rerun, new overlay, push, tag, or remote anchor.

## 11. Prior negative evidence references

- `docs/research/FSP-STAGE-LEDGER.md#L-025`: the prior 002A admission
  semantics failed review because always-false specialness, order sensitivity,
  synthetic self-certification, surviving normative mutations, and detached
  path/claim/self-hash checks remained. That banked negative review authorized
  the final code-first prebank but did not authorize H0.
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/closure.json`:
  the earlier same-agent kernel route closed at baseline equivalence. This
  closure does not reopen or reinterpret it.
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/closure.json`: the
  historical instrument-invalid route remains a separate boundary and is not
  a classification precedent for this pre-run packaging defect.

## 12. What this does not prove

This task does not prove or test H0, instrument validity, mechanism presence or
absence, theory truth or falsity, headroom, learning, adaptation, memory,
replay, transfer, agency, autonomy, subjectivity, consciousness, EGO readiness,
companion readiness, production readiness, user benefit, or mainline effect.
It does not validate the code-first prebank and does not authorize its run,
repair, correction, or replacement.
