# Fusion-Related Docs Audit (2026-06-24)
Scope: every non-versioned doc/README that describes Fusion, checked against shipped
code and against the v2 direction (drop DRACO; add execution grounding; keep "fusion"
name earned via judge-synthesis, not relabeled best-of-N). Versioned docs
(`website/versioned_docs/*`) are release snapshots — intentionally NOT edited.

## Files audited
1. `website/docs/tutorials/algorithm/looper/fusion.md`  — canonical user-facing reference
2. `website/docs/proposals/deliberation-algorithms.md`   — the design rationale/proposal
3. `website/docs/overview/collective-intelligence.md`     — overview framing
4. `bench/grounded_fusion/README.md`                      — DRACO bench (being retired)
5. `bench/grounded_fusion/FINDINGS.md`                    — DRACO results (keep as record)
6. `config/README.md`, `ml-binding/README.md`            — config/runtime mentions (peripheral)

## Verified: code ↔ docs consistency (fusion.md)
ACCURATE as shipped. Spot-checked against source:
- Reference modes in `config/fusion_config.go` = `hybrid|context|panel` ONLY.
  → fusion.md documents exactly these three. **`execution` does NOT exist yet** —
    so v2's "new `execution` reference mode" is genuinely net-new, not overclaiming. ✔
- `policy = weight|annotate|filter`, default `weight`; `filter` opt-in — matches code
  (`grounding.go`, `make_configs.py`) and FINDINGS rationale. ✔
- Early-exit (`shouldFusionEarlyExit`, panel-mode, unanimity-gated) and adaptive
  escalation (`shouldEscalateToSingleModel`, hard-complexity-gated) — match
  `fusion_servability.go`. ✔
- Prometheus metric names match `metrics` calls. ✔
- `CachedPanel` seam exists in `looper.go` (used by `fusioneval`) — not user-facing,
  correctly absent from fusion.md. ✔

## Findings / required edits

### F1 — DRACO is the documented eval anchor; v2 drops it (STALE) [proposal]
`deliberation-algorithms.md` §5 ("borrow the DRACO eval harness"), §7 ("attacks DRACO's
factual-accuracy axis"), §8 ("Borrow DRACO-style scoring to prove the lift") all pin the
*evaluation* to DRACO. With DRACO retired, these read as the current plan but are not.
**Edit:** add a status note to §8 — "DRACO A/B is retired (panel-mode consensus is a weak
oracle; see grounded_fusion/FINDINGS.md). The lift is now proven via execution-grounded
fusion on SWE-bench Verified — see bench/router_fusion_eval/DESIGN.md." Do NOT delete the
DRACO findings; they are the negative result that motivates execution grounding.

### F2 — "External verifier" already anticipated but unbuilt (ALIGN, low effort) [proposal]
`deliberation-algorithms.md` §6 already lists "**External verifier** — strong but an
operational dependency" as a third reference option, and §3.4.4 says "prefer ground truth
over mutual agreement." v2's `execution` reference mode is the concrete realization of
exactly this. **Edit:** in §6, rename/expand the "External verifier" bullet to
"**Execution** (run tests / tools) — ground-truth oracle for verifiable tasks (code);
see DESIGN.md", linking the new work. This makes the proposal self-consistent and shows
the direction was foreseen, not bolted on.

### F3 — bench/grounded_fusion/README.md doesn't say it's retired (STALE) [bench]
The README still reads as the active eval plan ("Context mode (next step)…", full-run
instructions). Per your call, DRACO is dropped. **Edit:** add a top banner:
"⚠️ RETIRED (2026-06): DRACO pursuit ended — panel-mode consensus is a weak/again-harmful
oracle (FINDINGS.md). Superseded by execution-grounded fusion on SWE-bench:
bench/router_fusion_eval/DESIGN.md. Kept for the record + reusable harness pieces
(rubric_judge, paired-bootstrap metrics, cached-panel seam)." Keep the code — metrics.py,
the cached-panel paired design, and compare_multiarm are directly reusable by v2.

### F4 — "fusion" naming guardrail not stated anywhere (PREVENTIVE) [proposal + new bench]
The novelty review's key risk: calling one-model-×-k "fusion" invites "best-of-N
rebranded." No doc currently draws this line. **Edit:** add one sentence to
`deliberation-algorithms.md` §3 and to DESIGN.md (done): "Fusion = the judge MERGES across
a candidate pool; single-model best@k selection is *verifier-guided best-of-N*, not
fusion." Protects the name you want to keep by making it earned.

### F5 — collective-intelligence.md / overview (CHECK, likely fine) [overview]
Frames the multi-model story. Verify it doesn't claim fusion "beats frontier by consensus"
(the DRACO-falsified framing). If it does, soften to the §3.1 mechanism (lift is the
judge's verify-mode synthesis, not consensus). Low priority; read before next release.

## What is NOT changing
- `fusion.md` runtime reference: accurate, no edits needed until the `execution` mode
  actually ships (then add a "Reference: execution" subsection mirroring context/panel).
- Versioned docs (v0.1/v0.2): frozen release snapshots — leave as-is.
- DRACO FINDINGS.md: preserved verbatim — it is the motivating negative result.

## Recommended edit order (cheap → high-value)
1. F3 banner on grounded_fusion/README.md (retire marker) — 2 min.
2. F1 status note + F2 execution bullet + F4 guardrail in deliberation-algorithms.md — 15 min.
3. F5 overview read-through — before next release.
4. fusion.md `execution` subsection — deferred until the mode ships.
