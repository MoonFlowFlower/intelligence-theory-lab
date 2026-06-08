# Uncertainty Update Contract

Pending feedback may reduce confidence or increase uncertainty.

Rules:

- pending feedback may reduce confidence or increase uncertainty.
- pending feedback may increment pending counterevidence counts.
- pending feedback may not change selector-visible predicted_effect_vector.
- single pending feedback cannot create a high-confidence selector-visible option.
- single pending feedback cannot increase sample_count as if it were admitted evidence.
- repeated or high-confidence feedback may be admitted only after context match and admission requirements are satisfied.
- admitted feedback must cite the pending records that caused admission.

Future execution must report confidence before/after, uncertainty before/after,
sample_count before/after, and whether each change was selector-visible.
