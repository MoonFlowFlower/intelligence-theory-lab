# trackf_checkpoint_commit.ps1 - operator checkpoint commit for Track-F (N0 S1-S5 work).
# Same private-index plumbing as s0_freeze.ps1 (shared index/lock untouched; safe while
# the rung1 harness is alive). The N0 card forbids executor (Codex) commits; the operator
# runs this at the end of each implementation session.
#
# Usage (repo root):
#   powershell -ExecutionPolicy Bypass -File scripts\trackf_checkpoint_commit.ps1 -Message "feat(fsp_pum_env): S1 simulator + unit tests"
# Optional: -Paths "src/fsp_pum_env","tests/fsp_pum_env"  (defaults below)

param(
    [Parameter(Mandatory=$true)][string]$Message,
    [string[]]$Paths = @("src/fsp_pum_env", "tests/fsp_pum_env", "artifacts/FSP-PUM-ENV-IDPROBE-001A")
)

# powershell.exe -File passes array args as one literal string; split defensively.
if ($Paths.Count -eq 1 -and $Paths[0] -match ",") {
    $Paths = $Paths[0] -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ }
}

$ErrorActionPreference = 'Stop'
$BRANCH = "codex/meta-theory-scaffold"
$tmpIndex = Join-Path $env:TEMP ("trackf_ckpt_" + [System.Guid]::NewGuid().ToString("N"))

# Frozen rule sources: any diff in these = governance drift, hard stop.
$FROZEN_FILES = @{
    "docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md"      = "0a5e38a5dbe979f138231fab9870bd16f60abca7"
    "docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md"                = "882a68de2973ec1dedb588b85c6ee2703b897a4f"
    "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md" = "c07eec2ac38423bed6788904bc15013e6e755410"
    "artifacts/FSP-PUM-ENV-IDPROBE-001A/frozen_design.json"           = "32d2cbd538f31694246b2e6bb7fd5377a329478f"
}
$ALLOWED_PREFIXES = @("src/fsp_pum_env", "tests/fsp_pum_env", "artifacts/FSP-PUM-ENV-IDPROBE-001A", "docs/research/FSP-STAGE-LEDGER.md", "docs/codex/tasks/", "docs/research/SESSION-HANDOFF")

function Cleanup {
    if (Test-Path Env:GIT_INDEX_FILE) { Remove-Item Env:GIT_INDEX_FILE }
    if (Test-Path $tmpIndex) { Remove-Item $tmpIndex -Force -ErrorAction SilentlyContinue }
    foreach ($v in @("GIT_AUTHOR_NAME","GIT_AUTHOR_EMAIL","GIT_COMMITTER_NAME","GIT_COMMITTER_EMAIL")) {
        if (Test-Path "Env:$v") { Remove-Item "Env:$v" }
    }
}
function Fail([string]$msg) { Write-Host "STOP: $msg" -ForegroundColor Red; Cleanup; exit 1 }
function GitOK { if ($LASTEXITCODE -ne 0) { Fail "git command failed (exit $LASTEXITCODE)" } }

if (-not (Test-Path ".git")) { Fail "not at repo root." }

# Frozen-sha drift check (live files vs freeze record) - runs every checkpoint.
foreach ($kv in $FROZEN_FILES.GetEnumerator()) {
    $live = (git hash-object -- $kv.Key).Trim(); GitOK
    if ($live -ne $kv.Value) { Fail ("GOVERNANCE DRIFT: frozen file changed on disk: " + $kv.Key + " (live " + $live.Substring(0,12) + " != frozen " + $kv.Value.Substring(0,12) + "). Do not commit; investigate and restore.") }
}

$env:GIT_AUTHOR_NAME = "Zhouyu"; $env:GIT_AUTHOR_EMAIL = "moonlight1939300864@gmail.com"
$env:GIT_COMMITTER_NAME = "Zhouyu"; $env:GIT_COMMITTER_EMAIL = "moonlight1939300864@gmail.com"

$headSha = (git --no-optional-locks rev-parse HEAD).Trim(); GitOK
$branchNow = (git --no-optional-locks rev-parse --abbrev-ref HEAD).Trim(); GitOK
if ($branchNow -ne $BRANCH) { Fail "on branch '$branchNow', expected '$BRANCH'." }

$env:GIT_INDEX_FILE = $tmpIndex
git read-tree $headSha; GitOK
git add -- $Paths; GitOK

$staged = @(git diff --cached --name-only $headSha); GitOK
if ($staged.Count -eq 0) { Fail "nothing staged under the given paths - no checkpoint needed." }
foreach ($p in $staged) {
    if ($p -match "tlgp|TLGP|FULL_RUN") { Fail "Track-T path staged: $p" }
    if ($FROZEN_FILES.ContainsKey($p)) { Fail "frozen file staged: $p (read-only; supersede-only)" }
    $ok = $false
    foreach ($pre in $ALLOWED_PREFIXES) { if ($p.StartsWith($pre)) { $ok = $true; break } }
    if (-not $ok) { Fail "path outside Track-F allowlist prefixes: $p" }
}
Write-Host ("Staging " + $staged.Count + " path(s):") -ForegroundColor Cyan
$staged | ForEach-Object { Write-Host ("  " + $_) }

$tree = (git write-tree).Trim(); GitOK
$commit = (git commit-tree $tree -p $headSha -m $Message).Trim(); GitOK
git update-ref "refs/heads/$BRANCH" $commit $headSha
if ($LASTEXITCODE -ne 0) { Fail "update-ref CAS failed: HEAD moved during checkpoint. Re-run." }
Cleanup
Write-Host "Checkpoint commit: $commit" -ForegroundColor Green
Write-Host "Push when convenient: git push"
