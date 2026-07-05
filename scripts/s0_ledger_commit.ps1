# s0_ledger_commit.ps1 - commit the operator's L-004 ledger append via the same
# private-index plumbing route (shared index / lock untouched). Run AFTER manually
# pasting the L-004 line into docs/research/FSP-STAGE-LEDGER.md.

$ErrorActionPreference = 'Stop'
$BRANCH = "codex/meta-theory-scaffold"
$LEDGER = "docs/research/FSP-STAGE-LEDGER.md"
$tmpIndex = Join-Path $env:TEMP ("s0_ledger_index_" + [System.Guid]::NewGuid().ToString("N"))

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
if (-not (Select-String -Path $LEDGER -Pattern "L-004" -Quiet)) { Fail "no L-004 line found in the ledger - paste it first." }

$env:GIT_AUTHOR_NAME = "Zhouyu"; $env:GIT_AUTHOR_EMAIL = "moonlight1939300864@gmail.com"
$env:GIT_COMMITTER_NAME = "Zhouyu"; $env:GIT_COMMITTER_EMAIL = "moonlight1939300864@gmail.com"

$headSha = (git --no-optional-locks rev-parse HEAD).Trim(); GitOK
$env:GIT_INDEX_FILE = $tmpIndex
git read-tree $headSha; GitOK
git add -- $LEDGER; GitOK
$staged = @(git diff --cached --name-only $headSha); GitOK
if ($staged.Count -ne 1 -or $staged[0] -ne $LEDGER) { Fail ("staged set is not exactly the ledger: " + ($staged -join ", ")) }
$tree = (git write-tree).Trim(); GitOK
$commit = (git commit-tree $tree -p $headSha -m "docs(ledger): L-004 S0 freeze accepted, P0.2 ACTIVE (operator transition_decision)").Trim(); GitOK
git update-ref "refs/heads/$BRANCH" $commit $headSha
if ($LASTEXITCODE -ne 0) { Fail "update-ref CAS failed: HEAD moved. Re-run." }
Cleanup
Write-Host "Ledger commit: $commit" -ForegroundColor Green
Write-Host "S0 ceremony fully closed. Verify: git --no-optional-locks log --oneline -4"
