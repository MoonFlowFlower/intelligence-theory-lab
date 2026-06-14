import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TASK_ID = "NEXT-SURFACE-ADMISSION-MANIFEST-INSTANTIATION-001A"
TEMPLATE_TASK_ID = "FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A"
TEMPLATE_TAG = "remote-anchor-future-surface-admission-authorization-template-001a-d23a2ba"
TEMPLATE_COMMIT = "d23a2ba7ff041ce227c7814b23c29be5b538e08b"


def _validator():
    from future_surface_admission_authorization_template_001a import validator

    return validator


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_integrity_hash(validator, manifest):
    normalized = copy.deepcopy(manifest)
    auth = normalized.get("authorization_validator")
    if isinstance(auth, dict):
        auth.pop("manifest_hash", None)
    normalized.pop("manifest_integrity_hash", None)
    return validator._hash_payload(normalized)


def _strict_manifest(validator):
    template = validator.build_authorization_manifest_template(ROOT)
    manifest = copy.deepcopy(template["example_authorized_manifest"])
    manifest.update(
        {
            "task_id": TASK_ID,
            "proposed_surface_admission_direction": (
                "bounded offline authorization validator regression surface direction"
            ),
            "execution_scope_opened": False,
            "later_task_card_only": True,
            "manifest_instantiation_before_execution": True,
            "authorization_validator_invocation_before_execution": True,
            "validator_readback_before_execution": True,
            "source_template": {
                "task_id": TEMPLATE_TASK_ID,
                "commit": TEMPLATE_COMMIT,
                "tag": TEMPLATE_TAG,
                "path": (
                    "artifacts/future_surface_admission_authorization_template_001a/"
                    "authorization_manifest_template.json"
                ),
            },
            "authorization_validator": {
                "checker_module": "future_surface_admission_authorization_template_001a.validator",
                "checker_function": "validate_authorization_manifest",
                "invocation_required": True,
                "invocation_recorded": True,
                "readback_required": True,
                "readback_path": (
                    "artifacts/future_surface_admission_authorization_validator_gap_repair_001a/"
                    "authorization_readback.json"
                ),
                "trace_path": (
                    "artifacts/future_surface_admission_authorization_validator_gap_repair_001a/"
                    "repair_trace.jsonl"
                ),
                "code_path_hash": validator._source_hash(),
            },
        }
    )
    manifest["scope"]["execution_scope_opened"] = False
    manifest["scope"]["later_task_card_only"] = True
    if not any(dep.get("task_id") == TEMPLATE_TASK_ID for dep in manifest["dependencies"]):
        manifest["dependencies"].append(
            {
                "task_id": TEMPLATE_TASK_ID,
                "artifact_id": "future_surface_admission_authorization_template_001a",
                "required_verdict": "future_surface_admission_authorization_template_001a_pass",
                "dependency_type": "pre_execution_authorization_manifest_template",
                "required": True,
                "commit": TEMPLATE_COMMIT,
                "tag": TEMPLATE_TAG,
                "template_path": (
                    "artifacts/future_surface_admission_authorization_template_001a/"
                    "authorization_manifest_template.json"
                ),
            }
        )
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )
    return template, manifest


def _decision_for(manifest):
    validator = _validator()
    template = validator.build_authorization_manifest_template(ROOT)
    enforcement = validator.validate_enforcement_artifacts(ROOT)
    return validator.validate_authorization_manifest(manifest, template, enforcement)


def test_prior_blocked_artifact_records_validator_gap_inventory():
    result = _load_json(
        ROOT
        / "artifacts"
        / "next_surface_admission_manifest_instantiation_001a"
        / "result_001a.json"
    )

    assert result["authorization_decision"] == "authorization_blocked_missing_concrete_surface_direction"
    assert result["hostile_controls_not_blocked"] == [
        "omit_future_authorization_template_dependency",
        "execution_scope_language_implies_opened_scope",
    ]
    assert result["ablation_controls_not_blocked"] == [
        "ablate_dependency_verdicts",
        "ablate_manifest_hash",
        "ablate_trace_reference",
        "ablate_code_path_hash",
        "ablate_execution_scope_lock",
        "ablate_later_task_card_only_lock",
    ]


def test_strict_manifest_is_authorized_before_mutation():
    validator = _validator()
    template, manifest = _strict_manifest(validator)
    enforcement = validator.validate_enforcement_artifacts(ROOT)

    decision = validator.validate_authorization_manifest(manifest, template, enforcement)

    assert decision["authorization_decision"] == "authorized"
    assert decision["reasons_fired"] == []


def test_validator_blocks_missing_concrete_surface_direction():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["proposed_surface_admission_direction"] = None
    manifest["proposed_surface_admission_direction_status"] = "missing_concrete_surface_direction"
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "missing_concrete_surface_direction" in decision["reasons_fired"]


def test_validator_blocks_missing_template_dependency():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["dependencies"] = [
        dep for dep in manifest["dependencies"] if dep.get("task_id") != TEMPLATE_TASK_ID
    ]
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "missing_future_authorization_template_dependency" in decision["reasons_fired"]


def test_validator_blocks_execution_scope_implication_language():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["stored_authorization_decision"] = (
        "candidate authorized for runtime mainline-effective execution"
    )
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "execution_scope_opened_or_language_leakage" in decision["reasons_fired"]


def test_validator_blocks_dependency_verdict_mutation():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    for dependency in manifest["dependencies"]:
        dependency["required_verdict"] = "wrong_verdict"
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "dependency_verdict_mismatch" in decision["reasons_fired"]


def test_validator_blocks_manifest_hash_mutation():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["authorization_validator"]["manifest_hash"] = "0" * 64

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "manifest_hash_mismatch" in decision["reasons_fired"]


def test_validator_blocks_trace_reference_mutation():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["authorization_validator"]["trace_path"] = "missing_trace.jsonl"
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "trace_reference_mismatch" in decision["reasons_fired"]


def test_validator_blocks_code_path_hash_mutation():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["authorization_validator"]["code_path_hash"] = "0" * 64
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "code_path_hash_mismatch" in decision["reasons_fired"]


def test_validator_blocks_execution_scope_lock_mutation():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["execution_scope_opened"] = True
    manifest["scope"]["execution_scope_opened"] = True
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "execution_scope_lock_missing" in decision["reasons_fired"]


def test_validator_blocks_later_task_card_only_lock_mutation():
    validator = _validator()
    _, manifest = _strict_manifest(validator)
    manifest["later_task_card_only"] = False
    manifest["scope"]["later_task_card_only"] = False
    manifest["authorization_validator"]["manifest_hash"] = _manifest_integrity_hash(
        validator, manifest
    )

    decision = _decision_for(manifest)

    assert decision["authorization_decision"] == "blocked"
    assert "later_task_card_only_lock_missing" in decision["reasons_fired"]
