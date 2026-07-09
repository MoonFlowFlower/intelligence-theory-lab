# K0-IMMUTABLE-FREEZE-001A

Status: BLOCKED ON ACCEPTED K0-R + ACCEPTED H1 / NO FORMAL RUN

Auto-Remote-Anchor: forbidden

## Task identity and problem

- Task id: `K0-IMMUTABLE-FREEZE-001A`
- Parent commit: `4e4700ca6e00b1a0e2dc3adf6a6e473b2f6ef6be`
- Problem: ITL must evaluate a stable artifact, not a changing Ego working tree.
  A wheel filename or source commit alone is insufficient: ABI, schemas,
  checkpoint, optimizer/config, adapters, H0/H1, heldout commitment, panel, and
  dependencies all need one verified manifest.

## Layer, mainline, enabled state, trigger

Engineering artifact-freeze/evidence hygiene only. No mainline integration.
Disabled until `EGO-K0-REFERENCE-KERNEL-001A` and H1 each have accepted,
clean, locally banked boundaries. Real trigger is an explicit local freeze CLI
that reads pinned commits/artifacts, builds in a temporary clean directory,
installs into a fresh environment, and emits computed hashes.

## Hypothesis and falsifier

A self-contained kernel wheel/CLI plus complete manifest can be installed and
replayed by ITL without importing Ego source or including product/test adapters.

Falsifier: dirty/unpinned source, dependency drift, missing hash, runtime import
from an Ego working tree, wheel inclusion of UI/SQLite/task generators, or
fresh-environment CLI mismatch.

## Preconditions

All must be pinned by full commit/hash and re-read before build:

- canonical parent;
- accepted Ego Foundation and K0-R results;
- accepted H0 and H1 results;
- callable `h0_acceptance.json` status `h0_contract_banked_valid` and
  `h1_acceptance.json` status `h1_instrument_accepted`, including card-bank
  commits, artifact hashes, producers, and code-path hashes;
- H0 heldout commitment (not raw reveal);
- kernel ABI/state/action/trace schema;
- initial checkpoint, optimizer config, kernel config, and dependency input.

Any uncommitted change in either repo is a stop. This card cannot repair K0-R or
H1 and cannot modify their source.

## Freeze target and package boundary

Build the declared `ego_k0_kernel` wheel from the exact Ego commit into a
temporary directory outside both working trees, then copy the final immutable
wheel into:

```text
artifacts/K0-IMMUTABLE-FREEZE-001A/
```

The wheel contains kernel contracts/state/model/update/planner/replay code and
CLI only. It must not contain or depend on:

- EgoOperator, EgoDesktop, pet/R-track code, UI, renderer, LLM, network,
  transports, runtime hooks, or mainline registration;
- the SQLite product adapter or any database instance;
- ITL generators, evaluator labels, family/split/order ids, baselines, metrics,
  or heldout data;
- a path/import dependency on either working tree.

ITL task generators and adapters remain outside the Ego wheel and communicate
only through the frozen ABI/capability manifest. Freeze separately builds a
self-contained immutable H1 runner wheel named
`itl_k0_h1_runner_bundle.whl` from the exact H1 acceptance manifest. It contains generators,
adapters, controls, baselines, rivals, scanners, replay, metrics, dependency
resolver, artifact writer, and CLI. Formal may not import the ITL working tree.

## Required freeze manifest

`freeze_manifest.json` must record and verify:

```yaml
wheel_sha256: string
source_commit: string
source_tree_hash: string
code_path_hash: string
package_version: string
cli_entrypoint: string
abi_version: string
state_schema_hash: string
action_schema_hash: string
trace_schema_hash: string
dependency_lock_hash: string
offline_wheelhouse_manifest_hash: string
offline_install_report_hash: string
python_platform: string
initial_checkpoint_hash: string
optimizer_config_hash: string
kernel_config_hash: string
adapter_capability_manifest_hash: string
h0_contract_hash: string
h1_instrument_hash: string
h1_runner_bundle_sha256: string
h1_runner_entrypoint: string
h1_runner_content_inventory_hash: string
heldout_seal_hash: string
baseline_panel_hash: string
component_dependency_matrix_hash: string
own_rule_constructor_contract_hash: string
own_rule_control_artifact_hash: string
build_command: [string]
producer_function: string
input_artifact_hashes: [string]
run_id: string
aggregation_rule: string
freeze_code_path_hash: string
```

