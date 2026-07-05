# SESSION-HANDOFF-FSP-20260704B

Scope: FSP-PUM-ENV-IDPROBE-001A **S3d** (should-win + NULL-env instrument). Successor to
`SESSION-HANDOFF-FSP-20260704A`. Claude role = independent auditor / red-team (implementation by
Codex, banking by operator). Claim ceiling unchanged: bounded offline mechanism evidence only.

---

## 0. CURRENT STATE (read first)
- HEAD = **`a0a211f`** (S3d PART0 CPU-time re-gate banked). Branch `codex/meta-theory-scaffold`.
  Parent = `c0c6bf4` (001B impl). Remote pushed: `f2c0b3a..a0a211f`.
- What just happened this session: the full battery was launched under 001B/L=30. Its PART-0 preflight
  **STOPped** (`STOP_s3d_part0_projection_exceeds_line`, wall projection 32.007 > 30). Claude audit
  found the STOP was decided on the **wrong metric** (wall-clock, not the exec-card-mandated per-unit
  CPU-time = **B1**). Codex re-computed the gate in CPU-time (standalone runner): **22.297 CPU-h ≤ 30
  = within_line**. That re-gate + the preserved wall-gate STOP are what got banked at `a0a211f`.
- **The battery never actually ran its units.** No S3d certificate / NULL result exists yet.
- **ONE open blocker = BL1** (below). The CPU-time fix lives only in a *standalone* runner; the real
  launch path (`s3d_battery_runner_line30.py` preflight) is still wall-gated. Fix BL1, then the battery
  is a separate authorized task.
- BL2 (host JSON cleanliness / preservation) is **RESOLVED** — host verify PASS; the NUL padding I saw
  was a FUSE-stale sandbox artifact, host files clean. Throwaway `bl2_host_verify.py` sits untracked in
  repo root; `Remove-Item bl2_host_verify.py` to delete.

