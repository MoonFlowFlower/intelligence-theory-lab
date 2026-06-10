# PREDICTIVE-ACTION-LEARNING-CONTRACT-001 — bounded experiment artifacts

## What was implemented

An isolated finite-state predictive-action learning experiment instantiating the
frozen skeleton (belief distribution, pseudo-count action-conditioned transition
model, pseudo-count observation model, all-action next-observation prediction,
pre-outcome NLL, entropy/calibration diagnostics, online belief + pseudo-count
updates, same-history all-action counterfactual logging), with 9 baselines,
10 ablations, 9 perturbations, an immutable hashed trace contract with
pre-outcome local-mock commitment, measured no-retrieval/no-replay attestation,
full-trace replay validation, cold-start duplicate runs, and gate/stop-condition
evaluation.

## How to run (from the repository root)

    python -m predictive_action_learning_contract_001 init --suite-dir <DIR>
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group core
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group baselines
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group ablations
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group protocol
    python -m predictive_action_learning_contract_001 run --suite-dir <DIR> --group perturbations
    python -m predictive_action_learning_contract_001 duplicates --suite-dir <DIR>
    python -m predictive_action_learning_contract_001 finalize --suite-dir <DIR> \
        --tests-exit-code <N> --tests-summary "<pytest tail>"

Tests: `python -m pytest tests/test_predictive_action_learning_contract_001*.py -q`

## Explicitly out of scope

EGO mainline, companion behavior, LLM integration/inference, prompts,
personality, emotion, relationship learning, UI, product demo, replay /
consolidation, long-term memory, RAG inside the learner, vector databases, web
access, learner tool use, policy optimization, model-free RL, neural world
models, autonomous agents, and any consciousness / subjective experience /
agency / functional-subject / AGI / companion-readiness claim.

## Evidence status

Commitment sink is a LOCAL MOCK (external timestamp services are forbidden lab
boundary items). Per task card 7.5 the evidence verdict is therefore capped at
`protocol_blocked_by_T1_external_commit_missing` regardless of gate outcomes.
