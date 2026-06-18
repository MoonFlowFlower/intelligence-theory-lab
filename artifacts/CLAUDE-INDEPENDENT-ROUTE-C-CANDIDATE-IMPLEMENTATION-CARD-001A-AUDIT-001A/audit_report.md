# 独立敌意审计：ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD-001A

## VERDICT

**`requires_implementation_card_revision_before_candidate_implementation`**

- 实现是否可推进（implementation may proceed）：**否（no）**
- 是否仍有 blocker：**是** — 两个（B4、B3 的 carry-through 弱化）
- RF-1 option-2 closure 是否足够强：**否** — 形状正确、实质改进，但"independence 锚"未定义、未绑定到 pre-run frozen pins，且未要求 positive control 攻击锚本身
- §6.3 fair-interventional saturation 风险是否被诚实约束：**部分** — 降级后果与"both-scored-high ≠ success"诚实写明，但 saturation gate 的 failability 未强制（无 demonstrated negative control 支撑）
- Layer：engineering-governance / implementation-card hostile audit only

我的角色（CLAUDE.md Same-Agent Bridge Audit Role 001）是独立审计，本次为该卡的**首次 in-repo 独立核验**（见下方 lineage 发现）。已只读核验卡的两份副本（artifact `card.md` sha256 `f9276bb7…`、research doc sha256 `e3d9eae9…`）+ result.json + 上游 AUDIT-001A / R1-REAUDIT-001A。未修改文件、未写 artifact、未实现、未运行 Gate、未触 push/tag/anchor、未触碰任何 PAT。

---

## BLOCKING ISSUES

**B-1 [BLOCK] B4 未被忠实重绑：margin/saturation gate 缺 demonstrated failing negative control。**
AUDIT-001A 的 B4 明确要求：margin gate 须含一个 demonstrated failing negative control（合成 candidate 未过 frozen margin → gate 返回 `close_or_downgrade`），saturation gate 同理（fair baseline 饱和 candidate → `close_or_downgrade`），且"every material gate must ship a demonstrated failing negative control"。

字符串级证据：`"negative control" / "demonstrated" / "demonstrably" / "synthetic" / "failing"` 在两份卡里出现 **0 次**。卡只在 §12/§13 描述 gate 的**输出逻辑**，在 §16 把"B4 margin/saturation failability"列为**标签**，§23 acceptance gate **未**列入"margin gate / saturation gate 各自交付一个 demonstrated failing negative control"。

这是本 lab 头号复发崩溃族（"gate 结构上不可 fail"/"non-fail-able 字段复发"）。卡对 leakage（§20"callable scanner/probe that demonstrably detects the injected leak")和 forged-provenance（§14/§23"fails closed")**都**要求了可证伪的 control —— 唯独决定 candidate 成败的两个核心 gate（margin、saturation）没有。这是不一致的遗漏，不是风格选择。按卡自身 §24 stop condition，"weakens RF-1 through RF-4 / omits any B1-B5 requirement"即停止条件；任务 §6 也显式要求此项。

**B-2 [BLOCK] B3 未被忠实重绑：access-parity artifact 被丢弃。**
AUDIT-001A B3 要求"an access-parity artifact comparing candidate and strongest fair baseline intervention budget, API, observations, action space, state access, and update access"。卡中 `"parity"` 在 artifact 副本出现 **0 次**，research 副本仅 §8 叙述性提及一次（"once access parity is enforced"），**未**作为 §21 material row / §22 source pin / §23 acceptance-gate 的**必产 artifact**。卡保留了 §15(RF-2) 的 feature-impoverishment control（覆盖 mechanism component 维度），但 access parity 是**独立维度**（预算/API/观测/动作/状态/更新访问）。缺它，"candidate 胜 fair baseline"可被不对等访问权混淆 —— 即"candidate 被给了更多 access"。

---

## REQUIRED FIXES（修订后方可接受）

1. **修 B-1：** 在 §12/§13 与 §23 acceptance gate、§21 material rows 中明确要求两个 demonstrated failing negative control —— (a) 合成 candidate 落入 frozen margin → 必须 `close_or_downgrade`；(b) fair baseline（含 graph-cache 挑战者）饱和 candidate → 必须 `close_or_downgrade`。措辞对齐 §20 已有的"demonstrably detects"标准。
2. **修 B-2：** 把 access-parity artifact 列为必产物（§21 material row + §22 source pin + §23 check），逐项比较 candidate 与最强 fair baseline 的 budget/API/observations/action-space/state-access/update-access。
3. **修 RF-1 option-2（见下）：** 定义"independent source artifact"= §22 的 pre-run frozen+hashed source pin（在任何 candidate run 之前固定），并要求 co-forged positive control **专门伪造/别名化该锚**，使 gate 被最危险用例检验，而非易挡的弱伪造。
4. **修 N4：** 显式写出 truth-seed disjointness（truth/self-set seed 与所有 candidate、baseline observation seed 不相交）。现仅有 §20"truth-seed contamination"positive control + §22"truth seeds"frozen input + §16 标签；`"disjoint"` 出现 0 次。任务 §7 要求"truth-seed isolation is explicit"。

---

## 逐项核验结果