Also emit dependency lock/report, wheel content inventory, import audit,
fresh-environment install report, CLI smoke trace/replay report, and failure
manifest on any failure.

Installation is offline and hash-locked: use `--no-index` with a manifested
local wheelhouse whose every artifact SHA-256 is recorded. Network resolution is
forbidden. Missing exact dependency artifacts are a stop, not permission to
resolve newer packages.

The callable producer is implemented only at:

```text
src/k0_immutable_freeze_001a/__init__.py
src/k0_immutable_freeze_001a/builder.py
src/k0_immutable_freeze_001a/verifier.py
src/k0_immutable_freeze_001a/cli.py
tests/k0_immutable_freeze_001a/test_builder.py
tests/k0_immutable_freeze_001a/test_verifier.py
```

Tests fail on working-tree imports, unhashed dependencies, bundle content leaks,
missing manifest fields, mutated config/checkpoint, or replay mismatch.

## Strongest baseline and collision record

### 1. Copy the Ego source tree
- Evidence: apparent reproducibility.
- Cheap failure: imports mutable files.
- Falsifier: change a working-tree file and observe run drift.
- Verdict: forbidden.

### 2. Hash wheel only
- Evidence: one immutable blob.
- Cheap failure: unpinned checkpoint/config/dependencies or hidden adapter.
- Falsifier: same wheel with changed external config changes behavior.
- Verdict: insufficient.

### 3. Complete manifest + clean install (selected)
- Evidence: exact artifact/ABI/config/dependency boundary.
- Cheap failure: undeclared import or missing input hash.
- Falsifier: fresh isolated install cannot reproduce the smoke trace.
- Expected failure: dependency or packaging leak; no formal run.

## Ablation, trace/replay, and provenance

No mechanism ablation or formal evaluation is authorized. Freeze smoke must
recompute a fixed dev-only action/state sequence from serialized state plus
observation in two fresh processes. Stored-output/hash-only playback fails.
Every report is callable and records producer, inputs, run id, seed/context,
aggregation, and code-path hash.

## Acceptance gate

Accept only if preconditions are banked/clean; all manifest fields and hashes
verify; Ego wheel and H1 bundle content/import audits exclude forbidden
surfaces; dependency lock and hashed offline wheelhouse are complete; both
artifacts install offline in a fresh environment; the H1 CLI can drive the Ego
CLI through only the frozen ABI; smoke/replay is exact; neither working tree is
imported; staged paths are exact; no heldout raw seed is revealed; and no formal
runner is launched.

## Claim ceiling

Immutable, locally installable artifact boundary and dependency provenance only.
No component presence, instrument validity, headroom, learning, replay benefit,
transfer, specialness, initiative, agency, autonomy, subjectivity,
consciousness, EGO readiness, product benefit, or mainline effect.

## Stop / rollback

Stop on dirty source, hash/dependency/import mismatch, missing accepted parent,
wheel content leak, mutable external checkpoint/config, smoke mismatch, or any
request to repair source. Before bank, discard only the attempted freeze output.
After bank, fixes require a new package/freeze version; never overwrite the old
wheel/manifest. Preserve failure artifacts.

## Expected changed files

- `docs/codex/tasks/K0-IMMUTABLE-FREEZE-001A.md` (card bank only)
- later, only the six producer/test paths above and these artifact names under
  `artifacts/K0-IMMUTABLE-FREEZE-001A/`: `ego_k0_kernel.whl`,
  `itl_k0_h1_runner_bundle.whl`, `freeze_manifest.json`, `dependency_lock.json`,
  `offline_wheelhouse_manifest.json`, `wheel_content_inventory.json`,
  `h1_bundle_content_inventory.json`, `import_audit.json`,
  `fresh_install_report.json`, `offline_install_report.json`,
  `cli_smoke_replay_report.json`, and conditional `failure_manifest.json`.

No Ego source/test change is authorized. Temporary build directories must be
outside repos and removed after hashes/reports are banked.

## Local commit and next action

Local card and later freeze-artifact commits are separately authorized after
their prerequisites/gates. Push/tag/remote anchor are forbidden. Next action is
none until K0-R and H1 are accepted.

## What this does not prove

Installability and immutability do not prove the kernel learns or matters.
