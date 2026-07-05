# S3d ideal kernel analysis 001A

Task: FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A.

Finding: the S3d cert-cell per-cell ideal path already instantiates
`src.fsp_pum_env.factored_filter.FactoredExactFilter` from the committed
runner's `_score_ideal_cell` path. The filter stores a full joint float64
log-weight vector and its `scatter_kernel_certificate()` reports in-place
log-weight updates plus query-time logsumexp normalization.

Resume decision: no faster flag or alternate ideal path was enabled in this
resume. Therefore no byte-identical regression proof was required here. The
required camouflage_off ideal exact value/regression proof would be mandatory
only if this card enabled a different path.

Claim ceiling: code-path analysis only; no new equivalence certificate, no
metric result, no speedup claim, and no science-rule change.

Producer: artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py::_write_ideal_kernel_analysis_note
Code path hash at write time: 39a1afcb9d025e1a5820aab1b21da4aa6125710b5f8a73f77c727cc21e0927b4