**RF-1 forged-provenance option-2（§14）— 结构齐全，但未达 airtight。**
到位：co-forged value+basis+inputs 自洽 positive control；inputs 须 pin 到 independent source artifact hash；rederive-basis 仅当 inputs source-pinned+independently hashed 才可采；self-declared 一致性不足；每个 material row 二选一（重执行 producer 比对 / rederive basis 并证明 inputs 未被 co-forge）；candidate-run material rows 在范围内、不下放 Gate。
残留洞：卡从未定义"independent"的含义，也未把它绑到 §22 pre-run frozen pins。§23 要求 positive control"fails closed"提供了 backstop —— **但前提是锚确实独立**；卡未要求 positive control 去伪造锚本身，故可能落入"弱伪造易挡、给出虚假信心"（同我此前 Phase 0 obs-baseline 必须真读 `handle_values` 的教训，及 EAV-001A 的 circular self-declared-digest bypass）。**结论：option-2 closure 形状正确、实质前进，但尚不可证为 airtight。**

**RF-2 pre-run mechanism-component lock（§15）— 通过。** 要求 `mechanism_component_spec.md` / `_lock.json` / `_lock.sha256`，minimal、independently specified outside candidate source、run 前 hash；feature-impoverishment control 使用该 pre-hashed component；candidate advantage 不得事后定义 component。符合要求。

**RF-3 independent anchoring B1-B5/N1-N4（§16）— 部分通过，且暴露 B-1/B-2。** 卡确实在正文**重述**了多数要求（N1→§7、B2→§10、B3/B5→§11、N2→§12/§22、B4→§12/§13、B1→§14、N3→§19、N4→§20/§22），而非仅指向 AUDIT-001A artifact —— 这一点满足 RF-3"不得只依赖 preserved artifact"。**但**该"独立重绑"是**有损的**：丢了 B3 access-parity artifact、丢了 B4 demonstrated negative controls。RF-3 正是为防止"用标签替代忠实重绑"而设；B-1/B-2 本质就是 RF-3 的忠实性失败。

**RF-4 diff hygiene（§17）— 通过。** 要求 `diff_name_status.txt` / `diff_stat.txt` / `forbidden_path_scan.json` / `changed_file_classification.json` / `git_status_before|after.txt`；逐项证明 src/tests/scripts/Gate/mainline/runtime/scheduler/bridge/product-admission/credential 是否被触；PAT hygiene 未解前 push/tag/remote-anchor 禁止。符合要求。

**Baselines（任务 §5）— 通过。** Passive family（§10）是 Phase 0 的超集，8 个 attacker 齐全（positional_first_k, mean, variance, correlation, pca_subspace, cross_episode, supervised, legal_field_membership），"additional 仅可 union"，`obs_only_family_max = max over union`。Fair-interventional family（§11）含 random / greedy info-gain / exhaustive legal query(same budget) / Bayesian-likelihood / lookup-imitation / direct optimizer + 全部 6 个 graph-cache（graph_lookup, transition_table, successor_map, count_table, fsm_planner, episodic_traversal），全部进 saturation judgment。

**STOP gates（任务 §6）— 框架诚实，failability 未强制。** §12"both-scored-high is not success"、§13 四条 close/downgrade 规则 + "STOP result is bounded negative evidence"、§8 falsifier、§25"do not tune margins or weaken the baseline"—— 降级后果与饱和风险被**诚实命名并正确绑定**。但因 B-1，gate 本身不被要求交付 demonstrated negative control，"每个 material gate fail-able"未满足。

**Evidence hygiene（任务 §7）— 多数到位。** §21 禁 literals/static dicts/self-report/unconditional clean/hand-filled JSON 并枚举 material rows；§19 replay 从 serialized state + legal history 重算、明确"stored-hash alone insufficient"、"tautological controls 不计 failability"、读 truth/evaluator-only/future/stored-verdict 则 fail closed；§20 leakage positive control 须 callable 且 demonstrably 检出。缺口仅 N4 disjointness 未显式（见 Required Fix 4）。

---

## NON-BLOCKING ISSUES

- **result.json 自报过头。** result.json 把 `B3`、`B4`、`RF_3` 全标 `"bound"`，但卡正文并未承载 B3 access-parity artifact、B4 demonstrated negative controls。这是 self-reported status 超出 artifact 实际内容 —— 在 governance 层即任务 §7"no self-report"的同型问题。外部观察者会看到：起草任务给自己丢弃的要求打了绿。修卡时应同步纠正该状态字段。
- **上游授权链为 preservation-only，非独立复现。** `AUDIT-001A` 与 `R1-REAUDIT-001A` 都自述"Audit/Re-audit source: operator-provided pasted text… Codex did not perform an independent re-audit"。即 B1-B5/N1-N4、RF-1..RF-4 及"accepted_for_candidate_implementation_card_drafting_only"裁决均源自 operator 粘贴文本的忠实保存，未在 repo 内独立复现。本次审计是该卡的首次独立 in-repo 核验。对 card-level 审计不阻断，但授权 lineage 立在"保存而非复现"的链节上，应记录在案。
- **provenance 小不一致。** result.json `docs_changed` 列出 `docs/decision_log.md`，但 decision_log 内未见任何 `ROUTE-C-CANDIDATE-IMPLEMENTATION-CARD` 条目。

---

## CLAIM CEILING

implementation-card hostile audit only。无 mechanism evidence、无 candidate evidence、无 Gate pass、无 mainline/runtime/live effect、无 agency/autonomy/consciousness/emotion/stable user benefit/EGO readiness。本审计不证明 Route C 机制有效，也不证明任何 ACSB/ACOLB 旧 artifact 强于其 preserved ceiling。

**What this does not prove：** 不证明卡修订后会通过、不证明候选可实现、不构成实现授权。修订须重新独立审计后，再由单独 operator 任务显式授权确切实现文件与范围 —— candidate 实现在此之前保持 forbidden。
