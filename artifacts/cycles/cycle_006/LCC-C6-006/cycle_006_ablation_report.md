# Cycle 006 Ablation Report

Verdict: representation_ablation_necessity_passed

- NoLearnedEncoderPolicy: match_rate=0.28, success_rate=0.34, equivalent=False
- NoHistoryPolicy: match_rate=0.42, success_rate=0.52, equivalent=False
- NoInterventionHistoryPolicy: match_rate=0.4, success_rate=0.5, equivalent=False
- NoCausalRepresentationPolicy: match_rate=0.3, success_rate=0.36, equivalent=False
- NuisanceOnlyRepresentationPolicy: match_rate=0.35, success_rate=0.38, equivalent=False
- RawObservationOnlyPolicy: match_rate=0.56, success_rate=0.58, equivalent=False
- NoCounterfactualQueryPolicy: match_rate=0.32, success_rate=0.4, equivalent=False
