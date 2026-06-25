# Execution-Grounded Fusion on SWE-bench (Design v2.1)
Status: APPROVED by committee re-review (2026-06-24) — empiricist APPROVE-WITH-CHANGES,
novelty NOVEL, systems FEASIBLE-WITH-CHANGES. v2.1 folds in all blocking changes.
Supersedes DESIGN.v1.md. Pre-registration: this document is the pre-registration. Do not
edit analysis choices after data collection begins; append an addendum instead.

## CONTRIBUTION FRAMING (novelty re-review — read first)
The spine of this work is a **measurement**: how much of the oracle best@k headroom a
*non-oracle* execution verifier recovers on repo-scale SWE-bench (`f`), plus the signal
quality `ρ` and the compute frontier. This contribution **stands independently** of
whether synthesis beats selection. The "fusion" result (C > A′) is a *finding within the
measurement*, NOT the paper's identity — so a null C≈A′ does not sink the contribution.
Headline-level claim = the measurement; fusion = a vertebra, not the flag.

## 0. What changed from v1 (committee-driven)
- **Reframed thesis** from "router fusion beats one model" → **a verifier-signal-quality
  measurement**: how much of the oracle best@k ceiling can a *non-oracle* execution
  verifier recover on repo-scale tasks, and at what compute. This is the execution-signal
  analog of our DRACO consensus-signal study (DRACO measured agreement-signal quality and
  found it weak/harmful; this measures execution-signal quality).
- **Kept the "fusion" name — earned, not relabeled.** Per the repo's own thesis
  (`deliberation-algorithms.md` §3): fusion's lift lives in the *judge's verify-mode
  synthesis over a candidate pool*, not in selection and not in the consistency score.
  Execution becomes a new grounding **reference mode** (`execution`) alongside the
  existing `context`/`panel`/`hybrid` — it swaps the weak panel-NLI oracle (DRACO
  Spearman +0.21, "useless as an oracle") for a real ground-truth oracle feeding the
  *same* synthesis step. The architecture (panel → judge analysis → synthesis) is unchanged.
- **Honest arm labels.** The single-model best@k arm is labeled **verifier-guided
  best-of-N**, not fusion. "Fusion" applies only to arms whose judge *merges* across a
  multi-candidate / multi-model pool (B, C, D).
- Added 9 hard conditions (C1–C9) from REVIEW_VERDICT.md, inlined below.

## 1. Thesis (pre-registered, falsifiable)
**Primary (measurement):** On repo-scale SWE-bench Verified, a non-oracle execution
verifier (self-generated and/or pre-existing repo tests) recovers a fraction
`f = (C − A) / (E − A)` of the oracle best@k headroom, with `f` reported with a paired
bootstrap CI. Secondary: characterize *when* the verifier signal is real (per-instance)
and how `f` trades against compute.

