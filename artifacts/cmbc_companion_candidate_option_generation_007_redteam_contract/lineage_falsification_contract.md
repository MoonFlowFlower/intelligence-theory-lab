# Lineage Falsification Contract

Purpose: test whether option lineage is real causal support rather than decorative trace text.

Required future checks:

- every admitted option has source refs and evidence support
- missing source refs are rejected or flagged
- corrupted source refs are detected
- lineage-source mismatch is detected
- deleting supporting lineage changes selected option probability or distribution
- deleting irrelevant lineage does not cause equivalent regression

Required future metrics:

```text
lineage_coverage_rate = 1.0
falsified_lineage_detected = true
missing_source_rejected_or_flagged = true
supporting_prior_deletion_effect = true
```

