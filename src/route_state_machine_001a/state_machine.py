from __future__ import annotations

TASK_ID = "ROUTE-STATE-MACHINE-001A"
TASK_ARTIFACT_DIR = "artifacts/ROUTE-STATE-MACHINE-001A"
PROGRAM_STATE_FILENAME = "program_state.json"
CURRENT_FRONTIER_ROUTE_ID = "N2-SBMC-ENV-REDESIGN-001A"
K0_PARENT_ROUTE_ID = "K0-DUAL-TRACK-SUPERSESSION-001A"
K0_PARENT_ALLOWED_ACTIONS = (
    "bank_ordered_child_cards",
    "run_route_state_machine_validation",
)
K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS = (
    "agency",
    "autonomy",
    "code_first_prebank_implementation",
    "consciousness",
    "ego_mainline_runtime",
    "experiment_execution",
    "formal_run",
    "foundation_implementation",
    "freeze",
    "h0_implementation",
    "h1_implementation",
    "k0_reference_implementation",
    "mechanism_validity",
    "remote_anchor",
    "scoring",
    "subjectivity",
    "theory_pressure",
    "ui_llm_deployment",
)
K0_RED_FIELD_ADDENDUM_PHASE = "FIRST_PAIR_READY_WITH_RED_FIELD_ADDENDUM"
K0_RED_FIELD_CORRECTION_PHASE = "FIRST_PAIR_READY_WITH_RED_FIELD_CORRECTION"
K0_H0_ADMISSION_PHASE = "FOUNDATION_READY_H0_ADMISSION_002A_REVIEW_REQUIRED"
K0_READY_PHASE = "CODE_FIRST_H0_PREBANK_AUTHORIZED"
K0_READY_ALLOWED_ACTIONS = (
    "implement_EGO-K0-FOUNDATION-001A",
    "implement_ITL-K0-H0-CODE-FIRST-PREBANK-001A",
    "run_route_state_machine_validation",
)
K0_READY_AUTHORIZED_IMPLEMENTATION_TARGETS = (
    "EGO-K0-FOUNDATION-001A",
    "ITL-K0-H0-CODE-FIRST-PREBANK-001A",
)
K0_READY_CHILD_AUTHORIZATIONS = {
    "EGO-K0-FOUNDATION-001A": True,
    "ITL-K0-H0-H1-INSTRUMENT-001A:H0": False,
    "EGO-K0-REFERENCE-KERNEL-001A": False,
    "ITL-K0-H0-H1-INSTRUMENT-001A:H1": False,
    "K0-IMMUTABLE-FREEZE-001A": False,
    "ITL-K0-FORMAL-EVIDENCE-001A": False,
}
K0_READY_REQUIRED_TRUE_AUTHORIZATIONS = (
    "code_first_prebank_implementation",
    "foundation_implementation",
)
K0_READY_REQUIRED_FALSE_AUTHORIZATIONS = tuple(
    key
    for key in K0_PARENT_REQUIRED_FALSE_AUTHORIZATIONS
    if key not in K0_READY_REQUIRED_TRUE_AUTHORIZATIONS
)
K0_READY_CHILD_CARD_BANKS = {
    "ego_foundation": "13bd9268993f74a41b4cc219855761681ab12b66",
    "ego_reference_kernel": "0f043254710b47700f2088213232aba777bd3f46",
    "itl_instrument_freeze_formal": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
}
K0_READY_BANKED_CARD_OBJECTS = (
    {
        "task_id": "K0-DUAL-TRACK-SUPERSESSION-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md",
        "blob": "11b0e09025d1064a1eb790f42d79f1db3c690f6d",
    },
    {
        "task_id": "EGO-K0-FOUNDATION-001A",
        "repo": "Ego",
        "commit": "13bd9268993f74a41b4cc219855761681ab12b66",
        "path": "docs/codex/tasks/ego-k0-foundation-001a/STAGE_CARD.md",
        "blob": "f100d78e48b8d9b21327ed86a5fb35305d11d534",
    },
    {
        "task_id": "EGO-K0-REFERENCE-KERNEL-001A",
        "repo": "Ego",
        "commit": "0f043254710b47700f2088213232aba777bd3f46",
        "path": "docs/codex/tasks/ego-k0-reference-kernel-001a/STAGE_CARD.md",
        "blob": "55f7ac62bf8aad61b3140c213812d7fb9a166acb",
    },
    {
        "task_id": "ITL-K0-H0-H1-INSTRUMENT-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/ITL-K0-H0-H1-INSTRUMENT-001A.md",
        "blob": "a642c5734d57af450104b115181a2f7dc18bb646",
    },
    {
        "task_id": "K0-IMMUTABLE-FREEZE-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/K0-IMMUTABLE-FREEZE-001A.md",
        "blob": "6f01764c2194061fa60c1b84ef6702c7a533cbea",
    },
    {
        "task_id": "ITL-K0-FORMAL-EVIDENCE-001A",
        "repo": "intelligence-theory-lab",
        "commit": "56f56a998a0ec6e897f98d9ce51a0d8b06eb0f92",
        "path": "docs/codex/tasks/ITL-K0-FORMAL-EVIDENCE-001A.md",
        "blob": "c0ce00ff953b389282ba16435ddc884564e2f27e",
    },
)
K0_PARENT_LEDGER_PATH = "docs/research/FSP-STAGE-LEDGER.md"
K0_PARENT_LEDGER_ENTRY_PREFIX = (
    "- L-020 | 2026-07-09 | transition_decision (operator accepted; transcribed by Codex) | "
    "K0 dual-track supersession REGISTERED under "
    "`docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md`."
)
K0_READY_LEDGER_ENTRY_PREFIX = (
    "- L-021 | 2026-07-09 | transition_decision (operator accepted; transcribed by Codex) | "
    "K0 dual-track moved REGISTERED -> READY_TO_IMPLEMENT for exactly "
    "`EGO-K0-FOUNDATION-001A` and `ITL-K0-H0-H1-INSTRUMENT-001A:H0`."
)
K0_READY_TRANSITION_CARD_PATH = "docs/codex/tasks/K0-DUAL-TRACK-READY-TRANSITION-001A.md"
K0_RED_FIELD_ADDENDUM_CARD_PATH = "docs/codex/tasks/K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A.md"
K0_RED_FIELD_CONTRACT_PATH = (
    "artifacts/K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A/red_field_contract.json"
)
K0_RED_FIELD_ADDENDUM_PIN = {
    "task_id": "K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A",
    "bank_commit": "bfbe215518a8f31fd300e600c73bb9d59e635335",
    "card_path": K0_RED_FIELD_ADDENDUM_CARD_PATH,
    "card_blob": "cc8b2720374bec1b566ede3c11d87c2290fb8345",
    "contract_path": K0_RED_FIELD_CONTRACT_PATH,
    "contract_blob": "ba1c55cfeeffbbf7e3c0da15b8b52dd836ef6511",
    "contract_sha256": "c1ada02360b26892ca4728b4c53ae36fa8dbf7f7202697c4288f64a1cb7be59c",
    "applies_to": ["K0-DUAL-TRACK", "ITL-K0-H0-H1-INSTRUMENT-001A:H0"],
    "precedence": "additive_overlay_controls_conflicting_K0_red_field_schema_and_enforcement_only",
    "required_before": ["bank_ITL-K0-H0-H1-INSTRUMENT-001A_H0"],
    "red_field_gate_status": "BANKED_AND_ENFORCED",
}
K0_RED_FIELD_LEDGER_ENTRY_PREFIX = (
    "- L-022 | 2026-07-09 | governance_addendum (operator authorized; transcribed by Codex) | "
    "K0 Red-field addendum `K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A` banked and enforced as the H0 prerequisite."
)
K0_RED_FIELD_CORRECTION_CARD_PATH = "docs/codex/tasks/K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A.md"
K0_RED_FIELD_CORRECTION_CONTRACT_PATH = (
    "artifacts/K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A/red_field_correction_contract.json"
)
K0_RED_FIELD_CORRECTION_PIN = {
    "task_id": "K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A",
    "bank_commit": "882be402395e7301cf69fcc0a0bae1eca8dfcd68",
    "card_path": K0_RED_FIELD_CORRECTION_CARD_PATH,
    "card_blob": "a186c78028a69a81c408f3985fa0112fae10b9a0",
    "contract_path": K0_RED_FIELD_CORRECTION_CONTRACT_PATH,
    "contract_blob": "9fcb9a0036fe09232f5a8619c755b24703d2c2d9",
    "contract_sha256": "2faa270dabebc4f83b8d51b689592a28fdfee96e44a80049835b40b31e304399",
    "applies_to": ["K0-DUAL-TRACK", "ITL-K0-H0-H1-INSTRUMENT-001A:H0"],
    "precedence": "additive_correction_controls_conflicting_red_field_terminal_formula_power_coverage_rng_and_claim_ceiling_fields_only",
    "required_before": ["bank_ITL-K0-H0-H1-INSTRUMENT-001A_H0"],
    "red_field_correction_gate_status": "BANKED_AND_ENFORCED",
}
K0_RED_FIELD_CORRECTION_LEDGER_ENTRY_PREFIX = (
    "- L-023 | 2026-07-09 | governance_correction (operator authorized; transcribed by Codex) | "
    "K0 Red-field semantic correction `K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A` banked and enforced as the final H0 prerequisite."
)
K0_H0_ADMISSION_CARD_PATH = "docs/codex/tasks/ITL-K0-H0-ADMISSION-CONTRACT-002A.md"
K0_H0_EFFECTIVE_CONTRACT_PATH = (
    "artifacts/ITL-K0-H0-ADMISSION-CONTRACT-002A/effective_h0_contract.json"
)
K0_H0_ADMISSION_PIN = {
    "task_id": "ITL-K0-H0-ADMISSION-CONTRACT-002A",
    "bank_commit": "baa7751cb04d2d365e50f2cd15e799bc40641042",
    "card_path": K0_H0_ADMISSION_CARD_PATH,
    "card_blob": "3e785f5b67212a0cc5d7f956126093c0b2ecd3d6",
    "contract_path": K0_H0_EFFECTIVE_CONTRACT_PATH,
    "contract_blob": "cd00a47810d7ed7218d22c24bac1a6cdcf152b6d",
    "contract_sha256": "668c52e0b4b9fc9a6405791a6b520b4a216bb1bd2b6578c0e3f9b2463091cfc8",
    "applies_to": ["K0-DUAL-TRACK", "ITL-K0-H0-H1-INSTRUMENT-001A:H0"],
    "precedence": "sole_effective_h0_semantic_source_no_implicit_inheritance",
    "required_before": ["independent_review", "separate_ready_transition"],
    "status": "BANKED_ENFORCED_REVIEW_REQUIRED",
}
K0_H0_ADMISSION_HISTORICAL_PIN = {
    **K0_H0_ADMISSION_PIN,
    "status": "ADMISSION_SEMANTIC_REVIEW_FAILED_HISTORICAL_ONLY",
}
K0_H0_EFFECTIVE_AUTHORITY = {
    "single_effective_semantic_source": K0_H0_EFFECTIVE_CONTRACT_PATH,
    "implicit_historical_inheritance": False,
    "historical_pins_retained": True,
    "historical_pins_semantic_authority": False,
}
K0_CODE_FIRST_TASK_CARD_PATH = "docs/codex/tasks/ITL-K0-H0-CODE-FIRST-PREBANK-001A.md"
K0_CODE_FIRST_TASK_PIN = {
    "task_id": "ITL-K0-H0-CODE-FIRST-PREBANK-001A",
    "bank_commit": "1fcafdc317fb3aed3b3e1cbf057e1f460e9308bd",
    "card_path": K0_CODE_FIRST_TASK_CARD_PATH,
    "card_blob": "523ea303c62b893d62db62fe6febb2ca3f2a5a88",
    "card_sha256": "19aefb27620bbc494d81065b4f44c01660c078409afaf551cb18aa7b01f6ff99",
    "status": "BANKED_CODE_FIRST_PREBANK_AUTHORIZED",
}
K0_CODE_FIRST_AUTHORITY = {
    "code_first_task_card": K0_CODE_FIRST_TASK_CARD_PATH,
    "domain_semantics_location": "src/itl_k0_h0_h1_instrument_001a/",
    "historical_admission_contract": K0_H0_EFFECTIVE_CONTRACT_PATH,
    "historical_contract_semantic_authority": False,
    "route_validator_interprets_h0_domain_semantics": False,
    "status": "CODE_FIRST_PREBANK_AUTHORIZED",
}
K0_H0_ADMISSION_LEDGER_ENTRY_PREFIX = (
    "- L-024 | 2026-07-09 | governance_replacement (operator authorized; transcribed by Codex) | "
    "Consolidated H0 admission contract `ITL-K0-H0-ADMISSION-CONTRACT-002A` banked and enforced as the sole effective H0 semantic source; H0 moved true -> false pending independent review and a separate READY transition."
)
K0_CODE_FIRST_LEDGER_ENTRY_PREFIX = (
    "- L-025 | 2026-07-09 | governance_replacement (operator authorized; transcribed by Codex) | "
    "H0 admission 002A semantic review failed and code-first prebank `ITL-K0-H0-CODE-FIRST-PREBANK-001A` was authorized."
)
K0_PARENT_LEDGER_LINE_SHA256 = "6dbc32929d0df4e646ce1af3a8010cf17f9d46ca79586f1c98075b0648f325cb"
K0_READY_LEDGER_LINE_SHA256 = "74fc0796fa500132809409364471d04ffb78315ce3bf20d8c30c58857b290cf5"
K0_RED_FIELD_LEDGER_LINE_SHA256 = "a5626cc32c83d84db46ac3f8a8ba5af755e7c2724aebdde7070b5ba3a7130a46"
K0_RED_FIELD_CORRECTION_LEDGER_LINE_SHA256 = "aa4be0e838de1769e6583b108f82700d3627ffeb5023ad46dc40a89ea6dfa909"
K0_H0_ADMISSION_LEDGER_LINE_SHA256 = "86c12243732f029d28fc57ab1c2a5f2919193066c10f7b7701b2b72c646231ed"
K0_RED_FIELD_PRESERVED_LEDGER_HASHES = {
    "L-020": K0_PARENT_LEDGER_LINE_SHA256,
    "L-021": K0_READY_LEDGER_LINE_SHA256,
    "L-022": K0_RED_FIELD_LEDGER_LINE_SHA256,
    "L-023": K0_RED_FIELD_CORRECTION_LEDGER_LINE_SHA256,
}
K0_H0_ADMISSION_EVENT = "h0_admission_contract_002a_banked_review_required"
K0_H0_PRESERVED_EVENT_COUNT = 5
K0_H0_PRESERVED_EVENTS_SHA256 = "bcdbd498c02b1c5d8c4f71870b1e452702c23c575fb6ea5f0215d05b8a5427b5"
K0_CODE_FIRST_AUTH_EVENT = "h0_admission_002a_semantic_review_failed_code_first_prebank_authorized"
K0_CODE_FIRST_PRESERVED_EVENT_COUNT = 6
K0_CODE_FIRST_PRESERVED_EVENTS_SHA256 = "3e4d1e14a9a7512095b38aeb46af729b7de0ae240e99b4cb5abe2c46d7b8fcc4"
K0_CODE_FIRST_PRESERVED_LEDGER_HASHES = {
    **K0_RED_FIELD_PRESERVED_LEDGER_HASHES,
    "L-024": K0_H0_ADMISSION_LEDGER_LINE_SHA256,
}
K0_H0_EVIDENCE_COMPONENT_IDS = (
    "V_model",
    "V_online",
    "V_replay",
    "V_memory",
    "V_transfer",
)
K0_H0_EVIDENCE_STATES = (
    "NOT_TESTED",
    "INVALID_INSTRUMENT",
    "ABSENT",
    "PRESENT_BOUNDED",
)
K0_H0_ADMISSION_CLAIM_CEILING = (
    "consolidated H0 admission task-card/schema/control-plane enforcement only"
)
K0_H0_FUTURE_CLAIM_CEILING = "immutable instrument preregistration contract banked only"
K0_H0_ORIGINAL_ARTIFACT_FILENAMES = (
    "h0_contract.json",
    "task_family_manifest.json",
    "generator_distribution.json",
    "adapter_capability_manifest.json",
    "access_budget_manifest.json",
    "metric_mde_contract.json",
    "baseline_panel.json",
    "component_control_mapping.json",
    "component_dependency_matrix.json",
    "protocol_manifest.json",
    "positive_control_manifest.json",
    "heldout_preimage_schema.json",
    "heldout_seal_manifest.json",
    "own_rule_constructor_contract.json",
    "public_dev_fixture_manifest.json",
    "smoke_contract.json",
    "h0_acceptance.json",
    "claim_ceiling.txt",
)
K0_H0_ADDED_ARTIFACT_FILENAMES = (
    "control_signature_contract.json",
    "control_signature_simulation.json",
    "determinism_contract.json",
    "control_signature_coverage_report.json",
)
K0_H0_FAILURE_ARTIFACT_FILENAME = "failure_manifest.json"
K0_H0_REPO_WRITE_ALLOWLIST = (
    "src/itl_k0_h0_h1_instrument_001a/__init__.py",
    "src/itl_k0_h0_h1_instrument_001a/h0_freeze.py",
    "tests/itl_k0_h0_h1_instrument_001a/test_h0_freeze.py",
    *(
        f"artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h0/{name}"
        for name in (
            K0_H0_ORIGINAL_ARTIFACT_FILENAMES
            + K0_H0_ADDED_ARTIFACT_FILENAMES
            + (K0_H0_FAILURE_ARTIFACT_FILENAME,)
        )
    ),
)
K0_H0_EXTERNAL_SIDE_EFFECT_ALLOWLIST = (
    "C:/Users/LEO/AppData/Local/EGO_K0_SEALED/ITL-K0-H0-H1-INSTRUMENT-001A/heldout_preimage.json",
)
K0_RED_FIELD_EVIDENCE_STATES = (
    "NOT_TESTED",
    "INVALID_INSTRUMENT",
    "ABSENT",
    "PRESENT_BOUNDED",
)
K0_RED_FIELD_CONTROL_STATES = (
    "NOT_APPLICABLE",
    "CONTROL_NOT_RUN",
    "CONTROL_INCONCLUSIVE",
    "CONTROL_EQUIVALENT",
    "CONTROL_SEPARATED",
)
K0_RED_FIELD_RIVAL_STATES = (
    "NOT_APPLICABLE",
    "RIVAL_NOT_RUN",
    "RIVAL_INCONCLUSIVE",
    "RIVAL_SATURATED",
    "RIVAL_SEPARATED",
)
K0_RED_FIELD_CORRECTED_CONTROL_STATES = K0_RED_FIELD_CONTROL_STATES + ("CONTROL_DOMINATED",)
K0_RED_FIELD_CORRECTED_RIVAL_STATES = K0_RED_FIELD_RIVAL_STATES + ("RIVAL_DOMINATED",)
K0_RED_FIELD_CORRECTED_CONTROL_EQUIVALENCE_TYPES = (
    "CANDIDATE_PARITY",
    "ADMISSION_CEILING_SATURATION",
    "OWN_RULE_AMORTIZED_PARITY",
    None,
)
K0_RED_FIELD_CORRECTION_CLAIM_CEILING = {
    "allowed": ["task_card_schema_control_plane_enforcement_only"],
    "forbidden": [
        "learned_model",
        "online_learning",
        "replay_contribution",
        "memory_causality",
        "transfer",
        "initiative",
        "agency",
        "autonomy",
        "subjectivity",
        "consciousness",
        "real_emotion",
        "functional_subject",
        "electronic_life",
        "EGO_readiness",
        "product_benefit",
        "mainline_effect",
    ],
}
K0_RED_FIELD_ARM_ROLES = (
    "CAUSAL_ABLATION",
    "SHORTCUT_CONTROL",
    "RIVAL",
    "INTEGRITY_CONTROL",
)
K0_RED_FIELD_COMPONENT_IDS = (
    "V_model",
    "V_online",
    "V_replay",
    "V_memory",
    "V_transfer",
    "V_special",
)
K0_RED_FIELD_GRAPH_CACHE_ARMS = (
    "graph_lookup",
    "transition_table",
    "successor_map",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
)

