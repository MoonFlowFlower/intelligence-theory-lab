# CLAUDE-INDEPENDENT-EVIDENCE-AUDIT-GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001C

Task ID: GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001C-NEGATIVE-AUDIT-PRESERVATION-AND-001D-REPAIR-CARD-001A

Mode: Evidence-governance preservation only.

Layer: Gate4 replacement negative-evidence preservation and targeted
repair-card drafting. This document does not authorize 001D implementation,
Gate5, admission, bridge, runtime, EGO-mainline, UI, LLM, AIRI, relationship,
emotion, deployment, or external services.

## Preservation Status

The Claude independent audit verdict is preserved as negative evidence:

```text
B — blocked_split_design_leakage_not_repaired
```

001C local pass artifacts are invalid for positive replacement-Gate4 use. The
001C candidate commit may be used only as a blocked evidence record and as the
source for a targeted 001D feedback-leakage repair card.

## Core Preserved Blocker

- `query_feedback = "prefers:{target}"` carries the target verbatim.
- The candidate extracts the target through `split(":")[1]`.
- The scanner defines feedback leakage patterns but scans only the observation
  bundle.
- `trace_records.jsonl` contains `prefers:<action>` while `leakage_report.json`
  says `clean`.
- Candidate score equals oracle positive control.
- No query-and-follow-feedback baseline is present.

## Verbatim Claude Audit

