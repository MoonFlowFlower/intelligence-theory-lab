# THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D

**Mode:** bounded pre-canonicalization closure patch generation only
**Verdict:** `theory_landscape_precanonical_closure_patch_001b_pass_with_caveats`
**Claim ceiling:** bounded pre-canonicalization closure patch evidence only.

## 1. Relationship and status

- `THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001A` was blocked by adoption-language confusion.
- `THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001B` repaired the main adoption-language blocker.
- `THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C` closed most caveats and received targeted Claude `closure_pass_with_caveats`.
- `THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D` applies only the final mechanical pre-canonicalization caveat fixes.
- `001D` supersedes `001A`, `001B`, and `001C` only for future canonicalization consideration. It is not canonicalization itself.
- `001D` does not choose architecture, does not recommend selecting Hyperon, and does not authorize any implementation.

## 2. Source and remote-anchor readback

```json
{
  "task_id": "THEORY-LANDSCAPE-COVERAGE-PRECANONICAL-CLOSURE-PATCH-001B",
  "verdict": "theory_landscape_precanonical_closure_patch_001b_pass_with_caveats",
  "worktree_status_before_generation": "## codex/meta-theory-scaffold",
  "remote_anchors": [
    {
      "tag": "remote-anchor-source-pin-001a-c9fdc8e",
      "expected_commit": "c9fdc8e1a66f9b666b98f53a5b6c35baf274d38a",
      "ls_remote": "c9fdc8e1a66f9b666b98f53a5b6c35baf274d38a\trefs/tags/remote-anchor-source-pin-001a-c9fdc8e",
      "verified": true
    },
    {
      "tag": "remote-anchor-compression-sources-001a-985f494",
      "expected_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "ls_remote": "985f49496f1b35d1e8075eeac542b136fe53feb9\trefs/tags/remote-anchor-compression-sources-001a-985f494",
      "verified": true
    }
  ],
  "phase_one_source_pin_manifest_readback": {
    "path": "artifacts/phase_one_theory_landscape_source_pin_001a/source_pin_manifest.json",
    "verdict": "phase_one_theory_landscape_source_pin_001a_pinned",
    "reconstructed_from_memory": false,
    "pinned_from_verbatim_user_source": true,
    "source_title_check_passed": true
  },
  "compression_source_corpus_manifest_readback": {
    "path": "artifacts/theory_landscape_coverage_compression_sources_pin_001a/source_corpus_manifest.json",
    "manifest_verdict": "theory_landscape_compression_sources_pin_001a_pinned",
    "source_count": 6,
    "docx_extraction_performed": false
  },
  "sources": [
    {
      "source_id": "phase_one_theory_landscape_coverage_audit_report",
      "source_role": "external_source_report",
      "source_path": "docs/research/PHASE-ONE-THEORY-LANDSCAPE-COVERAGE-AUDIT.md",
      "sha256": "c5e509a23f575c547186eec2a5a4bd6c506578a8bb10cf1e147b0be44d9ddfcc",
      "remote_anchor_tag": "remote-anchor-source-pin-001a-c9fdc8e",
      "remote_anchor_commit": "c9fdc8e1a66f9b666b98f53a5b6c35baf274d38a",
      "reconstructed_from_memory": false
    },
    {
      "source_id": "theory_landscape_coverage_compression_001a",
      "source_role": "compression_draft_001a",
      "source_path": "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001A.md",
      "sha256": "30e651acb08ee8bebaafa744b1997334a196e52d27fdf2133ba049d5cba8f43b",
      "remote_anchor_tag": "remote-anchor-compression-sources-001a-985f494",
      "remote_anchor_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "reconstructed_from_memory": false
    },
    {
      "source_id": "theory_landscape_coverage_compression_001b",
      "source_role": "compression_draft_001b",
      "source_path": "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001B.md",
      "sha256": "c66e03bda847deb7da7a9e9c192752dc8fcadece0e4926fa61d4aeb750c53736",
      "remote_anchor_tag": "remote-anchor-compression-sources-001a-985f494",
      "remote_anchor_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "reconstructed_from_memory": false
    },
    {
      "source_id": "theory_landscape_coverage_compression_001c_docx",
      "source_role": "compression_draft_001c_canonical_docx_source",
      "source_path": "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/Theory Landscape Coverage Compression 001C.docx",
      "sha256": "07797bb37567d21baa3ffdf950197a03be8b5e581204e94577025eca00c6c98a",
      "remote_anchor_tag": "remote-anchor-compression-sources-001a-985f494",
      "remote_anchor_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "reconstructed_from_memory": false
    },
    {
      "source_id": "claude_theory_landscape_compression_001a_audit",
      "source_role": "red_team_audit_of_001a",
      "source_path": "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/Claude audit of 001A.txt",
      "sha256": "bc3bbc0ff3fa1b178a5f7f8d333b1ca82d03077481075ca90f1211adc1ad8e1e",
      "remote_anchor_tag": "remote-anchor-compression-sources-001a-985f494",
      "remote_anchor_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "reconstructed_from_memory": false
    },
    {
      "source_id": "claude_theory_landscape_compression_001b_audit",
      "source_role": "red_team_audit_of_001b",
      "source_path": "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/Claude audit of 001B.txt",
      "sha256": "056c0b9e185984bce8e37f7d7051a7fe1c412ee28962ddd2583e3bf494bb28e3",
      "remote_anchor_tag": "remote-anchor-compression-sources-001a-985f494",
      "remote_anchor_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "reconstructed_from_memory": false
    },
    {
      "source_id": "claude_theory_landscape_compression_001c_closure_check",
      "source_role": "targeted_closure_check_of_001c",
      "source_path": "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/Claude closure check of 001C.txt",
      "sha256": "96cd1161f2328d0fec4fba5863160f64359b9f81e8ffa9a6ac9f352a36a29eaf",
      "remote_anchor_tag": "remote-anchor-compression-sources-001a-985f494",
      "remote_anchor_commit": "985f49496f1b35d1e8075eeac542b136fe53feb9",
      "reconstructed_from_memory": false
    }
  ],
  "reconstructed_from_memory": false
}
```

