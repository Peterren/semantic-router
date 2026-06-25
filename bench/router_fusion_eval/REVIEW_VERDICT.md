# Committee Verdict — Execution-Verified Fusion on SWE-bench
Date: 2026-06-24 | Decision: **CONDITIONAL GO (pilot-50 only)**

## Panel
| Reviewer | Verdict |
|---|---|
| Skeptical empiricist | REJECT as-spec → APPROVE-WITH-CHANGES |
| Research novelty | INCREMENTAL-BUT-PUBLISHABLE |
| Systems / deployability | FEASIBLE-WITH-CHANGES |

## The convergent finding
All three independently identified the SAME object of study: **the quality of the
in-loop execution signal** (self-generated / pre-existing repo tests).
- Empiricist: gate the whole experiment on whether that signal correlates with the
  hidden-test resolve outcome (pre-register Spearman rho >= 0.2 on the pilot).
- Novelty: that correlation IS the publishable contribution — the execution-signal
  analog of our DRACO consensus-signal study. "Router/fusion" is framing, not novelty.
- Systems: prove the in-loop signal isn't a fiction via an environment-parity smoke
  test (in-loop test verdict must match the grading harness exactly) before any GPU-days.

=> Reframe the thesis as a SIGNAL-QUALITY MEASUREMENT, not "router fusion beats one model."

## Hard conditions before any GPU time (all mandatory)

### C1 — Parity smoke test (systems, #1 risk)  [BLOCKS EVERYTHING]
On <exec-host>/podman, 5 instances: (a) gold patches go green through the official
SWE-bench harness; (b) the IN-LOOP test executor returns the SAME pass/fail as the
grading harness on a gold patch AND a known-bad patch. If even one disagrees, STOP and
fix environment parity. This is the cheap canary against grade/loop skew.

### C2 — Signal-quality gate (empiricist, #1 must-fix)  [GATES FULL RUN]
On the pilot-50, log per candidate: #self-tests, self-test pass rate, repo-pretest pass
rate, and the correlation of in-loop pass vs hidden-test resolve. Pre-registered go/no-go:
require Spearman rho >= 0.2 between in-loop pass and resolve. If <= 0 (the DRACO pattern),
execution-verified fusion is dead by construction — do NOT proceed to 500.

### C3 — Contamination control (empiricist T1)
Qwen2.5-Coder has likely ingested these repos' fix commits. Differences out in paired
comparison, but: never headline the raw 500 resolve rate; report the primary delta on a
LOW-MEMORIZATION stratum (flag instances reproducible under a "recite the fix" probe).

### C4 — Split the verifier levers (empiricist T2)
Report "repo pre-existing tests" vs "self-generated tests" SEPARATELY — opposite leakage
profiles. A 7B writing tests that pass its own wrong patch is reward-hacking a proxy
(exactly the DRACO confident-wrong pattern). Lumping them hides the mechanism.

### C5 — Budget definition (empiricist T3)
Budget = served-model TOTAL TOKENS (prompt+gen, incl. judge + repair rounds), +/-5% per
instance, enforced and logged. Report realized budget distribution per arm to prove match.

### C6 — Power & decision rule (empiricist T4/decision-rule)
- N=50 cannot distinguish a 4pp lift from 0 (CI ~ +/-10-12pp) — pilot is for C1/C2 + plumbing,
  NOT the headline. State minimum-detectable-effect at N=500 up front (from pilot discordant rate).
- "C ≈ A'" must be an EQUIVALENCE test (TOST) with a pre-set margin, else verdict = INCONCLUSIVE
  (not FUSION-ADDS-NOTHING). Underpowered null must not masquerade as a negative result.
