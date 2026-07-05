# s0_freeze.ps1 (v2, plumbing route) - FSP N0 S0 freeze ceremony, operator-executed (host-side).
# Governed by: docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A.md
# Run from repo root:  powershell -ExecutionPolicy Bypass -File scripts\s0_freeze.ps1
#
# v2 rationale: a live agent harness (rung1 Codex session) issues periodic `git add -u`
# snapshots. The pre-existing stale .git/index.lock is currently BLOCKING those from
# dirtying the shared index. Therefore this script: does NOT kill git processes, does
# NOT delete the lock, and NEVER touches the shared index. The entire ceremony runs on
# a private GIT_INDEX_FILE with plumbing commands (read-tree/add/write-tree/commit-tree/
# update-ref with compare-and-swap). Object-db writes and ref updates do not use
# .git/index.lock, so there is zero contention with the harness.

$ErrorActionPreference = 'Stop'

$tmpIndex = Join-Path $env:TEMP ("s0_freeze_index_" + [System.Guid]::NewGuid().ToString("N"))

function Cleanup {
    if (Test-Path Env:GIT_INDEX_FILE) { Remove-Item Env:GIT_INDEX_FILE }
    if (Test-Path $tmpIndex) { Remove-Item $tmpIndex -Force -ErrorAction SilentlyContinue }
    foreach ($v in @("GIT_AUTHOR_NAME","GIT_AUTHOR_EMAIL","GIT_COMMITTER_NAME","GIT_COMMITTER_EMAIL")) {
        if (Test-Path "Env:$v") { Remove-Item "Env:$v" }
    }
}

function Fail([string]$msg) {
    Write-Host ""
    Write-Host "STOP: $msg" -ForegroundColor Red
    Write-Host "Ceremony aborted. Shared index, lock, and refs untouched unless stated otherwise." -ForegroundColor Red
    Cleanup
    exit 1
}

function GitOK { if ($LASTEXITCODE -ne 0) { Fail "git command failed (exit $LASTEXITCODE)" } }

# ---------- constants ----------
$BRANCH = "codex/meta-theory-scaffold"
$CARD   = "docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md"
$CONST  = "docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md"
$PLAN   = "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md"
$FROZEN = "artifacts/FSP-PUM-ENV-IDPROBE-001A/frozen_design.json"
$FRECORD = "artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json"

$ALLOWLIST = @(
    "CLAUDE.md",
    "docs/codex/contracts/MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md",
    $PLAN,
    "docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A.md",
    $CONST,
    "docs/research/FSP-LADDER-MEMO-001A.md",
    "docs/research/FSP-MASTER-PHASE-PLAN-001A.md",
    "docs/research/FSP-ROADMAP-CONTINGENCY-001A.md",
    "docs/research/FSP-ROUTE-PROGRAM-001A-functional-subject-proxy-route-design.md",
    "docs/research/FSP-STAGE-LEDGER.md",
    "docs/research/SESSION-HANDOFF-FSP-20260701.md",
    $CARD,
    $FROZEN,
    $FRECORD,
    "artifacts/FSP-PUM-ENV-IDPROBE-001A/design_choices_rationale.md",
    "tests/fsp_pum_env/test_frozen_design.py"
)

# identity via env vars (plumbing-safe, no config mutation)
$env:GIT_AUTHOR_NAME = "Zhouyu"; $env:GIT_AUTHOR_EMAIL = "moonlight1939300864@gmail.com"
$env:GIT_COMMITTER_NAME = "Zhouyu"; $env:GIT_COMMITTER_EMAIL = "moonlight1939300864@gmail.com"

# ---------- preflight (read-only; --no-optional-locks everywhere) ----------
Write-Host "=== S0 preflight (v2 plumbing route) ===" -ForegroundColor Cyan

if (-not (Test-Path ".git")) { Fail "not at repo root (no .git here)." }

$branchNow = (git --no-optional-locks rev-parse --abbrev-ref HEAD).Trim(); GitOK
if ($branchNow -ne $BRANCH) { Fail "on branch '$branchNow', expected '$BRANCH'." }
$headSha = (git --no-optional-locks rev-parse HEAD).Trim(); GitOK
Write-Host "HEAD: $headSha"