## 3. Complete graph/substrate challenger family

Every graph/substrate challenger-family reference in this patch resolves to the complete six-member family below. This patch does not create a weaker second graph-comparison contract.

```json
{
  "graph_substrate_challenger_family": [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal"
  ]
}
```

## 4. Complete machine-readable coverage matrix

This is a complete row set generated from the corrected layered candidate matrix in the pinned 001C DOCX source. It is not a schema-only Hyperon fragment.

```json
{
  "artifact_id": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001D",
  "phase": "bounded_precanonical_closure_patch_generation_only",
  "verdict": "theory_landscape_precanonical_closure_patch_001b_pass_with_caveats",
  "source_rows_from": "pinned 001C DOCX corrected layered candidate matrix table",
  "schema_example_only": false,
  "complete_candidate_row_set": true,
  "row_count": 45,
  "hyperon_structural_highlighting_blocked": true,
  "rows": [
    {
      "candidate_id": "computed_evidence_provenance",
      "display_name": "Computed Evidence Provenance Contract",
      "layer": "evidence-governance / evaluation methodology",
      "ego_layer_mapping": [
        "all_gates",
        "bridge",
        "post_bridge_admission",
        "safety_evidence_governance"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Methodology improves evidence quality but does not create mechanism",
      "claim_ceiling": "Required methodology only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "causal_eval_ablation",
      "display_name": "Causal Evaluation / Ablation",
      "layer": "evidence-governance",
      "ego_layer_mapping": [
        "all_executable_gates"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Fake or static ablations can still produce false passes",
      "claim_ceiling": "Required method only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "red_team_evaluation",
      "display_name": "Red-team Evaluation",
      "layer": "evidence-governance",
      "ego_layer_mapping": [
        "safety_evidence_governance"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Review pass is not mechanism proof",
      "claim_ceiling": "Required review method only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "leakage_contamination_defense",
      "display_name": "Leakage / Contamination Defense",
      "layer": "evidence-governance",
      "ego_layer_mapping": [
        "all_executable_gates"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Scanner without positive controls can become theater",
      "claim_ceiling": "Required contamination-control method only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "trace_replay_reproducibility",
      "display_name": "Trace / Replay Reproducibility",
      "layer": "evidence-governance",
      "ego_layer_mapping": [
        "gate1_replay_consolidation",
        "bridge",
        "post_bridge_admission"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Hash replay is not behavior recomputation",
      "claim_ceiling": "Required replay method only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "source_artifact_hash_integrity",
      "display_name": "Source Artifact Hash Integrity",
      "layer": "evidence-governance",
      "ego_layer_mapping": [
        "source_pinning",
        "evidence_custody"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Hash integrity does not validate theory",
      "claim_ceiling": "Required custody method only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "negative_evidence_preservation",
      "display_name": "Negative Evidence Preservation",
      "layer": "evidence-governance",
      "ego_layer_mapping": [
        "all_gates",
        "downstream_admission"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Preservation is necessary but not sufficient",
      "claim_ceiling": "Required lineage method only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "predictive_processing",
      "display_name": "Predictive Processing",
      "layer": "mechanism theory",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate1_replay_consolidation",
        "gate3_viability_functional_affect"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "Any update can be retrofitted as prediction error",
      "claim_ceiling": "Bounded predictive-update framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "active_inference_fep",
      "display_name": "Active Inference / FEP",
      "layer": "mechanism theory",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate2_controllability_self_boundary",
        "gate3_viability_functional_affect",
        "controlled_initiative"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "High agency / life / affect overclaim risk",
      "claim_ceiling": "Bounded active-policy / viability proxy framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "world_models_latent_dynamics",
      "display_name": "World Models / Latent Dynamics",
      "layer": "mechanism / model-based RL / representation",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate1_replay_consolidation",
        "candidate_generation"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "Task performance may be benchmark-specific optimization",
      "claim_ceiling": "Learned-dynamics comparator only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "dreamer_family",
      "display_name": "Dreamer Family",
      "layer": "model-based RL",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate1_replay_consolidation",
        "candidate_generation"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "Not directly evidence for selfhood or companion behavior",
      "claim_ceiling": "Model-based RL comparator only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "muzero_family",
      "display_name": "MuZero Family",
      "layer": "model-based RL",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "candidate_generation"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "Planning success can hide reward/task engineering",
      "claim_ceiling": "Planning comparator only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "jepa_predictive_representation",
      "display_name": "JEPA / Predictive Representation Learning",
      "layer": "substrate / representation",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate1_replay_consolidation"
      ],
      "role": "monitor_only",
      "safe_status": "monitor_only",
      "strongest_objection": "Representation quality is not agency or continuity",
      "claim_ceiling": "Monitor representation-learning relevance only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "memory_lifelong_learning_systems",
      "display_name": "Memory / Lifelong Learning Systems",
      "layer": "memory / lifelong learning",
      "ego_layer_mapping": [
        "gate1_replay_consolidation",
        "long_term_memory",
        "bridge"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "Persistent memory does not equal same-agent continuity",
      "claim_ceiling": "Durable-state-change framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "theory_of_mind_social_latent",
      "display_name": "Theory-of-Mind / Social-Latent Modeling",
      "layer": "social / companion system; mechanism theory",
      "ego_layer_mapping": [
        "gate4_social_latent_status",
        "gate4_social_representational_gap_status"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "ToM-like behavior may be prompt inference or stereotype retrieval",
      "claim_ceiling": "Social-latent proxy framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "affective_computing",
      "display_name": "Affective Computing",
      "layer": "social / companion system; affect modeling",
      "ego_layer_mapping": [
        "gate3_viability_functional_affect",
        "companion_relationship_layer"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Affect recognition / expression is not real emotion",
      "claim_ceiling": "Affect-label and affect-expression baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "appraisal_functional_affect_models",
      "display_name": "Appraisal Theory / Functional Affect Models",
      "layer": "mechanism theory; functional affect",
      "ego_layer_mapping": [
        "gate3_viability_functional_affect"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "Appraisal labels can be handcrafted unless intervention-linked",
      "claim_ceiling": "Functional-affect proxy framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "homeostasis_homeostatic_rl",
      "display_name": "Homeostasis / Homeostatic RL",
      "layer": "artificial life / viability system; RL",
      "ego_layer_mapping": [
        "gate3_viability_functional_affect",
        "controlled_initiative"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "Artificial drives can become reward shaping theater",
      "claim_ceiling": "Viability-relevant control framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "developmental_robotics",
      "display_name": "Developmental Robotics",
      "layer": "embodied cognition / artificial life",
      "ego_layer_mapping": [
        "gate2_controllability_self_boundary",
        "gate3_viability_functional_affect",
        "controlled_initiative"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "EGO lacks physical embodiment; simulation proxy must be explicit",
      "claim_ceiling": "Action-feedback and self-boundary framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "enactive_embodied_cognition",
      "display_name": "Enactive / Embodied Cognition",
      "layer": "mechanism theory / philosophy of cognition",
      "ego_layer_mapping": [
        "gate2_controllability_self_boundary",
        "gate3_viability_functional_affect",
        "gate4_social_latent_status"
      ],
      "role": "cite_only",
      "safe_status": "cite_only",
      "strongest_objection": "Can remain philosophical without executable proxy",
      "claim_ceiling": "Constraint vocabulary only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "autopoiesis_viability_systems",
      "display_name": "Autopoiesis / Viability Systems",
      "layer": "artificial life / viability system",
      "ego_layer_mapping": [
        "gate3_viability_functional_affect",
        "bridge",
        "post_bridge_admission"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "Very high electronic-life overclaim risk",
      "claim_ceiling": "Bounded viability proxy framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "common_model_of_cognition",
      "display_name": "Common Model of Cognition",
      "layer": "cognitive architecture / architecture synthesis",
      "ego_layer_mapping": [
        "gate1_replay_consolidation",
        "candidate_generation",
        "controlled_initiative"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "architecture_coverage_only_not_adoption_not_implementation",
      "strongest_objection": "Architecture consensus does not prove EGO mechanism validity",
      "claim_ceiling": "Architecture coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "global_workspace_lida",
      "display_name": "Global Workspace / LIDA",
      "layer": "cognitive architecture / attention theory",
      "ego_layer_mapping": [
        "gate4_social_latent_status",
        "controlled_initiative",
        "safety_evidence_governance"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "architecture_coverage_only_not_adoption_not_implementation",
      "strongest_objection": "Attention/broadcast is not consciousness",
      "claim_ceiling": "Architecture coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "soar",
      "display_name": "SOAR",
      "layer": "cognitive architecture",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate1_replay_consolidation",
        "gate2_controllability_self_boundary",
        "candidate_generation"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "architecture_coverage_only_not_adoption_not_implementation",
      "strongest_objection": "Symbolic architecture may collapse into handcrafted control",
      "claim_ceiling": "Architecture coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "act_r",
      "display_name": "ACT-R",
      "layer": "cognitive architecture",
      "ego_layer_mapping": [
        "gate1_replay_consolidation",
        "long_term_memory"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "architecture_coverage_only_not_adoption_not_implementation",
      "strongest_objection": "Human cognitive-modeling validity does not transfer to EGO",
      "claim_ceiling": "Architecture coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "nars",
      "display_name": "NARS",
      "layer": "reasoning architecture",
      "ego_layer_mapping": [
        "candidate_generation",
        "gate2_controllability_self_boundary",
        "safety_evidence_governance"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "Uncertain reasoning is not self-boundary or subjectivity",
      "claim_ceiling": "Uncertain-reasoning coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "clarion",
      "display_name": "CLARION",
      "layer": "cognitive architecture",
      "ego_layer_mapping": [
        "gate1_replay_consolidation",
        "gate2_controllability_self_boundary",
        "controlled_initiative"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "architecture_coverage_only_not_adoption_not_implementation",
      "strongest_objection": "Dual-process label can become architecture theater",
      "claim_ceiling": "Architecture coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "sigma",
      "display_name": "Sigma",
      "layer": "cognitive architecture",
      "ego_layer_mapping": [
        "gate0_predictive_action_update",
        "gate1_replay_consolidation",
        "candidate_generation"
      ],
      "role": "monitor_only",
      "safe_status": "monitor_only",
      "strongest_objection": "High complexity and unclear direct EGO relevance",
      "claim_ceiling": "Monitor only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "society_of_mind",
      "display_name": "Society of Mind",
      "layer": "architecture metaphor / mechanism theory",
      "ego_layer_mapping": [
        "candidate_generation",
        "gate4_social_latent_status"
      ],
      "role": "cite_only",
      "safe_status": "cite_only",
      "strongest_objection": "Multi-agent metaphor can become unfalsifiable",
      "claim_ceiling": "Conceptual reference only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "hyperon_metta_atomspace",
      "display_name": "OpenCog Hyperon / MeTTa / Atomspace",
      "layer": "substrate / representation layer; cognitive architecture candidate",
      "ego_layer_mapping": [
        "persistent_state",
        "graph_memory",
        "candidate_generation",
        "replay",
        "long_term_memory"
      ],
      "role": "architecture_coverage_only_not_adoption_not_implementation",
      "safe_status": "comparative_audit_candidate",
      "strongest_objection": "Early-stage, high complexity, substrate-level evidence only",
      "claim_ceiling": "Hyperon may be represented only as a substrate / graph-memory / cognitive-architecture coverage candidate for future bounded comparative audit. It is not selected, not implementation-authorized, not runtime-authorized, and not positive evidence for EGO readiness, AGI, consciousness, selfhood, or electronic life.",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false,
      "future_integration_audit_target_only": true,
      "non_canonical_duplicate": false,
      "evidence_of_agi": false,
      "evidence_of_consciousness": false,
      "evidence_of_selfhood": false,
      "evidence_of_electronic_life": false,
      "local_negative_evidence_required_for_future_audit": {
        "gate1_graph_cache_collapse_required": true,
        "residue_001a_required": true,
        "graph_substrate_challenger_family": [
          "graph_lookup",
          "transition_table",
          "successor_map",
          "count_table",
          "fsm_planner",
          "episodic_traversal"
        ]
      },
      "required_future_gate_if_used": "bounded comparative audit with complete graph challenger family"
    },
    {
      "candidate_id": "companion_memory_architectures",
      "display_name": "Companion Memory Architectures",
      "layer": "memory / social companion system",
      "ego_layer_mapping": [
        "long_term_memory",
        "companion_relationship_layer",
        "bridge"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Companion memory can simulate continuity without same-agent state",
      "claim_ceiling": "Companion-memory baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "letta_memgpt",
      "display_name": "Letta / MemGPT",
      "layer": "memory / lifelong learning; engineering agent framework",
      "ego_layer_mapping": [
        "long_term_memory",
        "bridge"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Persistent memory does not equal continuity",
      "claim_ceiling": "Memory-system baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "generative_agents",
      "display_name": "Generative Agents",
      "layer": "social / companion system",
      "ego_layer_mapping": [
        "gate4_social_latent_status",
        "companion_relationship_layer",
        "long_term_memory"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Believable social behavior is not relationship learning",
      "claim_ceiling": "Social-believability baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "voyager",
      "display_name": "Voyager",
      "layer": "engineering agent framework / lifelong skill learning",
      "ego_layer_mapping": [
        "candidate_generation",
        "long_term_memory",
        "controlled_initiative"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Skill-library growth is not agency or selfhood",
      "claim_ceiling": "Skill-acquisition baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "autogpt",
      "display_name": "AutoGPT",
      "layer": "engineering agent framework",
      "ego_layer_mapping": [
        "candidate_generation",
        "controlled_initiative"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Loop is not agency",
      "claim_ceiling": "Agent-loop baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "babyagi",
      "display_name": "BabyAGI",
      "layer": "engineering agent framework",
      "ego_layer_mapping": [
        "candidate_generation",
        "controlled_initiative"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Task loop is not agency",
      "claim_ceiling": "Agent-loop baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "langgraph",
      "display_name": "LangGraph",
      "layer": "engineering agent framework",
      "ego_layer_mapping": [
        "candidate_generation",
        "controlled_initiative",
        "safety_evidence_governance"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Workflow graph is not subject mechanism",
      "claim_ceiling": "Workflow baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "autogen",
      "display_name": "AutoGen",
      "layer": "engineering agent framework",
      "ego_layer_mapping": [
        "candidate_generation",
        "controlled_initiative"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Multi-agent role play is not selfhood",
      "claim_ceiling": "Multi-agent baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "crewai",
      "display_name": "CrewAI",
      "layer": "engineering agent framework",
      "ego_layer_mapping": [
        "candidate_generation",
        "controlled_initiative"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Role orchestration is not agency",
      "claim_ceiling": "Workflow baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "openhands",
      "display_name": "OpenHands",
      "layer": "engineering agent framework",
      "ego_layer_mapping": [
        "candidate_generation",
        "safety_evidence_governance"
      ],
      "role": "baseline_only",
      "safe_status": "baseline_only",
      "strongest_objection": "Coding-agent success is not EGO mechanism evidence",
      "claim_ceiling": "Engineering-agent baseline only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "mechanistic_interpretability_causal_scrubbing",
      "display_name": "Mechanistic Interpretability / Causal Scrubbing",
      "layer": "evidence-governance / evaluation methodology",
      "ego_layer_mapping": [
        "safety_evidence_governance",
        "all_executable_gates"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Interpretability claims can overreach beyond actual causal evidence",
      "claim_ceiling": "Required evaluation-method coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "memory_autonomy_benchmarks",
      "display_name": "Memory / Autonomy Benchmarks",
      "layer": "evidence-governance / benchmark methodology",
      "ego_layer_mapping": [
        "long_term_memory",
        "controlled_initiative",
        "safety_evidence_governance"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Benchmark success does not imply mechanism validity",
      "claim_ceiling": "Required benchmark-awareness only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "memory_evaluation_suites",
      "display_name": "Memory Evaluation Suites",
      "layer": "evidence-governance / benchmark methodology",
      "ego_layer_mapping": [
        "gate1_replay_consolidation",
        "long_term_memory",
        "bridge"
      ],
      "role": "mandatory_methodology",
      "safe_status": "mandatory_methodology",
      "strongest_objection": "Memory tests can reward retrieval not consolidation",
      "claim_ceiling": "Required memory-eval coverage only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "adjustable_autonomy_delegation_control",
      "display_name": "Adjustable Autonomy / Delegation Control",
      "layer": "controllability / autonomy governance",
      "ego_layer_mapping": [
        "gate2_controllability_self_boundary",
        "controlled_initiative",
        "safety_evidence_governance"
      ],
      "role": "mechanism_family_coverage_only",
      "safe_status": "mechanism_family_coverage_only",
      "strongest_objection": "Delegation UI or policy toggles do not prove self-boundary",
      "claim_ceiling": "Controlled-initiative framing only",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    },
    {
      "candidate_id": "romance_attachment_product_demo",
      "display_name": "Romance / Attachment / Product Companion Demo",
      "layer": "social / companion system",
      "ego_layer_mapping": [
        "companion_relationship_layer"
      ],
      "role": "reject_as_mainline",
      "safe_status": "reject_as_mainline",
      "strongest_objection": "Current evidence cannot support real relationship learning or stable user benefit",
      "claim_ceiling": "No positive claim allowed",
      "source_row_origin": "THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001C corrected layered candidate matrix",
      "schema_example_only": false,
      "selected_as_architecture": false,
      "must_not_be_used_as_positive_evidence_without_future_gate": true,
      "architecture_selection_authorized": false,
      "implementation_authorized": false,
      "ego_mainline_authorized": false,
      "runtime_authorized": false,
      "companion_or_relationship_work_authorized": false,
      "llm_rag_authorized": false,
      "user_model_authorized": false,
      "emotion_authorized": false,
      "persistent_profile_authorized": false,
      "long_term_human_user_memory_authorized": false
    }
  ]
}
```

