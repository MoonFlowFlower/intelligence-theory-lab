# BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A — B-ii-R1 new-session handoff

Snapshot written: 2026-07-08. This handoff is a compact recovery pointer, not a
new source of truth. In the next session, re-read live repo state and the
artifacts named below before acting.

## Live readback before this handoff edit

- Repo: `D:/Project/AIProject/MyProject/intelligence-theory-lab`
- Branch: `codex/meta-theory-scaffold`
- Pre-handoff HEAD: `fc2f0401c62c285259a2d64add97dac24dc94e7e`
- Remote state at readback: branch ahead of `origin/codex/meta-theory-scaffold` by 4 local commits.
- Worktree before handoff edit: clean.
- Remote anchor / push / tag: not performed.

## Current boundary

Current stage: Phase B-ii-R1 adapter FAIRNESS repair completed locally; STOP for
Claude Red re-audit.

Claim ceiling: borrowed-adapter fairness hygiene only. No borrowed headroom, no
candidate verdict, no probe-validity result, no mechanism evidence, no learning,
no agency/autonomy/subjectivity/consciousness, and no EGO mainline effect.

Mainline integration status: none. All work is isolated to
`scripts/env_headroom_probe/`, tests, docs, and
`artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/`.

Enabled status: borrowed candidates are still not in official scored `ADAPTERS`.
The current CLI default remains contract-only unless a scoring path is explicitly
authorized in a later phase.

## Commit chain for this boundary

- `e500abbf9` — Phase A prereg freeze.
- `5dd8f6b0a` — Phase-A B1-B3 guard rework; frozen band/control set/expected verdicts ancestor.
- `2d17e2c9d` — Phase B-i controls-only scoring artifacts.
- `470f44909` — Phase B-ii borrowed symbolic adapter wiring.
- `fc2f0401c` — Phase B-ii-R1 adapter fairness repair.

The B-ii-R1 commit descends from `470f4490`.

## Frozen / do-not-edit boundary

Do not edit unless a new authorized card explicitly permits it:

- `EQUIVALENCE_BAND = 0.05`
- Control set:
  - `POS_INTERNAL_ESTAR`
  - `NEG_5A846D5_SCOUT`
- Expected control verdicts:
  - `POS_INTERNAL_ESTAR == HEADROOM`
  - `NEG_5A846D5_SCOUT == SATURATED`
- N2/R4 frozen specs.
- `src/` mechanism code.
- Any threshold/guard just to make a future env pass.

Forbidden next-session actions without explicit authorization:

- scoring any borrowed candidate env;
- computing borrowed candidate verdicts;
- computing or reusing `probe_valid` for candidates;
- weakening baselines, guard logic, band, or control expectations;
- pixel/physics adapters;
- remote anchor / push / tag;
- credentials or external services.

## Current adapter state after B-ii-R1

Artifact authority:

- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/borrowed_adapter_manifest.json`
- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/failure_manifest.json`

Manifest readback at handoff:

```json
{
  "phase": "PHASE_BII_R1_ADAPTER_FAIRNESS_REPAIR_ONLY",
  "scoring_performed": false,
  "probe_valid_computed": false,
  "candidate_verdicts_computed": false,
  "wired_adapters": [
    "bsuite:memory_len/0",
    "bsuite:memory_size/0",
    "bsuite:umbrella_length/0"
  ],
  "dropped_adapters": [
    "dm_alchemy:symbolic_default",
    "minigrid:MiniGrid-KeyCorridorS3R1-v0",
    "minigrid:MiniGrid-MemoryS13Random-v0"
  ]
}
```

Active borrowed adapters:

- `bsuite:memory_len/0`
- `bsuite:memory_size/0`
- `bsuite:umbrella_length/0`

For all active bsuite adapters:

- `oracle_from_O` score on eval: `1.0`
- guard: `VOID_TRIVIALLY_DECODABLE`
- future floor effect recorded: `SATURATED_BY_LEGAL_OBSERVATION_DECODER`
- interpretation: these are O-determined by a trivial legal decoder and must not
  be treated as borrowed-env HEADROOM.

Dropped adapters:

- `minigrid:MiniGrid-MemoryS13Random-v0`
  - reason: single reset observation O does not determine target branch; prior
    target would require private `unwrapped.success_pos` absent from O.
- `minigrid:MiniGrid-KeyCorridorS3R1-v0`
  - reason: single reset observation O does not determine target object identity;
    prior target would require private `unwrapped.obj` absent from O.
- `dm_alchemy:symbolic_default`
  - reason: cheap symbolic wiring unavailable in the current environment; do not fake it.

## What was verified in B-ii-R1

