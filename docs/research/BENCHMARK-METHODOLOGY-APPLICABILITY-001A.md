# BENCHMARK-METHODOLOGY-APPLICABILITY-001A

Status: research synthesis (external-benchmark methodology → lab applicability). NOT a task
card. Authorizes no implementation.

Central distinction (binding): the 8 surveyed projects are **capability / performance
benchmarks** — they answer "can an agent *do* X (generalize / remember / transfer / plan)?"
They do **NOT** answer the lab's question: "is the claimed mechanism *real* (non-trivial vs
a fair baseline, leak-free, intervention-valid), or theater?" A high score on any of them
is precisely the "looks capable" result the lab exists to interrogate. **Therefore: import
their *methodology patterns*, never their scores-as-evidence; and bolt the lab's gate
(triviality probe + real-fitted-baseline panel + leakage scan + fail-able verdict) onto any
world borrowed from them.** Capability ≠ mechanism ≠ subjecthood.

---

## 1. What each tests + the transferable pattern (verified)

| Benchmark | Tests | Test protocol | Transferable pattern |
|---|---|---|---|
| **Procgen** (Cobbe et al. 2019) | generalization + sample-efficiency | train on a finite set of procedurally-generated levels, **test on the full distribution → generalization gap** | **P1: procedural train/test split; gap = discriminator** |
| **MiniGrid/MiniWorld** (Chevalier-Boisvert et al. 2023) | goal-oriented behaviour under partial observability | minimal modular POMDPs; **unified 2D↔3D API → cross-observation-space transfer** | **P1 + transfer across obs spaces** |
| **Alchemy** (Wang/DeepMind 2021) | latent-structure inference, hypothesis-testing, experimentation | **latent causal structure resampled each episode**; agent must *experiment* to infer it; analysis toolkit + sample trajectories; compare to **ideal/Bayesian observer** | **P2: known latent + ideal-observer ceiling → test whether the agent INFERS the latent, not just scores** |
| **POPGym** (Morad et al. 2023) | memory | 15 partial-obs envs × difficulties + **13 memory-model baselines**; small/fast | **P3: isolate ONE capability via env design + a baseline PANEL** |
| **Meta-World** (Yu et al. 2019) | multi-task + meta generalization to new tasks | 50 manipulation tasks; ML1/10/45 + MT10/50; **success-rate on held-out tasks**; finding: learns single, **fails multi-task** | **P5: held-out NEW tasks reveal the failure** |
| **Continual World** (Wołczyk et al. 2021) | continual learning over a task sequence | sequence of Meta-World tasks; **3 metrics: performance / forgetting / forward-transfer** | **P4: decompose into named metrics (retain vs forget vs build-on)** |
| **AgentBench** (Liu et al. 2023) | LLM-as-agent reasoning/decision over multi-turn | 8 interactive envs; multi-round; success across diverse tasks | **(cautionary — see §4)** |
| **Craftax** (Matthews et al. 2024) | open-ended: deep exploration + long-horizon planning + memory + continual adaptation | JAX, 250× fast; achievement tree; **SOTA methods FAIL to make material progress** | **P6: a good test is one strong methods do NOT trivially pass** |

---

## 2. The transferable pattern catalog (what to steal)

- **P1 — procedural train/test split → generalization gap.** The core method for the
  learning axis: train on finite seeds/levels/tasks, test on held-out, the *gap* is the
  signal. Operationalizes "open-ended generalization vs behavior-tree" cleanly.
- **P2 — known latent + ideal-observer bound (Alchemy).** *The most valuable for this lab.*
  A world with a ground-truth latent (resampled per episode) that **requires
  experimentation/intervention to infer** lets you measure whether the agent *infers the
  latent* (vs a no-inference baseline) against a Bayesian ceiling. This is the lab's
  candidate-vs-oracle-vs-fair-baseline discipline with a *principled* latent.
- **P3 — isolate one capability + a baseline panel (POPGym).** Don't test "is it smart";
  test ONE thing (memory) in a world that *requires* it, against many baselines.
- **P4 — metric decomposition (Continual World): performance / forgetting / forward-transfer.**
- **P5 — the discriminating test is the held-out one (Meta-World).**
- **P6 — validity check: strong methods must NOT trivially pass** (Alchemy/Meta-World/Craftax
  all report SOTA failure). Mirrors the lab's K3/K4: a test everything passes is too weak.

---

