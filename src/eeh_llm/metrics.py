from typing import Dict, Any, List

def _longest_path_len(edges: List[Dict[str, str]]) -> int:
    succ = {}
    for e in edges or []:
        if not isinstance(e, dict): continue
        u, v = e.get("from"), e.get("to")
        if not u or not v: continue
        succ.setdefault(u, set()).add(v)
    visited = set(); best = 0
    def dfs(u, depth):
        nonlocal best
        best = max(best, depth)
        for v in succ.get(u, []):
            key = (u, v, depth)
            if key in visited: continue
            visited.add(key); dfs(v, depth+1)
    for u in list(succ.keys()): dfs(u, 1)
    return best

def _horizon_bucket(proj: Dict[str, Any]) -> int:
    if not isinstance(proj, dict): return 0
    for k in ["long","medium","short","immediate"]:
        arr = proj.get(k, [])
        if isinstance(arr, list) and len(arr) > 0:
            return {"immediate":1,"short":2,"medium":3,"long":4}[k]
    return 0

def compute_metrics_pair(data: Dict[str, Any]) -> Dict[str, Any]:
    h = data["human"]; a = data["asi"]
    return {
        "human": {
            "CausalDepthObserved": _longest_path_len(h.get("causal_links", [])),
            "EffectHorizonObserved": _horizon_bucket(h.get("projections", {})),
            "Breadth": len(h.get("factors", [])),
            "WorkingFacts": len(h.get("working_memory", {}).get("facts", [])),
            "WorkingCausalEdges": len(h.get("working_memory", {}).get("causal", [])),
            "Decision": h.get("decision",""),
            "EvictionCount": h.get("metrics",{}).get("EvictionCount",0)
        },
        "asi": {
            "CausalDepthObserved": _longest_path_len(a.get("causal_links", [])),
            "EffectHorizonObserved": _horizon_bucket(a.get("projections", {})),
            "Breadth": len(a.get("factors", [])),
            "WorkingFacts": len(a.get("working_memory", {}).get("facts", [])),
            "WorkingCausalEdges": len(a.get("working_memory", {}).get("causal", [])),
            "Decision": a.get("decision",""),
            "EvictionCount": a.get("metrics",{}).get("EvictionCount",0)
        }
    }
