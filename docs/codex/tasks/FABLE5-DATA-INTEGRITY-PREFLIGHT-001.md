# FABLE5-DATA-INTEGRITY-PREFLIGHT-001

## Title

Bounded data-integrity preflight after Claude Fable 5 safeguard concerns.

## Task ID

```text
task_id = FABLE5-DATA-INTEGRITY-PREFLIGHT-001
card_type = diagnostic preflight task card
research_layer = engineering implementation layer / evidence-infrastructure preflight
execution_authorized = diagnostic_audit_only
experiment_execution_authorized = false
artifact_rewrite_authorized = false
```

## Problem Definition

Recent public reporting about Claude Fable 5 indicates that some frontier AI
development requests may be refused, routed to a fallback model, or otherwise
served under safety classifiers. That risk can weaken trust in AI-assisted
analysis, generated code, and natural-language summaries.

The correct question for this repository is not:

```text
Did Claude Fable 5 make our theory true or false?
Did Claude Fable 5 remotely tamper with local artifacts?
Should we rerun all experiments because the article is worrying?
```

The correct bounded question is:

```text
Do current machine-readable evidence artifacts, frozen manifests, and git
state show any local integrity break, undocumented mutation, malformed data,
or undeclared model-assisted evidence path that would lower the claim ceiling
of existing lab results?
```

## Current Stage

This is a preflight / diagnostic task. It does not authorize a formal Gate
run, same-agent bridge run, experiment rerun, data regeneration, or any
upgrade to existing claims.

Current local risk signals that justify this preflight:

- the repository has many uncommitted deleted/untracked paths in `git status`
- at least one canonical record already states that earlier evidence lacked
  pre-run VCS freeze and can only be frozen from the later canonical commit
- public Fable 5 reporting raises a model-provenance risk for AI-generated
  analysis, but does not by itself prove local artifact tampering

## Prior Negative Evidence

This task inherits the lab's negative-evidence discipline:

- `docs/NEGATIVE_EVIDENCE_LEDGER.md` states that failures are append-only,
  failure artifacts must remain linked, and successor theories must cite
  relevant failed claims.
- `docs/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_CANONICAL_RECORD.md` records
  a binding VCS freeze limitation: original 001 / 001B / 001C code and
  artifacts were untracked in git at audit time, so pre-001 VCS freeze cannot
  be proved retroactively.
- `docs/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_CANONICAL_RECORD.md` protects
  canonical evidence paths from rewriting, regeneration, upward
  reinterpretation, or cleanup; corrections must go to errata.
- `docs/codex/tasks/R-G-GATE0-TO-GATE1-BRIDGE-001A.md` inherits prior Gate 1
  graph/cache collapse and latent residue collapse, so integrity review must
  not be reframed as new Gate 1 evidence.

## Hypothesis

H1:
The current repository evidence state can be classified without mutating prior
artifacts by checking frozen manifests, parseability, git/index state,
protected-path hash consistency, and model-provenance markers.

H0:
The apparent concern cannot be resolved from local evidence because protected
hashes mismatch, machine-readable artifacts fail to parse, canonical records
and artifacts disagree, dirty worktree state affects protected evidence, or
the audit would require rewriting/regenerating old artifacts.

## Baseline

Required comparison baselines:

- frozen SHA-256 manifest baseline where a manifest exists
- tracked git object baseline for tracked files
- filesystem inventory baseline for untracked artifacts
- canonical-record baseline for declared verdicts and claim ceilings
- null external-risk baseline: public Fable 5 reporting alone predicts no
  local file mutation unless local artifacts or provenance records show it
- natural-language-only baseline: prose summaries are not evidence unless
  backed by machine-readable artifacts

## Ablation

Run the diagnostic classification under these ablations:

- exclude natural-language summaries and inspect only machine-readable
  artifacts
- exclude untracked non-protected paths and classify only protected canonical
  paths
