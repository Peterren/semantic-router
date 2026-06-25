"""Arm D (heterogeneous-panel fusion): Sonnet-4.5 judge synthesizes ONE final patch from a panel of
candidate patches (Sonnet's own + Qwen's). Tests whether fusing a strong model with a weak one helps,
hurts, or is neutral vs the strong model alone."""
import json, os, ssl, urllib.request, sys
from datasets import load_dataset

CERT=os.environ.get("ANTHROPIC_MTLS_CERT", "<MTLS_CLIENT_CERT_PATH>")  # mTLS client cert for the internal gateway
EP=os.environ.get("ANTHROPIC_GATEWAY_URL", "https://<internal-anthropic-gateway>/v1/messages")

def sonnet(system, user, max_tokens=4096):
    ctx=ssl.create_default_context(); ctx.load_cert_chain(CERT,CERT); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    body={"model":"claude-sonnet-4-5","max_tokens":max_tokens,"system":system,
          "messages":[{"role":"user","content":user}]}
    req=urllib.request.Request(EP,data=json.dumps(body).encode(),
        headers={"Content-Type":"application/json","anthropic-version":"2023-06-01"})
    with urllib.request.urlopen(req,context=ctx,timeout=180) as r: d=json.load(r)
    return "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text")

ds=load_dataset("princeton-nlp/SWE-bench_Verified",split="test")
by_id={r["instance_id"]:r for r in ds}

sonnet_p=json.load(open("results_armA_sonnet/preds.json"))
qwen_p=json.load(open("results_armA/preds.json"))

ids=["scikit-learn__scikit-learn-14141","django__django-16082","pallets__flask-5014"]
SYS=("You are an expert software engineer. You are given a bug report and TWO candidate patches from "
     "different models. Synthesize the SINGLE best unified-diff patch that fixes the issue. You may pick "
     "one candidate, merge them, or write a better one. A candidate may be wrong or garbage; do not be "
     "anchored by a confidently-wrong candidate. Output ONLY a valid unified diff (git diff format), nothing else.")
out={}
for iid in ids:
    issue=by_id[iid]["problem_statement"][:6000]
    cs=sonnet_p.get(iid,{}).get("model_patch","") or "(empty)"
    cq=qwen_p.get(iid,{}).get("model_patch","") or "(empty)"
    user=(f"# Bug report\n{issue}\n\n# Candidate A (model 1)\n```diff\n{cs}\n```\n\n"
          f"# Candidate B (model 2)\n```diff\n{cq}\n```\n\nOutput ONLY the final unified diff:")
    print(f"fusing {iid} ...",file=sys.stderr)
    resp=sonnet(SYS,user)
    # strip code fences if present
    p=resp
    if "```" in p:
        import re
        m=re.search(r"```(?:diff)?\s*\n(.*?)```",p,re.DOTALL)
        if m: p=m.group(1)
    out[iid]={"model_patch":p.strip()+"\n","model_name_or_path":"fusionD"}
    print(f"  -> {len(p)} chars",file=sys.stderr)
json.dump(out,open("results_fusionD/preds.json","w"))
print("wrote results_fusionD/preds.json")