**Confirmatory (the fusion claim, DECOUPLED from the headline):** at matched served-model
token budget, execution-grounded fusion (C) beats verifier-guided best-of-N (A′) — i.e.
the judge's *synthesis/merge* adds value beyond *selecting* the best passing candidate.
C > A′ is the test that distinguishes "fusion" from "best-of-N". Per the novelty
re-review, this leg is the most exposed to a well-tuned A′ (an Agentless-style selector),
so it is pre-registered as a *secondary finding*: the measurement contribution holds
whether or not C > A′. Pre-registered success threshold for this leg: **C − A′ ≥ 5 pp**
resolve rate (the smallest synthesis gain we'd call meaningful); the equivalence margin
for "C ≈ A′" is **Δ_equiv = 3 pp** (see C6).

**Report f for BOTH C and A′** (novelty re-review, highest-value table): `f_C = (C−A)/(E−A)`
vs `f_A′ = (A′−A)/(E−A)` — "how much of the oracle ceiling does *pure selection* recover
vs *synthesis*." This quantified comparison IS the Agentless confrontation.

## 2. Object of study: the execution grounding signal
The DRACO line established consensus (panel-NLI) is a weak oracle (Spearman ≈ +0.21) and
harmful as a hard filter. This study replaces that reference with execution:

```
grounding.reference:   panel (NLI consensus)   →   execution (run tests)
ground truth:          internal agreement      →   external pass/fail
DRACO verdict:         weak/harmful oracle      →   THIS STUDY measures it
```

The headline number is the **recovered fraction f** and the **per-candidate correlation
ρ(in-loop pass, hidden resolve)** — not a raw resolve rate.

## 3. Infra topology (verified live 2026-06-24 — REUSE ONLY)
- **Inference:** `<gpu-host>` vLLM `Qwen/Qwen2.5-Coder-7B-Instruct` :8000, `max_model_len`
  32768. GPU 2.7 GB free, shared with OTHER LIVE EXPERIMENTS. **Hard concurrency cap 2–3;
  off-peak only; pre-flight abort if `memory.free < 2 GB` or sustained `util > 80%`. No new
  GPU loads, no second vLLM on this box.**
- **In-loop execution + grading:** `<exec-host>`, podman 5.8.2, x86_64, 96 cores, 235 GB
  RAM, 554 GB free disk. SWE-bench eval images run here natively (alias `docker→podman`).
  Pre-stage instance images (tens–100+ GB).
- **Mac:** runs only the `mini-swe-agent` v2.4.2 client (OpenAI-compatible) pointing at the
  remote endpoints. NO Docker on Mac (arm64) — nothing containerized runs here.
- **Scope (B3, corrected):** all arms on the pilot-50. The full-500 run carries the arms
  the decision rule needs — **A, A′, B, C, and E** (the rule is C vs A′ primary, C vs B
  secondary, E for the ceiling/`f`). Arm **D** (heterogeneous panel) stays pilot-only
  unless it is promising at 50, since it needs a 2nd served model the GPU box can't host
  now (see C-vs-D = exploratory). The earlier "C + A only" scoping was a bug: it could not
  evaluate the pre-registered C-vs-A′/C-vs-B rule.

## 4. Dataset & metric
- **SWE-bench Verified** (500 human-validated instances), public.
- **Pilot:** stratified 50 (by repo + difficulty). **Full:** 500, gated (see C2).
- Primary metric: **% resolved** (hidden FAIL_TO_PASS + PASS_TO_PASS pass). The grading
  signal is pure execution — no LLM judge in the grading path.
- Pre-registered: patch-apply failures and step-limit hits = **"not resolved"** (never
  dropped — dropping is informative censoring). Track apply-rate as a balance check.

## 5. Arms (all graded identically by the SWE-bench harness)
| Arm | Label | What | Isolates |
|-----|-------|------|----------|
| **A** | single best@1 | one rollout, Qwen2.5-Coder-7B | honest floor |
| **A′** | **verifier-guided best-of-N** (NOT fusion) | k temp-diverse samples, select best by non-oracle execution | does *selection* alone help? the fair competitive baseline |
| **B** | plain fusion (no execution) | k samples → judge synthesizes 1 patch, no execution grounding | does synthesis help without the oracle? (the DRACO-style consensus risk) |
| **C** | **execution-grounded fusion** [THE CLAIM] | k candidates → run non-oracle tests → judge synthesizes/repairs using execution feedback, ≤R rounds | synthesis + real oracle |
| **D** | **heterogeneous-panel fusion** | C but panel spans ≥2 model families; synthesis MERGES partial solutions | does panel diversity add over self-panel? (carries the "fusion" name hardest) |
| **E** | oracle ceiling (not deployable) | best@k selected by the HIDDEN tests | upper bound; defines headroom `E−A` |

Attribution: **B vs C** isolates the execution oracle; **A′ vs C** isolates synthesis-vs-
selection (the fusion test); **C vs D** isolates panel diversity; **E−A′** and **E−C**
bound how much a perfect selector would add.

## 6. Hard conditions (C1–C9, pre-registered)

**C1 — Parity smoke [BLOCKS ALL GPU TIME].** On <exec-host>, 5 instances: (a) gold patches
go green through the official harness; (b) the IN-LOOP test executor returns the SAME
pass/fail as the grading harness on a gold patch AND a known-bad patch. Any disagreement
→ STOP, fix environment parity. Guards the #1 systems risk (grade/loop skew makes C
"verified" against a fiction).

