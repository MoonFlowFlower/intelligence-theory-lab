# N2-SBMC-ENV-REDESIGN-001A-CLOSURE-ACCEPTANCE-001A

Status: AUTHORIZED local route-governance closure acceptance.

This card records the operator-approved terminal closure of
`N2-SBMC-ENV-REDESIGN-001A` after the local candidate-free STEP-A / STEP-B
packet routed the surface to `CLOSURE_REVIEW_REQUIRED` with
`closure_type=BASELINE_EQUIVALENCE`.

## task id

N2-SBMC-ENV-REDESIGN-001A-CLOSURE-ACCEPTANCE-001A

## problem definition

The route currently sits at `CLOSURE_REVIEW_REQUIRED` after
`graph_closure` reached the same ideal headroom as the candidate-free oracle on
the N2/SBMC pure-relational surface. The operator has accepted the closure. The
repo now needs a minimal machine-readable transition from closure review to a
terminal route-state boundary, plus one append-only stage-ledger entry.

## current layer

Engineering implementation + mechanism-route governance / evidence hygiene.
No mechanism, learning, agency, subjectivity, consciousness, EGO runtime, or
mainline-effect layer is authorized.

## current stage

Before this task:

- `N2-SBMC-ENV-REDESIGN-001A`: `CLOSURE_REVIEW_REQUIRED`
- `closure_type`: `BASELINE_EQUIVALENCE`
- `program_state.current_frontier_route_id`: `N2-SBMC-ENV-REDESIGN-001A`

This task may move the route to `ADJUDICATED` only for the accepted terminal
baseline-equivalence closure. It must not assign a successor frontier or start
a successor route.

## mainline target

None. Local route-state artifacts, local status readback, and local ledger only.
No EGO mainline/runtime/UI/API/LLM/AIRI/deployment path is touched.

## enabled-state requirement

The only enabled path is the existing local route-state CLI:

```powershell
$env:PYTHONPATH="src"
python -m route_state_machine_001a.routectl validate --root .
python -m route_state_machine_001a.routectl status --root .
python -m route_state_machine_001a.routectl dashboard --root .
```

## real-trigger evidence requirement

Real trigger evidence is limited to the operator's explicit acceptance in the
current Codex session plus callable `routectl` validation over serialized JSON
route-state artifacts. No live runtime trigger or mechanism trigger exists.

## hypothesis

A minimal transition to `ADJUDICATED` plus ledger/status readback will close the
review state without weakening the baseline-equivalence negative evidence or
creating a new roadmap/mechanism authorization.

## strongest baseline

A prose-only note could claim that closure was accepted while leaving the
machine-readable route state unresolved. This task must therefore update the
serialized route state and validate it through the existing callable routectl
path.

## ablation requirement

No mechanism ablation is authorized. Governance ablation is limited to reusing
the existing route-state validator/tests that block invalid route states,
missing closure packets, unsafe closure claims, and unsafe current-frontier
records.

## trace/replay requirement

No mechanism trace/replay is authorized. Governance replay is deterministic
revalidation from serialized `program_state.json`, route `state.json`,
`closure.json`, and `events.jsonl` files.

## computed-evidence provenance gate

`artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json` must be regenerated
by `python -m route_state_machine_001a.routectl validate --root .` and must keep
the existing callable-code provenance fields, including producer function,
input artifacts, run id, aggregation rule, code path hash, route summaries, and
verdict.

## acceptance gate

Accept only if all are true:

1. repo preflight reports clean worktree and no staged files before edits;
2. `.git/index.lock` is absent;
3. N2 starts as `CLOSURE_REVIEW_REQUIRED` with `closure_type=BASELINE_EQUIVALENCE`;
4. final N2 state is `ADJUDICATED`;
5. closure packet preserves `BASELINE_EQUIVALENCE`, mechanism/theory
   authorizations remain false, and forbidden claim ceiling remains intact;
