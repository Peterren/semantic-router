# Decisive model comparison — 2026-06-24
Same scaffold (mini-swe-agent backticks), same 3 EASY SWE-bench Verified instances,
same validated podman+SWE-bench grading. ONLY the model differs.

## RESULT
| Model | Access | Arm A (best@1) | Notes |
|-------|--------|----------------|-------|
| Qwen2.5-Coder-7B | vLLM (local GPU) | **0/3 resolved** | empty/broken patches; repetition loops; wrong-file edits |
| Qwen2.5-Coder-7B best@5 | vLLM | **0/1** on the gimme | even 5 rollouts on the 1-line scikit fix: 4 empty, 1 created an empty file in wrong path |
| **Claude Sonnet 4.5** | internal mTLS gateway (no GPU) | **3/3 resolved** | all 3 clean submissions, correct files (_show_versions.py / blueprints.py / expressions.py) |

## Interpretation — committee hypothesis CONFIRMED
- The 7B's 0/3 was a CAPABILITY-FLOOR result, exactly as the committee predicted. E (oracle
  best@k) ~= 0 for the 7B even on the easiest instance -> headroom E-A ~= 0 -> f=(C-A)/(E-A)
  undefined/unmeasurable on the 7B. The thesis was untestable on that substrate.
- Sonnet 4.5 resolves 3/3 easy instances cleanly. There is now a base agent that resolves a
  meaningful fraction -> real best@k headroom can exist -> the fusion/verification thesis is
  MEASURABLE with Sonnet as the base model.

## Implication for the experiment
- Switch the base model to Sonnet 4.5 (Path B, committee-recommended). No GPU needed (gateway),
  no disturbance to other experiments.
- Next: build a HARDER slice (easy instances all resolve at best@1, so there's no headroom to
  recover there either — need instances where best@1 sometimes fails but best@k/verification can
  recover). That is where arms A'/B/C/E actually have signal. The easy slice was for floor-testing;
  the real experiment needs instances in Sonnet's "sometimes-solves" band.
