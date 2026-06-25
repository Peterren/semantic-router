"""Sonnet-4.5 backend for mini-swe-agent via an internal mTLS Anthropic gateway (Anthropic Messages API, mTLS).
Subclasses LitellmTextbasedModel so it reuses the backticks (```mswea_bash_command```) action parser.
_query returns a litellm ModelResponse so query()/_calculate_cost/_parse_actions all work unchanged.
"""
import json, os, ssl, time, urllib.request
import litellm
from litellm import ModelResponse
from litellm.types.utils import Choices, Message, Usage
from minisweagent.models.litellm_textbased_model import LitellmTextbasedModel

_CERT = os.environ.get("ANTHROPIC_MTLS_CERT", "<MTLS_CLIENT_CERT_PATH>")  # mTLS client cert for the internal gateway
_ENDPOINT = os.environ.get("ANTHROPIC_GATEWAY_URL", "https://<internal-anthropic-gateway>/v1/messages")


def _split_system(messages):
    sys_txt = "\n\n".join(m.get("content", "") for m in messages if m.get("role") == "system")
    conv = [{"role": m["role"], "content": m.get("content", "")} for m in messages if m.get("role") != "system"]
    return sys_txt, conv


class GatewaySonnetModel(LitellmTextbasedModel):
    def _query(self, messages, **kwargs):
        model = self.config.model_name.replace("openai/", "").replace("anthropic/", "")
        if not model.startswith("claude"):
            model = "claude-sonnet-4-5"
        system, conv = _split_system(messages)
        body = {"model": model,
                "max_tokens": self.config.model_kwargs.get("max_tokens", 4096),
                "messages": conv}
        if system:
            body["system"] = system
        ctx = ssl.create_default_context(); ctx.load_cert_chain(_CERT, _CERT)
        ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        last = None
        for attempt in range(int(self.config.model_kwargs.get("num_retries", 5))):
            try:
                req = urllib.request.Request(_ENDPOINT, data=json.dumps(body).encode(),
                         headers={"Content-Type": "application/json", "anthropic-version": "2023-06-01"})
                with urllib.request.urlopen(req, context=ctx, timeout=self.config.model_kwargs.get("timeout", 180)) as r:
                    d = json.load(r)
                text = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")
                u = d.get("usage", {}) or {}
                stop = d.get("stop_reason") or "stop"
                fr = "length" if stop == "max_tokens" else "stop"
                resp = ModelResponse(
                    model=model,
                    choices=[Choices(index=0, finish_reason=fr,
                                     message=Message(role="assistant", content=text))],
                    usage=Usage(prompt_tokens=u.get("input_tokens", 0),
                                completion_tokens=u.get("output_tokens", 0),
                                total_tokens=u.get("input_tokens", 0) + u.get("output_tokens", 0)),
                )
                return resp
            except Exception as e:
                last = e
                time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"internal gateway Sonnet failed after retries: {last}")

    def _calculate_cost(self, response) -> dict:
        # internal gateway is internal/free for our purposes; report token usage, zero cost.
        u = getattr(response, "usage", None)
        pt = getattr(u, "prompt_tokens", 0) if u else 0
        ct = getattr(u, "completion_tokens", 0) if u else 0
        return {"cost": 0.0, "input_tokens": pt, "output_tokens": ct, "n_calls": 1}
