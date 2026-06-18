# 独立敌意再审计：`ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-R1`

范围锁定、只读。审计任务 ID：`CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-R1-REAUDIT-001A`。日期 2026-06-16。

## VERDICT

**`accepted_for_bounded_local_candidate_harness_implementation_authorization`**

- **是否可立即开始实现：** 否。接受 R1 只意味着该任务卡是一个干净合同、唯一 blocker 已闭合、已接受的合同层未被削弱。bounded 本地 candidate harness 实现仍需**单独的 operator 激活卡** + 执行期实跑独立审计(卡 §0/§7/§26/§33/§34)。本次再审不授予实现授权。
- **是否仍有 blocking issue：** 无。
- **角色:** CLAUDE.md Same-Agent Bridge Audit Role 001 独立审计。全程只读:未改卡、未改源码/测试、未动 Gate/mainline/runtime/bridge/scheduler/admission、未 commit/push/tag/anchor、未触 PAT/secret。仅在 `artifacts/CLAUDE-INDEPENDENT-...-R1-REAUDIT-001A/` 写本审计自身的 evidence artifact。

---

## 关键取证:挂载截断,不是证据缺口(决定性环节)

B-1 的成败完全取决于 `docs/decision_log.md` 是否真含支撑条目。两个读取通道给出**冲突视图**,我据此判定哪个是 ground truth:

| 通道 | 行数 | 字节 | sha256 前缀 | 结尾 | 含 B-1 条目? |
|---|---|---|---|---|---|
| Shell/FUSE 挂载(bash/python/cp 一致) | 17 | 907 | `1d9e168c` | **第 18 行 anchor 值中途切断**:`- Anchor: ``remote-a` | 否 |
| 权威文件读取(file API → Windows D:\) | 152 | — | — | 完整 §条目至 line 151 | **是(line 133–151)** |

**判定挂载视图为截断假象(facts):**

1. 挂载版 907 字节是权威 152 行文件的**逐字节前缀**,在第 18 行 token 中途("remote-a" | 应为 "remote-anchor-acp-bv-...-98be7f4")被切断。真实的、完整撰写的 decision log 不会在单词中途结束;字节级前缀截断是缓存/挂载伪影的标志。
2. 挂载内 git 同时损坏:`fatal: bad config line 18 in file .git/config`——本 lab 反复记录的 FUSE/.git 损坏家族。
3. 挂载报 `decision_log.md` mtime 为 `2026-06-16 05:05`,**早于**同一挂载报告的 001A 卡(`2026-06-17 00:20`)与 R1 卡(`2026-06-17 00:40`);而该文件的权威内容**引用**了这两张卡。frozen-at-05:05 的文件不可能引用其后才生成的卡 → 挂载的 mtime 与内容均为陈旧缓存。
4. **对照控件:** 新写入的 R1 卡在挂载与 result.json 中 sha256 完全一致(`beccf262`),两张卡在挂载里也完整未截断(614/640 行,尾行均为 "than its preserved claim ceiling.")。即挂载并非全局失效——它只对**预存**的 `decision_log.md` 持陈旧/截断缓存(新文件首读即新鲜,预存文件的缓存未失效)。

结论:权威文件读取是 ground truth。我**未**把挂载的"条目缺失"当作 absence 证据(这正是 CLAUDE.md 明令禁止的"renderer/mount-visible behavior mistaken for causal evidence")。

---

## 范围 1 — B-1 decision-log 虚假闭合:**已修复(repaired)**

权威读取 `docs/decision_log.md` 第 133–151 行确有 §30 声称标题的条目:`Route C candidate-harness 001A/R1 hostile audit preservation / decision-log provenance repair`。其内容逐项与卡 §30 吻合:被审 001A 卡、保留 Claude verdict `requires_task_card_revision_before_candidate_harness_implementation`、B-1 为唯一 blocker、R1 只修该 provenance-integrity 问题、candidate/Gate/mainline/runtime/live/commit/push/tag/anchor 全不授权、claim ceiling、Auto-Remote-Anchor forbidden。

result.json `decision_log_supporting_entry.direct_readback_strings` 六条全部在权威文件中命中(对应条目 line 137/138/139/143/144/150)。

与前次的本质差异:前次 B-1 是"完成时态肯定式虚假闭合自报 + 文件无条目";本次条目**真实在场且内容匹配**,落到本 lab 的红线另一侧。该唯一 blocker 闭合。

