# FUTURE-SURFACE-ADMISSION-AUTHORIZATION-TEMPLATE-001A

## Verdict target

`future_surface_admission_authorization_template_001a_pass`

## Layer

Engineering-governance / future task authorization template / surface-admission
precondition enforcement.

This is not a mechanism task. It is not a surface-admission execution task.
No Gate5, bridge, runtime, tournament, candidate, or EGO-mainline path is authorized.

## Parent boundary

- Boundary: `SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A`
- Commit: `22d8a09eb6747152f4d072d52c71f2725add87b1`
- Branch: `codex/meta-theory-scaffold`
- Tag: `remote-anchor-surface-admission-contract-enforcement-001a-22d8a09`

Future authorization manifests must keep this parent boundary as a dependency
reference. The branch may advance after this template is committed; the parent
commit remains the sealed dependency through the tag.

## Required manifest shape

Every future surface-admission authorization manifest must include:

- `SURFACE-ADMISSION-CONTRACT-HARDENING-001A` as a required dependency.
- `SURFACE-ADMISSION-CONTRACT-ENFORCEMENT-001A` as a required dependency.
- A pre-execution enforcement section naming
  `surface_admission_contract_enforcement_001a.validator`.
- The checker function to invoke before execution.
- A checker readback path, parse status, and readback hash.
- A parent boundary commit and tag reference.
- A rule banning `mechanism_score` before admission.
- A rule banning candidate, Gate5, bridge, runtime, tournament, and
  EGO-mainline scope.
- A rule banning old invalid COMPOSITE / CTSR / ACTION-CONDITIONED surfaces as
  mechanism evidence.
- A claim ceiling limited to surface-admission authorization hygiene only.

The checker must recompute authorization from serialized manifest/template
contents plus the enforcement readback artifacts. Stored verdict strings inside
future manifests are not authority.

## Required hostile controls

The validator must reject:

- superficial contract mention without checker invocation;
- checker invocation without readback;
- hardening-only dependency with missing enforcement dependency;
- enforcement-only dependency with missing hardening dependency;
- wrong enforcement verdict;
- corrupt or missing readback;
- missing G13/G14 requirement;
- missing anti-blacklist requirement;
- missing reason-control requirement;
- old invalid COMPOSITE / CTSR / ACTION-CONDITIONED surfaces cited as
  mechanism evidence;
- `mechanism_score` before admission;
- candidate / Gate5 / bridge / runtime / tournament / EGO-mainline scope;
- readiness inflation language;
- false full-suite pass claims.

## Required ablations

The validator must reject manifests or readbacks where any required field is
removed or corrupted:

- hardening dependency;
- enforcement dependency;
- checker invocation field;
- checker readback field;
- old invalid surface citation ban;
- no-`mechanism_score` rule;
- no-candidate / no-runtime / no-mainline scope rule;
- claim-ceiling field;
- parent commit reference;
- parent tag reference;
- enforcement verdict;
- readback hash or status.

## Artifact contract

The task emits:

- `artifacts/future_surface_admission_authorization_template_001a/result.json`
- `artifacts/future_surface_admission_authorization_template_001a/readback.json`
- `artifacts/future_surface_admission_authorization_template_001a/authorization_manifest_template.json`
- `artifacts/future_surface_admission_authorization_template_001a/hostile_control_report.json`
- `artifacts/future_surface_admission_authorization_template_001a/ablation_report.json`
- `artifacts/future_surface_admission_authorization_template_001a/authorization_trace.jsonl`
- `artifacts/future_surface_admission_authorization_template_001a/json_parse_verification.json`
- `artifacts/future_surface_admission_authorization_template_001a/claim_ceiling.txt`

## Claim ceiling

surface-admission authorization hygiene only.

This template may only support the claim that a future task-card template and
local authorization manifest/checker were created and tested against specified
bypass controls.

It does not prove mechanism validity, Gate4 validity, Gate5 validity, candidate
behavior, agency, autonomy, consciousness, emotion, subjectivity, companion
readiness, EGO readiness, runtime readiness, stable user benefit, or mainline
effect.

## Auto-Remote-Anchor

Auto-Remote-Anchor: conditional.

Remote anchor publication is allowed only if all validation controls pass,
focused checks pass, no mechanism surface is opened, no candidate/runtime/
mainline files are changed, and final local worktree status is clean after the
commit.
