# Dirty Worktree Risk Report

Generated UTC: 2026-06-11T10:01:30.856441+00:00

## Summary

- git status entries: 81
- protected dirty entries: 17
- non-protected dirty entries: 64
- protected tracked files in inventory: 0
- protected untracked files in inventory: 350
- manifest-covered files matched: 312
- manifest-covered missing files: 0
- manifest-covered mismatched files: 1

## Classification

Protected paths appear in dirty/untracked status. Because manifest-covered hashes match, this is classified as a VCS-freeze / staging caveat unless another stop condition is present.

This report does not authorize cleanup, rewrite, regeneration, or staging.

## Protected Dirty Entries

- `??` `artifacts/predictive_action_learning_contract_001/`
- `??` `artifacts/predictive_action_learning_contract_001c/`
- `??` `artifacts/predictive_action_learning_contract_001c_independent_audit/`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001.txt`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001B.txt`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CANONICAL-FREEZE.md`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CLOSEOUT-TASK.md`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CLOSEOUT.md`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-INDEPENDENT-AUDIT.md`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-T1-EXTERNAL-COMMIT.md`
- `??` `docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-T1-EXTERNAL-COMMIT.txt`
- `??` `docs/PREDICTIVE_ACTION_LEARNING_CONTRACT_001C_CANONICAL_RECORD.md`
- `??` `predictive_action_learning_contract_001/`
- `??` `predictive_action_learning_contract_001c/`
- `??` `tests/test_predictive_action_learning_contract_001.py`
- `??` `tests/test_predictive_action_learning_contract_001_baselines.py`
- `??` `tests/test_predictive_action_learning_contract_001c.py`

## Stop Conditions

- protected_hash_mismatch: 1
- model_provenance_unresolved: 118
- dirty_state_blocks_classification: 17
