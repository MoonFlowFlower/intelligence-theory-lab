# FSP-PUM-ENV-IDPROBE-001A — S3d PART 0 STOP bank runner
# Audited-safe wrapper of BANK-OPS-001A. Commits exactly the 6 STOP artifacts.
# Self-guarded: HEAD-pin, git reset, allowlist, staged-count, zero-deletion, per-file hash, single scoped commit, no push.
# This script itself is NOT part of the 6-file bank (scoped add ignores it).

$ErrorActionPreference = 'Stop'
$Repo = 'D:\Project\AIProject\MyProject\intelligence-theory-lab'
Set-Location -LiteralPath $Repo

$BasePinFull = '80bfad4f061962ffa0ba120ea3e08b97cb93c2c1'
$ExpectedCommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d PART0 projection STOP >12 CPU-h'
$BankPaths = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_preflight_rerun/s3d_preflight_guard_report.json',
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection_v1.json',
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection.json',
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_failure_manifest.json',
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py',
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-BANK-OPS-001A.md'
)
$ExpectedHashes = @{
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_preflight_rerun/s3d_preflight_guard_report.json' = '65fa823618d31aa69e6cfe37e18352b90355fefb45e859513685f1ee5e906d45'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection_v1.json' = 'fb40a41d3447d7c95da2cebb57a59ec50fcd16bd8d70fd6f80a7e7f16f0455db'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection.json' = '413ac0c70ce1f358c87a0fc468fbe91f194faf2cc12fc09924b0e34f66ec38a7'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_failure_manifest.json' = '22a4519f113f2cf7f891be9558fda5187112925fdcf2916086e997adab1055f9'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_projection_runner.py' = 'd686cfa5f798e6561737c206e3cf6f4507cb3c7e30ba24ef715f2fd06982d6ec'
}

$GitProcesses = @(Get-Process | Where-Object { $_.ProcessName -match '^git' })
$IndexLock = Join-Path $Repo '.git/index.lock'
if (Test-Path -LiteralPath $IndexLock) {
  if ($GitProcesses.Count -gt 0) {
    throw ".git/index.lock exists while git process(es) are running; stop for operator review."
  }
  Remove-Item -LiteralPath $IndexLock -Force
}

$CurrentHead = (& git rev-parse HEAD).Trim()
if ($CurrentHead -ne $BasePinFull) {
  throw "HEAD pin mismatch. Expected $BasePinFull but got $CurrentHead"
}

& git reset

foreach ($Path in $BankPaths) {
  if (-not (Test-Path -LiteralPath (Join-Path $Repo $Path))) {
    throw "Missing bank path: $Path"
  }
}

& git add -- $BankPaths

$NameStatus = @(& git diff --cached --name-status --)
$Deleted = @($NameStatus | Where-Object { $_ -match '^D\s+' })
if ($Deleted.Count -ne 0) {
  $Deleted | ForEach-Object { Write-Host $_ }
  throw 'Porcelain gate failed: staged deletion(s) present.'
}

$StagedNames = @(& git diff --cached --name-only --)
if ($StagedNames.Count -ne $BankPaths.Count) {
  Write-Host 'Expected staged paths:'
  $BankPaths | Sort-Object | ForEach-Object { Write-Host "  $_" }
  Write-Host 'Actual staged paths:'
  $StagedNames | Sort-Object | ForEach-Object { Write-Host "  $_" }
  throw "Porcelain gate failed: staged path count $($StagedNames.Count) != expected $($BankPaths.Count)."
}
$Diff = @(Compare-Object -ReferenceObject ($BankPaths | Sort-Object) -DifferenceObject ($StagedNames | Sort-Object))
if ($Diff.Count -ne 0) {
  $Diff | Format-Table -AutoSize | Out-String | Write-Host
  throw 'Porcelain gate failed: staged set differs from allowlist.'
}

Write-Host 'Host Get-FileHash cross-check:'
foreach ($Path in $BankPaths) {
  $Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Repo $Path)).Hash.ToLowerInvariant()
  if ($ExpectedHashes.ContainsKey($Path) -and $Hash -ne $ExpectedHashes[$Path]) {
    throw "SHA256 mismatch for $Path. Expected $($ExpectedHashes[$Path]) got $Hash"
  }
  [PSCustomObject]@{ Path = $Path; SHA256 = $Hash } | Format-Table -AutoSize
}

& git commit -m $ExpectedCommitMessage
& git --no-pager show --stat HEAD
