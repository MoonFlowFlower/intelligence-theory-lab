# FSP-PUM-ENV-IDPROBE-001A - bank S3d cell-headroom pre-check (+ its card)
# Pins the repair+diagnostic bank HEAD. Prints Get-FileHash (host-authoritative). No push.

$ErrorActionPreference = 'Stop'
$Repo = 'D:\Project\AIProject\MyProject\intelligence-theory-lab'
Set-Location -LiteralPath $Repo

$ExpectedHeadPrefix = '8cd95a0'   # repair+diagnostic bank; run this before any later commit
$CommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d cell-headroom pre-check (instrument-defect finding)'
$Allowlist = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cell_headroom_precheck_runner.py'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cell_headroom_precheck.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cell_headroom_precheck_trace.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cell_headroom_precheck_claim_ceiling.txt'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-CELL-HEADROOM-PRECHECK-001A.md'
)

$ActualHead = (& git rev-parse HEAD).Trim()
if (-not $ActualHead.StartsWith($ExpectedHeadPrefix)) {
  throw "HEAD pin mismatch: expected prefix $ExpectedHeadPrefix got $ActualHead"
}
foreach ($Path in $Allowlist) {
  if (-not (Test-Path -LiteralPath (Join-Path $Repo $Path))) { throw "Missing bank path: $Path" }
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

Write-Host 'Host Get-FileHash:'
foreach ($Path in $Allowlist) { Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Repo $Path) | Format-List }

& git commit -m $CommitMessage -- $Allowlist
& git --no-pager show --stat HEAD
Write-Host 'Banked cell-headroom pre-check. No push. Battery NOT green-lit: frozen S3d instrument needs a successor spec (see audit).'
