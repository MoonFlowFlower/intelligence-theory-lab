# Risk Register 006

## False Pass: Fixed 20-Action Table

Risk: anonymous option IDs hide a fixed recipe table.

Gate: fail with `fixed_twenty_action_table_detected`.

## Baseline Unfairness

Risk: expanded baselines receive weaker inputs than CMBC.

Gate: all baselines receive the same anonymous `CandidateOption` list.

## Renderer Control

Risk: renderer text or adversarial prompt changes `selected_option_id`.

Gate: renderer remains strictly post-selection and `renderer_action_change_rate = 0.0`.

## Evidence Rewrite

Risk: 003 or 005 results are relabeled as expanded evidence.

Gate: preserve 003 as small-action-set evidence and 005 shadow as N=7 compatibility evidence only.

## Distribution Collapse

Risk: expanded action space passes by collapsing probability onto one option.

Gate: future execution must report action distribution entropy and dominant action rate.
