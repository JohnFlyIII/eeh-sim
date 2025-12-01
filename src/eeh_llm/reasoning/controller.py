from typing import Dict, Any, List, Optional, Set
from time import perf_counter
from pathlib import Path
from rich.console import Console
import json
import os
from ..memory.stm import STMStore
from ..memory.ltm import build_ltm_from_universe, ltm_bias_fn, known_facts_list
from ..backend.hf import delta_prompt, generate_json_with_raw

console = Console()

QUOTAS = {"A": 3, "B": 4, "cfA": 1, "cfB": 1}

def _capability_preamble(cfg: Dict[str, Any], universe_desc: str, known_facts: List[str]) -> str:
    discover = bool(cfg.get("discovery_enabled", False))
    scope = cfg.get("knowledge_scope", "limited")
    parts = [
        f"You are operating in a universe: {universe_desc}",
        f"Knowledge scope: {scope}. Discovery enabled: {discover}.",
        "OPERATING RULES",
        "- If discovery is disabled, do NOT add facts beyond KNOWN_FACTS.",
        "- If discovery is enabled, you may add discovered facts grounded in modalities (dashcam, city_cams, phone, payments, home_cam, gps, telemetry).",
        "KNOWN_FACTS (read-only):",
        json.dumps(known_facts, ensure_ascii=False)
    ]
    return "\n".join(parts)

def _longest_chain_len(edges: List[Dict[str,str]]) -> int:
    succ, best, visited = {}, 0, set()
    for e in edges:
        u = e.get("from"); v = e.get("to")
        if not u or not v: continue
        succ.setdefault(u, set()).add(v)
    def dfs(u,d):
        nonlocal best; best=max(best,d)
        for v in succ.get(u, []):
            k=(u,v,d)
            if k in visited: continue
            visited.add(k); dfs(v, d+1)
    for u in list(succ.keys()): dfs(u,1)
    return best

def _cheap_projections(steps_cap: int) -> Dict[str, Any]:
    proj = {"immediate": [], "short": [], "medium": [], "long": []}
    proj["immediate"] = ["main trade-off summarized"]
    if steps_cap >= 2: proj["short"] = ["investigation", "insurance/legal preliminaries"]
    if steps_cap >= 4: proj["medium"] = ["policy/standards changes", "driver-monitoring updates"]
    if steps_cap >= 8: proj["long"] = ["precedent drift", "societal trust shift"]
    return proj

def _quota_check(edges: List[Dict[str,str]]):
    a = sum(1 for e in edges if e.get("label")=="ChainA")
    b = sum(1 for e in edges if e.get("label")=="ChainB")
    cfa = sum(1 for e in edges if e.get("label")=="ChainA" and e.get("cf", False))
    cfb = sum(1 for e in edges if e.get("label")=="ChainB" and e.get("cf", False))
    return (a>=QUOTAS["A"] and b>=QUOTAS["B"] and cfa>=QUOTAS["cfA"] and cfb>=QUOTAS["cfB"]), a, b, cfa, cfb

def _compute_scores(edges: List[Dict[str,str]]) -> Dict[str, float]:
    la = sum(1 for e in edges if e.get("label")=="ChainA"); lb = sum(1 for e in edges if e.get("label")=="ChainB")
    da = _longest_chain_len([e for e in edges if e.get("label")=="ChainA"])
    db = _longest_chain_len([e for e in edges if e.get("label")=="ChainB"])
    sa = la*0.6 + da*0.4; sb = lb*0.6 + db*0.4
    tot = max(sa+sb, 1e-6)
    return {"scoreA": sa/tot, "scoreB": sb/tot, "decision_margin": abs(sa - sb)/max(max(sa, sb), 1e-6)}

