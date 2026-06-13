
`CLAUDE-INDEPENDENT-AUDIT-DRAFT-FUTURE-EXECUTABLE-GATE4-DESIGN-CARD-001A`

## 1. Verdict

`claude_independent_audit_draft_future_executable_gate4_design_card_001a_blocked_requires_revision`

## 2. Layer

`engineering-governance / independent design audit only`(本审计不产生机制证据,不实现代码,不运行实验。)

## 3. Source verification readback

- Branch checked:`codex/meta-theory-scaffold`(从 `.git/HEAD` 读取,绕过 `.git/config` 第19行损坏)
- HEAD checked:`7685f9c735b416a814d70e032be5afd2f4b4f8f6`(`.git/refs/heads/codex/meta-theory-scaffold`)——**与任务卡声明的 sealed boundary 完全一致**
- Tag readback:`remote-anchor-draft-future-executable-gate4-design-card-001a-7685f9c → 7685f9c…` ✓
- Prior redesign boundary:`remote-anchor-gate4-task-family-theory-coverage-redesign-001a-e9d9969` tag 存在;draft 自身 `source_pin_readback.json` 把父边界钉在 `e9d9969`(其生成时 remote/local/tag 三方 exact_match)——与"draft 是 e9d9969 之后那一个 commit"一致 ✓
- Files inspected:draft 包全部 11 个文件 + `future_gate4_design_card.md`;prior redesign 8 个文件;002C `result.json`;002D `anti_zeno_check / closed_or_open_route_manifest / recommended_next_route / result`
- Files missing:**无**

事实/未验证项区分:本地 HEAD/branch/tag 三者一致指向 `7685f9c`(已验证);**remote 侧在 `7685f9c` 的封存我没有独立复核**(离线只读审计 + config 损坏,无法 `ls-remote`)。这是 non-blocking unknown,不影响判定。

## 4. Audit summary

**需要修订后才能作为下一步实现基线(needs revision before any implementation)。**

骨架是合格的:它正确地把问题从"再造一个更难的同族 toy POMDP"重构为"先定义一个让 shortcut 等价成为决定性失败的证据契约";leakage / replay / ablation / provenance / claim-ceiling 五项都达到可证伪标准,并真实修复了本谱系历史上的多个复发缺陷(non-fail-able scanner、ablation-clip 伪造、stub 喂入、whitelist 逃逸)。但在**唯一真正决定"未来 pass 是否有意义"的那条轴——baseline 覆盖 + 等价判定规则——上,draft 反而出现了相对其所继承的 sealed guardrails 的退化**。因此不能 pass。

## 5. Strongest objection

draft 读起来很严,但它的**绑定契约(machine-readable baseline_contract)是比它声称继承的 sealed `baseline_collapse_guardrails.json` 更窄的集合**:它静默删除了 `graph_cache_family`(项目规则强制、且本 lab 有 `graph_cache_collapse` 前科)和 `query_capable_imitation_baseline`,同时把 "tie / candidate-equivalent" 的数值边界留空。后果是:一个忠实照此契约实现的未来任务,完全可能让一个 `transition_table`/`successor_map` 捷径或一个脚本化 active-prober 达到 candidate-equivalent,却在事后口径下被判为"低于 candidate"——**重演一次 002C 级的 baseline collapse,而该契约不会捕获它**。draft 在所有地方都强,唯独在那条真正裁决"未来 pass 有没有含义"的轴上不够。

## 6. Fatal issues(真正的 blocker)

**F1 — Baseline 套件相对 sealed guardrails 退化:`graph_cache_family` 被整族删除**
- Evidence:sealed `artifacts/gate4_task_family_theory_coverage_redesign_001a/baseline_collapse_guardrails.json` 明列 `graph_cache_family`,`required_members = [graph_lookup, transition_table, successor_map, count_table, fsm_planner, episodic_traversal]`。draft `future_gate4_baseline_contract.json` 的 baseline_ids 中**无任何一个**;对整个 draft 包 grep `graph_cache|transition_table|successor|fsm_planner|episodic_traversal|count_table` 命中数为 0(只有散文 `DRAFT-…-001A.md:92` 一句 "graph/cache recovery",而绑定契约里没有)。
- Why it matters:`CLAUDE.md` 的 Preflight Audit Rule 明文规定 "graph-cache family challengers are **mandatory** when representational or environment claims are made"。本 draft 的目标恰恰做出表征/环境主张——其家族正是由 transition/successor/delayed-consequence 因果结构定义("delayed consequence depends on updated partner belief"),这正是 `transition_table`/`successor_map` 最易复原的结构。memory 中 Gate1 EXEC-001 已有 `graph_cache_collapse` 前科。删掉它 = 把最危险的挑战者从契约里拿走。
- Required revision:把 `graph_cache_family`(全部 6 个成员)加回 `baseline_contract.json` 与 `stop_condition_contract.json`,带 `ties_or_beats_candidate` 停机,与 sealed guardrails 对齐。
- Blocks implementation:**Yes**。

