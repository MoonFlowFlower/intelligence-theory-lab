"""Claim-ceiling language scan (audit question 1). Read-only.
Finds forbidden-claim terms in all 001/001B/001C docs, reports, artifacts, and
code, then classifies each hit as negated/disclaimer context vs potential claim.
"""
import json
import os
import re

REPO = "/sessions/magical-clever-cannon/mnt/intelligence-theory-lab"
OUT = os.path.join(REPO, "artifacts/predictive_action_learning_contract_001c_independent_audit")

SCOPES = [
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001.txt",
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001B.txt",
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-T1-EXTERNAL-COMMIT.md",
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-T1-EXTERNAL-COMMIT.txt",
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CLOSEOUT.md",
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-CLOSEOUT-TASK.md",
    "docs/PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-INDEPENDENT-AUDIT.md",
    "artifacts/predictive_action_learning_contract_001",
    "artifacts/predictive_action_learning_contract_001c",
    "predictive_action_learning_contract_001",
    "predictive_action_learning_contract_001c",
    "tests/test_predictive_action_learning_contract_001.py",
    "tests/test_predictive_action_learning_contract_001_baselines.py",
    "tests/test_predictive_action_learning_contract_001c.py",
]

TERMS = [
    r"consciousness", r"conscious\b", r"subjective experience", r"sentien",
    r"real emotion", r"\bagency\b", r"self.aware", r"functional.subject",
    r"electronic life", r"\bAGI\b", r"companion.read", r"EGO.{0,12}read",
    r"outperform.{0,30}retrieval", r"superior.{0,30}retrieval",
    r"predictive.{0,20}superiority", r"beats? retrieval",
    r"proof.{0,40}(bayesian|transformer|scaling)",
    r"prove[sd]?\b.{0,50}(correct|true|final)",
    r"autonom",
]
NEG = re.compile(
    r"(not|never|no |non-|forbidden|must not|does not|do not|cannot|isn't|"
    r"impossible|refus|block|denied|without|unsupported|caveat|ceiling|"
    r"disclaim|residual|限制)", re.I)

hits = []
for scope in SCOPES:
    base = os.path.join(REPO, scope)
    files = []
    if os.path.isfile(base):
        files = [base]
    else:
        for root, _d, fns in os.walk(base):
            files += [os.path.join(root, f) for f in fns
                      if f.endswith((".md", ".txt", ".json", ".py"))
                      and not f.endswith(".jsonl")]
    for p in files:
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for i, line in enumerate(text.splitlines()):
            for term in TERMS:
                for m in re.finditer(term, line, re.I):
                    window = line[max(0, m.start() - 120):m.end() + 120]
                    hits.append({
                        "file": os.path.relpath(p, REPO),
                        "line": i + 1,
                        "term": term,
                        "snippet": line.strip()[:240],
                        "negated_or_disclaimer_context": bool(NEG.search(window)),
                    })

unnegated = [h for h in hits if not h["negated_or_disclaimer_context"]]
out = {"n_hits": len(hits), "n_unnegated": len(unnegated),
       "unnegated_hits_for_manual_review": unnegated,
       "all_hits": hits}
with open(os.path.join(OUT, "claim_language_scan.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print(f"total hits: {len(hits)}; un-negated needing manual review: {len(unnegated)}")
for h in unnegated:
    print(f"  {h['file']}:{h['line']} [{h['term']}] {h['snippet'][:160]}")
