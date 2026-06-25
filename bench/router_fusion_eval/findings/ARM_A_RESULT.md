# Arm A result — Qwen2.5-Coder-7B on SWE-bench Verified (3 easy instances)
Date 2026-06-24 | step_limit 120, temp 0.3, rep_penalty 1.1, max_tokens 4096, auto-extract ON
Graded via validated C1 harness path.

## RESULT: 0/3 resolved
| instance | patch | graded | failure mode |
|----------|-------|--------|--------------|
| scikit-learn-14141 | 83c (auto-extract) | UNRESOLVED | wrote fix into scratch `patch.txt`, NEVER applied to source -> extracted diff only touches patch.txt |
| pallets-flask-5014 | 5285c (auto-extract) | UNRESOLVED | REPETITION LOOP: same `if not name:` line repeated ~40x, literal `\n` as text. rep_penalty 1.1 insufficient |
| django-16082 | empty | unresolved(empty) | 0 file edits in 43-57 turns; pure investigation, context overflow |

## Honest interpretation
- This is a REAL capability/scaffold result, not an infra artifact (auto-extract + grading both verified working).
- The 7B exhibits THREE distinct small-model failure modes:
  1. Correct-reasoning / broken-edit-mechanics (earlier scikit run: right "joblib" fix, bad syntax).
  2. Plan-in-scratchpad-but-never-apply (this scikit run: fix in patch.txt, source untouched).
  3. Degenerate repetition loops (flask: same line x40), only partly mitigated by repetition_penalty.
- NONE of these are reasoning-ceiling failures per se; they are agentic-execution failures. But they DO mean
  Qwen2.5-Coder-7B + mini-swe-agent default scaffold resolves ~0% even on EASY SWE-bench Verified instances.

## Implication for the experiment (the key question for committee)
- If arm A (best@1) ~= 0% on easy instances, then E (oracle best@k) is likely very low too: sampling k loops
  that each fail to produce a VALID applied patch cannot select a good one. E-A may be ~0 -> f undefined.
- The bottleneck is NOT the fusion/verification idea; it is that the base agent rarely produces a single
  VALID candidate patch. The thesis needs a base agent that resolves >0% so there is headroom to recover.
- Two honest paths:
  (A) Invest in scaffold (better submit discipline, loop-breaking, apply-patch tooling) until 7B resolves
      a non-trivial % on easy instances, THEN run the fusion arms. Risk: large eng effort, still a weak model.
  (B) The thesis is most meaningful with a model that ALREADY resolves a moderate % (e.g. a 32B coder or a
      frontier endpoint) where best@k headroom is real. Qwen-7B may simply be below the capability floor
      where verifier-guided selection/fusion has anything to select from.