**F2 — `query_capable_imitation_baseline` 被删除**
- Evidence:guardrails 明列 `query_capable_imitation_baseline`(access = "same query budget and observations as candidate",用于 "Detect scripted active querying or prompt-level social behavior")。draft 包内 grep `query_capable|imitation` 命中 0。
- Why it matters:draft 目标显式包含主动探测——`heldout_partner_family_delta` = "active probe usefulness depends on posterior uncertainty",ablation 含 `remove_active_belief_update_preserve_observation_access`。design card md:119 还专门"拒绝 prompt-level or socially plausible behavior as evidence",却没有任何 baseline 把这条拒绝**算子化**。缺它 → 脚本化主动提问/模仿捷径未被挑战,candidate 可借脚本探测"赢"而不被证伪。
- Required revision:加回 `query_capable_imitation_baseline`,query budget 与 candidate 相等,带停机条件。
- Blocks implementation:**Yes**。

**F3 — "ties_or_beats / candidate-equivalent" 的等价裕度未定义、未冻结**
- Evidence:对 draft 包 grep `margin|tolerance|epsilon|confidence_interval|effect_size|tie_band|min_gap` = **空**。`baseline_claim_rule` 与全部 stop 条件都用 "ties or beats" / "candidate-equivalent performance",但无数值带;`evidence_contract` 的 `threshold_must_be_frozen_before_run` 只冻结了 candidate 自身的过线阈值,**没有冻结 candidate-vs-baseline 的等价判定带**。
- Why it matters:这正是审计要拦的 post-hoc scoring 杠杆。看到结果后,"tie" 可被重新解释,把本应触发 baseline 等价的结果说成 candidate 领先。本 lab 有明确的阈值/clip 事后操纵前科(PREFLIGHT-001B)。无冻结裕度 = 一条留给未来的逃逸通道。
- Required revision:预注册一个冻结的等价带(固定 ε 或统计判等规则,如 bootstrap CI 重叠),运行前声明,对所有 baseline 统一适用;并把"等价裁决规则"列入 provenance。
- Blocks implementation:**Yes**。

## 7. Non-fatal concerns

- **NF1 — baseline 的函数类/算力预算 parity 未钉**:`serialized_state_decoder` 与 candidate 共享 `serialized_state + observation` 同一输入(replay_contract 已确认 candidate 也只从这两者重算)。谁赢取决于 decoder 被允许多强,而契约只说 "candidate-equivalent serialized_state",未约束 decoder 的模型类/拟合预算。风险双向:decoder 过弱 → candidate 靠容量赢(claim inflation);decoder 不受限 → 永远判等(虽 fail-closed 安全)。此问题自 guardrails 继承,非 draft 独有,但 draft 有机会收紧而未收紧。建议:要求声明并冻结 baseline 的函数类/算力预算 parity,并把 candidate 优势框定为 access-class 差异而非容量差异。
- **NF2 — primary metric 计算式延迟且无反同义反复条款**:`literal_score_forbidden` 在,但没有"metric 不得在定义上被 candidate 自身输出 schema 满足"的显式条款。鉴于 PREFLIGHT-001B 的 metric 同义反复前科,应补一条 candidate-agnostic 要求。
- **NF3 — external theory scan 被跳过**:002D 的 open route 写的是"redesign **from a higher-level theory scan**";REDESIGN-001A 以"repo coverage 已足够"覆盖之(已封存于 e9d9969,非本 draft 引入)。残留风险:cross-family transfer 仍是合成 partner-belief POMDP 的精细化,需确保是不同的判别层,而非"更难的 002C"。属上游既定决策,这里只作语境标注。
- **NF4 — remote 侧 7685f9c 封存未在本离线审计中独立复核**(本地三方一致,非阻断)。

## 8. Baseline-collapse assessment

**部分达标,尚不充分。** 针对 002C 的**字面**塌缩(`result.json` 确认:candidate=1.0,`serialized_state_decoder`=1.0,触发 `full_bundle_decoder` / `serialized_state_decoder` 等价停机),draft 把这五个实际塌缩族(serialized_state_decoder、full_bundle_decoder、static_belief_table、pair_count、ngram_trace_lookup)全部纳入,并把任意 tie 设为硬停——这点是对的。但因 F1、F2 删族 + F3 等价带留空,它**不能完整阻止 baseline collapse 被漏判**。结论:尚未真正防住 002C 式等价复发。