```text
# 独立否定审计最终报告
**任务**: CLAUDE-INDEPENDENT-EVIDENCE-AUDIT-GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001C-LEAKAGE-REPAIR
**模式**: 只读独立否定审计(未修改任何源/测试/工件;未 push;未 tag)

## Verdict
**B — `blocked_split_design_leakage_not_repaired`**

001C 没有结构性修复 001B 的 split-design 观测-目标泄漏。它把携带目标的信号从观测字段 `baseline_hint` **改名并搬迁**到反馈通道 `query_feedback = "prefers:{target}"`,只发给 candidate(baseline 一律拿不到),并把所有泄漏检测装置(scanner bundle、observation-only decoder、recoverability check、positive control)的扫描范围都圈定在**观测面**上——恰好绕开了真正承载答案的通道。candidate 在行为上等同于 oracle label-access 正控。

## 核心证据(机器可复算,非依赖 result.json)
决定性矛盾,逐字节可验证:

- `core.py:250` `query_feedback=f"prefers:{target}"` → 反馈通道逐字携带目标。
- `core.py:419-422` candidate 做 `feedback.value.split(":",1)[1]` → 直接取出目标;`choose_final_action` 原样输出(`:440`);`score=1.0` 按构造必然成立(`:479`)。
- `core.py:67` scanner 自己把 `prefers:direct_response / …` 定义为 "feedback value leakage"。
- `core.py:834-845` `build_raw_observation_bundle` 只装 `episode.observation`,**从不装 feedback**。
- 实测:`trace_records.jsonl` 含 **56 条** `prefers:<action>`(candidate 自己的决策记录里全是泄漏模式),而 `leakage_report.json` verdict = **"clean"**。扫描器对真正的泄漏通道结构性不可见。
- candidate **1.0** == `oracle_label_positive_control` **1.0**;`observation_only_majority` 0.25,`random_cycle` 0.268。candidate 就是套了 `query_feedback` 名牌的 oracle。
- 消融与此完全自洽且只能佐证泄漏:`no_active_query` 0.25 / `shuffled` 0.0 / `counterfactual` 0.0 / `corrupted` 0.25 —— 这正是"反馈即答案"的特征,无法把"反馈=答案"和"反馈=可推断信号"区分开。

与 001B 对照:001B 因 `baseline_hint=target+1`(观测面、`hint_inverter`=1.0)被 block;001C 改成 `query_feedback=target`(反馈面、`split(":")` 取出)。泄漏更直接,只是搬了家并让检测器看不到新家。`repair_delta_from_001b.json` 自陈 "removed baseline_hint from the real observation surface" + "made candidate success depend on active-query feedback update" —— 后一句正是泄漏搬迁本身。

## 源状态 Readback
- current branch: `codex/meta-theory-scaffold`
- HEAD: `fec4b7f8847c26116918ee9871851543515fdd6a`
- parent: `e4b2f180a8a9643fc6fb45383855051ec8d4c310`(与声明的 sealed boundary 一致)
- HEAD == 目标 commit:**是**
- ahead of origin:**是,领先 1 commit,未 push**(`0 1`)
- git status:工作区索引显示 FUSE 挂载产物(null-sha1 cache、index.lock 不可删、deleted/unmerged 条目),**非本 commit 内容**;`git diff parent..HEAD` 纯增量(24 文件 / +70140 / 0 删除),全部在 `001c` 路径下
- 旧 001B / 旧 Gate4-001C 路径被改:**否**(git 增量,旧目录 0 字节变化)
- Gate5 / admission / bridge / runtime 文件被改:**否**(唯一 `001b` 命中是新增的 `repair_delta_from_001b.json` 报告,非旧文件改写)

## 复算结果
- 命令:`pytest test_…_001b.py test_…_001c.py -q` → **24 passed**;`python -m …_001c` → exit 0(在 `/tmp` clone 内运行,不污染挂载)。
- 工件复现:20 个工件中 **18 个逐字节一致**;12/12 实质证据工件(candidate / baseline / decoder / independence / ablation / replay / leakage / leakage-PC / threshold / active-query / provenance / result)**全部字节一致**。
- 2 个差异均为环境/自指,非阻断:`source_pin_readback.json`(`observed_head` 因 clone 检出在 commit 本身、作者运行在 commit 之前;结构性自指,与历史 001E 审计同类非阻断)、`non_mutation_guard.json`(运行时对受保护路径重新哈希)。
- 指标是否真实计算:**是**。provenance 把每个家族绑定到可调用 producer 的 `code_path_hash` 并拒绝 static injection;无常量/静态字典/硬编码期望值;非"仅测试断言 pass"。

## 各维度读数
- candidate score: **1.0**(按构造必然)
- strongest ordinary non-oracle baseline: **`random_cycle_baseline` 0.2679**(16 个 baseline 含全部强制 graph-cache 挑战者 graph_lookup/transition_table/successor_map/count_table/fsm_planner/episodic_traversal,但**无一**能用 query/feedback 通道)
- observation-only decoder: **`full_lookup_table` 0.25**(全部 29 个 single/pairwise/full 特征均 0.25 = 4 类随机基线)——观测面**确属干净**,decoder 本身**真强**(注入 target_label/baseline_hint 时正控达 1.0)
- leakage scanner: clean;positive control detected = true,**但只向观测 bundle 注入泄漏**(`:868-887`),从不向 feedback 路径注入 → 正控与真实泄漏面脱节(命中任务 §4 阻断项)
- ablation: 真实重跑(`run_candidate_on_episode(intervention_id=…)`,非事后贴标签)
- replay: 真实重算(`update_from_feedback`+`choose_final_action` 重算并比对,corrupt_state/feedback/observation 三个 fail-able 控制必须 mismatch)
- provenance: 真实(producer 哈希绑定 + 拒绝 static 注入)
- old-artifact non-mutation: **确认未改写**(git 增量;001B blocked-routing 记录保留,verdict 仍为 `gate4_replacement_001b_blocked_split_design_failure_preserved`)

## Blocking issues(阻断)
1. **(主因)反馈通道 = 逐字目标标签**,candidate 独占,所有泄漏检测被圈定在观测面 → split-design 泄漏未结构性移除,仅改名搬迁(任务 §3)。
2. **leakage 正控与真实输入 schema 脱节**:正控注入观测 bundle,真实泄漏在 feedback_history;扫描器对 feedback 通道在原理上 non-fail-able(任务 §4)。
3. **baseline menu 在关键维度仍弱**:缺"query-and-follow-feedback"基线。补上它会与 candidate 同为 1.0,直接暴露 baseline 等价性。这是把泄漏伪装成机制优势的使能条件(任务 §5,等价 C)。

## Non-blocking issues
- `source_pin_readback.json` 运行前/后自指不可复现(结构性,非阻断)。
- `non_mutation_guard` 运行时重哈希在异环境不能复现自身记录值;权威非改写证据是 git 增量,故仅记为自洽小瑕疵。
- 测试与代码**工程质量高、诚实**(强制了 leaked-decoder / budget-disparity / replay-corruption / static-injection / oracle-failure 等失败路径)——本案不是造假或 patch-to-pass,而是**真实可复现的证据忠实地记录了一个被搬迁的泄漏**,且检测装置被圈定到看不见它。这是设计/概念失败,不是完整性失败。

## Required fixes(供后继任务,审计不实现)
最低成本方向二选一:(a) 让 feedback 非逐字、含噪/部分,使"照搬 stated preference" < candidate,逼出多次 query 的真正整合,并把 query-and-follow-feedback 纳入 baseline;或 (b) 若"单次 stated preference→action"确为目标机制,则补该 baseline 并按 **baseline 等价**出否定/等价结论(而非 pass)。同时把 feedback_history 纳入 scanned bundle 与 recoverability 面,并增加针对 feedback 路径的泄漏正控。

## 是否可进入 remote-anchor 任务
**否。** 不满足 A 的前提。

## Stop conditions triggered
§3 观测-目标泄漏(反馈通道直含目标);§4 正控与真实 schema 脱节;§5 baseline 缺关键挑战者。三项独立触发,verdict 收敛于 B。

## Claim ceiling(本审计自身)
本审计仅产出:在该有界 toy harness 内,001C **观测面**泄漏确已移除且观测-only decoder 为真,但**反馈通道携带逐字目标且所有泄漏检测被圈定到观测面之外**,故 001B 的 split-design 泄漏未被结构性修复。

## What this does not prove(本审计不证明)
不证明该实现存在造假/篡改(恰相反,证据诚实且可复现);不证明 001C 完全无价值(观测面平衡是真实局部进展);不对 replacement Gate4 一般有效性、Gate5/admission/bridge/runtime 就绪、social agency、selfhood、consciousness、real emotion、stable autonomy、user benefit 作任何判断。

---

一句话:**001C 把答案从观测字段挪进了 feedback 通道,再把检漏仪对准了观测字段。candidate 的 1.0 不是推断社会潜变量,而是 `split(":")[1]` 读出被递过来的标签——它和 oracle 正控是同一个东西。建议 verdict B,不可进 remote-anchor。**
```

## Routing Implication

The preserved audit blocks positive 001C use. The next allowed action is only:

```text
draft_targeted_001d_feedback_leakage_repair
```

No remote anchor, tag, push, Gate5, admission, bridge, runtime, or EGO-mainline
authorization is allowed by this preservation document.

## Claim Ceiling

001C negative audit was preserved, and a targeted 001D repair card was drafted.

No stronger claim is authorized.