## 3. Mapping to Track 1.1 + the three problems

| Lab target | Steal from | Concrete use |
|---|---|---|
| **Track 1.1 — learning/generalization** | Procgen P1 + Alchemy P2 | minimal procedural world, train/test split, **+ a known latent the agent must infer**, measured vs ideal-observer + no-inference baseline |
| **Memory** (problem 1) | POPGym P3 | partial-obs world that *requires* memory + difficulty levels + memory-architecture baseline panel; tests "is this memory mechanism real vs a cache/lookup" |
| **Self-maintenance over time** (problem 3) | Continual World P4 | measure identity/skill retention as **forgetting + forward-transfer**, not vibes |
| **Proactivity** (problem 2) | *(none directly)* | these test capability, not initiative-*source*; that's AIDSP territory (goals+world-model already produce it). No benchmark here isolates "internal-state-driven initiative." |

---

## 4. Cautions (killer-catalog mapping)

- **C1 — capability ≠ mechanism ≠ subjecthood.** Importing these measures *capability*. You
  still need ablation + intervention to claim the mechanism is real, and you can **never**
  claim self/feeling from a benchmark score. (Claim ceiling.)
- **C2 — richer = more false passes.** Craftax/Meta-World/AgentBench are rich → reward
  hacking, lookup, heuristic/prompt policies pass. The lab's standing warning holds: borrow
  the *pattern* into a **minimal** world, do not migrate the lab into the big benchmark.
- **C3 — these worlds lack the lab's anti-leak/anti-degeneracy gate.** They report *score*,
  not "score from a real mechanism vs a leak/lookup." Any borrowed world MUST wear: K3
  (balanced metric + triviality probe), K4 (real fitted baselines — POPGym's 13 are a
  starting panel), K5 (fail-able verdict), K6 (statistical leakage scan). **The benchmark
  gives the world; the lab gives the gate.**
- **C4 — AgentBench is the cautionary counter-example, not a template.** It evaluates
  *LLM agents* by task success — exactly the "looks alive via language / confabulation"
  surface the lab rejects, and LLM integration is forbidden in this lab. Do NOT evaluate a
  companion by "does it complete impressive tasks." Use AgentBench only to remember what NOT
  to do.

---

## 5. The Alchemy ↔ grounding-gate nuance (do not over-read)

Alchemy proves you *can* construct a world whose latent is **non-observation-decodable** and
requires experimentation to infer — i.e., it satisfies **K1** by construction. This is
genuinely useful for *latent-inference / learning-axis* questions. **But it does not reopen
the closed self-state route:** K2 (interventional-baseline saturation) remains — you would
still have to beat a fair Bayesian/ideal-observer-approximating interventional baseline, and
the self-state co-binding was shown non-identifiable
(`SELF-BOUNDARY-INTERVENABLE-LATENT-NEGATIVE-LINEAGE-AND-KILLER-CATALOG-001A`, K2). Alchemy
helps build a better K1-world for *structure-learning*; it is not a K2 escape for *self*.

---

## 6. Bottom line

- **Do NOT** migrate the lab into Procgen/Craftax/AgentBench (capability-not-mechanism;
  richer→false-pass; LLM/companion content is contract-forbidden here).
- **DO** steal: **P1 (train/test gap)** + **P2 (known-latent + ideal-observer bound)** for the
  Track 1.1 learning gate; **P3 (POPGym memory-isolation + baseline panel)** for the memory
  problem; **P4 (Continual World forgetting/transfer)** for self-maintenance — each in a
  **minimal** world with the lab's gate bolted on.
- **Expect more negatives.** These benchmarks *report that strong methods fail* — consistent
  with the lab's standing pattern. A hard borrowed world will more likely yield a clean
  bounded negative than a positive "self" result. That is the lab working, not failing.

## Claim ceiling
Methodology-import analysis only. No mechanism evidence produced; no route authorized;
capability benchmarks cannot evidence self/feeling/agency/subjectivity.

## Sources
Procgen arXiv:1912.01588 · MiniGrid/MiniWorld arXiv:2306.13831 (OpenReview PFfmfspm28) ·
Alchemy arXiv:2102.02926 (OpenReview eZu4BZxlRnX) · POPGym arXiv:2303.01859 ·
Meta-World arXiv:1910.10897 · Continual World arXiv:2105.10919 · AgentBench arXiv:2308.03688 ·
Craftax arXiv:2402.16801.
