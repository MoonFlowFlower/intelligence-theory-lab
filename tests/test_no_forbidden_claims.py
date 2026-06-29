from itl_devbench.eval.audit import audit_manifest
from itl_devbench.eval.run_matrix import run_benchmark


def test_audit_succeeds_normally_and_fails_on_forbidden_claim_injection(tmp_path):
    run_dir = run_benchmark(
        config={"width": 7, "height": 7, "max_ticks": 12, "smoke_seeds": [0]},
        smoke=True,
        output_root=tmp_path,
    )

    clean = audit_manifest(run_dir / "manifest.json")
    assert clean["verdict"] == "audit_succeeded"

    report_path = run_dir / "report.md"
    report_path.write_text(
        report_path.read_text(encoding="utf-8") + "\nThis would be a forbidden consciousness claim.\n",
        encoding="utf-8",
    )
    dirty = audit_manifest(run_dir / "manifest.json")

    assert dirty["verdict"] == "audit_failed"
    assert any(check["name"] == "forbidden_claim_strings_absent" for check in dirty["failed_checks"])
