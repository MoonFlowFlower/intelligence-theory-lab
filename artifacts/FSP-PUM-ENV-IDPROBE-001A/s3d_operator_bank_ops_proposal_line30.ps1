# Proposed operator-only bank ops for FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A
# Codex generated this script but did not run it. It performs no push.
$ErrorActionPreference = 'Stop'
$ExpectedHead = 'f18636420757fcab57efd45c7e66ded6cead3b98'
$CommitMessage = 'bank FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A line30 STOP artifacts'
$Allowlist = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection_line30.0.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cert_sets_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/ablation_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.csv'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_operator_bank_ops_proposal_line30.ps1'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_freshness_manifest.json'
)

$ActualHead = (git rev-parse HEAD).Trim()
if ($ActualHead -ne $ExpectedHead) {
  throw "HEAD pin mismatch: expected $ExpectedHead got $ActualHead"
}

git reset --

$ExistingAllowlist = @()
foreach ($Path in $Allowlist) {
  if (Test-Path -LiteralPath $Path) {
    $ExistingAllowlist += $Path
  }
}

if ($ExistingAllowlist.Count -ne $Allowlist.Count) {
  throw "Allowlist path missing: expected $($Allowlist.Count) got $($ExistingAllowlist.Count)"
}

git add -- $ExistingAllowlist

$Staged = @(git diff --cached --name-only)
if ($Staged.Count -ne $ExistingAllowlist.Count) {
  throw "Staged count mismatch: expected $($ExistingAllowlist.Count) got $($Staged.Count): $($Staged -join ', ')"
}

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

Write-Host 'Banked scoped S3d line30 STOP artifacts locally. No push was performed.'