ROUTE_STATES = (
    "PROPOSED",
    "REGISTERED",
    "READY_TO_IMPLEMENT",
    "IMPLEMENTING",
    "RUN_ATTEMPTED",
    "EVIDENCE_PACKET_READY",
    "CLOSURE_REVIEW_REQUIRED",
    "ADJUDICATED",
    "NEXT_FRONTIER_ASSIGNED",
    "REDESIGN_REQUIRED",
    "RERUN_REQUIRED",
    "OPS_FIX_REQUIRED",
    "TOMBSTONED",
)

CLOSURE_TYPES = (
    "THEORY_PRESSURE",
    "INSTRUMENT_INVALID",
    "BASELINE_EQUIVALENCE",
    "IMPLEMENTATION_DEFECT",
    "OPERATION_ERROR",
    "LEAKAGE_OR_CHEATING",
    "METRIC_DEGENERACY",
    "UNDERPOWERED",
    "GOVERNANCE_STOP",
    "INCONCLUSIVE",
    "SCOPE_MISMATCH",
    "ARTIFACT_ONLY",
)

REQUIRED_THEORY_PRESSURE_EVIDENCE = (
    "baseline",
    "ablation",
    "replay",
    "provenance",
)

CURRENT_FRONTIER_FORBIDDEN_AUTHORIZATIONS = (
    "mechanism_validity",
    "theory_pressure",
    "scoring",
    "experiment_execution",
)

