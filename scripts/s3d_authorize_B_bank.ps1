# FSP-PUM-ENV-IDPROBE-001A - S3d authorize-B bank
# Banks the SIGNED budget decision (Option B + line L) together with the battery exec card,
# so the authorization + execution spec are on record BEFORE Codex runs the battery.
# Refuses to commit if BUDGET-DECISION section 8 is still unsigned. Pins the probe-bank HEAD. No push.

$ErrorActionPreference = 'Stop'
$Repo = 'D:\Project\AIProject\MyProject\intelligence-theory-lab'
Set-Location -LiteralPath $Repo

$ExpectedHeadPrefix = '086e948'   # probe-bank commit; run this right after that bank
$CommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d authorize B: signed budget line-raise + battery exec card'
$DecisionPath = 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md'
$ExecCardPath = 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A.md'
$Allowlist = @($DecisionPath, $ExecCardPath)

# --- HEAD pin ---
$ActualHead = (& git rev-parse HEAD).Trim()
if (-not $ActualHead.StartsWith($ExpectedHeadPrefix)) {
  throw "HEAD pin mismatch: expected prefix $ExpectedHeadPrefix got $ActualHead"
}

# --- signing gate: refuse to bank an unsigned decision ---
$decision = Get-Content -Raw -LiteralPath $DecisionPath
if ($decision -notmatch '\[[xX]\]\s*B') {
  throw "BUDGET-DECISION section 8 not signed: Option B is not checked ([x] B). Fill section 8 first."
}
if ($decision -match 'Operator:\s+_{10,}') {
  throw "BUDGET-DECISION section 8 not signed: Operator line still blank. Fill Operator + Date + line first."
}

# --- existence ---
foreach ($Path in $Allowlist) {
  if (-not (Test-Path -LiteralPath (Join-Path $Repo $Path))) { throw "Missing bank path: $Path" }
}

git reset --

git add -- $Allowlist

$Staged = @(& git diff --cached --name-only --)
if ($Staged.Count -ne $Allowlist.Count) {
  Write-Host 'Expected:'; $Allowlist | Sort-Object | ForEach-Object { Write-Host "  $_" }
  Write-Host 'Actual:'; $Staged | Sort-Object | ForEach-Object { Write-Host "  $_" }
  throw "Staged count mismatch: $($Staged.Count) != $($Allowlist.Count)"
}
$Unexpected = @($Staged | Where-Object { $Allowlist -notcontains $_ })
if ($Unexpected.Count -ne 0) { throw "Unexpected staged paths: $($Unexpected -join ', ')" }

$Deleted = @(& git diff --cached --name-status -- | Where-Object { $_ -match '^D\s' })
if ($Deleted.Count -ne 0) { throw "Zero-deletion gate failed: $($Deleted -join '; ')" }

Write-Host 'Host Get-FileHash cross-check:'
foreach ($Path in $Allowlist) {
  Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $Repo $Path) | Format-List
}

git commit -m $CommitMessage -- $Allowlist
& git --no-pager show --stat HEAD
Write-Host 'Authorization banked locally. No push performed. Now hand the battery card + Codex prompt to Codex.'