- compare protected-path hash checks with full-repository dirty-state checks
- compare model-provenance scan results with and without docs-only files
- treat every LLM/Claude/Fable mention as non-evidence unless it appears on a
  machine evidence path

If verdict changes only because docs-only prose is included, the result must
be classified as documentation-provenance risk, not artifact tampering.

## Trace / Replay Requirement

The audit must write only to:

```text
artifacts/fable5_data_integrity_preflight_001/
```

Required audit artifacts:

- `result.json`
- `command_ledger.jsonl`
- `git_status_snapshot.txt`
- `file_inventory.json`
- `protected_manifest_verification.json`
- `machine_artifact_parse_report.json`
- `canonical_record_consistency.json`
- `model_provenance_scan.json`
- `dirty_worktree_risk_report.md`
- `failure_manifest.json` if any stop condition triggers
- `claim_ceiling.txt`

Every inspected file record must include, when practical:

- path
- file size
- modified time
- SHA-256
- tracked/untracked/deleted status
- parse status for JSON / JSONL / CSV / YAML
- whether the path is protected by a canonical record
- whether the path is machine evidence, docs-only evidence, or code/test
  support

No protected artifact may be rewritten to make this audit pass.

## Acceptance Gate

This preflight can pass only if:

- all protected files covered by an existing SHA-256 manifest match their
  recorded hashes
- protected canonical evidence paths are not rewritten
- machine-readable artifacts needed for current claim ceilings parse
  successfully or are explicitly listed as failures
- dirty worktree changes are classified by path and do not silently alter a
  protected evidence verdict
- every current claim ceiling remains equal to or weaker than the canonical
  record
- model-provenance scan finds no undeclared Claude/Fable/LLM dependency on
  machine evidence paths, or records it as a caveat without upgrading claims
- command ledger is complete enough to replay the audit classification

Pass verdict name:

```text
fable5_data_integrity_preflight_no_local_integrity_break_detected
```

Fail / blocked verdict names:

```text
fable5_data_integrity_preflight_protected_hash_mismatch
fable5_data_integrity_preflight_machine_artifact_parse_failure
fable5_data_integrity_preflight_dirty_state_blocks_classification
fable5_data_integrity_preflight_model_provenance_unresolved
fable5_data_integrity_preflight_scope_stop
```

## Stop Conditions

Stop and write `failure_manifest.json` if any of the following occurs:

- a protected frozen artifact hash mismatches its manifest
- a protected artifact is missing
- an audit step would require rewriting, regenerating, or cleaning prior
  artifacts
- a current verdict relies only on prose without machine-readable backing
- dirty worktree state prevents distinguishing local edits from evidence
  mutation
- any check requires external API keys, LLM calls, Claude/Fable access, EGO
  runtime integration, UI behavior, deployment, or global schema migration
- the task starts becoming a formal Gate run, bridge run, or new mechanism
  experiment

## Rollback Plan

Rollback is limited to deleting only the newly created audit output directory
for this task and, if abandoned before execution, this task card.

Do not modify, delete, regenerate, or clean existing evidence artifacts.
Corrections to prior evidence must be written as future errata, not by editing
the original record.

## Claim Ceiling

Maximum allowed claim:

```text
bounded local data-integrity preflight result for current repository evidence
state after Fable 5 safeguard concerns
```

Forbidden claims:

- no historical tampering ever occurred
- Fable 5 did or did not influence any past assistant reasoning unless
  provenance evidence shows it
- existing mechanism claims are stronger than their canonical records
- Gate 1 replay/consolidation evidence
- same-agent bridge evidence
- EGO mainline readiness
- companion readiness
- agency, consciousness, subjective experience, real emotion, self-awareness,
  functional-subject, electronic-life, or AGI evidence

## What This Cannot Prove

This task cannot prove that no pre-freeze historical mutation occurred. It
cannot prove that all past assistant reasoning was served by the intended
model. It cannot repair missing pre-run VCS freeze evidence. It cannot turn
clean hashes or parseable files into stronger mechanism evidence. It only
classifies the current local evidence state under a bounded audit contract.