## 1. IMMEDIATE NEXT ACTION
Hand Codex the **BL1 fix prompt** in §2 (port the CPU-time projection+gate into the canonical battery
runner's preflight, as a single shared routine, proven by a discriminating test). Precondition is
satisfied at HEAD `a0a211f` (regate runner banked; 001B signed@`8dd8675`+banked@`c0c6bf4`; L=30
signed@`f186364`). The prompt hard-codes no HEAD; Codex reads current HEAD (`a0a211f`) to pin its
bank-ops proposal. Then Claude audits (§3) before any bank. Battery full run = a further separate task
after BL1 is audited and banked.

## 2. BL1 Codex prompt (rule source = 001B + BATTERY-EXEC-001A; conformance repair, no science change)
```
角色: FSP lab executor(Codex),只实现本卡,不做治理判断、不跑 git、不跑 battery。

先完整读(read-only,禁改):
- docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A.md(§process parallelism 74–80 行 = 闸门度量强制:line/gate/guard 用 per-unit CPU-time〔process user+sys〕,"逼近 L 先串行隔离重测主导单元再 STOP";gate 行为不变 = "projection > L → STOP")
- docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001B.md(冻结规则源;DELTA3 声明 s3d_battery_runner_line30.py 为 canonical runner)
- docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-BUDGET-DECISION-001A.md(L=30 已签)
- artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_cputime_regate_runner.py(已审计通过、已 banked@a0a211f 的 CPU-time 投影+主导单元串行重测逻辑 = 本次要移植的参考实现)

问题(Claude 审计 BL1):CPU-time 修复只在独立 regate runner 里;真正发射路径 s3d_battery_runner_line30.py 的 preflight 仍调 wall 基 _run_part0_projection_line(line 715 `ideal["wall_clock_seconds"]*160/3600`;family/sklearn 成员不记 process_cpu)并在 line 285 用 wall 求和判闸。用此 runner 发射 battery 会重触 B1(竞争时抽 ~32→假 STOP,空闲时抽 ~22→过,非确定)。runtime guard(line 942/946 用 process_cpu_seconds)已正确,不动。

前置门(不满足→写 failure manifest 并 STOP):001B 已签且 banked;L=30 已签;s3d_part0_cputime_regate_runner.py 已 banked(HEAD a0a211f)。

任务(仅把发射路径 preflight 改为 CPU-time 合规;单一逻辑路径;禁改任何 certificate/NULL 评分):
1. 把 CPU-time 投影+判闸+主导单元串行重测的**投影数学**抽成一个**共享函数**,放进 canonical 文件 s3d_battery_runner_line30.py(DELTA3 已声明其 canonical);函数输入 = 各单元 measured wall & process_cpu 秒 + units,输出 = CPU-h 总额、wall-h 总额(disclosed)、逐单元 wall/CPU>1.25 flag、gate relation。s3d_part0_cputime_regate_runner.py 改为**调用同一函数**(不得保留第二份投影数学)。
2. battery runner 的 _run_part0_projection_line 为**每个**投影单元补记 per-unit process CPU-time(prefix-family 全成员 / sklearn / GRU / bootstrap;现仅 generation+ideal 有),仅在现有测量外层加 time.process_time() bracket,不改任何 fit/score/度量数值。
3. preflight 用该共享函数,`projected_cpu_hours` 字段语义改为 **CPU-h 总额**;line 285 判闸不动(`if projection["projected_cpu_hours"] > applied_line → STOP`),现在即按 CPU-h 判。保留 wall 总额为 disclosed 字段。
4. 逼近 L(按 regate 已审的同一 margin/逻辑)时,对主导单元(ideal / nearest_neighbor / discounted_LS)串行隔离重测再判 STOP;heldout 800–999 禁触,重测取 fit/val 域用户。
5. gate 行为、L=30、ρ 阈值、strength 3.2、guard k=5、member set、NULL MDE、spec 一律不变;不新增 test-only 逻辑路径;runtime guard 不动。

判别测试(必写,钉死 B1 且可证伪,tests/fsp_pum_env/ 下):
- T1(共享函数确定性):喂**固定** measured 秒,断言 CPU-h 总额、wall-h 总额、gate 判定逐位可复算;断言 regate runner 与 battery runner 调同一函数得**完全相同**输出。
- T2(B1 杀手测试):构造一组 measured 秒使 **wall 求和 > L 且 CPU 求和 ≤ L**,断言 preflight 判 within_line **不 STOP**;再构造 CPU 求和 > L,断言 STOP。
- T3(instrumentation):断言 _run_part0_projection_line 产出的每个投影单元测量 dict 均含 process_cpu_seconds 键(prefix-family/sklearn/gru/bootstrap 全覆盖)。

硬约束:禁改 certificate/NULL 评分 helper(macro_balanced_accuracy 等)——只动 PART-0 成本投影计时+判闸;禁改 fit/score 数值;禁跑 battery(本卡不产 result.json/battery 工件/projection 实测文件);禁 git;禁碰 heldout 800–999;保全 wall-gate STOP 证据与 *_wall_gate_noncompliant_v1 副本不删不 patch;任何新写 JSON 必须整文件截断写(open 'w')并对**磁盘字节**做 strict json.load round-trip 自校验、断言无尾随 NUL/空白(防复发 NUL 填充缺陷)。

必产:
- 改动 s3d_battery_runner_line30.py(共享投影函数 + preflight CPU 判闸 + 全单元 CPU 记录 + 串行重测)
- 改动 s3d_part0_cputime_regate_runner.py(改调共享函数)
- 新/改 tests/fsp_pum_env/ 测试(T1/T2/T3)
- 修复卡 docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-CPUTIME-LAUNCHPATH-001B.md(task id/problem/hypothesis/baseline=wall-gate preflight/ablation=去掉 CPU 记录退回 wall 应复现 32.007 型 STOP/trace-replay=T1-T3/acceptance/claim ceiling/stop/rollback=还原 preflight 到 wall 版、science 零改)

新鲜度自证:每改动/新文件 sha256 + 行数 diff 摘要 + py_compile + pytest 数(含 T1/T2/T3 全绿)+ "certificate/NULL 评分逐位不变"断言 + "single projection routine(regate 与 battery runner 同源)"断言 + "battery 未运行" + "heldout 未触" + "banked/保全工件字节不变(host 待核)"。

claim ceiling:至多「发射路径 preflight 已合规于 CPU-time 度量、B1 在发射路径亦修复(经 T2 判别测试)」;不含 battery/certificate/NULL 证据;不升级为环境有效性/gap/机制/agency/EGO。

完成后停下(禁自 bank),产 operator bank-ops 提议(HEAD-pin a0a211f + git reset -- + allowlist〔仅本卡改动的 code+tests+修复卡〕+ staged 计数等值 + 零删除 + 逐文件 Get-FileHash + scoped `git commit -m <msg> -- <paths>` + 无 push),报告贴回 Claude 审计。battery 全量运行 = 审计+bank 后的独立授权任务,不在本卡。
```

## 3. BL1 audit checklist (when Codex returns — do NOT trust the summary)
- **Single projection routine**: the CPU-h projection+gate math exists in exactly ONE function (in the
  canonical `s3d_battery_runner_line30.py`); the regate runner calls it. No second/divergent copy.
- **T2 is the killer**: a test where wall-sum > L but CPU-sum ≤ L asserts **no STOP**; CPU-sum > L
  asserts STOP. This is the falsifiable proof B1 is fixed on the launch path. Confirm it exists + green.
- **Instrumentation (T3)**: every projection unit's measurement dict now carries `process_cpu_seconds`
  (prefix-family / sklearn / gru / bootstrap — not just generation+ideal).
- **Gate line 285 semantics**: `projected_cpu_hours` is now the CPU-h total; wall total disclosed
  alongside; gate behavior unchanged (STOP iff CPU-h > L; L=30 untouched).
- **No science drift**: certificate/NULL scoring helpers (`macro_balanced_accuracy`, etc.) byte-/digest-
  unchanged; only cost/timing touched. ρ thresholds 0.50/0.80/0.90, strength 3.2, guard k=5, 18-member
  set, NULL MDE all unchanged (would be governance self-mod).
- **Battery NOT run**; heldout 800–999 untouched.
- **JSON hygiene**: any JSON Codex writes is a truncating write with on-disk strict-parse self-check
  (no NUL-tail recurrence). Re-run `bl2_host_verify.py` after the bank if in doubt.
- **Bank-ops proposal**: HEAD-pin `a0a211f`, scoped allowlist (only BL1 code+tests+card), staged-count
  equality + unexpected-path throw + zero-delete, scoped `git commit -m … -- <paths>`, **no push**.

## 4. Commit lineage this session
- `c0c6bf4` — (session start) 001B impl banked.
- (battery run) wall-gate `STOP_s3d_part0_projection_exceeds_line`, 32.007 > 30 — the STOP artifacts
  were later preserved as `*_wall_gate_noncompliant_v1` (not banked separately).
- **`a0a211f`** — S3d PART0 CPU-time re-gate banked (17 files: regate runner + CPU-time projection
  `s3d_compute_projection_line30.0_cputime_regate.json` (22.297 CPU-h within_line) + fix card
  `…-S3D-PART0-CPUTIME-REGATE-001A.md` + claim_ceiling + result.json (within_line) + failure_manifest
  (normalized) + 10× `*_wall_gate_noncompliant_v1`). Pushed to remote. ← HEAD

## 5. The B1 story + the noise correction (the key caveat for the whole S3d budget gate)
The exec card (§74–80) mandates the line/gate/guard use **per-unit CPU-time** (contention-robust
realization of the spec's "threads=1 wall-clock"), and "if CPU-h approaches L, re-measure the dominant
units serially before any STOP." The battery runner gated on a **wall-clock sum** and never recorded
CPU-time for the dominant members — so the mandated gate was never evaluated (B1).

**But the decisive fact from re-running: the projection is timing-noise-dominated, not metric-dominated.**
Same computation, two runs: wall 32.007 (run 1) vs 22.426 (run 2) = **−44%**. The ideal unit's CPU-time
alone swung 56.6 → 40.6 → 38.8 s across measurements (−31%). The B1 wall→CPU correction was only ~0.6%
this run. So:
- **L = 30 sits *inside* the two-run projection band [22.3, 32.0].** Neither the run-1 STOP nor the
  run-2 GO is a robust gate decision — both are noise draws.
- Reported ±SE (ideal ±0.09 s, NN ±252 s) is **within-run across 3 users only**; it does NOT capture
  cross-run variance (NN cross-run 32% vs within-run 4%). Do not treat ±SE as the uncertainty.
- **Standing lesson**: CPU-h budgeting on a contended single machine is intrinsically ±40–140% noisy,
  and a single-sample projection ×1120 is a noise amplifier. **The PART-0 preflight is not a useful
  go/no-go instrument at L=30; the CPU-time runtime guard@30 (line 942/946, metric-correct) is the real
  cost control. Do NOT reflexively raise the line** — the issue is projection noise + a code-path bug,
  not the line value.

## 6. After BL1 is audited+banked: the battery task
- It will be a separate authorized task (operator budget-risk decision). Once BL1 makes the preflight
  CPU-compliant, the cleanest route is: **launch and let the CPU-time runtime guard@30 backstop it**
  (worst case it STOPs near 30 and returns to operator; a 2nd breach returns to operator, no auto-raise).
  Chasing a "clean" preflight pass = chasing noise.
- **Residual risk to flag**: the 001B FactoredExactFilter cert-cell coverage (constant-cell ideal +
  flat_theta + stable_facts) was validated only by the 001B-impl's own 6-cell tests, **never by a full
  battery run** (this session STOPped at PART-0 before cell execution; the prior `STOP_UNEXPECTED_EXCEPTION`
  on flat_theta/stable_facts was pre-001B). So the first real battery may still surface a cell-execution
  issue. If it does, that is a bounded negative (preserve + route), not a reason to weaken the spec.
- Battery acceptance/audit contract is unchanged from 20260704A §4 (per-member ρ vs per-cell ideal on
  the canonical banked-runner scorer; cell-validity guard k=5 on the ideal before member scoring;
  NULL-env metric ≤ chance+0.005 incl. ideal → any breach = FAIL_NULL_FALSE_HEADROOM all void;
  parallel bit-identical-to-serial on a sampled unit; replay reconstructs verdicts from trace).

## 7. Standing rules / lessons (carried + new)
- **CPU-h noise / don't-raise-line** (NEW, §5): the budget gate measures noise at these margins; the
  runtime guard is the real control.
- **FUSE-stale** (reconfirmed this session, Nth time): the sandbox's sha256 / byte view of a host-edited
  file can differ from the host (this session: sandbox saw NUL-padded result.json + wall projection
  690af9de; host was clean + 42be81db). **Host `Get-FileHash` / behavioral gates / `bl2_host_verify.py`
  are authoritative; the sandbox has no evidentiary force for host-edited files.**
- **JSON truncating write**: emit JSON with a full truncating write + on-disk strict-parse self-check;
  in-place shorter overwrites can leave stale tails.
- **Flat-signing scope** [[itl-signing-scope-flat-development]]: file-in signature + one scoped commit =
  the signature; separate authorize scripts only for the four load-bearing types (threshold/guard/
  claim-ceiling motion, budget-line raise, spec supersession). BL1 touches none of those (metric
  conformance only) → executor-safe, no new signature.
- **Preserve report generators + failure evidence**; `git commit -m <msg> -- <paths>` (`-m` BEFORE `--`).
- **Adjudicate only with the canonical banked-runner scorer.**

## 8. Repo hygiene debt (isolated from S3d; do NOT sweep into a task commit)
- ~13+ `M` files are EOL churn (autocrlf): AGENTS.md, docs/decision_log.md, several gate4/ctsr/
  action_conditioned artifacts, plus S2/S3 artifacts. The scoped bank-ops (allowlist + `git reset` +
  count/unexpected/zero-delete gates) keep these out of every bank. Worth a separate CRLF-vs-content
  cleanup pass; `git diff --ignore-cr-at-eol` distinguishes real changes from CRLF noise.
- Lingering dirty **STOP-era primaries** (s3d_certificate_report / s3d_null_env_report / baseline_
  comparison / replay_report / trace.* in their void form) were NOT banked at `a0a211f` (only their
  `_wall_gate_noncompliant_v1` copies were). Working tree stays dirty on those; harmless, reconcile when
  convenient.
- `git prune` still queued (too many unreachable loose objects warning on push).

## 9. Queue (after BL1)
- BL1 fix → Claude audit → operator bank → then battery full run (separate authorized task, §6).
- Track-T: rung1 LFS bank still partial (`2575d1a`); L-005 ledger entry pending.
- MPVL / borrowed-stack registry: design-only, queued.
- Repo hygiene pass (§8); `git prune`.

## 10. What none of this proves
No S3d certificate / NULL result (battery not run). The banked `a0a211f` proves only: B1 (wall-gate) was
a real bug; under the CPU-time metric this run's projection was ≤ L; the wall-gate STOP is preserved as
failure evidence. It does **not** prove the battery costs ≤ 30 (noise band straddles L), nor environment
validity, baseline power, gap, mechanism, learning, agency, EGO, or companion readiness.
Full detail in memory: `MEMORY.md` + `fsp-route-program-001a.md` (this session appended in full).