**唯一残留(non-blocking caveat):** result.json 的 `sha256_after_entry = 9336E693...` 无法字节级复算——所有 shell/挂载读取只返回 907 字节截断前缀,故只能得到截断版 sha(`1d9e168c`),而非全文 sha。条目**内容**已由权威读取独立核验,因此这是一个"不可复核但未被证伪"的自证哈希,**不是**矛盾。建议下一层用非截断读取器复算并嵌入 producer provenance。按本次范围规则(非阻断项不升级为 blocker,除非 R1 自身新削弱或制造直接矛盾),不阻断。

---

## 范围 2 — 八个已接受合同层:**保留且未削弱(preserved without weakening)**

方法:`prior 001A 卡` 与 `R1 卡` 的 unified diff 在 **§7–§29 无任何 hunk**(逐字节相同);并用权威 Read 工具对两卡 §13–§21 交叉复核,逐字一致。前序审计已认定 001A 的这些段为 PASS,R1 未改 → 未削弱。

| # | 合同层 | 锚点 | 结论 |
|---|---|---|---|
| 1 | scope discipline | §0/§24/§25/§28/§31/§32 | 保留;**加强**(activation-status 与 §0 forbidden 新增 `commit`) |
| 2 | statistical noise-floor / CI binding | §13 | 逐字保留 |
| 3 | margin & saturation failability | §17 | 逐字保留 |
| 4 | access parity | §16 | 逐字保留 |
| 5 | RF-1 option-2 provenance closure | §18 | 逐字保留 |
| 6 | truth-seed isolation | §19 | 逐字保留 |
| 7 | passive + fair-interventional baseline families | §14(8 passive 超集 + `obs_only_family_max`)/§15(6 通用 + 6 graph-cache + `fair_interventional_family_max`) | 逐字保留 |
| 8 | evidence hygiene / replay / leakage / material-row provenance | §20 ablation / §21 replay-recompute / §22 leakage 12 类 / §23 material-row 13 字段 | 逐字保留 |

---

## 范围 3 — R1 是否引入新缺陷:**无**

- **新授权泄漏:** 无。§0/§30/§33 与 result.json 全部授权旗为 false(candidate / gate-mainline-runtime-live / source / tests / scripts / gate-runner / mainline-bridge-scheduler-admission / commit-push-tag-anchor 皆 false,auto_remote_anchor=forbidden)。
- **新虚假声明:** 无。当前唯一受检声明(§30 B-1 闭合)已由权威读取证实为真。
- **削弱 failability:** 无。要求段逐字保留;且 R1 把 `commit` 加入 forbidden = 加强。
- **scope 扩张:** 无。§24 未来 allowlist 仍为 4 条路径;06-17 工作窗仅触及 `artifacts/**`、`docs/research/**`、`docs/decision_log.md`(allowed),`src/`、`tests/` 零改动。
- **§35 新增处理得当:** 把前 3 条 non-blocking note 显式降级为"future-activation 考量,非当前实现证据",是正确降级,非 scope creep。
- **governance self-modification:** 无。R1 是前向合同,未改判它的 protocol/schema/baseline/failure-taxonomy/evidence-schema;decision-log 条目是 preservation 记录,非规则变更。

---

## blocking / non-blocking / required fixes

- **Blocking:** 无。
- **Required fixes:** 无(B-1 已修;前次的 REQUIRED FIX 已按"真加 bounded 条目"路径完成)。
- **Non-blocking(带入执行卡,不阻断):**
  1. `sha256_after_entry` 自证、不可经截断挂载复核 → 下一层用非截断读取器复算 + 嵌 producer provenance。
  2. 三条 carry-forward future-activation 考量仍待执行卡处理:钉最小 seed 数 + CI/噪声底法;对称命名 `clean_anchor_control.json`;final report 显式列 access-parity 结果。
- **是否可进入实现:** 否——需单独 operator 激活卡 + 执行期实跑独立审计。本卡作为干净前驱已就绪。

## What this does not prove

不证明未来 harness 会被授权实现、不证明任何 Route C candidate 可实现或会过任何 Gate、不构成机制/隐藏自集/自边界证据、无任何 mainline/runtime/live 效果,亦不证明任何既往 ACSB/ACOLB/Route C artifact 强于其 preserved ceiling。

## Sources

- `docs/research/ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-R1.md`(被审卡 §0–§36)
- `docs/research/ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A.md`(diff 基线)
- `artifacts/ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-R1/{result.json, card.md}`
- `docs/decision_log.md`(B-1 权威 readback,152 行视图)
- `artifacts/CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-HARNESS-IMPLEMENTATION-TASK-CARD-001A-AUDIT-001A/audit_report.md`(前序审计:B-1 + 八层来源)
