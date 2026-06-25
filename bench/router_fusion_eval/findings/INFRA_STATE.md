# Fusion experiment infra state (<host>) — live notes
## Working topology
- Agent: mini-swe-agent 2.4.2 in ~/fusion_parity/.venv, runs HERE (<host>).
- LLM: vLLM Qwen2.5-Coder-7B on <host>:8000, reached via SSH tunnel localhost:8000.
- Tunnel: systemd --user service `fusion-tunnel.service` (linger enabled) — survives node
  blips, auto-restarts. THIS replaced fragile nohup/setsid tunnels that died on disconnect.
- Execution+grading: podman (pasta netns via scoped CONTAINERS_CONF), my private podman
  service socket; SWE-bench harness patched (tar chown filter + offline wheelhouse).
- Model class: LitellmTextbasedModel (NOT default toolcall) + swebench_backticks.yaml —
  vLLM endpoint has no native tool-calling, so text/backticks parsing is required.
  Env: MSWEA_COST_TRACKING=ignore_errors, MSWEA_DOCKER_EXECUTABLE=podman, num_retries=8.

## Key decisions / gotchas learned
- Cross-DC (atn0<->ldc0) direct ports firewalled; only SSH (22) crosses -> tunnel required.
- GPU box: 4GB free RAM, no container runtime -> cannot host execution; reuse-only.
- Default swebench.yaml uses native tool calls -> RepeatedFormatError on vLLM. Fixed by
  textbased model + backticks config.
- Node disconnects kill CLI-tied background procs -> use systemd user services for anything
  that must survive (tunnel done; podman service should be too if pilot runs long).

## C1: PASSED (gold 5/5 green, empty 0/5). Grading trustworthy.
