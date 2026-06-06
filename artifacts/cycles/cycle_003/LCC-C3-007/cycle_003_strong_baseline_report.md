# Cycle 003 Strong Baseline Report

Verdict: strong_baselines_not_equivalent

Baselines: {
  "PassiveLearnerPolicy": {
    "match_rate": 0.2,
    "equivalent": false
  },
  "GreedyImmediateValuePolicy": {
    "match_rate": 0.25,
    "equivalent": false
  },
  "RandomDiagnosticPolicy": {
    "match_rate": 0.52,
    "equivalent": false
  },
  "NearestNeighborTracePolicy": {
    "match_rate": 0.58,
    "equivalent": false
  },
  "ContextualHeuristicBaseline": {
    "match_rate": 0.33,
    "equivalent": false
  },
  "StaticDiagnosticTableBaseline": {
    "match_rate": 0.62,
    "equivalent": false
  }
}

OracleDiagnosticUpperBound is diagnostic-only.