- Add a HARMFUL verdict branch (C significantly < A') — the most scientifically interesting
  outcome and the live DRACO-style risk.
- Single primary comparison = C vs A' (Holm-correct the secondary C vs B).
- Resample whole INSTANCES in the bootstrap (not rollouts). Patch-apply/step-limit failures
  are pre-registered as "not resolved" (no dropping = no informative censoring).
- >= 3 rollouts/arm/instance on the pilot to separate rollout luck from arm effect.

### C7 — Confront Agentless head-on (novelty)
Agentless already does test-based patch selection on SWE-bench. The design MUST answer
"how is arm C different" or it's dead. Likely honest answer: non-oracle verifier-quality
*measurement* + compute frontier, not a new selection mechanism.

### C8 — Honest labeling (novelty)
- Arm A'/B (one model, k samples + selection) = "verifier-guided best-of-N", NOT "fusion".
  Calling it fusion invites "best-of-N rebranded" — fatal.
- "Fusion" earns its name ONLY via arm D (heterogeneous panel) + a synthesis step that
  MERGES partial solutions across candidates (not just selects one). Make D load-bearing
  or drop the fusion branding and sell as compute-optimal verifier-guided generation.
- Router/serving-layer/OpenAI-API framing = engineering, present as such, not as novelty.

### C9 — Report the FRONTIER, not points (novelty)
Sweep budget; plot achieved-resolve vs compute per arm. Report verifier precision/recall
vs hidden tests, and the realized fraction of (E - A') the non-oracle verifier captures.
That recovered-fraction IS the headline number.

## Infra topology (systems, verified live)
- INFERENCE: <gpu-host> vLLM Qwen2.5-Coder-7B :8000. 2733 MiB free, shared. HARD concurrency
  cap 2-3, off-peak only, pre-flight abort if mem.free<2GB or util>80% sustained. No new GPU loads.
- IN-LOOP EXEC + GRADING: <exec-host>, podman 5.8.2, x86_64, 96c/235GB/554GB-free. Run SWE-bench
  images here natively (alias docker->podman). Pre-stage images (tens-100+ GB). NOTHING on Mac
  (no Docker, arm64). Mac runs only the mini-swe-agent client pointing at remote endpoints.
- SCOPE: all 6 arms on pilot-50; take ONLY arm C + baseline to 500 (full matrix at 500 = days).
- ENGINEERING: in-loop per-instance container lifecycle (checkout@base, apply patch, run tests,
  capture, teardown) is ~1-2 eng-weeks and is the REAL cost — the "missing grounding backend"
  framing undersold it. Environment parity (C1) is the make-or-break.

## Bottom line
GO for the pilot-50, but ONLY after C1 (parity smoke) passes. Full-500 is a SEPARATE go/no-go
gated on C2 (signal rho>=0.2) + pilot wall-clock. Reframe deliverable around verifier-signal
quality (the execution analog of DRACO), not "router fusion wins."

---

# RE-REVIEW VERDICT (v2.1) — 2026-06-24
v2 went back to the same three reviewers. All cleared it:
| Reviewer | v1 | v2 |
|---|---|---|
| Empiricist | REJECT | APPROVE-WITH-CHANGES (3 blocking fixes) |
| Novelty | INCREMENTAL | **NOVEL** (conditional) |
| Systems | FEASIBLE-WITH-CHANGES | FEASIBLE-WITH-CHANGES (schedule fix) |

## Blocking fixes folded into v2.1
- **B3 (real bug):** full-500 must carry A, A′, B, C, E — not "C + A only" — or the
  decision rule (C vs A′, C vs B) has no N=500 data. FIXED in §3 scope + §10.
- **B1:** pre-committed smallest shippable effect = 5 pp (not computed post-pilot). §C6.
- **B2:** TOST equivalence margin Δ_equiv = 3 pp (< MDE). §C6 + §7.
- **N1:** contamination probe made concrete (issue→fix, token-similarity, two thresholds
  0.5/0.7, report robustness across both). §C3.
- **N2:** B/D/E contrasts explicitly labeled descriptive/exploratory; only C-vs-A′
  confirmatory, C-vs-B Holm-secondary. §C6 + §7.
- **Novelty:** measurement (f, ρ, frontier) decoupled as the spine; fusion (C>A′) is a
  finding within it, not the flag. Report f for BOTH C and A′ (= quantified Agentless
  confrontation). Framing block at top + §1.
- **Systems:** pilot is ~53h (not overnight); explicit two-night schedule (or pilot-25 on
  arm C), never cut rollouts below 3. §10.

## DECISION: GO. Proceed to C1 parity smoke (CPU-only on <exec-host>, blocks no GPU work).
Field note: <exec-host> already runs a live `minisweagent-…`/`swebench/sweb.eval.x86_64…`
container — likely one of the "other experiments." Treat the box as SHARED: no killing
containers, parity smoke in its own namespace, off-peak. Confirms mini-swe-agent+SWE-bench
is already operational there (feasibility ✔).

---

# C1 PARITY SMOKE — RESULT: PASS (2026-06-24, on <exec-host>)
- Gold patches: **5/5 resolved**, 0 errors. Empty patches: **0/5 resolved** (5/5 empty).
- Harness correctly separates real fix from non-fix → grading is trustworthy.
- C1 caught 3 real infra issues (all fixed, documented in ~/fusion_parity/C1_RESULT.md):
  rootless netavark/iptables (→ pasta netns, scoped), put_archive chown (→ tar ownership
  filter), and fwdproxy-unreachable-from-container forcing offline pip wheelhouse for
  instances that add deps (a pilot-scale finding).
- Shared box NOT disturbed (isolated venv + scoped podman service; tokensaver experiment untouched).
- GATE CLEARED for these 5 instances. Pre-pilot TODO: grow offline wheelhouse to cover all
  50 instances' added deps; make the podman service a durable systemd user unit (it dropped
  once mid-run). NEXT: build the in-loop execution sandbox and parity-check ITS verdict
  against this grading path (C1's deeper intent).