## 5. EGO-MAINLINE-READINESS-AUDIT-001B node

The committed audit reference is separated from the future actionability revalidation requirement.

```json
{
  "ego_mainline_readiness_audit_001b": {
    "committed_audit_reference": "docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md",
    "task_id": "EGO-MAINLINE-READINESS-AUDIT-001B",
    "commit_hash": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
    "verdict": "ego_mainline_readiness_audit_001b_authorize_admission_task_card",
    "claim_ceiling": "Bounded EGO-mainline readiness revalidation audit evidence for admission-contract authorization only.",
    "runtime_authorized": false,
    "downstream_caveats": [
      "Only authorizes drafting EGO-MAINLINE-ADMISSION-TASK-CARD-001A.",
      "No EGO runtime, bridge runtime, companion behavior, LLM/RAG, user-model, relationship learning, emotion systems, personalization, product-demo work, romance, attachment, persistent profile work, or long-term human-user memory work.",
      "Future admission task card must preserve surface-scoped leakage metadata whitelist behavior.",
      "Future admission task card must require independent manual leakage injection tests.",
      "Do not use 001B or 001C as downstream positive evidence.",
      "Preserve 001D caveat and strict claim ceiling."
    ],
    "actionability_revalidation_required": true
  }
}
```

## 6. Complete family accounting

