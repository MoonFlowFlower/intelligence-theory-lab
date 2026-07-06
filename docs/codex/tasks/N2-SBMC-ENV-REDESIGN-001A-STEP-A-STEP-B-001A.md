# N2-SBMC-ENV-REDESIGN-001A-STEP-A-STEP-B-001A

Status: AUTHORIZED bounded implementation / candidate-free execution card.

This card authorizes exactly one local candidate-free STEP-A / STEP-B run for
`N2-SBMC-ENV-REDESIGN-001A`, plus the matching repo-local route-state-machine
readback update. It does not authorize a mechanism candidate, subject proxy,
EGO runtime work, push, tag, or remote anchor.

## task id

N2-SBMC-ENV-REDESIGN-001A-STEP-A-STEP-B-001A

## problem definition

The current route-state frontier is `N2-SBMC-ENV-REDESIGN-001A`, a design-only
card that superseded a lookup-solvable scout. The project now needs the fastest
candidate-free evidence-bearing check: freeze the redesigned sparse relational
environment and run the baseline-first battery to determine whether the surface
is lookup-solvable, graph-closure-solvable, unidentifiable, or blocked by an
evidence-path failure.

## current layer

Engineering implementation + mechanism-route governance / evidence hygiene.
Mechanism hypothesis support only through candidate-free environment evidence.
No subjectivity / agency / consciousness layer.

## current stage

Route frontier `N2-SBMC-ENV-REDESIGN-001A` is `REGISTERED` before this task.
This task may move it to `CLOSURE_REVIEW_REQUIRED` only if STEP-B emits a
machine-readable closure-worthy verdict such as baseline equivalence.

## mainline target

None. Isolated local package, tests, artifacts, and route-state artifacts only.
No EGO runtime/mainline integration.

## enabled-state requirement

Only the local CLI/module path may be enabled:

```powershell
$env:PYTHONPATH="src"
python -m n2_sbmc_env_redesign_001a.runner --output-dir artifacts/N2-SBMC-ENV-REDESIGN-001A
python -m route_state_machine_001a.routectl status --root .
```

No runtime, UI, API, LLM, AIRI, deployment, or companion path is enabled.

## real-trigger evidence requirement

The final evidence claim requires a real command invocation of the candidate-free
runner that writes machine-readable artifacts under:

```text
artifacts/N2-SBMC-ENV-REDESIGN-001A/
```

At minimum the run must write:

- `step_a_preregistration.json`
- `result.json`
- `trace.jsonl`
- `baseline_comparison.json`
- `ablation_report.json`
- `replay_report.json`
- `leakage_report.json`
- `computed_evidence_provenance.json`
- `claim_ceiling.txt`
- `failure_manifest.json` when any stop/failure condition fires

## hypothesis

H1: sparse coverage breaks the per-user lookup shortcut from the old scout.
H2: metadata stripping and value-aware, style-matched item representation prevent
surface/provenance leakage from carrying the label.
H3, expected: cheap graph closure / arc consistency over the known relation and
covered observations recovers the ideal headroom; if so the correct verdict is
baseline equivalence / engineering-sufficient close, not mechanism evidence.
H4, unlikely and not optimized for: ideal has headroom that graph closure cannot
reach, which would require a separate follow-up environment/mechanism card.

## strongest baseline

The decisive baseline is `graph_closure`, a cheap graph-cache / arc-consistency
member. Additional required floors are `per_user_lookup_nn`,
`value_aware_embedding_outlier`, `frequency_marginal`, `predict_all`,
`predict_none`, and `majority`. If any fair baseline reaches the ideal within
the equivalence band, report baseline equivalence or invalid instrument; do not
weaken the baseline panel.

## ablation requirement

STEP-B must rerun callable controls:

- remove covered observations: `graph_closure` must degrade;
- wrong relation table: `graph_closure` and ideal/closure consistency must
  degrade;
- theta-canary leakage positive control: scanner must fire and decode accuracy
  must rise;
- sparse coverage control: no test target attribute may be directly observed in
  the trusted seed.

## trace/replay requirement

Replay must recompute non-ideal detector behavior from serialized
`item_repr + trusted_seed + relation_tables + detector_name + seed`, not from
stored hashes or stored scores. Non-ideal replay must not read `theta`, labels,
future observations, or audit-only fields.

## computed-evidence provenance gate

Every score or verdict-bearing row must record:

- `producer_function`
- `input_artifacts`
- `run_id`
- seed / user / episode ids
- `aggregation_rule`
- `code_path_hash`

The final verdict must be derived by a callable function from these computed
artifacts, not from a static literal dictionary.

## acceptance gate

