# PROCESS-INTERVENTION-PREFLIGHT-001A Stage0 Freeze Anchor Contract

## Required Stage0 Freeze

Before any future executable verifier run, freeze:

```text
task_card_hash
environment_family_definition
train_test_split
intervention_set
control_implementations_or_closed_form_procedures
control_access_contracts
resource_budgets
trace_commitment_protocol
match_metrics
separation_statistics
behavior_probe_protocol
oracle_leakage_probes
acceptance_gate
claim_ceiling
stop_conditions
```

If external anchoring is used, Stage0 must record:

```text
external_anchor
anchor_time
first_verifier_run_time
freeze_before_anchor = true
anchor_before_verifier = true
freeze_commit_or_tag
sha256_manifest
```

## Non-Self-Attestation Rule

Verdict-string tests are not acceptance evidence.

Executable acceptance must be computed by independent verifier code or a
closed-form audit. The candidate system must not self-attest acceptance.
Executable-layer tests must assert structure, frozen inputs, boundary flags,
replayability, and allowed failure verdicts. Verdict-string tests are not
acceptance evidence.

Failure verdicts:

```text
process_intervention_preflight_001a_amendment_001_failed_stage0_freeze_missing
process_intervention_preflight_001a_amendment_001_failed_self_attestation
process_intervention_preflight_001a_amendment_001_failed_verdict_string_test
```
