# Corrected operator-only bank ops for FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A STOP.
# Correction vs s3d_operator_bank_ops_proposal_line30.ps1 (kept as emitted record, also banked):
#   1. HEAD pin updated 5416206 -> eadcba8 (operator banked the 20260705A handoff after Codex's
#      dulwich readback; the original pin would throw).
#   2. Adds this corrected script + the original proposal to the allowlist.
#   3. Stale .git\index.lock guard (standing lesson).
# Auditor: Claude, 2026-07-05. Pattern: HEAD-pinned, git reset first, allowlist-scoped
# add/commit, required-core-subset, zero deletion, no unexpected staged paths, no push.
$ErrorActionPreference = 'Stop'
$ExpectedHead = 'eadcba858546690dff5c5c75953805fd32e68e8d'
$CommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d resume STOP resume_reuse_gate_failed (spot-check mismatch; GRU nondeterminism evidence)'
$Allowlist = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/baseline_comparison_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/replay_report_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_certificate_report_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_ideal_kernel_analysis_001a.md'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_null_env_report_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_operator_bank_ops_proposal_line30.ps1'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_stop_bank_ops_corrected_001a.ps1'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__cert__camouflage_off.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__cert__constant_none.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__cert__constant_saturated.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__cert__flat_theta.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__cert__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__cert__stable_facts.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/ideal__null__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__count_table__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__episodic_traversal__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__fsm_planner__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__global_prior__constant_none.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__majority__constant_none.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__nearest_neighbor_user_matching__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__obs_decoder_gbt__camouflage_off.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__obs_decoder_gru__camouflage_off.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__obs_decoder_logreg__camouflage_off.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__predict_all__constant_saturated.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__predict_none__constant_none.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__rag_k5_episode_retrieval__stable_facts.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__running_average_preference_regressor__flat_theta.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__seq_full_history_no_action_conditioning__constant_none.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__seq_window_with_action_conditioning_W15_no_cross_session_persistence__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__successor_map__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__transition_table__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__count_table__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__episodic_traversal__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__fsm_planner__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__global_prior__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__majority__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__nearest_neighbor_user_matching__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__obs_decoder_gbt__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__obs_decoder_gru__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__obs_decoder_logreg__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__predict_all__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__predict_none__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__rag_k5_episode_retrieval__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__running_average_preference_regressor__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__seq_full_history_no_action_conditioning__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__seq_window_with_action_conditioning_W15_no_cross_session_persistence__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__successor_map__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__transition_table__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace_void_line30_v1.csv'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace_void_line30_v1.jsonl'
  'tests/fsp_pum_env/test_s3d_part0_cputime_launchpath.py'
)
$RequiredCoreSubset = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py'
  'tests/fsp_pum_env/test_s3d_part0_cputime_launchpath.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest_void_line30_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace_void_line30_v1.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace_void_line30_v1.csv'
)

if (Test-Path -LiteralPath '.git\index.lock') {
  throw 'Stale .git\index.lock present. Confirm no live git process, remove it manually, re-run.'
}

$ActualHead = (git rev-parse HEAD).Trim()
if ($ActualHead -ne $ExpectedHead) {
  throw "HEAD pin mismatch: expected $ExpectedHead got $ActualHead"
}

git reset --

$MissingCore = @($RequiredCoreSubset | Where-Object { -not (Test-Path -LiteralPath $_) })
if ($MissingCore.Count -ne 0) {
  throw "Required core subset missing on disk: $($MissingCore -join ', ')"
}

$ExistingAllowlist = @()
foreach ($Path in $Allowlist) {
  if (Test-Path -LiteralPath $Path) {
    $ExistingAllowlist += $Path
  }
}

git add -- $ExistingAllowlist

$Staged = @(git diff --cached --name-only)
$Unexpected = @($Staged | Where-Object { $Allowlist -notcontains $_ })
if ($Unexpected.Count -ne 0) {
  throw "Unexpected staged paths: $($Unexpected -join ', ')"
}

$Deleted = @(git diff --cached --name-status | Where-Object { $_ -match '^D\s' })
if ($Deleted.Count -ne 0) {
  throw "Zero-deletion gate failed: $($Deleted -join '; ')"
}

foreach ($Path in $ExistingAllowlist) {
  Get-FileHash -Algorithm SHA256 -LiteralPath $Path | Format-List
}

git commit -m $CommitMessage -- $ExistingAllowlist

Write-Host 'Banked S3d resume STOP evidence locally. No push was performed.'
