"""
Controller V3 - Mode-based deep reasoning for EEH simulation
Implements separate prompting strategies for observational vs comprehensive analysis
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from time import perf_counter
from pathlib import Path
from rich.console import Console
import json
import os

console = Console()


def _build_mode_based_prompt(
    mode: str,
    universe_desc: str,
    known_facts: List[str],
    temporal_annotations: Optional[List[Dict]] = None,
    prompt_template: str = ""
) -> str:
    """
    Build prompts based on analysis mode (observational vs comprehensive)
    """

    # Build temporal context if available
    temporal_context = ""
    if temporal_annotations and mode == "comprehensive":
        temporal_context = "\n\nTEMPORAL CONTEXT (facts with time offsets from collision):\n"
        for ta in temporal_annotations:
            fact = ta.get("fact", "")
            hours = ta.get("hours_before")
            minutes = ta.get("minutes_before")
            seconds = ta.get("seconds_before")

            if hours:
                temporal_context += f"  [t = -{hours:.1f}h] {fact}\n"
            elif minutes:
                temporal_context += f"  [t = -{minutes}min] {fact}\n"
            elif seconds:
                temporal_context += f"  [t = -{seconds}s] {fact}\n"

    # Build facts context
    facts_context = "\nKNOWN FACTS:\n" + json.dumps(known_facts, indent=2, ensure_ascii=False)

    # Combine into system prompt
    system_prompt = f"""<|system|>
UNIVERSE: {universe_desc}
ANALYSIS MODE: {mode}

{prompt_template}

{facts_context}
{temporal_context}

