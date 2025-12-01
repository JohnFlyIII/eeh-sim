from typing import Dict, Any, Set, List

def build_ltm_from_universe(scn: Dict[str,Any], agent_name: str) -> Set[str]:
    u = (scn.get("universes", {}) or {}).get(agent_name, {})
    facts = u.get("known_facts", []) or []
    return {str(f).strip().lower() for f in facts if isinstance(f, str)}

def known_facts_list(scn: Dict[str,Any], agent_name: str) -> List[str]:
    u = (scn.get("universes", {}) or {}).get(agent_name, {})
    facts = u.get("known_facts", []) or []
    return [str(f).strip() for f in facts if isinstance(f, str)]

def ltm_bias_fn(ltm_set: Set[str]):
    def score(txt: str) -> float:
        t = str(txt).strip().lower()
        if not t:
            return 0.0
        if t in ltm_set:
            return 1.0
        for seed in ltm_set:
            if seed in t or t in seed:
                return 0.6
        return 0.0
    return score
