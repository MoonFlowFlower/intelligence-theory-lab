# FSP-PUM-ENV-IDPROBE-001A - bank S3d ideal-variant repair + stable-fact recommend diagnostic
# Banks the filter fix (on-disk host sha256 confirmed 31ee442c... by the diagnostic step-0 gates),
# its repair evidence + card, and the diagnostic evidence + card. Pins the STOP-bank HEAD.
# Prints Get-FileHash per file (host-authoritative); structural guards gate the commit. No push.

$ErrorActionPreference = 'Stop'
$Repo = 'D:\Project\AIProject\MyProject\intelligence-theory-lab'
Set-Location -LiteralPath $Repo

$ExpectedHeadPrefix = '66a4738'   # STOP-artifacts bank; run this before any later commit
$CommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d ideal-variant repair + stable-fact recommend diagnostic (CELL headroom finding)'
$Allowlist = @(
  'src/fsp_pum_env/factored_filter.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_ideal_variant_repair_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_ideal_variant_repair_trace_flat_theta.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_ideal_variant_repair_trace_stable_facts.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_ideal_variant_repair_failure_manifest.json'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-IDEAL-VARIANT-REPAIR-001A.md'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_stablefact_recommend_diagnostic.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_stablefact_recommend_diagnostic_trace.jsonl'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-STABLEFACT-RECOMMEND-DIAGNOSTIC-001A.md'
)

$ActualHead = (& git rev-parse HEAD).Trim()
if (-not $ActualHead.StartsWith($ExpectedHeadPrefix)) {
  throw "HEAD pin mismatch: expected prefix $ExpectedHeadPrefix got $ActualHead"
}

foreach ($Path in $Allowlist) {
  if (-not (Test-Path -LiteralPath (Join-Path $Repo $Path))) { throw "Missing bank path: $Path" }
}

# On-disk filter must equal the diagnostic-validated host hash (integrity anchor for the one code file).
$FilterHash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Repo 'src/fsp_pum_env/factored_filter.py')).Hash.ToLowerInvariant()
if ($FilterHash -ne '31ee442c90200247eaddac6d3a7989ce297ac6fd63d601178258efaccba9b774') {
  throw "factored_filter.py host hash $FilterHash != diagnostic-validated 31ee442c...; STOP for review."
}

& git reset --

& git add -- $Allowlist

$Staged = @(& git diff --cached --name-only --)
if ($Staged.Count -ne $Allowlist.Count) {
  Write-Host 'Expected:'; $Allowlist | Sort-Object | ForEach-Object { Write-Host "  $_" }
  Write-Host 'Actual:';   $Staged   | Sort-Object | ForEach-Object { Write-Host "  $_" }
  throw "Staged count mismatch: $($Staged.Count) != $($Allowlist.Count)"
}
$Unexpected = @($Staged | Where-Object { $Allowlist -notcontains $_ })
if ($Unexpected.Count -ne 0) { throw "Unexpected staged paths: $($Unexpected -join ', ')" }

$Deleted = @(& git diff --cached --name-status -- | Where-Object { $_ -match '^D\s' })
if ($Deleted.Count -ne 0) { throw "Zero-deletion gate failed: $($Deleted -join '; ')" }

Write-Host 'Host Get-FileHash (eyeball vs auditor record):'
foreach ($Path in $Allowlist) {
  Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Repo $Path) | Format-List
}

& git commit -m $CommitMessage -- $Allowlist
& git --no-pager show --stat HEAD
Write-Host 'Banked repair + diagnostic locally. No push. Battery is NOT green-lit yet (see cell-headroom finding).'
