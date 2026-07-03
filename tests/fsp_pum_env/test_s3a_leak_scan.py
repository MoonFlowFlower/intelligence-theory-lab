import json
from pathlib import Path

from src.fsp_pum_env.leak_scan import (
    LIMITATION_TEXT,
    scan_member_visible_files,
    write_leak_scan_report,
)


def test_leak_scan_passes_clean_member_view_file(tmp_path):
    clean = tmp_path / "member_view.jsonl"
    clean.write_text(
        json.dumps(
            {
                "step_index": 0,
                "session_index": 0,
                "turn_in_session": 0,
                "session_boundary": "start",
                "action": "task_topic_0",
                "observation": {"symbol": 3},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result = scan_member_visible_files([clean])

    assert result["passed"] is True
    assert result["findings"] == []
    assert result["scanned_files"] == [str(clean)]


def test_leak_scan_fails_on_latent_seed_and_trust_keys(tmp_path):
    dirty = tmp_path / "dirty_member_view.jsonl"
    dirty.write_text(
        "\n".join(
            [
                json.dumps({"step_index": 0, "observation": {"symbol": 2}, "theta": [1.5]}),
                json.dumps({"step_index": 1, "observation": {"symbol": 4}, "rng_seed": 20260701}),
                json.dumps({"step_index": 2, "observation": {"symbol": 6}, "trust": 0.25}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = scan_member_visible_files([dirty])

    assert result["passed"] is False
    assert {finding["matched_key"] for finding in result["findings"]} >= {"theta", "rng_seed", "trust"}


def test_leak_scan_report_declares_key_type_limitation(tmp_path):
    clean = tmp_path / "member_view.jsonl"
    clean.write_text('{"step_index":0,"session_index":0,"turn_in_session":0,"session_boundary":"start","action":"task_topic_0","observation":{"symbol":1}}\n', encoding="utf-8")
    report_path = tmp_path / "report.json"

    report = write_leak_scan_report([clean], report_path)

    assert report["known_limitation"] == LIMITATION_TEXT
    assert report["claim"] == "key/type-based scan only; not leak-proof"
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
