# Baseline Equivalence Report

Gate: True

Baselines: {
  "ActionLabelHeuristicBaseline": {
    "equivalent": false,
    "match_rate": 0.3333333333333333,
    "selected_actions": [
      "a1",
      "a0",
      "a1",
      "a2",
      "a0",
      "a2",
      "a0",
      "a1",
      "a0"
    ]
  },
  "StaticSafetyTableBaseline": {
    "equivalent": false,
    "match_rate": 0.6666666666666666,
    "selected_actions": [
      "a1",
      "a1",
      "a1",
      "a2",
      "a2",
      "a2",
      "a0",
      "a0",
      "a0"
    ]
  },
  "EffectBlindBaseline": {
    "equivalent": false,
    "match_rate": 0.3333333333333333,
    "selected_actions": [
      "a0",
      "a0",
      "a0",
      "a0",
      "a0",
      "a0",
      "a0",
      "a0",
      "a0"
    ]
  }
}

OracleEffectUpperBound is diagnostic only, not a valid competitor.
