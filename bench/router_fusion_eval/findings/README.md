# Execution-Grounded Fusion — Experiment Bank (pilot, banked 2026-06)

This directory banks a pilot investigation into **execution-grounded fusion** on SWE-bench
Verified, run end-to-end (mini-swe-agent harness, rootless-podman execution, official
SWE-bench grading). It is a **pilot**: directional, underpowered, and explicitly NOT a
publishable result. It is banked so the negative findings, the validated harness, and the
open questions are not lost.

See the parent `DESIGN.md` (v2.1) for the pre-registered design and committee review history,
and `REVIEW_VERDICT.md` for the committee gates.

## TL;DR — what we learned

1. **C1 grading parity PASSED** (`C1_RESULT.md`): gold patches 5/5 resolve, empty 0/5. The
   SWE-bench grading path is trustworthy. (Caught + fixed 3 real rootless-podman issues:
   netavark/iptables → pasta netns; put_archive chown; offline pip wheelhouse.)

2. **Capability floor** (`MODEL_COMPARISON.md`): Qwen2.5-Coder-7B resolves ~0% even on easy
   instances (0/3 easy, 0/1 best@5 on a 1-line fix). Claude Sonnet 4.5 resolves 3/3 easy,
   13/21 (62%) on a warm-image slice. **Methodological caveat:** the headroom metric
   f=(C−A)/(E−A) is *undefined* when E≈A≈0, so execution-grounded fusion is unmeasurable
   below a base-capability floor. (This is a precondition note, not a discovery — cf.
   Brown et al. "Large Language Monkeys" coverage floor.)

3. **Weak+strong fusion did not help** (`FUSION_PILOT_FINDINGS.md`): on 8 Sonnet-failures,
   Sonnet+Qwen-7B patch-level fusion recovered 0/8; Sonnet best@3 recovered 2/8.
   **NOT statistically significant — McNemar exact p=0.50, N=8, ~10-20x underpowered.**
   Directionally consistent with the Mixture-of-Agents finding that weak members don't help
   a strong proposer, but this pilot does NOT establish it.

## What is SETTLED (don't re-run)
- Consensus/panel-NLI as a grounding oracle (DRACO killed it).
- Hard-drop filtering of panel responses (DRACO: harmful).
- Fusing a much-weaker model into a strong one (pilot directional + MoA literature).

## What is OPEN (not tested here)
- **In-loop execution-grounded repair vs budget-matched best@k** — the actual thesis. This
  pilot only tested PATCH-LEVEL post-hoc synthesis, which is the wrong/weaker intervention.
- **Context-mode faithfulness** against real RAG sources (different signal; never exercised).
- **Verifier-recovered-headroom frontier**: oracle → execution → LLM-judge → majority →
  single-shot, at matched cost with CIs, on a capable base model. (Both reviewers: this is
  the only thing worth scaling, and only as a workshop-tier empirical contribution.)

## If scaling (committee-specified minimal powered design)
- In-loop **arm C**, NOT patch-level. Primary test: **C vs budget-matched self-consistency B**,
  paired McNemar. Token-matched. Pairs: Sonnet+Sonnet and Sonnet+peer-frontier (drop Sonnet+Qwen).
  N≈130-200 enriched for the failure band. Gate f to the capable-base regime. Rename: drop "fusion",
  the contribution is verifier-quality measurement.

## Layout
- `*.md` — findings writeups (pilot findings, model comparison, arm-A, C1 parity, infra).
- `findings/evidence/` — small grading reports (`*.json`) + prediction files = the actual numbers.
- `findings/configs/` — mini-swe-agent run configs + podman containers.conf.
- `findings/harness_patches/` — the internal gateway-Sonnet model class + patch-level fusion synthesis scripts.

## Reproduce
Harness: mini-swe-agent v2.4.2, model class `anthropic_gateway_model.GatewaySonnetModel` (Sonnet via
an internal mTLS Anthropic gateway, mTLS) or `LitellmTextbasedModel` (Qwen via local vLLM). Execution+grading in
rootless podman (pasta netns, see `configs/containers.conf`). Grading = official SWE-bench harness.