Accept this local task only if all are true:

1. focused tests pass;
2. STEP-B runner writes the required artifacts;
3. JSON artifacts parse;
4. leakage positive control fires and clean scan is clean;
5. replay recomputation passes and is not hash-only;
6. ablations are callable and consumed by the final verdict;
7. route-state-machine `status` validates after the update;
8. git staged/committed paths are limited to the expected scope below.

## claim ceiling

Local candidate-free N2/SBMC environment-preflight evidence and route-state
readback only. A baseline-equivalence result is a valid negative / closure
packet, not mechanism validity. No theory pressure, no scoring validity beyond
the local contract, no certified environment beyond the bounded artifact, no
belief-maintenance mechanism success, no agency, autonomy, subjectivity,
consciousness, EGO readiness, companion readiness, production readiness, or
mainline effect.

## stop condition

Stop and report without rescuing the route if any of these occurs:

- `theta`, label, provenance, source, user id, or audit-only fields enter
  non-ideal `item_repr`;
- sparse coverage fails;
- leakage positive control does not fire;
- clean leakage scan fires;
- replay recomputation fails;
- `graph_closure` cannot be recomputed from legal serialized inputs;
- thresholds are changed after seeing results;
- implementation reaches for a candidate mechanism;
- route-state validation fails after scoped update.

## rollback plan

Revert only the files added/modified by this card:

- `docs/codex/tasks/N2-SBMC-ENV-REDESIGN-001A-STEP-A-STEP-B-001A.md`
- `src/n2_sbmc_env_redesign_001a/`
- `tests/n2_sbmc_env_redesign_001a/`
- `artifacts/N2-SBMC-ENV-REDESIGN-001A/`
- `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/events.jsonl`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/closure.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`
- `docs/research/FSP-STAGE-LEDGER.md`

Do not revert or rewrite historical PUM-ENV / S3d artifacts.

## expected changed files

Expected:

- create `src/n2_sbmc_env_redesign_001a/__init__.py`
- create `src/n2_sbmc_env_redesign_001a/model.py`
- create `src/n2_sbmc_env_redesign_001a/detectors.py`
- create `src/n2_sbmc_env_redesign_001a/runner.py`
- create `tests/n2_sbmc_env_redesign_001a/test_candidate_free_step_b.py`
- create `artifacts/N2-SBMC-ENV-REDESIGN-001A/*`
- create/modify the N2 route-state files named in the rollback plan
- append one ledger observation/transition entry to `docs/research/FSP-STAGE-LEDGER.md`

## forbidden changes

- EGO mainline/runtime/UI/API/LLM/AIRI/deployment files;
- candidate mechanism implementation;
- old PUM-ENV/S3d evidence rewriting;
- global schema migrations;
- threshold tuning after results;
- removing or weakening graph-closure / graph-cache baselines;
- `git add -A` or broad staging;
- push, tag, or remote anchor.

## Auto-Remote-Anchor decision

Auto-Remote-Anchor: forbidden.

## collision record

### Candidate A: minimal implementation

- Evidence it would produce: quick generator + a few baseline scores.
- Strongest cheap baseline that could match: per-user lookup or direct
  relation check.
- Leakage / hard-coding risk: high if labels or theta leak into item features,
  or if graph closure is only a test-only path.
- Smallest falsifying test: non-ideal guard allows `theta` or a test item uses a
  covered target attribute.
- Expected failure mode: false headroom or lookup-solvable invalid instrument.

### Candidate B: strongest baseline / shortcut explanation

- Evidence it would produce: explicit graph closure, lookup, frequency,
  embedding, and degenerate floors before any candidate mechanism.
- Strongest cheap baseline that could match: graph closure / AC-3.
- Leakage / hard-coding risk: medium if `graph_closure` silently reads audit
  fields.
- Smallest falsifying test: replay recomputation fails when only serialized
  legal inputs are provided.
- Expected failure mode: baseline equivalence; this is a valid negative.

### Candidate C: mechanism-faithful implementation

- Evidence it would produce: a same-agent or belief-memory mechanism over the
  redesigned environment.
- Strongest cheap baseline that could match: graph closure or known continual
  replay once the mechanism is specified.
- Leakage / hard-coding risk: high at this stage because environment headroom is
  not yet measured.
- Smallest falsifying test: strongest fair baseline reaches ideal within the
  equivalence band.
- Expected failure mode: overbuilding before environment certification.

### Selected approach

Candidate B. It maximizes discriminative value at this stage by testing the
strongest cheap explanation first. If graph closure solves the task, close or
downgrade the N2 pure-relational surface; do not implement a mechanism to
rescue it.