Commands/evidence from the B-ii-R1 closeout:

- Targeted adapter tests:
  - `python -m pytest -q tests/env_headroom_probe/test_phase_bii_r1_adapter_fairness.py tests/env_headroom_probe/test_phase_bii_borrowed_adapters.py`
  - result: `6 passed`
- Compile check:
  - `python -m compileall -q scripts/env_headroom_probe tests/env_headroom_probe/test_phase_bii_borrowed_adapters.py tests/env_headroom_probe/test_phase_bii_r1_adapter_fairness.py`
  - result: ok
- Contract readback:
  - `official_scoring_enabled=false`
  - `equivalence_band=0.05`
  - controls unchanged: `POS_INTERNAL_ESTAR=HEADROOM`, `NEG_5A846D5_SCOUT=SATURATED`
- Borrowed scoring guard check:
  - `python -m scripts.env_headroom_probe.runner --mode recompute --env bsuite:memory_len/0`
  - result: `unknown env adapter: bsuite:memory_len/0`
- Scope check before commit:
  - `git diff --cached --check`
  - result: passed, with CRLF warnings only.

Important limitation: no full candidate battery, no borrowed-env scoring, no
candidate verdicts, no Phase B-iii execution, and no probe-valid computation
were run in B-ii-R1.

## Claude Red re-audit focus

Claude should audit `fc2f0401c` for:

1. `oracle_from_O` receives only legal `O`, not private env state, rewards,
   `y`, `y_star`, filenames, or record ids.
2. MiniGrid reset-only adapters are truly dropped and cannot silently emit
   private-state targets.
3. bsuite trivial O-decoder guard is blocking for future scoring; it must not
   be bypassable into HEADROOM.
4. `frequency_marginal` remains N/A for non-contamination envs rather than a
   straw baseline.
5. No band/control/expected-verdict/threshold edits occurred.
6. No candidate scoring or candidate verdict artifact was emitted.
7. The handoff itself is not treated as evidence; machine-readable artifacts and
   source/test code remain the authority.

## Next-session startup checklist

Run these before proposing any next action:

```powershell
cd D:\Project\AIProject\MyProject\intelligence-theory-lab
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch
git merge-base --is-ancestor 470f4490 HEAD; if ($LASTEXITCODE -eq 0) { "descends_from_470f4490=yes" } else { "descends_from_470f4490=no" }
git show --stat --oneline --name-status fc2f0401c
python -m pytest -q tests/env_headroom_probe/test_phase_bii_r1_adapter_fairness.py tests/env_headroom_probe/test_phase_bii_borrowed_adapters.py
```

Then read:

- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.md`
- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-STEP-A-PREREG-001A.md`
- `docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-PHASE-BII-R1-ADAPTER-FAIRNESS-REPAIR.md`
- `scripts/env_headroom_probe/adapters.py`
- `tests/env_headroom_probe/test_phase_bii_r1_adapter_fairness.py`
- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/borrowed_adapter_manifest.json`
- `artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/failure_manifest.json`

## Pasteable next-session prompt

```text
We are in D:\Project\AIProject\MyProject\intelligence-theory-lab.
Recover current truth from git and artifacts first; do not trust this prompt alone.

Task lineage: BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A.
Current boundary: Phase B-ii-R1 adapter fairness repair committed at
fc2f0401c62c285259a2d64add97dac24dc94e7e; STOP for Claude Red re-audit.

Do NOT score candidates, compute candidate verdicts, compute probe_valid for
candidates, edit band/control/expected verdicts, touch src mechanism code,
N2/R4 specs, pixel/physics adapters, credentials, push, tag, or remote-anchor.

First read:
- docs/codex/handoffs/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-BII-R1-HANDOFF.md
- docs/codex/tasks/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A-PHASE-BII-R1-ADAPTER-FAIRNESS-REPAIR.md
- scripts/env_headroom_probe/adapters.py
- artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/borrowed_adapter_manifest.json
- artifacts/BORROW-FIRST-ENV-SELECTION-AND-HEADROOM-PROBE-001A/failure_manifest.json

Then perform only the explicitly authorized next step. If Claude Red-audit has
not passed, do not start B-iii.
```

## Next minimal closed-loop action

Hand `fc2f0401c62c285259a2d64add97dac24dc94e7e` plus this handoff to Claude for
Red re-audit. Only after Claude Red-audit passes and the operator explicitly
authorizes a new card should Codex consider any Phase B-iii candidate action.

## What this handoff does not prove

This handoff does not prove borrowed-env headroom, candidate validity, probe
validity for candidates, learning, transfer, agency, autonomy, subjectivity,
consciousness, EGO readiness, production readiness, or mainline effect.
