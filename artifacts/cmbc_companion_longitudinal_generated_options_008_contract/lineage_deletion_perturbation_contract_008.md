# Lineage Deletion And Perturbation Contract 008

Future execution must preserve causal traceability from source outcomes through generated option lineage into prediction and action distribution.

Required probes:

- delete final-option supporting source lineage
- delete irrelevant source lineage
- delete one source of a composed option
- perturb admitted outcome support
- perturb pending counterevidence without admission
- perturb retired option source after retirement

Passing behavior:

- deleting final supporting lineage changes selected-option probability or selected option
- deleting irrelevant lineage does not cause comparable regression
- outcome perturbation changes admission-filtered effect vectors only when admitted
- pending perturbation can alter uncertainty but not selector-visible effect vectors
- retired option source perturbation does not affect distribution unless option is reactivated

Minimum future gates:

```text
source_deletion_effect = true
irrelevant_source_deletion_non_regression = true
outcome_perturbation_effect = true
pending_perturbation_selector_visible_effect_delta = 0.0
retired_option_selected_rate = 0.0
```