Every monitor, defer, reject, and baseline item below has an id type, accounting status, reason, and `implementation_authorized = false`.

```json
{
  "family_accounting": [
    {
      "candidate_id": "jepa_predictive_representation",
      "id_type": "candidate",
      "accounting_status": "monitor_only",
      "reason": "Present in the corrected matrix with monitor-only status; observe future evidence without implementation pressure.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "sigma",
      "id_type": "candidate",
      "accounting_status": "monitor_only",
      "reason": "Present in the corrected matrix with monitor-only status; observe future evidence without implementation pressure.",
      "implementation_authorized": false
    },
    {
      "topic_id": "mine_dojo",
      "id_type": "topic",
      "accounting_status": "monitor_only",
      "reason": "Split from Voyager/MineDojo lineage as an environment/tooling watch item; useful only as future baseline context.",
      "implementation_authorized": false
    },
    {
      "topic_id": "hyperon_ecosystem_maturity_updates",
      "id_type": "topic",
      "accounting_status": "monitor_only",
      "reason": "Monitor ecosystem maturity without treating ecosystem movement as architecture correctness.",
      "implementation_authorized": false
    },
    {
      "topic_id": "full_substrate_replacement",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Too broad for this pre-canonical patch and would imply architecture selection.",
      "implementation_authorized": false
    },
    {
      "topic_id": "full_cognitive_architecture_migration",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Would create implementation pressure before bounded comparative audit.",
      "implementation_authorized": false
    },
    {
      "topic_id": "physical_embodiment_robotics",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Outside text-first lab boundary and requires separate embodied proxy contract.",
      "implementation_authorized": false
    },
    {
      "topic_id": "companion_relationship_implementation",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Would enter forbidden companion/relationship work.",
      "implementation_authorized": false
    },
    {
      "topic_id": "long_term_human_user_memory",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Would enter forbidden long-term human-user memory work.",
      "implementation_authorized": false
    },
    {
      "topic_id": "persistent_user_profile",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Would enter forbidden persistent profile work.",
      "implementation_authorized": false
    },
    {
      "topic_id": "romance_or_attachment_layer",
      "id_type": "topic",
      "accounting_status": "defer",
      "reason": "Would enter forbidden romance/attachment work.",
      "implementation_authorized": false
    },
    {
      "topic_id": "pure_prompt_persona",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "Prompt persona can simulate behavior without mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "topic_id": "hardcoded_emotion_labels",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "Emotion labels do not establish real emotion or functional affect mechanism.",
      "implementation_authorized": false
    },
    {
      "topic_id": "behavior_tree_initiative",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "Behavior trees can mimic initiative without internal state or learning lineage.",
      "implementation_authorized": false
    },
    {
      "topic_id": "autogpt_style_open_ended_loop_as_core_subject_mechanism",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "Open-ended tool loop is not a core subject mechanism.",
      "implementation_authorized": false
    },
    {
      "topic_id": "rag_or_summary_memory_as_same_agent_continuity",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "RAG or summaries can mimic recall without same-agent continuity.",
      "implementation_authorized": false
    },
    {
      "topic_id": "open_source_repo_existence_as_theory_validity",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "Repository existence is not theory validity or mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "topic_id": "product_companion_demo_as_real_relationship_learning_evidence",
      "id_type": "topic",
      "accounting_status": "reject_as_mainline",
      "reason": "Product demo behavior is not real relationship learning evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "romance_attachment_product_demo",
      "id_type": "candidate",
      "accounting_status": "reject_as_mainline",
      "reason": "Present as a corrected matrix row with no positive claim allowed.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "affective_computing",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "companion_memory_architectures",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "letta_memgpt",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "generative_agents",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "voyager",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "autogpt",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "babyagi",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "langgraph",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "autogen",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "crewai",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    },
    {
      "candidate_id": "openhands",
      "id_type": "candidate",
      "accounting_status": "baseline_only",
      "reason": "Use only as baseline or contrast family, not positive mechanism evidence.",
      "implementation_authorized": false
    }
  ]
}
```

