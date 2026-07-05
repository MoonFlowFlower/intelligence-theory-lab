# SESSION-HANDOFF-FSP-20260704A

Scope: FSP-PUM-ENV-IDPROBE-001A **S3d** (should-win + NULL-env instrument). Successor to
`SESSION-HANDOFF-FSP-20260703C`. Claude role = independent auditor / red-team (implementation by
Codex, banking by operator). Claim ceiling unchanged: bounded offline mechanism evidence only.

## 0. CURRENT STATE (read first)
- HEAD = `c0c6bf4` (001B implementation banked). Branch `codex/meta-theory-scaffold`.
- The S3d instrument was found defective mid-run and **repaired via a signed successor spec (001B)**.
  Instrument is now executable. **The only thing left is to run the full battery under 001B.**
- Working tree shows several `M` on the 001B files (`factored_filter.py`, `s3d_battery_runner_line30.py`,
  `s3d_001b_impl_*`) — these are **EOL churn** (autocrlf), content is committed at `c0c6bf4`. Not real
  changes. (See §6 hygiene debt.)

## 1. IMMEDIATE NEXT ACTION
Run the full S3d battery under 001B. Hand the battery Codex prompt (below) to Codex; its precondition
now passes (001B signed@`8dd8675`, 001B impl banked@`c0c6bf4`, L=30 signed@`f186364`). Then Claude
audits the result (§4 checklist) before any bank.

Battery Codex prompt (rule source = 001B, NOT 001A):
```
角色: FSP lab executor(Codex),只实现本卡,不做治理判断、不跑 git。
先完整读(read-only,禁改):
- docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A.md(执行卡)
- docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001B.md(当前冻结规则源=001B,supersedes 001A;18成员/ρ阈值/k×SE guard k=5/canonical scorer)
- docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md(L=30 已签)
前置门(不满足→写 failure manifest 并 STOP):001B §7 已签且已 banked;001B 实现已 banked(HEAD c0c6bf4);L=30 已签。规则源用 001B。runner guard 已是 k×SE(k=5),别再改。
跑全量 S3d should-win + NULL-env battery(001B):18 成员 cert(每成员 ρ vs per-cell ideal 锚,canonical scorer=banked runner,ρ≥各自阈值 0.50/0.80/0.90)+ 2 cert-only 变体 + BASE-invariance + NULL-env(每成员含 ideal,metric≤chance+0.005)+ cell-validity guard(ideal−chance≥k×SE,k=5,在 ideal 上先于 member 算)。
硬约束:不改 spec/ρ/strength 3.2/member set/guard k;进程并行(每 worker threads=1、不超订、GPU 关);CPU-h 用 contention-robust process CPU-time;PART0 在 L=30 下重门(写新 projection 文件,>30→STOP);runtime guard >30→STOP、二次越线回 operator;禁 git;禁碰 heldout 800-999;banked 工件字节不变;失败保留不 patch;NULL false-headroom→FAIL_NULL_FALSE_HEADROOM 全 void。报告生成器保留为工件(别用即弃 temp 脚本)。
必产(artifacts/FSP-PUM-ENV-IDPROBE-001A/):s3d_certificate_report.json、s3d_null_env_report.json、result.json、trace.jsonl/csv、baseline_comparison.json、ablation_report.json、replay_report.json、失败则 failure_manifest.json、claim_ceiling。
新鲜度自证:每新工件 sha256 + wall-clock + 总 contention-robust CPU-h + N + 逐成员 ρ 与 CI + 逐 cell guard + 「banked 工件字节不变」核对 + py_compile/pytest 数。
claim ceiling:至多「line 30、001B 冻结契约内的 S3d should-win + NULL-env instrument 证据」;不升级为环境有效性/gap/机制/agency/EGO。
完成后停下,产 operator bank-ops 提议(HEAD-pin+reset+allowlist+staged 计数+零删除+逐文件 Get-FileHash+scoped `git commit -m <msg> -- <paths>`+无 push),报告贴回给 Claude 审计,再由 operator bank。不要自行 bank。
```

## 2. Commit lineage this session (80bfad4 → c0c6bf4)
- `17cce05` — S3d PART0 projection STOP >12 CPU-h (pre-registered budget line breached; banked negative).
- `086e948` — variance-probe bank (cross-run timing noise 38–140% dominates; two full estimates 19.25 & 17.09 both >12 → STOP robust).
- `f186364` — authorize B: **signed** budget line-raise (leo, L=30) + battery exec card.
- `66a4738` — battery line30 STOP artifacts (battery ran, `STOP_UNEXPECTED_EXCEPTION`: FactoredExactFilter raised on flat_theta/stable_facts).
- `8cd95a0` — ideal-variant repair (flat_theta+stable_facts) + stable-fact recommend diagnostic.
- `75ff55d` — cell-headroom pre-check (found the instrument defects → triggered 001B).
- `8dd8675` — **001B signed** (leo; guard 2a k=5; firewall ack).
- `c0c6bf4` — **001B implementation** (constant-cell ideal + k×SE guard + canonical scorer). ← HEAD

