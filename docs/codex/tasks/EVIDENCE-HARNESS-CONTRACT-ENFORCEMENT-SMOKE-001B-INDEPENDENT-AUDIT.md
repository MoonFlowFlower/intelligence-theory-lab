# EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001B-INDEPENDENT-AUDIT

## Task ID

`EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001B-INDEPENDENT-AUDIT`

## Mode

Independent audit of the enforcement smoke only.

This is not a Gate repair task.
This is not a Gate execution task.
This is not a mechanism validation task.
This is not Gate4 001C continuation.
This is not Gate5/admission/runtime/bridge work.
This must not modify the existing 001A enforcer implementation.

## Problem Definition

The 001A enforcement smoke showed that the canonical contract can reject known
false-pass surfaces, including Gate4 001B, but it may still be brittle. This
audit tests whether the 001A enforcer is merely detecting known strings/shapes
or whether it can reject or block adversarial false-pass variants without
relying on static task-id denylist logic.

## Current Stage

Engineering implementation plus bounded evidence-harness audit. The output is
not Gate validity evidence and not mechanism validity evidence.

## Hypothesis

If the 001A enforcer has bounded enforcement value, adversarial false-pass
fixtures with renamed fields, indirect pass claims, hidden readiness claims,
result.json leakage, and baseline/ablation/replay shortcuts should not classify
as `admissible_downstream_evidence`.

This task does not prove the enforcer complete or generally safe. It only
audits whether the current smoke has obvious bypasses.

## Baseline

Baseline failure mode: the enforcer rejects only the known Gate4 001B strings,
hard-coded fixture ids, static task ids, static commit hashes, or exact field
names, while renamed or semantic false-pass evidence is admitted downstream.

## Ablation

No mechanism ablation is run. The audit uses adversarial fixture variants that
remove exact 001A field names while preserving false-pass risk semantics.

## Trace / Replay Requirement

No mechanism replay is run. The audit invokes the existing 001A callable
`evaluate_bundle` for each fixture and records actual class, rule ids, detected
categories, static-denylist involvement, task-id dependency, and incorrect
admission status.

## Scope

Allowed:

- inspect the existing 001A enforcer source, tests, docs, and artifacts
- create independent audit source under
  `src/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`
- create independent audit tests under
  `tests/test_evidence_harness_contract_enforcement_smoke_001b_independent_audit.py`
- create adversarial fixtures under
  `artifacts/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`
- invoke the existing 001A enforcer as black-box callable code
- produce audit artifacts and result files

Forbidden:

- do not modify the 001A enforcer source
- do not modify the 001A enforcer tests
- do not modify old artifacts
- do not rewrite historical verdicts
- do not repair Gate4 001B
- do not repair Gate0/Gate1/Gate2/Gate3/Gate4
- do not continue, restore, push, anchor, or use provisional Gate4 001C
- do not enter Gate5, admission, runtime, or bridge
- do not claim Gate validity, mechanism validity, theory validity, architecture
  correctness, or EGO-mainline readiness

## Required Output Paths

- `docs/codex/tasks/EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001B-INDEPENDENT-AUDIT.md`
- `src/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`
- `tests/test_evidence_harness_contract_enforcement_smoke_001b_independent_audit.py`
- `artifacts/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`

## Required Artifacts

Under `artifacts/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`:

- `audited_enforcer_inventory.json`
- `adversarial_fixture_manifest.json`
- `black_box_invocation_report.json`
- `bypass_attempt_report.json`
- `static_denylist_audit_report.json`
- `source_pattern_audit_report.json`
- `test_quality_audit_report.json`
- `contract_coverage_gap_report.json`
- `adversarial_result_matrix.json`
- `result.json`
- `claim_ceiling.txt`
- `execution_manifest.json`
- `json_parse_verification.json`

## Acceptance Gate

This task passes only if:

- starting HEAD equals `5b4cdbeedb380aafa8da9ead827e1b40b04d8153`
- worktree is clean before generation
- existing 001A enforcer source/tests/artifacts are not modified
- old Gate artifacts/tests/verdicts are not modified
- provisional Gate4 001C is not used
- independent audit invokes the existing 001A enforcer as callable code
- all required adversarial fixtures are created
- each adversarial fixture is actually evaluated
- no adversarial false-pass fixture is classified as
  `admissible_downstream_evidence`
- governance negative control is classified differently from false-pass fixtures
- static-denylist-only rejection is checked
- 001A test quality is audited
- all JSON artifacts parse
- downstream authorization fields remain false
- no Gate validity or mechanism validity is claimed

## Stop Condition

Stop and report blocked if the start state mismatches, the worktree is dirty
before generation, the existing 001A enforcer cannot be invoked as callable code,
the task requires modifying 001A source/tests/artifacts, the task requires using
provisional Gate4 001C, any downstream authorization would become true, or
Codex cannot produce adversarial fixtures without hard-coding the expected audit
result.

## Rollback Plan

Remove only:

- `docs/codex/tasks/EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001B-INDEPENDENT-AUDIT.md`
- `src/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`
- `tests/test_evidence_harness_contract_enforcement_smoke_001b_independent_audit.py`
- `artifacts/evidence_harness_contract_enforcement_smoke_001b_independent_audit/`

Historical artifacts, tests, verdicts, and the 001A enforcer remain unchanged.

## Downstream Authorization

- `downstream_entry_authorized`: false
- `gate4_001c_authorized`: false
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false

## Claim Ceiling

`bounded independent audit of evidence-harness enforcement smoke only`

## What This Cannot Prove

This independent audit does not prove Gate validity, mechanism validity, theory
validity, architecture correctness, Gate4 001C authorization, Gate5
authorization, admission authorization, runtime authorization, bridge
authorization, EGO-mainline readiness, agency, selfhood, consciousness, real
emotion, relationship learning, or stable autonomy.