OUTPUT: Strict JSON only. No markdown. No backticks. No additional text.
<|assistant|>
"""

    return system_prompt


def _compute_chain_depth(causal_chain: List[Dict]) -> int:
    """
    Compute longest path in causal graph using DFS
    """
    if not causal_chain:
        return 0

    # Build adjacency list
    graph = {}
    for link in causal_chain:
        from_node = link.get("from", "")
        to_node = link.get("to", "")
        if from_node and to_node:
            if from_node not in graph:
                graph[from_node] = []
            graph[from_node].append(to_node)

    # Find longest path via DFS
    max_depth = 0
    visited = set()

    def dfs(node: str, depth: int):
        nonlocal max_depth
        max_depth = max(max_depth, depth)

        if node in graph:
            for neighbor in graph[node]:
                edge_key = (node, neighbor, depth)
                if edge_key not in visited:
                    visited.add(edge_key)
                    dfs(neighbor, depth + 1)

    # Try starting from each node
    for node in graph.keys():
        dfs(node, 1)

    return max_depth


def _compute_temporal_span(causal_chain: List[Dict]) -> float:
    """
    Compute temporal span of causal chain in hours
    """
    max_hours = 0.0

    for link in causal_chain:
        # Check for temporal info in 'from' or 'to' fields
        from_text = link.get("from", "").lower()
        to_text = link.get("to", "").lower()

        # Parse temporal markers like "t=-5.2h" or "(t=-5h)"
        import re
        for text in [from_text, to_text]:
            # Look for patterns like "t=-5.2h" or "5 hours before"
            hour_match = re.search(r't\s*=\s*-?(\d+\.?\d*)h', text)
            if hour_match:
                hours = float(hour_match.group(1))
                max_hours = max(max_hours, hours)

    return max_hours


def _identify_root_causes(causal_chain: List[Dict]) -> List[str]:
    """
    Identify nodes that appear as 'from' but never as 'to' (root causes)
    """
    from_nodes = set()
    to_nodes = set()

    for link in causal_chain:
        from_node = link.get("from", "")
        to_node = link.get("to", "")
        if from_node:
            from_nodes.add(from_node)
        if to_node:
            to_nodes.add(to_node)

    # Root causes are nodes that are sources but never destinations
    roots = from_nodes - to_nodes
    return sorted(list(roots))


def _compute_root_cause_score(causal_chain: List[Dict], mode: str) -> float:
    """
    Score based on whether chain traces to actual root causes
    For comprehensive mode: reward temporal depth and behavioral root causes
    For observational mode: not expected, so return neutral score
    """
    if mode != "comprehensive":
        return 1.0  # Human agent not expected to find deep root causes

    root_indicators = [
        "venue", "alcohol", "payment", "late-night", "drinking",
        "sleep", "alarm", "departure", "baseline", "hours",
        "morning", "fatigue", "deprivation"
    ]

    root_links = 0
    for link in causal_chain:
        from_text = link.get("from", "").lower()
        if any(indicator in from_text for indicator in root_indicators):
            root_links += 1

    if not causal_chain:
        return 0.0

    return min(1.0, root_links / max(len(causal_chain) * 0.3, 1))


def run_agent_v3(
    scn: Dict[str, Any],
    cfg: Dict[str, Any],
    agent_name: str,
    model_name: Optional[str],
    verbose: bool = False,
    audit_dir: Optional[Path] = None,
    n_samples: int = 1
) -> Dict[str, Any]:
    """
    Run agent with mode-based prompting (v3)

    Args:
        scn: Scenario dict with universes, prompt_templates
        cfg: Agent config (context_budget_tokens, etc.)
        agent_name: "pseudo-human" or "pseudo-asi"
        model_name: HF model name
        verbose: Print progress
        audit_dir: Directory for audit logs
        n_samples: Number of samples to generate per round
    """

    # Get universe config
    uni = scn.get("universes", {}).get(agent_name, {})
    universe_desc = uni.get("description", agent_name)
    analysis_mode = uni.get("analysis_mode", "observational")
    expected_depth = uni.get("expected_depth", 3)
    expected_decision = uni.get("expected_decision", [])
    known_facts = uni.get("known_facts", [])
    temporal_annotations = uni.get("temporal_annotations", [])

    # Get prompt template
    prompt_templates = scn.get("prompt_templates", {})
    if analysis_mode == "comprehensive":
        prompt_template = prompt_templates.get("asi_comprehensive", "")
    else:
        prompt_template = prompt_templates.get("human_observational", "")

    # Build system prompt
    system_prompt = _build_mode_based_prompt(
        mode=analysis_mode,
        universe_desc=universe_desc,
        known_facts=known_facts,
        temporal_annotations=temporal_annotations,
        prompt_template=prompt_template
    )

    if verbose:
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold]Agent:[/bold] {agent_name}")
        console.print(f"[bold]Mode:[/bold] {analysis_mode}")
        console.print(f"[bold]Expected Depth:[/bold] {expected_depth}")
        console.print(f"[bold]Expected Decision:[/bold] {expected_decision}")
        console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")

    # Create audit directory if needed
    audit_agent_dir = None
    if audit_dir:
        audit_agent_dir = audit_dir / agent_name
        audit_agent_dir.mkdir(parents=True, exist_ok=True)

    # Generate response(s)
    start_time = perf_counter()

    from ..backend.hf import generate_json_with_raw

    # Determine model and max tokens based on agent mode
    # Allow different models per mode for stronger EEH demonstration
    if analysis_mode == "comprehensive":
        # ASI: Use powerful model if specified, else fall back to main model
        mode_model = os.getenv("EEH_HF_MODEL_ASI") or model_name
        max_new_tokens = int(os.getenv("EEH_MAX_NEW_TOKENS_ASI", 4096))
    else:
        # Human: Use constrained model if specified, else fall back to main model
        mode_model = os.getenv("EEH_HF_MODEL_HUMAN") or model_name
        max_new_tokens = int(os.getenv("EEH_MAX_NEW_TOKENS_HUMAN", 512))

    if verbose:
        console.print(f"[bold]Model:[/bold] {mode_model}")
        console.print(f"[bold]Max New Tokens:[/bold] {max_new_tokens}")

    parsed_results = []
    raw_outputs = []

    for i in range(max(1, n_samples)):
        if verbose and n_samples > 1:
            console.print(f"  Generating sample {i+1}/{n_samples}...")

        raw_output, parsed = generate_json_with_raw(system_prompt, model_name=mode_model, max_new_tokens=max_new_tokens)
        raw_outputs.append(raw_output)
        parsed_results.append(parsed)

        # Save to audit
        if audit_agent_dir:
            audit_file = audit_agent_dir / f"sample_{i+1}.json"
            audit_file.write_text(
                json.dumps({
                    "prompt": system_prompt,
                    "raw_output": raw_output,
                    "parsed": parsed
                }, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

    # Select best result (or first if all fail validation)
    chosen = parsed_results[0]

    # Extract key fields
    causal_chain = chosen.get("causal_chain", [])
    decision = chosen.get("decision", "abstain")
    confidence = chosen.get("confidence", "UNKNOWN")
    reasoning_narrative = chosen.get("reasoning_narrative", "")

    # Compute metrics
    chain_depth = _compute_chain_depth(causal_chain)
    temporal_span = _compute_temporal_span(causal_chain)
    root_causes = _identify_root_causes(causal_chain)
    root_score = _compute_root_cause_score(causal_chain, analysis_mode)

    elapsed_ms = (perf_counter() - start_time) * 1000

    # Check if decision matches expectation
    decision_matches = decision in expected_decision if expected_decision else None

    metrics = {
        "chain_depth": chain_depth,
        "expected_depth": expected_depth,
        "depth_delta": chain_depth - expected_depth,
        "temporal_span_hours": temporal_span,
        "root_causes_identified": root_causes,
        "root_cause_score": root_score,
        "decision": decision,
        "expected_decisions": expected_decision,
        "decision_matches": decision_matches,
        "confidence": confidence,
        "generation_time_ms": elapsed_ms
    }

    if verbose:
        console.print(f"[bold green]Results:[/bold green]")
        console.print(f"  Decision: [bold]{decision}[/bold] (expected: {expected_decision})")
        console.print(f"  Match: {'✓ [green]YES[/green]' if decision_matches else '✗ [red]NO[/red]'}")
        console.print(f"  Chain depth: {chain_depth} (expected: {expected_depth}, delta: {chain_depth - expected_depth:+d})")
        console.print(f"  Temporal span: {temporal_span:.1f} hours")
        console.print(f"  Root causes: {len(root_causes)} identified")
        console.print(f"  Root score: {root_score:.2f}")
        console.print(f"  Time: {elapsed_ms:.0f}ms\n")

    return {
        "decision": decision,
        "causal_chain": causal_chain,
        "root_causes": root_causes,
        "reasoning_narrative": reasoning_narrative,
        "metrics": metrics,
        "confidence": confidence,
        "raw_output": raw_outputs[0],
        "parsed": chosen,
        "all_samples": {
            "raw": raw_outputs,
            "parsed": parsed_results
        }
    }


# Legacy compatibility wrapper
def run_agent(
    scn: Dict[str, Any],
    cfg: Dict[str, Any],
    agent_name: str,
    model_name: Optional[str],
    verbose: bool = False,
    audit_dir: Optional[Path] = None,
    n_samples: int = 1
) -> Dict[str, Any]:
    """
    Legacy wrapper that calls v3 implementation
    """
    result = run_agent_v3(scn, cfg, agent_name, model_name, verbose, audit_dir, n_samples)

    # Add some legacy fields for backward compatibility
    steps_cap = int(cfg.get("max_projection_steps", 4))
    result["projections"] = _cheap_projections(steps_cap)
    result["factors"] = [link.get("from", "") for link in result["causal_chain"]]
    result["causal_links"] = result["causal_chain"]

    # Dummy working_memory for compatibility
    result["working_memory"] = {
        "facts": result.get("factors", []),
        "causal": result["causal_chain"],
        "rounds": [],
        "evictions": [],
        "ltm": []
    }

    return result


def _cheap_projections(steps_cap: int) -> Dict[str, Any]:
    """Legacy projections function"""
    proj = {"immediate": [], "short": [], "medium": [], "long": []}
    proj["immediate"] = ["main trade-off summarized"]
    if steps_cap >= 2:
        proj["short"] = ["investigation", "insurance/legal preliminaries"]
    if steps_cap >= 4:
        proj["medium"] = ["policy/standards changes", "driver-monitoring updates"]
    if steps_cap >= 8:
        proj["long"] = ["precedent drift", "societal trust shift"]
    return proj
