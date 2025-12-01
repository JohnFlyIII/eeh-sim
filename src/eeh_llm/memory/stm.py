import time
from typing import List, Dict, Any
from ..utils import clamp01

def _now_ts(): return time.time()
def _normalize(v, lo, hi):
    if hi <= lo: return 0.0
    return clamp01((v - lo) / (hi - lo))

class STMStore:
    def __init__(self, facts_cap: int, causal_cap: int, weights: Dict[str, float]):
        self.facts_cap = facts_cap; self.causal_cap = causal_cap; self.weights = weights
        self.facts: List[Dict[str, Any]] = []; self.causal: List[Dict[str, Any]] = []
        self.log_evict: List[Dict[str, Any]] = []

    def _score_fact(self, item: Dict[str, Any]) -> float:
        w = self.weights
        rec = 1.0 - _normalize(_now_ts() - item["ts"], 0, 30)
        return (w.get("ltm_weight",1.0) * item.get("ltm_bias", 0.0)
              + w.get("recency_weight",0.6) * rec
              + w.get("novelty_weight",0.5) * item.get("novelty", 0.0))

    def _score_edge(self, item: Dict[str, Any]) -> float:
        w = self.weights
        rec = 1.0 - _normalize(_now_ts() - item["ts"], 0, 30)
        return (w.get("ltm_weight",1.0) * item.get("ltm_bias", 0.0)
              + w.get("recency_weight",0.6) * rec
              + w.get("novelty_weight",0.5) * item.get("novelty", 0.0)
              + w.get("causal_centrality_weight",0.7) * item.get("centrality", 0.0))

    def _evict_until_fit(self):
        while len(self.facts) > self.facts_cap:
            victim = min(self.facts, key=self._score_fact)
            self.log_evict.append({"type":"fact","item":victim["text"],"score": self._score_fact(victim)})
            self.facts.remove(victim)
        while len(self.causal) > self.causal_cap:
            victim = min(self.causal, key=self._score_edge)
            self.log_evict.append({"type":"edge","item":(victim["from"],victim["to"]),"score": self._score_edge(victim)})
            self.causal.remove(victim)

    def _dedup_facts(self):
        seen = set(); out = []
        for it in self.facts:
            k = it["text"].strip().lower()
            if k not in seen: seen.add(k); out.append(it)
        self.facts = out

    def _dedup_edges(self):
        seen = set(); out = []
        for it in self.causal:
            u, v = (it.get("from","").strip().lower(), it.get("to","").strip().lower())
            lbl = it.get("label","").strip()
            if not u or not v: continue
            k = (u,v,lbl)
            if k not in seen: seen.add(k); out.append(it)
        self.causal = out

    def add_facts(self, facts_new: List[str], ltm_bias_lookup) -> None:
        now = _now_ts()
        for f in facts_new or []:
            if not isinstance(f,str) or not f.strip(): continue
            t = f.strip()
            self.facts.append({"text": t, "ts": now, "uses": 0, "ltm_bias": ltm_bias_lookup(t), "novelty": 1.0})
        self._dedup_facts(); self._evict_until_fit()

    def add_edges(self, edges_new: List[Dict[str,str]], ltm_bias_lookup) -> None:
        now = _now_ts()
        def centrality_for(e):
            base = [{"from":x.get("from"),"to":x.get("to")} for x in self.causal]
            if not base: return 0.0
            prev_tos = {x["to"] for x in base}; prev_froms = {x["from"] for x in base}
            return (0.6 if e["from"] in prev_tos else 0.0) + (0.4 if e["to"] in prev_froms else 0.0)
        for e in edges_new or []:
            if not isinstance(e, dict): continue
            u = (e.get("from","").strip(),)
            v = (e.get("to","").strip(),)
            u = u[0]; v = v[0]
            lbl = (e.get("label","").strip() or "")
            cf  = bool(e.get("cf", False))
            if not u or not v: continue
            self.causal.append({"from": u, "to": v, "label": lbl, "cf": cf, "ts": now, "uses": 0,
                                "ltm_bias": ltm_bias_lookup(u) + ltm_bias_lookup(v),
                                "centrality": centrality_for({"from":u,"to":v}),
                                "novelty": 1.0})
        self._dedup_edges(); self._evict_until_fit()

    def snapshot_plain(self):
        return ([x["text"] for x in self.facts],
                [{"from": x["from"], "to": x["to"], "label": x.get("label",""), "cf": x.get("cf", False)} for x in self.causal])
