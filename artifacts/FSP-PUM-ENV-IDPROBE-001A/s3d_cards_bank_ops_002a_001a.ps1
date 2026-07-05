# Operator-only scoped bank for the S3d cards: interpretation pre-reg (signed) + BUDGET-DECISION-002A
# (signed) + resume card + launch checklist. Guarded like the STOP bank-ops. Operator runs; no push.
# PRECONDITION: you have signed BUDGET-DECISION-002A §6 (mode / L / endgame / firewall / name / date).
# Author: Claude (auditor), 2026-07-05.
$ErrorActionPreference = 'Stop'

# HEAD after the STOP bank (d983b59). If you have committed anything since, update this.
$ExpectedHead  = 'd983b59'
$CommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d bank interp pre-reg + budget-decision-002A(signed) + resume card + checklist'

$Allowlist = @(
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-INTERPRETATION-PREREG-001A.md'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-002A.md'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A.md'
  'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-LAUNCH-OPERATOR-CHECKLIST-001A.md'
)
$Budget = 'docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-002A.md'

# HEAD pin (prefix match, so short or full hash both work).
$ActualHead = (git rev-parse HEAD).Trim()
if (-not $ActualHead.StartsWith($ExpectedHead)) {
  throw "HEAD pin mismatch: expected $ExpectedHead* got $ActualHead"
}

# Light signature pre-check: refuse to bank an UNSIGNED budget note.
$b = Get-Content -Raw -LiteralPath $Budget
if ($b -notmatch '\[[xX]\]\s*(reuse-completed|full re-run)') { throw "BUDGET-DECISION-002A §6: no resume mode checked — sign it first." }
if ($b -notmatch 'New line L\s*=\s*[0-9]') { throw "BUDGET-DECISION-002A §6: New line L is blank — sign it first." }
if ($b -notmatch 'Operator:\s*\S') { throw "BUDGET-DECISION-002A §6: Operator is blank — sign it first." }

# Clear index unconditionally (poisoned-index guard).
git reset --

$Existing = @()
foreach ($p in $Allowlist) { if (Test-Path -LiteralPath $p) { $Existing += $p } }
git add -- $Existing

$Staged = @(git diff --cached --name-only)

# Gate 1 — nothing unexpected staged.
$Unexpected = @($Staged | Where-Object { $Allowlist -notcontains $_ })
if ($Unexpected.Count -ne 0) { throw "Unexpected staged paths: $($Unexpected -join ', ')" }
# Gate 2 — zero file deletions.
$Deleted = @(git diff --cached --name-status | Where-Object { $_ -match '^D\s' })
if ($Deleted.Count -ne 0) { throw "Zero-deletion gate failed: $($Deleted -join '; ')" }
# Gate 3 — all four cards staged (they are new untracked files, so all must appear).
$Missing = @($Existing | Where-Object { $Staged -notcontains $_ })
if ($Missing.Count -ne 0) { throw "Expected cards not staged: $($Missing -join ', ')" }

Write-Host "STAGED ($($Staged.Count)):"; $Staged | ForEach-Object { Write-Host "  $_" }
Write-Host "`nSHA256 of staged files:"
foreach ($p in $Staged) { Get-FileHash -Algorithm SHA256 -LiteralPath $p | Format-List }

git commit -m $CommitMessage -- $Staged
Write-Host "`nBanked S3d cards locally (interp pre-reg + 002A signed + resume + checklist). No push."
