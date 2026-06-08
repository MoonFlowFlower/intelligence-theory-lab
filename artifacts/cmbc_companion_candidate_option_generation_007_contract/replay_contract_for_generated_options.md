# Replay Contract For Generated Options

Replay must reconstruct the option set and full option distribution.

Future traces must include proposal IDs, admitted option IDs, selector-visible payload hashes, lineage trace references, evidence support references, option uncertainty before selection, prediction before action for every admitted option, full option distribution over the admitted set, selected option ID, and post-selection renderer adapter input hash.

Replay cannot rely on hidden generator text, natural-language descriptions, semantic labels, renderer text, evaluator metrics, oracle effects, or expected outputs.
