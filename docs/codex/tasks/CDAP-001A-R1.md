# CDAP-001A-R1 — DOCS-BANK TASK CARD

## task id

`CDAP-001A`

Revision: `R1`.

## problem definition

Bank `CDAP-001A-R1` as a docs-only route input: a row-level collapse-certificate family table over
the 9 named criterion families. The bank must land only after the three pre-bank requirements in the
operator instruction are satisfied:

1. Patch A: Row 6 score-object split.
2. Patch B: Row 9 current-contract wording with fixed-prior/meta-MDP caveat and
   `SPECIFICATION_GAP` treatment.
3. Provenance resolution: every prior cite is resolved to an in-repo path plus commit anchor, or the
   row is explicitly tagged `[CONJECTURE — provenance unresolved]`.

This task is a Yellow docs bank only. It must not create callables, source code, Step-B execution,
agent runs, scoring, thresholds, schema migrations, or EGO/runtime/mainline changes.

## current stage

Docs-only route input / design-analysis bank. No experiment is opened. No mechanism route is admitted.

## current layer

Engineering implementation + mechanism-hypothesis route analysis. Claim ceiling is docs-only
evidence hygiene / route input over named families.

## mainline target

No EGO mainline target. No runtime target. The only target is repository documentation/artifact
banking under the allowed paths.

## enabled-state requirement

Enabled state is repository-local documentation only:

- `docs/codex/tasks/CDAP-001A-R1.md`
- `docs/research/CDAP-001A-R1-family-table.md`
- `artifacts/CDAP-001A/result.json`
- `artifacts/CDAP-001A/claim_ceiling.txt`

No callable, `src/`, tests, agent, training, Step-B, or runtime path is enabled.

## real-trigger evidence requirement

Real-trigger evidence is limited to a git object-store readback after commit:

- only the 4 allowed paths changed;
- Patch A and Patch B are present in the landed table;
- every cite is either `path@commit` or the row is tagged `[CONJECTURE — provenance unresolved]`;
- claim ceiling matches `artifacts/CDAP-001A/claim_ceiling.txt` and `result.json`;
- no `src/`, callable, harness, Step-B, agent/training, EGO mainline, UI/companion, LLM/AIRI,
  threshold, schema, or prior-artifact rewrite is present.

## hypothesis

For the nine named score-object families, the current Red-audited analysis classifies Rows 1–8 as
shadow-dominated or oracle-scored under equal access, and Row 9 as out-of-contract routing to fork A
rather than an admissible bounded target.

## strongest baseline

The strongest baseline explanation is that each bounded criterion family is a score object over an
equal-access trace/access tuple, so a Bayes-optimal-for-C shadow, oracle label, or simple trace mimic
absorbs the apparent mechanism signal. For open-ended/cross-episode claims, a pre-frozen finite
meta-MDP with fixed prior/horizon/compute/objective restores the Bayes-optimal meta-policy wall.

## ablation requirement

No ablation is executed in this bank. The bank records only docs-level collapse certificates and
prior-cite provenance. Any future Step-B/fork-A execution must supply independent callable ablations
under a separate bounded task card.

## trace/replay requirement

No trace/replay is executed in this bank. The table cites prior trace/replay or negative-evidence
artifacts only when they are resolvable to repo path plus commit. Future executable use must require
recompute-from-serialized-state replay under a separate task card.

## computed-evidence provenance gate

This task is not an evidence-producing executable experiment. Its provenance gate is:

- cite only in-repo artifacts with commit anchors;
- do not use memory-only citations as provenance;
- if a prior cite cannot be resolved in repo, tag the affected row
  `[CONJECTURE — provenance unresolved]`;
- do not convert this docs bank into callable evidence or Gate evidence.

## collision record

### Candidate 1 — minimal docs bank

- Evidence produced: a row table, claim ceiling, and machine-readable summary only.
- Strongest cheap baseline that could match it: prose consistency; no mechanism evidence.
- Leakage / hard-coding risk: low for runtime, but high for claim inflation if table language is read
  as a proof of universal closure.
