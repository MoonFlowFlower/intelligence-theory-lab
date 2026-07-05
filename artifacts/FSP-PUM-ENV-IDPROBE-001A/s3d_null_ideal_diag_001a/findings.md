# S3D-NULL-IDEAL-DIAG-001A findings

Verdict: `RESIDUAL_ACTION_STRUCTURE_VIA_STYLEMAP`.

Branch fired: wrong-style overall chance and history/posterior independent.  Decision scope: canonical NULL overall metric; recommend-turn-conditional reported separately because small selected-user samples can be finite-support inflated.

Numbers:
- T1 TRUE style_map overall = 0.068111356836; recommend = 0.08333333333333333.
- T3 WRONG style_map overall = 0.023946123654; recommend = 0.08333333333333333.
- T2 history-independence max distribution diff = 0; prediction mismatches = 0.
- T4 posterior-independence max zero-vs-after-true diff = 0; max zero-vs-after-random diff = 0.
- T5 expected overall macro = 0.071090600310; T1-minus-expected overall = -0.002979243474.
- T5 eval-range analytic TRUE style overall/recommend = 0.072653554296 / 0.072219203123.
- T5 eval-range analytic WRONG style overall/recommend = 0.029980929035 / 0.029874498856.

Scope resolution: T5 found 1 internal recommend action variant with internal center {'recommend': 8}.  The selected users had surface centers {'640': 6, '641': 18, '642': 1}; style-only enumeration over eval users 640..799 had 31 distinct surface centers.  Thus the pooled recommend scorer is not a single fixed surface-mode predictor even though the posterior is independent.

Fix class only, not implemented here: A) env-response-uniform would remove NULL_env action-conditioned residual structure; B) guard-floor-redefine would redefine the NULL guard floor to allow action-conditioned style_map privilege.  This diagnostic does not choose or implement either fix.