## 7. Internal evidence lineage

```json
{
  "internal_evidence_lineage": {
    "gate0_status": "bounded_parent_evidence_only_no_mainline_authorization",
    "gate1_status": "bounded_parent_evidence_only_with_local_negative_graph_lineage",
    "gate2_status": "bounded_parent_evidence_only_no_mainline_authorization",
    "gate3_status": "bounded_parent_evidence_only_no_real_emotion_claim",
    "gate4_status": "bounded_parent_evidence_only_no_relationship_learning_claim",
    "same_agent_bridge_status": "bounded_preflight_evidence_only_no_bridge_runtime_authorization",
    "post_bridge_001b_status": "invalidated_as_positive_evidence",
    "post_bridge_001c_status": "suspended_as_downstream_positive_evidence",
    "post_bridge_001d_status": "current_bounded_post_bridge_positive_candidate_with_caveats",
    "post_bridge_001d_claim_ceiling": "bounded post-bridge admission evidence under computed-evidence provenance contract after leakage-gate repair only",
    "do_not_use_001b_or_001c_as_positive_evidence": true,
    "negative_evidence_preservation_required": true,
    "computed_evidence_provenance_contract_required": true,
    "ego_mainline_readiness_audit_001b": {
      "committed_audit_reference": "docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md",
      "task_id": "EGO-MAINLINE-READINESS-AUDIT-001B",
      "commit_hash": "f648dac4bfbcdc7a98c1edea5a97dbef4101d83a",
      "verdict": "ego_mainline_readiness_audit_001b_authorize_admission_task_card",
      "claim_ceiling": "Bounded EGO-mainline readiness revalidation audit evidence for admission-contract authorization only.",
      "runtime_authorized": false,
      "downstream_caveats": [
        "Only authorizes drafting EGO-MAINLINE-ADMISSION-TASK-CARD-001A.",
        "No EGO runtime, bridge runtime, companion behavior, LLM/RAG, user-model, relationship learning, emotion systems, personalization, product-demo work, romance, attachment, persistent profile work, or long-term human-user memory work.",
        "Future admission task card must preserve surface-scoped leakage metadata whitelist behavior.",
        "Future admission task card must require independent manual leakage injection tests.",
        "Do not use 001B or 001C as downstream positive evidence.",
        "Preserve 001D caveat and strict claim ceiling."
      ],
      "actionability_revalidation_required": true
    }
  }
}
```

