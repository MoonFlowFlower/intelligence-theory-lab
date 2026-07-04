# Proposed operator-only bank ops for FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-VARIANCE-PROBE-001A
# Codex generated this script but did not run it.  It performs no push.
$ErrorActionPreference = 'Stop'
$ExpectedHead = '17cce05396c000097a4939aafe6f026322a36dd6'
$CommitMessage = 'bank FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-VARIANCE-PROBE-001A variance probe artifacts'
$Allowlist = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_runner.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_trace.csv'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_bank_ops.ps1'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-VARIANCE-PROBE-001A.md'
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
if ($ExistingAllowlist.Count -lt 4) {
  throw "Too few variance-probe files exist for scoped banking: $($ExistingAllowlist.Count)"
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

Write-Host 'Banked scoped variance-probe commit locally. No push was performed by this script.'
