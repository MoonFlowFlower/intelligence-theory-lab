# SAME_AGENT_BRIDGE_EVIDENCE_SCHEMA_001

Task: SAME-AGENT-BRIDGE-GOVERNANCE-001-FIXA
Mode: evidence report schema only. No implementation.

Every future same-agent bridge execution must write machine-readable evidence
under `artifacts/same_agent_bridge_001a/`. Natural-language summaries are not
evidence unless backed by these artifacts.

## Verdict Enum

The top-level verdict must be one of:

```text
pass
fail
blocked
inconclusive
```

Specific causes such as `schema_fragmentation`, `graph_cache_equivalent`, or
`threshold_tuning_dependency` must appear in `failure_taxonomy_labels`, not as
the top-level verdict.

## Required Frozen Decision Package

Before first execution, the evidence package must include a frozen decision
record with:

- metrics
- number of training seeds
- number of held-out seeds
- held-out split rule
- baseline equivalence margin
- minimum same-agent held-out delta
- minimum ablation sensitivity margin
- definition of "matches or beats"
- margin-freeze ordering requirement
- baseline competence checks
- control competence checks
- unresolved placeholder audit

If any field is unresolved, implementation is blocked.

## Required Evidence Report Fields

`result.json` or an equivalent machine-readable evidence report must include:

```json
{
  "verdict": "pass | fail | blocked | inconclusive",
  "claim_ceiling": "bounded same-agent Gate0-to-Gate1 bridge evidence under the specified trace/replay contract",
  "environment_seeds": [],
  "held_out_seeds": [],
  "training_seed_count": "implementation_blocking_unresolved_until_frozen",
  "held_out_seed_count": "implementation_blocking_unresolved_until_frozen",
  "held_out_split_rule": "implementation_blocking_unresolved_until_frozen",
  "metrics": "implementation_blocking_unresolved_until_frozen",
  "baseline_equivalence_margin": "implementation_blocking_unresolved_until_frozen",
  "minimum_same_agent_held_out_delta": "implementation_blocking_unresolved_until_frozen",
  "minimum_ablation_sensitivity_margin": "implementation_blocking_unresolved_until_frozen",
  "matches_or_beats_definition": "implementation_blocking_unresolved_until_frozen",
  "baseline_results": {},
  "graph_cache_family_results": {},
  "baseline_competence_results": {},
  "control_competence_results": {},
  "ablation_results": {},
  "same_agent_delta": {},
  "same_agent_continuity_report": {},
  "bridge_dependency_result": {},
  "trace_causality_result": {},
  "leak_scan_result": {},
  "ru