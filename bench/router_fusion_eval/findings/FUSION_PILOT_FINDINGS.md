# Does fusing Sonnet 4.5 with Qwen-7B help? — PILOT FINDINGS (directional, underpowered)
2026-06-24. STATUS: pilot only. NOT statistically significant. NOT a verdict.

## ⚠️ Statistical honesty (read first)
- Headline comparison is PAIRED on an 8-instance failure band. McNemar exact **p = 0.50**.
- This is ~10-20x under-powered. A real claim needs ~50-100 failure-band instances (≈100-160 total
  at the observed ~62% solve rate); we ran 22 total / 8 in-band.
- All numbers below are DIRECTIONAL. Do not state "fusion does not help" as established fact.

## What we ran (same scaffold + grading throughout; mini-swe-agent backticks; SWE-bench Verified)
- 22 warm-image instances, 9 repos. Sonnet-4.5 alone (best@1): **13/21 = 62%** (Wilson 95% CI 41-79%; 1 instance grading gap).
- On the 8 instances Sonnet-alone FAILED (the only band where fusion can add value), 3 conditions:

| Condition | Recovered of 8 | 95% CI | Note |
|-----------|----------------|--------|------|
| Sonnet alone (best@1) | 0/8 | by construction | baseline = the failure band |
| Sonnet + Qwen-7B fusion (Sonnet judge synthesizes from {Sonnet,Qwen} patches) | **0/8** | 0-32% | patch-level fusion, NOT in-loop arm C |
| Sonnet best@3 (3 independent Sonnet rollouts) | **2/8** | 5-57% | recovered pylint-4970, pylint-6386 |

McNemar (fusion vs best@3): discordant best@3-only=2, fusion-only=0 → **p=0.50, not significant.**

## What is DIRECTIONALLY suggested (NOT proven)
1. Fusing a much-weaker model (Qwen-7B) into a strong one (Sonnet) did not recover any failures in this
   small sample, while simply re-sampling Sonnet recovered 2. Suggestive that fusing-DOWN is not the
   efficient use of compute — but p=0.50, so this is a hypothesis, not a result.
2. Fusion did not HURT on easy instances (3/3 preserved; the judge ignored Qwen's garbage). The DRACO
   anchoring risk did not materialize with an explicit "don't be anchored" instruction. (Also small N.)

## What is SOLID (larger effect, less ambiguous)
- The CAPABILITY-FLOOR finding: Qwen-7B alone = 0/3 easy + 0/1 best@5 on the 1-line gimme; Sonnet = 3/3
  easy, 13/21 overall. Execution-grounded fusion is UNMEASURABLE below a base-model capability threshold
  (E≈A≈0 → f=(C-A)/(E-A) undefined). This model-floor framing is the most defensible takeaway and is a
  large, repeatable effect — though still only ~25 instances total.

## Known limitations (why this is a pilot, not a paper)
- N way too small (p=0.50 headline). - Patch-level fusion only; NOT the in-loop execution-grounded arm C
  the design was built around. - Budget NOT strictly token-matched (best@3 used ~more compute and still
  won, which only strengthens direction, but isn't a clean budget-matched test). - Single model pair;
  can't separate "fusion useless" from "fusing-DOWN useless" without a Sonnet+Sonnet or Sonnet+peer panel.
  - One grading gap (pylint-4551 fusion, pylint-4604 slice).

## Honest verdict
Inconclusive but directionally consistent with "weak-model fusion ≤ best@k on a strong base, and the real
lever is base-model capability + best@k / execution-verified repair." Needs a powered run to claim anything.