CURRENT_FRONTIER_FORBIDDEN_ACTION_TOKENS = (
    "mechanism_validity",
    "mechanism validity",
    "theory_pressure",
    "theory pressure",
    "score",
    "scoring",
    "experiment",
    "execution",
)

AUTHORIZED_TASK_PATHS = (
    "docs/codex/tasks/ROUTE-STATE-MACHINE-001A.md",
    "docs/codex/tasks/ROUTE-STATE-MACHINE-001B-CURRENT-FRONTIER-GATE.md",
    "docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md",
    "docs/codex/tasks/K0-DUAL-TRACK-READY-TRANSITION-001A.md",
    "docs/codex/tasks/K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A.md",
    "docs/codex/tasks/K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A.md",
    "docs/codex/tasks/ITL-K0-H0-ADMISSION-CONTRACT-002A.md",
    "docs/codex/tasks/ITL-K0-H0-CODE-FIRST-PREBANK-001A.md",
    "docs/research/FSP-STAGE-LEDGER.md",
    "docs/research/ROUTE-STATE-MACHINE-001A.md",
    "docs/research/ROUTE-STATE-MACHINE-001B-CURRENT-FRONTIER-GATE.md",
    "src/route_state_machine_001a/__init__.py",
    "src/route_state_machine_001a/routectl.py",
    "src/route_state_machine_001a/state_machine.py",
    "src/route_state_machine_001a/validator.py",
    "tests/route_state_machine_001a/test_validator.py",
    "artifacts/ROUTE-STATE-MACHINE-001A/program_state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/schemas/route_state.schema.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/schemas/closure_packet.schema.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/closure.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/events.jsonl",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/events.jsonl",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/state.json",
    "artifacts/ROUTE-STATE-MACHINE-001A/routes/K0-DUAL-TRACK-SUPERSESSION-001A/events.jsonl",
    "artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md",
    "artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json",
    "artifacts/K0-DUAL-TRACK-RED-FIELD-ADDENDUM-001A/red_field_contract.json",
    "artifacts/K0-DUAL-TRACK-RED-FIELD-CORRECTION-001A/red_field_correction_contract.json",
    "artifacts/ITL-K0-H0-ADMISSION-CONTRACT-002A/effective_h0_contract.json",
)

ROADMAP_LIKE_MARKERS = (
    "roadmap",
    "new-mechanism",
    "mechanism-route",
    "route-candidate",
    "frontier",
    "admission",
    "bridge",
    "mainline",
    "runtime",
    "ego-readiness",
)

TERMINAL_STATES = (
    "ADJUDICATED",
    "NEXT_FRONTIER_ASSIGNED",
    "REDESIGN_REQUIRED",
    "RERUN_REQUIRED",
    "OPS_FIX_REQUIRED",
    "TOMBSTONED",
)