## 9. Leakage assessment

**达标(可证伪、含正控)。** `leakage_contract` 列 9 类 positive control(target / partner_id / context_id / episode_order / file_path / config / schema_split / scoring_artifact / prompt_text),停机条件含 `any_positive_control_not_detected` 与 `scanner_not_callable_or_not_invoked`。正控是对历史 `block_leakage_scanner_not_fail_able`、stub 喂入、whitelist 逃逸缺陷的真实防御——draft 内未重新引入任何 whitelist 通道。无 blocker。

## 10. Replay assessment

**达标(强制重算,非比较)。** `replay_contract` 要求从 `serialized_state + observation` 重算,显式拒绝 stored_outputs / stored_actions / trace-only / hash-only / static_dictionary / unconditional_pass,并含 4 条必须失败的失败路径测试(`stale_cache_output_injection`、`hash_only_replay_substitution`、`stored_action_replay_substitution`、`baseline_cached_metric_substitution`)。满足"重算而非比较 + stale-cache/stored-output 失败路径"标准。无 blocker。

## 11. Split and transfer assessment

**结构上足够具体,语义上仍延迟。** split_contract 给出 train/heldout partner families、heldout schemas、3 个 counterfactual interventions、distribution shifts、frozen seed/context/episode manifests、`block_if_declared_but_unused`、6 项 schema-equivalence 检查——足以约束实现者在 split/leakage 上不作弊。残留:每个家族的实际生成语义(到底隐藏什么、观测空间、counterfactual 如何计算、transfer 指标的数值定义)仍是一行描述符。对 design card 可接受,但 NF1/NF2 正是这种欠定会咬人的地方。判定:concrete enough,非 blocker,但需配合 NF1/NF2 收紧。

## 12. Provenance assessment

**达标,仅缺一项。** 要求 producer_function / input_artifacts / run_id / seed / context+episode IDs / aggregation_rule / code_path_hash / threshold_frozen / literal_score_forbidden / access-rights,并禁止 literal/static/unconditional metric。唯一缺口正是 F3:**比较规则本身(等价裁决)未被钉进 provenance**。补上 F3 即闭合。

## 13. Anti-Zeno assessment

**契约层面合格。** `stop_condition_contract` 编码了 002D 闭合:`same_family_002c_patch_or_002e_route → blocked_anti_zeno_violation`,且 `closure_rule` 禁止在同一任务内以阈值调参/隐藏字段/选择性重跑/同族打补丁来修复——与 002D `recommended_next_route.forbidden_next_actions` 一致。故未来一旦决定性失败 → 保留负证据 + 闭合,而非自动打补丁。残留 NF3。判定:失败导向闭合/修订,非无限打补丁。

## 14. Claim ceiling assessment

**边界正确。** forbidden-claims 清单在 `result.json` / `evidence_contract` / design card md 三处一致且完整(valid Gate4 / social-latent inference / mechanism validity / agency / selfhood / consciousness / emotion / autonomy / EGO / runtime / companion / user benefit 全列)。无 claim inflation。无 blocker。

## 15. Recommendation

`draft_revision_required_before_anchor`

修订闭合 F1(加回 graph_cache_family 6 成员)、F2(加回 query_capable_imitation_baseline)、F3(冻结等价裁决带并入 provenance)三项后,可重新提交独立审计以争取 `remote_anchor_claude_audit_pass`。**不建议直接进入实现。** 不建议 `external_theory_scan_required_before_revision`——目标本身可被算子化,缺的是 baseline 覆盖与判定规则,而非理论。

---

**Claim ceiling(本审计):** 仅为独立设计审计结论 + 对一张未来任务卡的实现就绪性判断 + 已识别的 blocker/非阻断风险。不主张 valid Gate4、机制有效、social-latent inference、agency、selfhood、consciousness、emotion、autonomy、EGO/runtime/companion readiness 或 user benefit。

**What this does not prove:** 不证明未来 Gate4 会/不会通过;不证明 cross-family social causal transfer 充分;不证明任何 partner-latent 机制有效或无效;不证明修订后契约一定能击败未来 baseline。本审计只判断:按当前 draft 的**绑定契约**实现,尚不能被有意义地约束去防住 baseline-collapse / 弱 baseline / post-hoc scoring 这三项,因此需修订后才可作为实现基线。

**Strict non-actions honored:** 未实现代码、未跑实验/pytest、未建 harness、未改任何 repo 文件、未创建 002E、未改 draft、未进入 Gate5/admission/bridge/runtime/EGO-mainline。