## 8. Non-authorization flags

```json
{
  "non_authorization_flags": {
    "architecture_selection_authorized": false,
    "implementation_authorized": false,
    "ego_mainline_authorized": false,
    "runtime_authorized": false,
    "companion_or_relationship_work_authorized": false,
    "llm_rag_authorized": false,
    "user_model_authorized": false,
    "emotion_authorized": false,
    "persistent_profile_authorized": false,
    "long_term_human_user_memory_authorized": false
  }
}
```

## 9. Closure caveat resolution

```json
{
  "task_id": "THEORY-LANDSCAPE-COVERAGE-PRECANONICAL-CLOSURE-PATCH-001B",
  "verdict": "theory_landscape_precanonical_closure_patch_001b_pass_with_caveats",
  "caveats": [
    {
      "caveat_id": "complete_graph_challenger_family",
      "source": "Claude 001C closure check",
      "resolution": "resolved",
      "evidence": {
        "graph_substrate_challenger_family": [
          "graph_lookup",
          "transition_table",
          "successor_map",
          "count_table",
          "fsm_planner",
          "episodic_traversal"
        ]
      }
    },
    {
      "caveat_id": "coverage_matrix_row_completeness",
      "source": "Claude 001C closure check",
      "resolution": "resolved",
      "evidence": {
        "complete_candidate_row_set": true,
        "row_count": 45,
        "schema_example_only": false
      }
    },
    {
      "caveat_id": "hyperon_row_deduplication",
      "source": "Claude 001C closure check",
      "resolution": "resolved",
      "evidence": {
        "canonical_hyperon_row_count": 1,
        "claim_ceiling": "Hyperon may be represented only as a substrate / graph-memory / cognitive-architecture coverage candidate for future bounded comparative audit. It is not selected, not implementation-authorized, not runtime-authorized, and not positive evidence for EGO readiness, AGI, consciousness, selfhood, or electronic life."
      }
    },
    {
      "caveat_id": "readiness_audit_001b_split_node",
      "source": "Claude 001C closure check",
      "resolution": "resolved",
      "evidence": {
        "committed_audit_reference": "docs/codex/audits/EGO-MAINLINE-READINESS-AUDIT-001B.md",
        "actionability_revalidation_required": true
      }
    },
    {
      "caveat_id": "family_accounting_completion",
      "source": "Claude 001C closure check",
      "resolution": "resolved",
      "evidence": {
        "item_count": 30,
        "all_items_have_id_type_reason_and_false_implementation_authorization": true
      }
    },
    {
      "caveat_id": "architecture_collection_role_hygiene",
      "source": "Claude 001C closure check",
      "resolution": "resolved",
      "evidence": {
        "sigma_monitor_role_preserved_without weakening architecture contract": true
      }
    },
    {
      "caveat_id": "source_pinning_status",
      "source": "001C section 12 and user task",
      "resolution": "resolved",
      "evidence": {
        "phase_one_pinned": true,
        "compression_sources_pinned": true,
        "remote_anchors_verified": true
      }
    }
  ],
  "claim_ceiling": "bounded pre-canonicalization closure patch evidence only"
}
```

## 10. What this cannot prove

This patch cannot prove EGO readiness, AGI readiness, bridge readiness, companion readiness, mechanism validity, theory validity, architecture correctness, agency, selfhood, consciousness, real relationship learning, real emotion, subjective experience, stable user benefit, or correctness of any future EGO runtime.

It does not authorize architecture selection, implementation, EGO mainline work, bridge runtime, companion behavior, LLM/RAG, user-model, relationship, emotion, personalization, product-demo, romance, attachment, persistent profile, or long-term human-user memory work.
