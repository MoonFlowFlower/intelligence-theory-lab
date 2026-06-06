# Cycle 003 Ablation Report

Verdict: ablation_necessity_passed

Ablations: {
  "NoUncertaintyPolicy": {
    "match_rate": 0.38,
    "equivalent": false,
    "failure_signature": "diagnostic timing collapses"
  },
  "NoInterventionHistoryPolicy": {
    "match_rate": 0.42,
    "equivalent": false,
    "failure_signature": "post-identification transfer collapses"
  },
  "NoPosteriorUpdatePolicy": {
    "match_rate": 0.31,
    "equivalent": false,
    "failure_signature": "posterior uncertainty remains high"
  },
  "NoCounterfactualQueryPolicy": {
    "match_rate": 0.36,
    "equivalent": false,
    "failure_signature": "effect swap sensitivity collapses"
  },
  "PassiveOnlyTrainingPolicy": {
    "match_rate": 0.22,
    "equivalent": false,
    "failure_signature": "correlation mistaken for intervention"
  }
}
