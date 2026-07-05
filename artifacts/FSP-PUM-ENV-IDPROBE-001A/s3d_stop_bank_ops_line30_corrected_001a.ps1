# Corrected operator-only bank ops for the L=30 battery STOP (runtime_guard_exceeded).
# Supersedes the DEFECTIVE s3d_operator_bank_ops_proposal_line30.ps1, which allowlisted 4 stale
# untracked reports (cert/null/baseline/replay were NOT regenerated this run) and the unchanged
# tracked runner.py (would zero-stage and trip its strict count gate).
# Author: Claude (auditor), 2026-07-05. Operator runs this; Codex/Claude do not. No push.
$ErrorActionPreference = 'Stop'

# HEAD the STOP evidence was produced against (per result.json git_readback: head_hash 2a4502a...).
# The battery run committed nothing (Codex no-git). IF you have since banked the interpretation
# pre-reg card, HEAD advanced by exactly that one commit — confirm `git log --oneline -3` shows only
# that, then set $ExpectedHead to the current HEAD before running.
$ExpectedHead  = '2a4502ae9469ad41dd448aaa793509148b7265b1'
$CommitMessage = 'FSP-PUM-ENV-IDPROBE-001A S3d L30 battery STOP runtime_guard_exceeded (results void) boundary evidence'

# Fresh STOP evidence only. EXCLUDES: s3d_battery_runner_line30.py (unchanged, already committed);
# s3d_certificate_report.json / s3d_null_env_report.json / baseline_comparison.json /
# replay_report.json (untracked STALE — not regenerated this run; do not bank as battery output).
$Allowlist = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.csv'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_freshness_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/ablation_report.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection_line30.0.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_cert_sets_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_stop_bank_ops_line30_corrected_001a.ps1'
)

# Core STOP evidence that MUST stage (else the bank is incomplete). The rest of the allowlist may be
# legitimately unchanged (zero-stage) — that is tolerated, not an error.
$Required = @(
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/result.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/failure_manifest.json'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.jsonl'
  'artifacts/FSP-PUM-ENV-IDPROBE-001A/trace.csv'
)

$ActualHead = (git rev-parse HEAD).Trim()
if ($ActualHead -ne $ExpectedHead) {
  throw "HEAD pin mismatch: expected $ExpectedHead got $ActualHead (see the note above about the interpretation-card commit)."
}

# Clear the index unconditionally first (poisoned-index guard, per git-sandbox-constraints).
git reset --

$ExistingAllowlist = @()
foreach ($Path in $Allowlist) {
  if (Test-Path -LiteralPath $Path) { $ExistingAllowlist += $Path }
}

git add -- $ExistingAllowlist

$Staged = @(git diff --cached --name-only)

# Gate 1 — nothing unexpected staged (staged subset of allowlist).
$Unexpected = @($Staged | Where-Object { $Allowlist -notcontains $_ })
if ($Unexpected.Count -ne 0) { throw "Unexpected staged paths: $($Unexpected -join ', ')" }

# Gate 2 — zero deletions.
$Deleted = @(git diff --cached --name-status | Where-Object { $_ -match '^D\s' })
if ($Deleted.Count -ne 0) { throw "Zero-deletion gate failed: $($Deleted -join '; ')" }

# Gate 3 — every core STOP-evidence file staged.
$MissingRequired = @($Required | Where-Object { $Staged -notcontains $_ })
if ($MissingRequired.Count -ne 0) {
  throw "Required STOP evidence not staged (unexpected — investigate before banking): $($MissingRequired -join ', ')"
}

# Gate 4 — at least the core staged.
if ($Staged.Count -lt $Required.Count) { throw "Too few staged files: $($Staged.Count)" }

# Transparency: which allowlisted files did NOT stage (legitimately unchanged this run).
$Unstaged = @($ExistingAllowlist | Where-Object { $Staged -notcontains $_ })
Write-Host "STAGED ($($Staged.Count)):"; $Staged | ForEach-Object { Write-Host "  $_" }
if ($Unstaged.Count -ne 0) {
  Write-Host "ALLOWLISTED-BUT-UNCHANGED (not banked, already at current content):"
  $Unstaged | ForEach-Object { Write-Host "  $_" }
}

# Provenance: hash each staged file (record these).
Write-Host "`nSHA256 of staged files:"
foreach ($Path in $Staged) { Get-FileHash -Algorithm SHA256 -LiteralPath $Path | Format-List }

# Scoped commit of exactly the staged paths. No push.
git commit -m $CommitMessage -- $Staged

Write-Host "`nBanked L30 battery STOP (void) boundary evidence locally. No push performed."
Write-Host "NOTE: the defective s3d_operator_bank_ops_proposal_line30.ps1 and the 4 stale reports"
Write-Host "      (cert/null/baseline/replay) were intentionally NOT banked. You may delete the"
Write-Host "      defective proposal; leave the stale reports for the resume card's *_v1 preservation."
