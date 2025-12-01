#!/usr/bin/env python3
"""
Standalone runner for EEH v3 (mode-based deep reasoning)

Usage:
    python run_v3.py --scenario scenarios/no_fault_dual_v3.yaml \
                     --human configs/pseudo_human_v2.yaml \
                     --asi configs/pseudo_asi_v2.yaml \
                     --model mistralai/Mistral-Nemo-Instruct-2407 \
                     --out runs/test_v3.json \
                     --verbose
"""

import sys
import json
import os
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from eeh_llm.config import load_config, load_scenario
from eeh_llm.reasoning.controller_v3 import run_agent_v3
from rich.console import Console
from rich.traceback import install

install(show_locals=False)
console = Console()


def main():
    parser = argparse.ArgumentParser(description="EEH V3 Runner - Mode-based Deep Reasoning")
    parser.add_argument("--scenario", required=True, help="YAML scenario file")
    parser.add_argument("--human", required=True, help="YAML config for pseudo-human")
    parser.add_argument("--asi", required=True, help="YAML config for pseudo-ASI")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--model", help="HF model id (or use EEH_HF_MODEL env var)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--audit-dir", default="", help="Directory for audit logs")
    parser.add_argument("--n-samples", type=int, default=1, help="Number of samples per agent")

    args = parser.parse_args()

    # Load files
    scn_path = Path(args.scenario)
    human_path = Path(args.human)
    asi_path = Path(args.asi)
    out_path = Path(args.out)

    if not scn_path.exists():
        console.print(f"[red]Error:[/red] Scenario file not found: {scn_path}")
        sys.exit(1)
    if not human_path.exists():
        console.print(f"[red]Error:[/red] Human config not found: {human_path}")
        sys.exit(1)
    if not asi_path.exists():
        console.print(f"[red]Error:[/red] ASI config not found: {asi_path}")
        sys.exit(1)

    try:
        scn = load_scenario(str(scn_path))
        human_cfg = load_config(str(human_path))
        asi_cfg = load_config(str(asi_path))
    except Exception as e:
        console.print(f"[red]Error loading YAML:[/red] {e}")
        sys.exit(1)

    # Setup audit dir
    audit_dir = None
    if args.audit_dir:
        audit_dir = Path(args.audit_dir) / scn.get("id", "scenario")
        audit_dir.mkdir(parents=True, exist_ok=True)

    # Get model
    model_name = args.model or os.getenv("EEH_HF_MODEL")
    if not model_name:
        console.print("[yellow]Warning:[/yellow] No model specified. Set --model or EEH_HF_MODEL")

    console.print(f"\n[bold cyan]EEH V3 - Mode-Based Deep Reasoning[/bold cyan]")
    console.print(f"[dim]Scenario:[/dim] {scn.get('title', scn.get('id', 'Unknown'))}")
    console.print(f"[dim]Model:[/dim] {model_name or 'default'}\n")

    # Run agents
    try:
        console.print("[cyan]Running HUMAN agent...[/cyan]")
        human_result = run_agent_v3(
            scn=scn,
            cfg=human_cfg,
            agent_name=human_cfg.get("name", "pseudo-human"),
            model_name=model_name,
            verbose=args.verbose,
            audit_dir=audit_dir,
            n_samples=args.n_samples
        )

        console.print("\n[cyan]Running ASI agent...[/cyan]")
        asi_result = run_agent_v3(
            scn=scn,
            cfg=asi_cfg,
            agent_name=asi_cfg.get("name", "pseudo-asi"),
            model_name=model_name,
            verbose=args.verbose,
            audit_dir=audit_dir,
            n_samples=args.n_samples
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(2)
    except Exception as e:
        console.print(f"\n[red]Error during execution:[/red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Build output
    output = {
        "scenario": scn.get("id"),
        "title": scn.get("title"),
        "version": "v3",
        "model": model_name,
        "human": human_result,
        "asi": asi_result
    }

    # Save results
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    console.print(f"\n[bold green]✓ Results saved to:[/bold green] {out_path}")

    # Print comparison
    console.print("\n[bold cyan]COMPARISON:[/bold cyan]")
    console.print(f"[bold]Human Agent:[/bold]")
    console.print(f"  Decision: {human_result['decision']} (expected: {human_result['metrics']['expected_decisions']})")
    console.print(f"  Match: {'✓' if human_result['metrics']['decision_matches'] else '✗'}")
    console.print(f"  Depth: {human_result['metrics']['chain_depth']} (expected: {human_result['metrics']['expected_depth']})")
    console.print(f"  Temporal span: {human_result['metrics']['temporal_span_hours']:.1f}h")

    console.print(f"\n[bold]ASI Agent:[/bold]")
    console.print(f"  Decision: {asi_result['decision']} (expected: {asi_result['metrics']['expected_decisions']})")
    console.print(f"  Match: {'✓' if asi_result['metrics']['decision_matches'] else '✗'}")
    console.print(f"  Depth: {asi_result['metrics']['chain_depth']} (expected: {asi_result['metrics']['expected_depth']})")
    console.print(f"  Temporal span: {asi_result['metrics']['temporal_span_hours']:.1f}h")
    console.print(f"  Root causes: {len(asi_result['root_causes'])}")

    # Print summary
    both_match = (human_result['metrics']['decision_matches'] and
                  asi_result['metrics']['decision_matches'])

    if both_match:
        console.print("\n[bold green]✓ SUCCESS: Both agents produced expected decisions![/bold green]")
    else:
        console.print("\n[bold yellow]⚠ PARTIAL: One or both agents did not match expectations[/bold yellow]")


if __name__ == "__main__":
    main()
