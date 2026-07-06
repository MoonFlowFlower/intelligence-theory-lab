# Proposed operator-only bank ops for FSP-PUM-ENV-IDPROBE-001A-S3D-GRU-SEED-DETERMINISM-REPAIR-001A
# Codex generated this script but did not run it. No push is performed.
# Pattern: HEAD-pinned, git reset first, allowlist-scoped add/commit,
# required-core-subset existence, zero deletion, no unexpected staged paths.
# Allowlist is limited to paths currently modified/untracked in Codex readback.
$ErrorActionPreference = 'Stop'
$ExpectedHead = '273137f06218313abc074a4b5ef78ae9ccd934d4'
$CommitMessage = 'bank FSP-PUM-ENV-IDPROBE-001A-S3D-GRU-SEED-DETERMINISM-REPAIR-001A artifacts'
$Allowlist = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/ablation_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/baseline_comparison.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest_reuse_gate_stop_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/replay_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result_reuse_gate_stop_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cert_sets_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_certificate_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage1_decision.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage1_gbt_control.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage1_gru_A.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage1_gru_B.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage2_gates.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage2_gbt_control.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage2_gru_postfix_A.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage2_gru_postfix_B.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage2_running_average_control.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_ideal_kernel_analysis_001a.md'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_null_env_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_operator_bank_ops_proposal_line30.ps1'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_manifest_reuse_gate_stop_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__discounted_LS_lambda_0.95__flat_theta.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__obs_decoder_gru__camouflage_off.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__seq_full_history_no_action_conditioning__constant_none.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__cert__seq_window_with_action_conditioning_W15_no_cross_session_persistence__low_diversity.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__discounted_LS_lambda_0.95__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__obs_decoder_gru__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__seq_full_history_no_action_conditioning__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_unit_results/member__null__seq_window_with_action_conditioning_W15_no_cross_session_persistence__NULL_env.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.csv'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.jsonl'
  'src/fsp_pum_env/battery/obs_decoders.py'
  'tests/fsp_pum_env/test_s3d_part0_cputime_launchpath.py'
)
$RequiredCoreSubset = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py'
  'src/fsp_pum_env/battery/obs_decoders.py'
  'tests/fsp_pum_env/test_s3d_part0_cputime_launchpath.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.csv'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage1_decision.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_gru_determinism_diag/stage2_gates.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result_reuse_gate_stop_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest_reuse_gate_stop_v1.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_resume_manifest_reuse_gate_stop_v1.json'
)

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

$DeletedAllowlist = @($Allowlist | Where-Object { -not (Test-Path -LiteralPath $_) })
if ($DeletedAllowlist.Count -ne 0) {
  throw "Allowlist contains missing/deleted paths: $($DeletedAllowlist -join ', ')"
}

git add -- $ExistingAllowlist

$Staged = @(git diff --cached --name-only)
$Unexpected = @($Staged | Where-Object { $Allowlist -notcontains $_ })
if ($Unexpected.Count -ne 0) {
  throw "Unexpected staged paths: $($Unexpected -join ', ')"
}

$MissingStaged = @($ExistingAllowlist | Where-Object { $Staged -notcontains $_ })
if ($MissingStaged.Count -ne 0) {
  throw "Allowlisted path did not stage a change: $($MissingStaged -join ', ')"
}

$Deleted = @(git diff --cached --name-status | Where-Object { $_ -match '^D\s' })
if ($Deleted.Count -ne 0) {
  throw "Zero-deletion gate failed: $($Deleted -join '; ')"
}

foreach ($Path in $ExistingAllowlist) {
  Get-FileHash -Algorithm SHA256 -LiteralPath $Path | Format-List
}

git commit -m $CommitMessage -- $ExistingAllowlist

Write-Host 'Banked scoped S3d GRU determinism repair artifacts locally. No push was performed.'
