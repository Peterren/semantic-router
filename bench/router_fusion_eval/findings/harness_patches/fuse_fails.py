"""Arm D fusion on the 8 Sonnet-failure instances: Sonnet-4.5 judge synthesizes ONE patch from
the panel {Sonnet's own attempt, Qwen's attempt}. Tests if a heterogeneous panel recovers failures."""
import json, os, ssl, urllib.request, sys, re
from datasets import load_dataset
CERT=os.environ.get("ANTHROPIC_MTLS_CERT", "<MTLS_CLIENT_CERT_PATH>")  # mTLS client cert for the internal gateway
EP=os.environ.get("ANTHROPIC_GATEWAY_URL", "https://<internal-anthropic-gateway>/v1/messages")
def sonnet(system,user,mt=4096):
    ctx=ssl.create_default_context();ctx.load_cert_chain(CERT,CERT);ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
    body={"model":"claude-sonnet-4-5","max_tokens":mt,"system":system,"messages":[{"role":"user","content":user}]}
    req=urllib.request.Request(EP,data=json.dumps(body).encode(),headers={"Content-Type":"application/json","anthropic-version":"2023-06-01"})
    with urllib.request.urlopen(req,context=ctx,timeout=180) as r: d=json.load(r)
    return "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text")
fails=json.load(open('sonnet_slice_verdict.json'))['failed']
ds=load_dataset("princeton-nlp/SWE-bench_Verified",split="test"); byid={r["instance_id"]:r for r in ds}
sp=json.load(open("results_sonnet_slice/preds.json")); qp=json.load(open("results_qwen_fails/preds.json"))
SYS=("You are an expert software engineer. Given a bug report and TWO candidate patches from different "
     "models (both may be wrong), synthesize the SINGLE best unified-diff patch that fixes the issue. "
     "Pick one, merge, or write better. Do NOT be anchored by a confidently-wrong candidate. "
     "Output ONLY a valid git unified diff, nothing else.")
out={}
for iid in fails:
    issue=byid[iid]["problem_statement"][:7000]
    cs=sp.get(iid,{}).get("model_patch","") or "(empty)"; cq=qp.get(iid,{}).get("model_patch","") or "(empty)"
    user=f"# Bug report\n{issue}\n\n# Candidate A\n```diff\n{cs}\n```\n\n# Candidate B\n```diff\n{cq}\n```\n\nOutput ONLY the final unified diff:"
    print("fusing",iid,file=sys.stderr)
    try:
        resp=sonnet(SYS,user); p=resp
        m=re.search(r"```(?:diff)?\s*\n(.*?)```",p,re.DOTALL)
        if m: p=m.group(1)
        out[iid]={"instance_id":iid,"model_name_or_path":"fusionD","model_patch":p.strip()+"\n"}
        print("  ->",len(p),"chars",file=sys.stderr)
    except Exception as e:
        print("  ERR",str(e)[:100],file=sys.stderr); out[iid]={"instance_id":iid,"model_name_or_path":"fusionD","model_patch":""}
json.dump(list(out.values()),open("preds_fusionD_fails.json","w"))
print("wrote preds_fusionD_fails.json with",len(out),"patches")
