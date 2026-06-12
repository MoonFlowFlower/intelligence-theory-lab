# 审计报告:GATE4-001C-FAILURE-PRESERVING-REPAIR-TASK-CARD-001A @ 6e5b94b

## Verdict

**`task_card_audit_failed_contract_gap`**

卡片整体质量高:不授权执行、001B 负证据定位正确、11–12 caveat 继承准确、ablation/replay/provenance 合同实质有效。但存在两个仍允许 false-pass 复用的合同缺口,修复成本低(一次 amendment),修复前不应作为执行卡 parent。

## 独立验证(非自报字段,本审计重新计算)

经核实:`6e5b94b` 父提交 = `2f01c49`(与 starting HEAD 声明一致);提交为纯新增(15 文件,无修改/删除,旧 Gate 工件与 Claude 审计未动);13/13 JSON 经 Python 独立解析通过;4 个 parent anchor tag 本地解析哈希与 `parent_anchor_matrix.json` 逐一相符;provisional `d7b5b7a`(真实存在:1621 行 runner + 测试,共 32 文件,仅在 `backup/gate4-001c-provisional-d7b5b7a` 分支)**不是** `6e5b94b` 的祖先;11–12 caveat 与 2f01c49 审计原文逐字一致(TSA-only → 准确类别 `blocked_pending_audit`,且明确禁止 "twelve independent confirmations" 误读)。焦点 1–4、6、7、9 实质满足。

## Blocking issues

**B1 — "Gate4 001B" 指代未钉死,姊妹 001B 家族未覆盖(false-pass 复用通道)。** 仓库中存在三个 Gate4 lineage 的 001B 工件族:`ego_mainline_gate4_preflight_executable_001b`(被封存拒绝,= `90dc4b9`,canonical harness contract 已钉此哈希)、`gate4_social_latent_inference_001b`、`gate4_social_representational_gap_preflight_001b`。后两者自报 verdict 仍是 `*_bounded_pass`,仅靠 241d69c 的 12-target quarantine 拦截。本卡片及其全部矩阵从未给 "Gate4 001B" 写下 task_id/工件目录/提交哈希,也从未声明 12 个 quarantined targets 对未来 001C 继续不可采信。后果:未来执行卡可引用 `gate4_social_latent_inference_001b` 的 "bounded_pass" 作支持性叙事而不违反本卡任何字句;`reject_gate4_001b_pass_evidence` 测试因 task_id 字符串不同不会触发。这是 001D 已记录的命名混叠通道在本卡的再现条件。

**B2 — whitelist/豁免逃逸通道未继承。** Canonical harness contract(lineage 内规则源,本卡复制了其禁止清单的大部分)明确禁止 "leakage scans with broad whitelist behavior";该项是 lineage 中两次复发的实际缺陷(POST-BRIDGE-001D 残留通道、GATE4-PREFLIGHT-001B 复发)。本卡 `leakage_requirement_matrix` 恰好漏掉这一条:positive control 在被扫描范围内可检出、真实工件在豁免路径中逃逸的扫描器,完全符合本卡现有 scanner contract。卡片也未要求把 001A harness 作为 challenger 跑在未来 001C 产出 bundle 上,且未要求预声明扫描范围。

## Non-blocking issues

N1:本起草任务自身工件含手写不可失败字段(`worktree_clean_before_generation`、`all_required_json_parsed`、`all_parent_remote_tags_observed`、`provisional_gate4_001c_used:false`;`json_parse_verification.json` 自指、无保留命令输出)——该模式家族第三次复发;本审计已独立重验关键项故降级,但执行卡不得复制此风格。N2:Authorization Boundary 的禁止动词列表漏 "read"(stop conditions、prohibited-use matrix、test matrix 中有,不一致但有覆盖)。N3:baseline matrix 的 `required_record` 为 7 条完全相同的模板字符串——作为统一要求可接受,接近 boilerplate 边界;其余矩阵(anchor 哈希、ablation 逐条禁止替代、scanner 清单)为具体条目,焦点 11 总体通过。N4:卡片未把 canonical harness contract 文档/提交(`b114246`)列入 anchor,尽管它是被部分复制的规则源。N5:"authorizes only future task-card review" 措辞与起草用途略有出入。

## Missing execution-scope details(执行卡必须补齐)

候选机制定义(具体 src 路径与入口);exact allowed/forbidden 文件清单;exact 测试文件与命令;exact 执行工件文件名;数据/episode/context schema(episode 数、partner/context 集、seed 列表、train/heldout 切分规则、counterfactual pair 构造);逐 baseline 的度量定义与聚合;**预声明的 pass/fail 阈值及阈值选择规则**(CLAUDE.md 强制);最小分布强度/样本量(防 weak-test-distribution pass);replay 比较规则取值(exact vs tolerance、确定性/seed 策略);执行用 verdict 分类表含显式失败 verdict(防 001D 混叠);执行 stop conditions 与预算;baseline 独立性约束(不得复用候选的 latent 模块)+ 同 episode 集评测;provenance 中 input artifact 哈希与 protected-artifact before/after 哈希;是否将 001A harness 作为 challenger 跑产出 bundle 的明确决定。

## Claim ceiling assessment

通过。Ceiling("bounded Gate4 001C failure-preserving repair task-card drafting only")在卡片、`claim_ceiling.txt`、`result.json` 间一致;六个授权位全 false 且三处冗余记录;what-this-does-not-prove 清单充分;卡片文本无超 ceiling 表述。本审计自身 ceiling:仅为对该任务卡的独立审计,不构成 Gate4 有效性、机制有效性或任何执行授权。

## Next-step recommendation

先出一个小型 amendment(001B 版任务卡或对本卡的受控修订):(1) 钉死指代——`gate4_001b := 90dc4b9` + 工件目录,枚举两个姊妹 001B 家族及 241d69c 全部 12 个 quarantined targets 对未来 001C 继续 `quarantined_from_downstream_use`;(2) leakage contract 增加 whitelist/豁免禁止 + 预声明扫描范围 + harness-challenger 要求(或书面豁免理由)。修复后该卡可作为执行卡 parent;执行卡起草时以上"缺失范围清单"为必填字段。仍不执行 Gate4 001C。

本报告未写入仓库。如需按惯例以 `docs: preserve Claude audit ...` 形式留档,说一声即可。