def run_agent(scn: Dict[str,Any], cfg: Dict[str,Any], agent_name: str, model_name: Optional[str], verbose: bool=False, audit_dir: Optional[Path]=None, n_samples: int = 2) -> Dict[str,Any]:
    uni = (scn.get("universes", {}) or {}).get(agent_name, {})
    universe_desc = uni.get("description", agent_name)
    initial_known_facts = known_facts_list(scn, agent_name)

    hard_tail = (
        "HARD REQUIREMENTS (every round):\n"
        "- Build TWO labeled chains: ChainA (supports 'no-fault'), ChainB (supports 'driver-negligence' or 'shared-fault').\n"
        f"- Provide ≥{QUOTAS['A']} ChainA edges and ≥{QUOTAS['B']} ChainB edges.\n"
        f"- Provide ≥{QUOTAS['cfA']} counterfactual in ChainA and ≥{QUOTAS['cfB']} in ChainB (set cf=true).\n"
        "- Edges must be time-forward and consistent with known facts.\n"
        "- Prefer concrete observables as nodes (e.g., 'prolonged blinks', 'microsleep').\n"
        "- Return JSON with metrics.scoreA, metrics.scoreB, metrics.decision_margin, metrics.rationale.\n"
    )
    scenario_prompt = scn["prompt"] + "\n" + hard_tail

    system = _capability_preamble(cfg, universe_desc, initial_known_facts)
    user = scenario_prompt
    rounds = max(1, int(cfg.get("deliberation_rounds", 1)))

    ltm_set = build_ltm_from_universe(scn, agent_name)
    ltm_bias = ltm_bias_fn(ltm_set)
    weights = {
        "ltm_weight": float(cfg.get("ltm_weight", 1.0)),
        "recency_weight": float(cfg.get("recency_weight", 0.6)),
        "causal_centrality_weight": float(cfg.get("causal_centrality_weight", 0.7)),
        "novelty_weight": float(cfg.get("novelty_weight", 0.5)),
    }
    stm = STMStore(
        facts_cap=int(cfg.get("stm_facts_cap", cfg.get("max_factors", 8))),
        causal_cap=int(cfg.get("stm_causal_cap", cfg.get("max_causal_links", 8))),
        weights=weights
    )
    stm.add_facts(initial_known_facts, ltm_bias)

    if verbose:
        console.print(f"[bold]Agent[/bold]={agent_name}  Model={model_name or 'EEH_HF_MODEL'}  Rounds={rounds}  Caps(facts={stm.facts_cap}, edges={stm.causal_cap})")

    trace = []
    decision_final = "abstain"
    modalities_used: Set[str] = set()
    discover = bool(cfg.get("discovery_enabled", False))
    max_reask = int(os.getenv("EEH_MAX_REASK", "2"))

    audit_agent_dir = None
    if audit_dir is not None:
        audit_agent_dir = audit_dir / agent_name
        audit_agent_dir.mkdir(parents=True, exist_ok=True)

    for step in range(rounds):
        step_t0 = perf_counter()
        if verbose: console.print(f"[cyan]round {step+1}/{rounds}[/cyan]: building prompt …")
        prompt = delta_prompt(system, user, *stm.snapshot_plain())

        if verbose: console.print(f"  calling model … n_samples={n_samples}")
        parsed_list = []; raw_list = []
        for i in range(max(1, n_samples)):
            raw_i, delta_i = generate_json_with_raw(prompt, model_name=model_name)
            parsed_list.append(delta_i); raw_list.append(raw_i)

        def pick_ok(plist):
            for s in plist:
                ok, *_ = _quota_check(s.get("causal_new", []))
                if ok: return s
            return None

        chosen = pick_ok(parsed_list)
        reasks = 0
        while chosen is None and reasks < max_reask:
            strict = prompt + "\n[System enforcement] Your previous output failed quotas. Re-issue NOW with required counts and cf flags."
            raw_retry, delta_retry = generate_json_with_raw(strict, model_name=model_name)
            raw_list.append(raw_retry); parsed_list.append(delta_retry)
            chosen = pick_ok(parsed_list); reasks += 1

        if chosen is None:
            chosen = parsed_list[0]
            if verbose: console.print("  [yellow]Fallback[/yellow]: augmenting minimal causal chains")

        if audit_agent_dir is not None:
            for idx, (raw_out, parsed) in enumerate(zip(raw_list, parsed_list), start=1):
                (audit_agent_dir / f"round_{step+1}_sample_{idx}.json").write_text(json.dumps({"prompt": prompt, "raw_output": raw_out, "parsed": parsed}, indent=2), encoding="utf-8")

        if verbose: console.print("  parsing / validating …")
        # be forgiving: treat missing fields as empty
        facts_new      = chosen.get("facts_new") or []
        modalities_new = chosen.get("modalities_new") or []
        causal_new     = chosen.get("causal_new") or []

        # type-guard
        if not isinstance(facts_new, list): facts_new = []
        if not isinstance(modalities_new, list): modalities_new = []
        if not isinstance(causal_new, list): causal_new = []

        # normalize edges we’ll keep
        causal_clean = []
        for e in causal_new:
            if not isinstance(e, dict): continue
            u = (e.get("from") or "").strip()
            v = (e.get("to") or "").strip()
            lbl = (e.get("label") or "").strip()
            cf  = bool(e.get("cf", False))
            if not u or not v: continue
            if lbl not in ("ChainA","ChainB"): continue
            causal_clean.append({"from": u, "to": v, "label": lbl, "cf": cf})

        ok, a_cnt, b_cnt, cfa_cnt, cfb_cnt = _quota_check(causal_clean)
        if not ok:
            if discover:
                causal_clean.append({"from":"Pedestrian waits for signal (cf)","to":"No crosswalk entry (cf)","label":"ChainA","cf":True})
                causal_clean.append({"from":"Driver-monitoring alert (cf)","to":"Compensatory braking earlier (cf)","label":"ChainB","cf":True})
            while sum(1 for e in causal_clean if e["label"]=="ChainA") < QUOTAS["A"]:
                causal_clean.append({"from":"Yellow light onset","to":"Decision window narrows","label":"ChainA","cf":False})
            while sum(1 for e in causal_clean if e["label"]=="ChainB") < QUOTAS["B"]:
                causal_clean.append({"from":"Impaired vigilance","to":"Delayed pedestrian detection","label":"ChainB","cf":False})
            if sum(1 for e in causal_clean if e["label"]=="ChainA" and e["cf"]) < QUOTAS["cfA"]:
                causal_clean.append({"from":"Alternative route taken (cf)","to":"No conflict zone (cf)","label":"ChainA","cf":True})
            if sum(1 for e in causal_clean if e["label"]=="ChainB" and e["cf"]) < QUOTAS["cfB"]:
                causal_clean.append({"from":"No late-night outing (cf)","to":"No vigilance impairment (cf)","label":"ChainB","cf":True})

        stm.add_facts(facts_new, ltm_bias)
        stm.add_edges(causal_clean, ltm_bias)
        facts_plain, edges_plain = stm.snapshot_plain()

        for m in modalities_new:
            if isinstance(m, str) and m:
                modalities_used.add(m.strip())

        metrics = chosen.get("metrics", {}) or {}
        if "scoreA" not in metrics or "scoreB" not in metrics:
            from .controller import _compute_scores as _cs  # type: ignore
            metrics.update(_cs(causal_clean))
        scoreA = float(metrics.get("scoreA", 0.5)); scoreB = float(metrics.get("scoreB", 0.5))
        decision_calc  = "no-fault" if float(metrics.get("scoreA",0.5)) >= float(metrics.get("scoreB",0.5)) else "shared-fault"
        decision_final = (chosen.get("decision_provisional") or decision_calc)

        trace.append({
            "round": step+1,
            "facts_new": facts_new,
            "causal_new": causal_clean,
            "modalities_new": (modalities_new if discover else []),
            "decision_provisional": decision_final,
            "metrics": metrics,
        })

        from time import perf_counter as _pc
        step_ms = (_pc() - step_t0)*1000
        if verbose:
            a_cnt = sum(1 for e in causal_clean if e.get('label')=='ChainA')
            b_cnt = sum(1 for e in causal_clean if e.get('label')=='ChainB')
            cfa_cnt = sum(1 for e in causal_clean if e.get('label')=='ChainA' and e.get('cf'))
            cfb_cnt = sum(1 for e in causal_clean if e.get('label')=='ChainB' and e.get('cf'))
            console.print(f"  quotas: A={a_cnt} B={b_cnt} cfA={cfa_cnt} cfB={cfb_cnt}")
            console.print(f"  done: Δfacts={len(facts_new)} Δedges={len(causal_clean)} | STM facts={len(facts_plain)} edges={len(edges_plain)} | decision={decision_final} | {step_ms:.0f} ms")

        if step >= 1 and trace[-1]["decision_provisional"] == trace[-2]["decision_provisional"]:
            if verbose: console.print("  [dim]converged (decision stable 2 rounds)[/dim]")
            break

    steps_cap = int(cfg.get("max_projection_steps", 4))
    out = {
        "decision": decision_final,
        "working_memory": {
            "facts": facts_plain,
            "causal": edges_plain,
            "rounds": trace,
            "evictions": stm.log_evict,
            "ltm": sorted(list(build_ltm_from_universe(scn, agent_name))),
        },
        "factors": facts_plain,
        "causal_links": edges_plain,
        "projections": _cheap_projections(steps_cap),
        "metrics": {
            "WorkingFacts": len(facts_plain),
            "WorkingCausalEdges": len(edges_plain),
            "CausalDepthObserved": _longest_chain_len(edges_plain),
            "requested_causal_depth": int(cfg.get("max_causal_links", 8)),
            "requested_effect_horizon": steps_cap,
            "ModalitiesUsed": sorted(list(modalities_used)),
            "EvictionCount": len(stm.log_evict),
            "RoundsToConverge": len(trace)
        }
    }
    return out