**C2 — Signal-quality gate [GATES FULL-500].** On pilot-50, log per candidate:
#self-tests, self-test pass rate, repo-pretest pass rate, and ρ = Spearman(in-loop pass,
hidden resolve). **Require ρ ≥ 0.2 to proceed to 500.** ρ ≤ 0 = the DRACO pattern =
thesis dead by construction; stop.

**C3 — Contamination control.** Qwen2.5-Coder likely ingested these repos' fix commits.
It differences out in paired comparison, but: NEVER headline the raw 500 resolve rate;
report the primary delta on a **low-memorization stratum**. **Probe spec (N1, made
concrete):** for each instance, prompt the base model with the issue text + file path
(NO test, NO hint) and ask for the fix; score verbatim/near-verbatim overlap with the
gold patch (normalized token-level similarity). Pre-register TWO thresholds (e.g.
similarity ≥ 0.5 and ≥ 0.7 = "memorized") and **report the primary delta's robustness
across both** — the stratum must not rest on a single black-box cutoff. Optional
confirmatory: a post-cutoff held-out set (e.g. SWE-bench-Live).

**C4 — Split the verifier levers.** Report **repo-pre-existing tests** vs **self-generated
tests** SEPARATELY (opposite leakage profiles). A 7B writing tests that pass its own wrong
patch is reward-hacking a proxy — the DRACO confident-wrong pattern. Lumping hides the
mechanism. Arm C is run in both sub-modes.

**C5 — Budget definition.** Budget = served-model **total tokens** (prompt+completion,
including judge + repair rounds), **±5% per instance**, enforced and logged. Report
realized per-arm budget distribution to prove the match held.

**C6 — Power & decision rule.**
- N=50 cannot distinguish a 4pp lift from 0 (CI ≈ ±10–12pp). Pilot is for C1/C2/plumbing
  + variance estimation, NOT the headline.
- **Pre-committed thresholds (B1/B2, fixed NOW, not post-pilot):** smallest shippable
  effect (MDE target) = **5 pp** resolve rate for C vs A′. Equivalence margin
  **Δ_equiv = 3 pp** (< MDE, so "different" and "≈" cannot both hold). Compute the
  pilot-implied MDE at N=500 from the A′-vs-C discordant-pair rate (McNemar); **if the
  implied MDE > 5 pp, expand N or declare the C-vs-A′ leg underpowered BEFORE the full
  run** (the measurement contribution still proceeds).
- **"≈" is an equivalence test (TOST)** at Δ_equiv = 3 pp; if the CI is wider than the
  margin → verdict = **INCONCLUSIVE**, never "adds nothing" (underpowered null ≠ negative).
- **Single primary comparison: C vs A′.** Holm-correct the one secondary, C vs B. **All
  contrasts involving B, D, E are DESCRIPTIVE/EXPLORATORY** (N2): CIs reported, but NO
  ship decision rides on them and none may be post-hoc promoted to a confirmatory claim.
- Bootstrap resamples **whole instances** (not rollouts). ≥3 rollouts/arm/instance on the
  pilot to separate rollout luck from arm effect; report rollout variance.

**C7 — Confront Agentless.** Agentless already does test-based patch selection on
SWE-bench. Stated delta: this is a **verifier-signal-quality measurement** (recovered
fraction f + compute frontier + non-oracle vs oracle gap), and the synthesis/merge step
(C, D) vs pure selection (A′) — not a new selection mechanism. The design must report
where C diverges from an Agentless-style selector.

**C8 — Honest labeling.** A′ = "verifier-guided best-of-N", not fusion. "Fusion" =
arms whose judge MERGES across candidates (B/C/D). Router/serving-layer/OpenAI-API framing
is engineering, presented as such, not as novelty.

