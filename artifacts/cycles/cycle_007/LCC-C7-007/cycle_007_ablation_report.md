# Cycle 007 Ablation Report

Verdict: relational_ablation_necessity_passed

- NoRelationalEncoderPolicy: match_rate=0.3, success_rate=0.38, equivalent=False
- EntityIDOnlyPolicy: match_rate=0.36, success_rate=0.42, equivalent=False
- NoRoleBindingPolicy: match_rate=0.33, success_rate=0.4, equivalent=False
- NoRelationCompositionPolicy: match_rate=0.44, success_rate=0.52, equivalent=False
- NoInterventionHistoryPolicy: match_rate=0.48, success_rate=0.55, equivalent=False
- NoCounterfactualQueryPolicy: match_rate=0.34, success_rate=0.41, equivalent=False
- RawObservationOnlyPolicy: match_rate=0.54, success_rate=0.56, equivalent=False
