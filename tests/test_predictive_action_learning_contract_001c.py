"""001C tests: anchored sink, offline verifier, masked equality, fake-pass
detection. All anchoring uses the LOCAL fake TSA (monkeypatched transport);
such tokens must verify cryptographically but be refused as external evidence."""

import base64
import json
import os

import pytest

from predictive_action_learning_contract_001 import config as cfg
from predictive_action_learning_contract_001.runner import run_episode
from predictive_action_learning_contract_001.suite import _base
from predictive_action_learning_contract_001.validator import validate_run_dir
from predictive_action_learning_contract_001c import sink as sinkmod
from predictive_action_learning_contract_001c.compare import compare_run
from predictive_action_learning_contract_001c.fake_tsa import FakeTSA
from predictive_action_learning_contract_001c.verify import verify_run_dir

TS = cfg.SEEDS["test_seed_base"] + 900


@pytest.fixture(scope="module")
def fake_tsa():
    return FakeTSA()


@pytest.fixture()
def anchored_transport(fake_tsa, monkeypatch):
    monkeypatch.setattr(sinkmod, "TRANSPORT", fake_tsa.transport)
    return fake_tsa


def run(tmp, run_id, commit, seed=TS, steps=60, **kw):
    s = _base(run_id, "test", seed, steps, kw.pop("rule", "AS-CYCLE-001"), **kw)
    s["config_manifest_hash"] = "test_config_manifest_hash"
    if commit:
        s["commit"] = commit
    d = os.path.join(str(tmp), run_id)
    return run_episode(s, d), d


def test_anchored_run_verifies_but_is_not_external(tmp_path, anchored_transport):
    _records, d = run(tmp_path, "anchored", "rfc3161_anchored")
    rep = verify_run_dir(d)
    assert rep["ok"], rep["errors"]
    assert rep["n_commits"] == 60
    assert len(rep["anchors"]) >= 2          # seq-0 anchor + final anchor
    assert all(a["ok"] for a in rep["anchors"])
    # cryptographically valid, but test-CA signed => never external evidence
    assert all(a["is_test_ca"] for a in rep["anchors"])
    assert rep["external_valid"] is False


def test_001_validator_accepts_anchored_run(tmp_path, anchored_transport):
    _records, d = run(tmp_path, "anchored_v", "rfc3161_anchored")
    rep = validate_run_dir(d)
    assert rep["ok"], rep


def test_masked_equality_local_mock_vs_anchored(tmp_path, anchored_transport):
    _r1, d1 = run(tmp_path, "lm", None, steps=120)
    _r2, d2 = run(tmp_path, "an", "rfc3161_anchored", steps=120)
    cmpres = compare_run(d2, d1)
    assert cmpres["identical"], cmpres   # seam changes commitment only, not behavior


def test_anchor_precedes_outcome_reveal(tmp_path, anchored_transport):
    records, d = run(tmp_path, "chrono", "rfc3161_anchored")
    anchors = [json.loads(x) for x in open(os.path.join(d, "anchors.log.jsonl"))]
    post0 = next(r for r in records
                 if r["event_type"] == "POST_STEP" and r["t"] == 0)
    seq0 = next(a for a in anchors if a["covers_through_seq"] == 0)
    assert seq0["anchor_monotonic_ns"] < post0["obs_reveal_monotonic_ns"]


def test_tampered_token_rejected(tmp_path, anchored_transport):
    _r, d = run(tmp_path, "tamper", "rfc3161_anchored")
    path = os.path.join(d, "anchors.log.jsonl")
    lines = open(path).read().splitlines()
    a = json.loads(lines[0])
    raw = bytearray(base64.b64decode(a["token_b64"]))
    raw[len(raw) // 2] ^= 0xFF
    a["token_b64"] = base64.b64encode(bytes(raw)).decode()
    lines[0] = json.dumps(a, sort_keys=True, separators=(",", ":"))
    open(path, "w").write("\n".join(lines) + "\n")
    rep = verify_run_dir(d)
    assert not rep["ok"]


def test_wrong_imprint_rejected(tmp_path, anchored_transport):
    _r, d = run(tmp_path, "imprint", "rfc3161_anchored")
    path = os.path.join(d, "anchors.log.jsonl")
    lines = open(path).read().splitlines()
    a = json.loads(lines[0])
    a["chain_head"] = "0" * 64   # token no longer matches the claimed head
    lines[0] = json.dumps(a, sort_keys=True, separators=(",", ":"))
    open(path, "w").write("\n".join(lines) + "\n")
    rep = verify_run_dir(d)
    assert not rep["ok"]
    assert any(not a["ok"] for a in rep["anchors"])


def test_chain_gap_detected(tmp_path, anchored_transport):
    _r, d = run(tmp_path, "gap", "rfc3161_anchored")
    path = os.path.join(d, "commits.log.jsonl")
    lines = open(path).read().splitlines()
    del lines[10]
    open(path, "w").write("\n".join(lines) + "\n")
    rep = verify_run_dir(d)
    assert not rep["ok"]
    assert any("chain recomputation mismatch" in e or "coverage" in e
               for e in rep["errors"])


def test_missing_final_anchor_is_coverage_gap(tmp_path, anchored_transport):
    _r, d = run(tmp_path, "cover", "rfc3161_anchored")
    path = os.path.join(d, "anchors.log.jsonl")
    lines = open(path).read().splitlines()
    open(path, "w").write("\n".join(lines[:-1]) + "\n")  # drop final anchor
    rep = verify_run_dir(d)
    assert not rep["ok"]
    assert any("coverage gap" in e for e in rep["errors"])


def test_unreachable_tsa_aborts_run_without_fake_tokens(tmp_path, monkeypatch):
    def dead(url, tsq):
        raise OSError("no route")
    monkeypatch.setattr(sinkmod, "TRANSPORT", dead)
    with pytest.raises(sinkmod.AnchoringError):
        run(tmp_path, "dead_tsa", "rfc3161_anchored")
    # no anchors were fabricated
    assert not os.path.exists(os.path.join(str(tmp_path), "dead_tsa", "anchors.log.jsonl")) \
        or open(os.path.join(str(tmp_path), "dead_tsa", "anchors.log.jsonl")).read() == ""