**C9 — Report the frontier, not points.** Sweep k / budget; plot achieved-resolve vs
compute per arm. Report verifier **precision/recall vs hidden tests** and the realized
**recovered fraction f = (C−A)/(E−A)**. That fraction is the headline.

## 7. Pre-registered decision rule
**The measurement contribution (f_C, f_A′, ρ, frontier) reports regardless of the below.**
The decision rule governs only the secondary fusion finding, on the C-vs-A′ paired
resolve-rate delta at N=500 (MDE 5 pp, Δ_equiv 3 pp, Holm-corrected secondary C-vs-B):
- **SHIP-EXECUTION-FUSION** if C > A′ (CI excludes 0, Holm) AND C > B.
- **VERIFICATION-IS-THE-LEVER** if C > B but C ≈ A′ (TOST within 3 pp): the oracle
  helps but synthesis ≈ selection — keep verifier-guided best-of-N, drop the synthesis claim.
- **FUSION-ADDS-NOTHING** only if C ≈ A′ ≈ B by TOST within 3 pp (adequately powered).
- **HARMFUL** if C significantly < A′ (the live DRACO-style risk; scientifically the most
  interesting — means the non-oracle verifier steers wrong).
- **INCONCLUSIVE** if CIs exceed the 3 pp equivalence margin (underpowered) — report f with CI.
- Always report **E−C** (remaining headroom) and **E−A** (total headroom; if tiny, no
  selector can help on this model/dataset — check first).
- Contrasts involving **B, D, E are descriptive/exploratory** (C6/N2); no ship decision
  rides on them.

## 8. Deliverables
- `verdict.json`: per-arm resolve rate (+ low-memorization stratum), paired deltas + CIs,
  realized budgets, ρ, recovered fraction f, decision label.
- Compute-quality frontier plot (resolve vs served-model tokens, all arms, with E ceiling).
- Per-instance trace: in-loop signal vs hidden outcome; verifier precision/recall;
  self-generated vs repo-pretest sub-mode breakdown.
- Verifier-quality writeup (the execution analog of `grounded_fusion/FINDINGS.md`).

## 9. Engineering plan & cost (honest)
The "missing grounding backend" framing undersold this. Two large pieces:
1. **In-loop execution sandbox** (~1–2 eng-weeks, the real cost): per-instance podman
   container lifecycle on <exec-host> — checkout@base commit, install deps, apply candidate
   patch, run non-oracle tests, capture pass/fail, teardown — wired so in-loop verdicts
   EXACTLY match the grading harness (C1). Exposed to the looper as a new
   `grounding.reference: execution` backend / the `fusioneval` driver's execution mode.
2. **Harness wiring:** mini-swe-agent arm configs (base_url per arm), budget accounting
   (C5), ≥3-rollout orchestration, stratified sampler, concurrency-capped client (C6/infra).

## 10. Gating sequence
1. C1 parity smoke (½ day, CPU-only on <exec-host>) — BLOCKS everything.
2. Build in-loop sandbox + arm harness.
3. **Pilot-50 (all arms A/A′/B/C/D, ≥3 rollouts each)** — compute ρ (C2), pilot-implied
   MDE (C6/B1), realized budgets (C5). **Schedule (systems re-review): the pilot is
   ~33–80h compute (~53h central), NOT an overnight job** — arm C alone is ~70% of the
   work. Run as TWO off-peak windows: night 1 = {A, A′, B, D} at 50×3 (~25h); night 2 =
   arm C at 50×3 (~28h). If a single window is forced, cut arm C's pilot to 25 instances
   (still yields a usable ρ). Never cut rollouts below 3.
4. **Full-500 go/no-go** = C2 (ρ ≥ 0.2) AND acceptable pilot wall-clock AND pilot-implied
   MDE ≤ 5 pp (else expand N or run C-vs-A′ as underpowered/estimation). **Full run carries
   A, A′, B, C, E** (B3); arm D only if pilot-promising.
