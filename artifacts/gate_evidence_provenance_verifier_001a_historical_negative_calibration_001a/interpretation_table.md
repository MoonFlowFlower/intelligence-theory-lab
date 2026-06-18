# Historical Negative Calibration Interpretation Table

Current layer: engineering-governance / historical negative calibration for local provenance-shape verifier.

Claim ceiling: diagnostic calibration only. `provenance_wellformed_only`, if observed, is shape-only and non-admissive.

| Bundle | Exit code | Verifier verdict | Expected schema failure | Conservative classification | Non-admission interpretation |
| --- | ---: | --- | --- | --- | --- |
| `artifacts/acolb_001a` | 0 | `invalid_schema_or_parse_failure` | true | `schema_incompatible_diagnostic_only` | diagnostic only; no Gate pass, no admission, no historical evidence rehabilitation |
| `artifacts/acp_bv_distribution_harness_001b_execution_001a` | 0 | `invalid_schema_or_parse_failure` | true | `schema_incompatible_diagnostic_only` | diagnostic only; no Gate pass, no admission, no historical evidence rehabilitation |
| `artifacts/route_c_candidate_harness_001a` | 0 | `invalid_schema_or_parse_failure` | true | `schema_incompatible_diagnostic_only` | diagnostic only; no Gate pass, no admission, no historical evidence rehabilitation |
| `artifacts/candidate_free_route_c_baseline_separation_probe_001a` | 0 | `invalid_literal_or_detached_verdict` | false | `invalid_shape_diagnostic_only` | diagnostic only; no Gate pass, no admission, no historical evidence rehabilitation |

No filename-mapping shim was created. Historical bundles were not copied into verifier fixture format.