# live git processes: recorded, NOT fatal (harness snapshots are expected; we bypass the shared index)
$liveGit = @(Get-Process -Name git -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
Write-Host ("Live git processes (recorded, tolerated): " + $(if ($liveGit) { $liveGit -join ", " } else { "none" }))
if (Test-Path ".git/index.lock") {
    Write-Host "NOTE: .git/index.lock present and DELIBERATELY LEFT IN PLACE (it shields the shared index from harness add -u)." -ForegroundColor Yellow
}

# CLAUDE.md integrity
if (-not (Select-String -Path "CLAUDE.md" -Pattern "episodic_traversal" -Quiet)) {
    Fail "CLAUDE.md tail check failed ('episodic_traversal' not found) - possible truncation. Do not commit it."
}
$claudeAdd = $true
$numstat = git --no-optional-locks diff --ignore-cr-at-eol --numstat HEAD -- CLAUDE.md; GitOK
if (-not $numstat) {
    Write-Host "CLAUDE.md has no content diff vs HEAD; dropping it from the allowlist (ops card 4.1)." -ForegroundColor Yellow
    $claudeAdd = $false
} else {
    $parts = ($numstat -split "\s+")
    if (-not ($parts[0] -eq "1" -and $parts[1] -eq "0")) {
        Fail ("CLAUDE.md real diff vs HEAD is not exactly +1/-0 (got +" + $parts[0] + "/-" + $parts[1] + "). Inspect: git --no-optional-locks diff --ignore-cr-at-eol HEAD -- CLAUDE.md")
    }
}

foreach ($f in @($CARD, $CONST, $PLAN, $FROZEN)) {
    if (-not (Test-Path $f)) { Fail "missing required file: $f" }
}
$cardText = [System.IO.File]::ReadAllText($CARD)
foreach ($ph in @("__SHA_CONSTITUTION__", "__SHA_PLAN__", "__SHA_FROZEN_DESIGN__")) {
    if (-not $cardText.Contains($ph)) { Fail "card freeze block placeholder missing: $ph (already filled? aborting to avoid double-run)" }
}

$py = $null
foreach ($cand in @("python", "py")) {
    if (Get-Command $cand -ErrorAction SilentlyContinue) { $py = $cand; break }
}
if ($null -eq $py) { Fail "no python found on PATH; the frozen_design validator is a hard S0 gate." }
& $py "tests/fsp_pum_env/test_frozen_design.py"
if ($LASTEXITCODE -ne 0) { Fail "frozen_design.json validator FAILED - nothing to freeze." }

$autocrlf = git --no-optional-locks config core.autocrlf; if ($LASTEXITCODE -ne 0) { $autocrlf = "unset" }
Write-Host "Preflight OK (core.autocrlf=$autocrlf)." -ForegroundColor Green

# ---------- sha computation + placeholder fill ----------
Write-Host "=== Computing canonical blob shas ===" -ForegroundColor Cyan
$shaConst  = (git hash-object -- $CONST).Trim();  GitOK
$shaPlan   = (git hash-object -- $PLAN).Trim();   GitOK
$shaFrozen = (git hash-object -- $FROZEN).Trim(); GitOK

$cardText = $cardText.Replace("__SHA_CONSTITUTION__", $shaConst).Replace("__SHA_PLAN__", $shaPlan).Replace("__SHA_FROZEN_DESIGN__", $shaFrozen)
[System.IO.File]::WriteAllText((Resolve-Path $CARD), $cardText, (New-Object System.Text.UTF8Encoding($false)))
$shaCard = (git hash-object -- $CARD).Trim(); GitOK

$frTemplate = @'
{
  "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
  "stage": "S0 freeze ceremony",
  "date": "__DATE__",
  "executed_by": "operator (Zhouyu), personally, per execution plan S0 (operator + Codex); committable inputs drafted by Claude (auditor) at operator request - disclosed for S6 audit",
  "ceremony_route": "private GIT_INDEX_FILE plumbing (read-tree/add/write-tree/commit-tree/update-ref CAS); shared index and its lock deliberately untouched because a live harness issues periodic add -u snapshots",
  "canonical_blob_shas": {
    "card": "__SHA_CARD__",
    "constitution": "__SHA_CONST__",
    "execution_plan": "__SHA_PLAN__",
    "frozen_design": "__SHA_FROZEN__"
  },
  "freeze_commit_sha": "pending",
  "bookkeeping_commit_sha": "pending",
  "base_head_at_ceremony": "__HEAD__",
  "frozen_readonly_from_now": ["card", "constitution", "execution_plan", "frozen_design (supersede-only, per constitution)"],
  "committed_but_living": ["ledger (append-only)", "phase plan", "roadmap", "ladder memo", "route program", "signature standard", "CLAUDE.md", "handoff", "S0 ops card"],
  "environment_provenance": { "core_autocrlf": "__AUTOCRLF__", "sha_method": "git hash-object with default filters == committed blob", "live_git_processes_at_ceremony": "__LIVEGIT__" },
  "known_textual_inconsistencies": "card R1 header 'DRAFT - NOT AUTHORIZED' wording reconciled pre-freeze with operator sign-off (operator executed this ceremony after review)",
  "run1_stop_reference": "see S0 ops card section 14 changelog (failure evidence preserved; run-2 pivoted to plumbing after harness snapshots were identified)"
}
'@
$frText = $frTemplate.Replace("__DATE__", (Get-Date -Format "yyyy-MM-dd")).Replace("__SHA_CARD__", $shaCard).Replace("__SHA_CONST__", $shaConst).Replace("__SHA_PLAN__", $shaPlan).Replace("__SHA_FROZEN__", $shaFrozen).Replace("__AUTOCRLF__", "$autocrlf").Replace("__HEAD__", $headSha).Replace("__LIVEGIT__", $(if ($liveGit) { $liveGit -join "," } else { "none" }))
[System.IO.File]::WriteAllText((Join-Path (Get-Location) $FRECORD), $frText, (New-Object System.Text.UTF8Encoding($false)))

# ---------- private-index staging (shared index never touched) ----------
Write-Host "=== Private-index staging (plumbing) ===" -ForegroundColor Cyan
$env:GIT_INDEX_FILE = $tmpIndex
git read-tree $headSha; GitOK

$addList = $ALLOWLIST
if (-not $claudeAdd) { $addList = $addList | Where-Object { $_ -ne "CLAUDE.md" } }
git add -- $addList; GitOK

$staged = @(git diff --cached --name-only $headSha) | Sort-Object; GitOK
$expected = @($addList) | Sort-Object
$diff = Compare-Object -ReferenceObject $expected -DifferenceObject $staged
if ($diff) {
    $detail = ($diff | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" }) -join "; "
    Fail "private-index staged set does not equal allowlist. Detail: $detail"
}
if ($staged -match "tlgp|TLGP|FULL_RUN") { Fail "Track-T path detected in staged set." }
Write-Host ("Staged exactly " + $staged.Count + " allowlisted paths in the private index.") -ForegroundColor Green

# ---------- commit 1 via plumbing + CAS ref update ----------
$msg1 = "docs(freeze): FSP N0 S0 freeze - governance stack committed; frozen_design.json zero-TBD (validator PASS); canonical shas in card freeze block + freeze_record.json (Track F only; operator-executed plumbing ceremony; R1 header reconciled with operator sign-off; CLAUDE.md +1 additive contracts bullet)"
$tree1 = (git write-tree).Trim(); GitOK
$commit1 = (git commit-tree $tree1 -p $headSha -m $msg1).Trim(); GitOK
git update-ref "refs/heads/$BRANCH" $commit1 $headSha
if ($LASTEXITCODE -ne 0) { Fail "update-ref CAS failed: HEAD moved during the ceremony (Track T banked something?). Nothing was overwritten. Re-run the script; it will re-base on the new HEAD." }
Write-Host "Freeze commit: $commit1" -ForegroundColor Green

# ---------- 3-way identity verification ----------
Write-Host "=== 3-way identity verification ===" -ForegroundColor Cyan
$checks = @(
    @{ name = "card";           path = $CARD;   expected = $shaCard   },
    @{ name = "constitution";   path = $CONST;  expected = $shaConst  },
    @{ name = "execution_plan"; path = $PLAN;   expected = $shaPlan   },
    @{ name = "frozen_design";  path = $FROZEN; expected = $shaFrozen }
)
$allOK = $true
foreach ($c in $checks) {
    $live = (git hash-object -- $c.path).Trim()
    $tree = ((git ls-tree $commit1 -- $c.path) -split "\s+")[2]
    $ok = ($live -eq $c.expected) -and ($tree -eq $c.expected)
    if (-not $ok) { $allOK = $false }
    $status = "OK "; if (-not $ok) { $status = "FAIL" }
    Write-Host ("[" + $status + "] " + $c.name + " live=" + $live.Substring(0,12) + " record=" + $c.expected.Substring(0,12) + " tree=" + $tree.Substring(0,12))
}
if (-not $allOK) { Fail "3-way identity FAILED. Do NOT delete the commit (append-only history). Report this output; freeze is NOT achieved." }

# ---------- commit 2 (bookkeeping) via plumbing + CAS ----------
$frText = [System.IO.File]::ReadAllText((Resolve-Path $FRECORD))
$frText = $frText.Replace('"freeze_commit_sha": "pending"', '"freeze_commit_sha": "' + $commit1 + '"')
[System.IO.File]::WriteAllText((Resolve-Path $FRECORD), $frText, (New-Object System.Text.UTF8Encoding($false)))
git add -- $FRECORD; GitOK
$tree2 = (git write-tree).Trim(); GitOK
$commit2 = (git commit-tree $tree2 -p $commit1 -m "docs(freeze): record S0 freeze commit sha in freeze_record.json (bookkeeping)").Trim(); GitOK
git update-ref "refs/heads/$BRANCH" $commit2 $commit1
if ($LASTEXITCODE -ne 0) { Fail "update-ref CAS failed on bookkeeping commit. Freeze commit $commit1 stands; re-run bookkeeping manually." }

Cleanup

# ---------- summary ----------
Write-Host ""
Write-Host "=== S0 FREEZE COMPLETE (plumbing route) ===" -ForegroundColor Green
Write-Host ("freeze commit:      " + $commit1)
Write-Host ("bookkeeping commit: " + $commit2)
Write-Host ("card sha:           " + $shaCard)
Write-Host ("constitution sha:   " + $shaConst)
Write-Host ("execution plan sha: " + $shaPlan)
Write-Host ("frozen_design sha:  " + $shaFrozen)
Write-Host ""
Write-Host "NOTE: `git status` may look odd until the shared index catches up (it is still shielded by the old lock; the harness or a later `git reset` will refresh it AFTER the rung1 session ends). The branch ref and commits above are the truth; verify with: git --no-optional-locks log --oneline -3" -ForegroundColor Yellow
Write-Host ""
Write-Host "NEXT (manual, operator): append this line to docs/research/FSP-STAGE-LEDGER.md, then re-run ONLY the ledger commit helper: powershell -ExecutionPolicy Bypass -File scripts\s0_ledger_commit.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host ("- L-004 | " + (Get-Date -Format "yyyy-MM-dd") + " | transition_decision (accepted) | P0.2 ACTIVE: S0 freeze complete. Freeze commit " + $commit1.Substring(0,12) + " + bookkeeping " + $commit2.Substring(0,12) + "; canonical blob shas in artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json; card+constitution+plan+frozen_design read-only (supersede-only) from here; S1 (sealed simulator) open per execution plan. Ceremony executed by operator personally via private-index plumbing; frozen_design.json drafted by Claude (auditor), reviewed and accepted by operator at commit. | authorized-by: operator")
Write-Host ""
Write-Host "Then paste the full console output back to Claude for post-hoc verification." -ForegroundColor Yellow