6. `program_state` does not assign a new successor frontier or authorize
   mechanism validity, theory pressure, scoring, experiment execution, runtime,
   or mainline work;
7. `docs/research/FSP-STAGE-LEDGER.md` appends exactly one closure acceptance
   entry;
8. `routectl validate/status/dashboard` pass after the update;
9. focused route-state tests pass;
10. staged/committed paths are limited to the expected changed files.

## claim ceiling

Local route-governance terminal closure only. This is valid negative /
baseline-equivalence route closure, not mechanism validity, not theory
pressure, not scoring validity, not certified environment evidence, not agency,
not autonomy, not subjectivity, not consciousness, not EGO readiness, not
companion readiness, and not mainline effect.

## stop condition

Stop and report if:

- the starting route is no longer `CLOSURE_REVIEW_REQUIRED`;
- the closure type is not `BASELINE_EQUIVALENCE`;
- existing dirty/staged paths overlap planned paths;
- validation fails after the scoped update;
- the update requires source-code changes, schema changes, mechanism
  experiments, scoring, successor-route implementation, runtime integration, or
  push/tag/remote-anchor;
- any change would rewrite historical PUM-ENV/S3d artifacts.

## rollback plan

Before commit, rollback is limited to reverting the files listed in expected
changed files for this card. Do not touch unrelated user work or historical
artifacts.

## expected changed files

- `docs/codex/tasks/N2-SBMC-ENV-REDESIGN-001A-CLOSURE-ACCEPTANCE-001A.md`
- `docs/research/FSP-STAGE-LEDGER.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/closure.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/events.jsonl`
- `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`

## forbidden changes

- No mechanism candidate, scoring run, successor route implementation, or new
  environment design.
- No EGO runtime/mainline/UI/API/LLM/AIRI/deployment/API-key files.
- No source-code/schema changes unless validation reveals a governance blocker
  that this card explicitly cannot resolve.
- No historical PUM-ENV/S3d evidence rewriting.
- No `git add -A` or broad staging.
- No push, tag, or remote anchor.

## local commit authorization

A single local commit is authorized if the acceptance gate passes and staged
paths exactly match the expected changed files that actually changed.

## Auto-Remote-Anchor decision

Auto-Remote-Anchor: forbidden.

## collision record

### Candidate A: prose-only acceptance

- Evidence produced: a human-readable note saying closure was accepted.
- Strongest cheap baseline that could match it: existing chat/session context.
- Leakage / hard-coding risk: high; route state can remain unresolved while
  prose implies closure.
- Smallest falsifying test: `routectl status` still reports
  `CLOSURE_REVIEW_REQUIRED`.
- Expected failure mode: false closure / stale route-state readback.

### Candidate B: minimal terminal route-state transition

- Evidence produced: serialized route state moves to `ADJUDICATED`, closure
  packet records operator acceptance, events/ledger/status are append-only or
  readback updates, and `routectl` validates.
- Strongest cheap baseline that could match it: manual JSON edit without
  validation.
- Leakage / hard-coding risk: medium if allowed next actions quietly authorize
  successor mechanism work.
- Smallest falsifying test: final `closure.json` authorizes mechanism evidence
  or final `program_state.json` starts a successor route.
- Expected failure mode: governance claim inflation.

### Candidate C: successor runtime-kernel route creation

- Evidence produced: a new runtime-kernel task/frontier.
- Strongest cheap baseline that could match it: drift-aware continual replay /
  graph-cache family depending on the successor regime.
- Leakage / hard-coding risk: high because closure acceptance should not be
  bundled with route replacement.
- Smallest falsifying test: the closure commit also creates a new mechanism
  route.
- Expected failure mode: anti-Zeno violation and route-boundary contamination.

## selected approach

Candidate B only. Close the accepted N2 baseline-equivalence review as a local
terminal governance boundary. Leave successor runtime-kernel design to a
separate bounded task card.