- Smallest falsifying test: object-store readback shows a missing patch, unresolved cite without a
  conjecture tag, or a changed forbidden path.
- Expected failure mode: provenance cite absent in repo, causing a conjecture downgrade.

### Candidate 2 — strongest shortcut/baseline explanation

- Evidence produced: explicit classification that Bayes-optimal-for-C, oracle scoring, trace mimic,
  or fixed-prior meta-policy absorbs the named criteria.
- Strongest cheap baseline that could match it: equal-access Bayes/shadow or faithful label baseline.
- Leakage / hard-coding risk: replacing a mechanism claim with an analysis shortcut; acceptable here
  because this is a docs-only collapse table, not a mechanism implementation.
- Smallest falsifying test: a named bounded stationary C where candidate passes while the
  Bayes-optimal-for-C shadow fails under audited access parity.
- Expected failure mode: unresolved prior cite weakens row provenance, not a route pass.

### Candidate 3 — mechanism-faithful implementation

- Evidence produced: none in this task; would require executable environments, baselines,
  ablations, leakage positive controls, and replay.
- Strongest cheap baseline that could match it: integrated cache, Bayes/meta-policy, fitted
  interventional baseline, or trace mimic.
- Leakage / hard-coding risk: high if implemented from this table without a separate frozen
  metric/baseline/ablation contract.
- Smallest falsifying test: same-access baseline tie or oracle/label leakage.
- Expected failure mode: Step-B execution would overrun the docs-only authorization.

Selected approach: Candidate 1 with Candidate 2 stated as the collapse explanation. Candidate 3 is
forbidden here.

## acceptance gate

Accept only if all are true:

1. Changed files are exactly the four allowed paths.
2. `docs/research/CDAP-001A-R1-family-table.md` contains Patch A and Patch B.
3. Each prior cite is a repo path plus commit anchor or the affected row is tagged
   `[CONJECTURE — provenance unresolved]`.
4. `artifacts/CDAP-001A/result.json` agrees with the family table verdicts.
5. `artifacts/CDAP-001A/claim_ceiling.txt` matches the claim ceiling text used in the table and
   result JSON.
6. No callable, `src/`, Step-B, agent/training, prior-artifact rewrite, EGO mainline, UI/companion,
   LLM/AIRI, threshold, schema, or global config path is changed.
7. A git object-store readback verifies the committed bytes.

## claim ceiling

Docs-only route input over the named nine families. This bank does not prove universal closure,
fork-A success, mechanism validity, functional subjectivity, agency, subjectivity, consciousness,
EGO readiness, runtime readiness, companion readiness, or mainline effect.

## stop condition

Stop and report without committing if:

- any forbidden path is dirty after edits;
- any prior artifact must be rewritten to make a cite work;
- Patch A or Patch B cannot be landed;
- claim ceiling text would need to be softened or strengthened;
- a cite is unresolved but the affected row is not tagged `[CONJECTURE — provenance unresolved]`;
- staging scope contains anything outside the four allowed paths;
- object-store readback cannot verify the committed files.

## rollback plan

Docs-only rollback: revert the single commit. No runtime, mainline, schema, source, or artifact
history rewrite is required.

## expected changed files

- `docs/codex/tasks/CDAP-001A-R1.md`
- `docs/research/CDAP-001A-R1-family-table.md`
- `artifacts/CDAP-001A/result.json`
- `artifacts/CDAP-001A/claim_ceiling.txt`

## forbidden changes

- `src/**`
- any callable, harness, agent, training, Step-B, or source implementation;
- `src/criterion_shadow_probe/`;
- EGO mainline, UI/companion, LLM/AIRI, deployment, API keys, external services;
- thresholds, schemas, global config;
- rewrite/patch/delete of any prior CSSP/ACBU/grounding-gate/Gate4/RESIDUE artifact;
- any softening or strengthening of the claim-ceiling text.

## Auto-Remote-Anchor decision

Auto-Remote-Anchor: forbidden.

Direct operator instruction authorizes a branch push after the single exact-scope commit if the
acceptance gate passes. No tag or remote-anchor publication is authorized by this card.
