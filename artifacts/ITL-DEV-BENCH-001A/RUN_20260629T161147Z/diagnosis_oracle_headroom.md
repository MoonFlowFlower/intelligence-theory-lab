# ITL-DEV-BENCH-001B Oracle Headroom Diagnosis

Current run: RUN_20260629T161147Z
Previous invalid benchmark-validation evidence preserved: RUN_20260629T151318Z

Layer: benchmark validation and engineering repair only.
Claim ceiling: benchmark/headroom repair only.

Diagnosis:
- The prior oracle control was hidden-state-aware but not objective-aligned.
- The primary metric is `total_reward` with higher-is-better orientation.
- A hidden-state upper control must choose actions that optimize that same reward objective, including waiting when movement has negative expected value.

Repair:
- Oracle action selection now evaluates legal safe paths by net reward under hidden rules.
- Candidate minimal-loop policy and PE/memory/planner variants are unchanged.
- Graph-cache remains a frozen observation/outcome baseline and is audited for access scope.

Graph-cache audit verdict: graph_cache_access_contract_ok
Aggregate oracle headroom valid: True
Aggregate oracle score: 11.866666666666667
Aggregate baseline scores: {'random_policy': -6.733333333333333, 'obs_only_policy': -2.066666666666667, 'generic_fsm': -2.8666666666666667, 'graph_cache': -7.4}

If any stage violates oracle headroom, the benchmark remains invalid for candidate claims.
