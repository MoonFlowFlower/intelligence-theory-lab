# Baseline Dependency Audit

{
  "baseline_contract_blocks_expansion": false,
  "existing_baselines_use_fixed_action_ids": true,
  "expanded_baseline_contract_required_before_execution": true,
  "interpretation": "Baseline contracts must be expanded before a valid expanded execution, but the 004 clean failure happened before baseline scoring. This is not the primary blocker for the observed small_action_set_only verdict.",
  "requirements_for_005_or_later": [
    "baselines must receive the same anonymous CandidateOption list",
    "baselines must not read semantic labels or renderer text",
    "frequency and nearest-neighbor baselines must operate on option features and public outcomes only"
  ],
  "static_points": [
    "StrongHeuristicBaseline returns act_4/act_6/act_2",
    "RAGMemoryPromptBaseline returns act_4/act_6/act_2/act_0",
    "003 reexecute strong and expanded contextual baselines compare over the small action set"
  ]
}
