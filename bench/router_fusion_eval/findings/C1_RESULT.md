# C1 Parity Smoke — RESULT: PASS (2026-06-24)
Gate from DESIGN.md v2.1 §C1. Run on <host> (podman, x86_64), isolated venv
~/fusion_parity, scoped podman service — the shared box's other experiment (tokensaver
RULER + its minisweagent containers) was NOT disturbed.

## Result
| Check | Expectation | Observed | Verdict |
|-------|-------------|----------|---------|
| Gold patches (5 pylint) | all RESOLVE (green) | **5/5 resolved, 0 errors** | ✅ |
| Empty patches (5 pylint) | all UNRESOLVED (red) | **0/5 resolved, 5/5 empty_patch** | ✅ |

The official SWE-bench harness correctly separates a real fix from a non-fix on these
instances — no false greens, no false reds. This validates that grading is trustworthy
before any GPU spend.

Instances: pylint-dev__pylint-{4551,4604,4661,4970,6386} (SWE-bench Verified).

## NOTE — what C1 caught (the point of the gate)
A naive run FAILED first, in two distinct ways, both now fixed and documented:
1. **netavark/iptables** — rootless podman default bridge needs `ip_tables` kmod →
   "Operation not permitted" → containers couldn't START. Fix: pasta netns via a SCOPED
   `CONTAINERS_CONF` (`conf/containers.conf`) + my own `podman system service` on a private
   socket (`/run/user/<uid>/fusion_podman.sock`). Global default left untouched.
2. **rootless chown on put_archive** — harness tars patch.diff/eval.sh preserving host uid
   (<uid>) → `lchown: invalid argument` inside the userns. Fix: tar `filter=` resets
   ownership to uid/gid 0 in `swebench/harness/docker_utils.py:copy_to_container`.
3. **fwdproxy unreachable from container** — pylint-4661's gold patch adds a NEW dep
   (`appdirs` in setup.cfg); eval's `pip install -e .` must fetch it, but fwdproxy
   (IPv6-only, filtered) rejects in-container connections → ModuleNotFoundError → gold
   "fails". Fix: offline wheelhouse — `wheels/` + `PIP_FIND_LINKS=/wheels` + `PIP_NO_INDEX=1`
   injected via env+volume in `docker_build.py:create_container`. THIS IS A PILOT-SCALE
   FINDING: any instance that adds a pip dependency needs its wheel pre-staged offline.

## Reusable artifacts (for the pilot)
- `conf/containers.conf` — pasta netns (scoped, no global change).
- scoped `podman system service` on a private socket — NOTE: needs a keep-alive (systemd
  user unit) for long runs; it vanished once mid-smoke (also a node-disconnect happened).
- harness patches (in the isolated venv): docker_utils tar-ownership filter;
  docker_build PIP_FIND_LINKS/volume injection. Re-apply if the venv is rebuilt.
- `wheels/` offline dep cache — must be grown to cover deps SWE-bench instances add.
- `docker->podman` shim in `bin/`.

## Gate decision
C1 = PASS. The blocking gate on GPU time is cleared FOR THESE 5 INSTANCES. Before the
pilot-50, grow the wheelhouse (pre-scan all 50 gold patches' setup.* / requirements for
added deps) and stand up the podman service as a durable unit. Next: build the in-loop
execution sandbox so the IN-LOOP verdict can be parity-checked against this grading path
(C1's deeper intent — same-verdict on gold AND known-bad, which the empty-patch arm
already half-demonstrates at the grading layer).