## 3. Why 001B exists (the instrument defect story)
The banked cell-headroom pre-check (`s3d_cell_headroom_precheck.json`, cert-faithful banked-runner
scorer) showed the frozen 001A instrument was **not executable**:
1. `constant_none`/`constant_saturated` — `IDEAL_MISSPEC`: the exact filter silently fell through to
   θ-tables on the constant cert variants (ideal ≈ chance).
2. `camouflage_off` (S2-validated central cell) — exact ideal `0.0966` (= banked `0.09948`), headroom
   `0.065 < 0.10`: the 001A `≥0.10` cell-validity guard was **unreachable by the optimal predictor**.
3. recommend-scope metric was scorer-sensitive (`0.0586` old inline vs `0.1363` banked runner, 2.3×);
   canonical scorer never pinned.
Correction: caught a wrong prior conclusion — the earlier stable-fact diagnostic (`0.0586`, non-cert
inline scorer) had labelled stable_facts "defective"; the cert-faithful pre-check (`0.1363`) shows it
VALID. Lesson: use the banked cert-runner scorer, not ad-hoc inline scorers.
001B (signed, banked) fixes all three: DELTA1 ideal models every cell (constant cells added, generative-
derived, anti-leak verified); DELTA2 guard → `ideal−chance ≥ k·SE_cell`, k=5 (firewall: on the ideal,
before member scoring; ρ thresholds & strength 3.2 untouched); DELTA3 pins the banked runner scorer,
voids the old one, fixture-verified. 001B-impl audited ACCEPT (all 6 cells pass k=5; constant ideal=1.0;
camouflage 0.09948 regression exact; protected artifacts byte-unchanged).

## 4. Battery audit checklist (when Codex returns the battery result)
Verify, per 001B, do NOT trust the summary:
- Precondition really passed (001B signed+banked, impl@c0c6bf4, L=30) — not spoofed.
- Each of 18 members: ρ = (member−chance)/(ideal−chance) on the **canonical (banked-runner) scorer**;
  rag uses recommend-turn-conditional; PASS = ρ ≥ pre-registered threshold (0.50/0.80/0.90); bootstrap
  95% CI reported (frozen bootstrap stream).
- cell-validity guard: `ideal−chance ≥ 5·SE_cell` computed **on the ideal before member scoring**
  (firewall); every cell passes or STOP `s3d_cell_headroom_defect`.
- NULL-env: metric ≤ chance+0.005 for every member incl. ideal; any breach = FAIL_NULL_FALSE_HEADROOM,
  all S3d void.
- Anti-tuning red-team: `strength=3.2` and ρ thresholds byte-unchanged; guard not moved; no member/scorer
  swap; canonical scorer = banked runner not a reinvention.
- PART0 re-gate ≤ 30 (contention-robust CPU-time); runtime guard; parallelism no-oversubscribe threads=1
  GPU off; results bit-identical to serial on a sampled unit; banked artifacts byte-unchanged; replay
  reconstructs verdicts from trace.
- Report generator preserved as an artifact (not a removed temp script — recurring Codex lapse, §5).

## 5. Standing rules / lessons established this session (also in memory)
- **Flat-signing scope** [[itl-signing-scope-flat-development]]: file-in signature + one scoped commit =
  the signature; NO separate authorize scripts. But signatures are RETAINED for the four load-bearing
  change types: threshold/guard/claim-ceiling motion, budget-line raise, spec supersession.
- **FUSE-stale**: the sandbox's sha256 of a host-edited file can be STALE; host `Get-FileHash` /
  behavioral gates are authoritative (bit us on `factored_filter.py`: sandbox `0e367149` vs host
  `31ee442c`). For provenance of edited code, trust host hash + re-run gates on-disk, not the sandbox.
- **Preserve report generators**: Codex twice used throwaway `*_tmp.py` report scripts then deleted them,
  leaving reports not exactly replayable. Require the generator to be a preserved artifact.
- **git commit arg order**: `git commit -m <msg> -- <paths>` (`-m` BEFORE `--`; the reverse makes `-m`
  a pathspec).
- **Causal-claim / scorer discipline**: adjudicate only with the canonical banked-runner scorer.

## 6. Repo hygiene debt (isolated from S3d; diagnose separately, not blocking)
`git reset` surfaced ~13 unrelated `M` files (AGENTS.md, docs/decision_log.md, several
gate4/ctsr/action_conditioned artifacts) — almost certainly EOL churn (autocrlf) plus AGENTS.md's
pending anti-commentary line. Scoped banks have stayed isolated from these. Worth a separate cleanup
pass (git diff to separate real changes from CRLF noise); do NOT sweep them into an S3d commit.

## 7. Queue (post-battery)
- Bank the battery result (after Claude audit) → S3d verdict → route per outcome (all-pass = S3d
  should-win instrument evidence; any member FAIL / cell-defect = bounded negative + route decision).
- Track-T: rung1 LFS bank still partial (2575d1a); L-005 ledger entry pending.
- MPVL / borrowed-stack registry: design-only, queued.
- Repo hygiene pass (§6).

## 8. What none of this proves
No S3d certificate/NULL result yet (battery not run). No environment-validity, baseline-power, gap,
mechanism, learning, agency, EGO, or companion claim. 001B is a corrected instrument, not evidence.
Full detail in memory: `MEMORY.md` + `fsp-route-program-001a.md` (this session appended in full).
