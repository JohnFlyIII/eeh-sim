#!/usr/bin/env python3
"""
Generate enhanced HTML report from v3 results JSON

Usage:
    python generate_report_v3.py runs/no_fault_v3_20251102_235053.json
    python generate_report_v3.py runs/no_fault_v3_20251102_235053.json --output custom_report.html
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from eeh_llm.report_v3 import build_report_v3
from rich.console import Console

console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="Generate enhanced HTML report from EEH v3 results"
    )
    parser.add_argument("json_file", help="Path to v3 results JSON file")
    parser.add_argument(
        "--output", "-o",
        help="Output HTML path (default: same as JSON with .html extension)"
    )
    parser.add_argument(
        "--figures-dir", "-f",
        help="Directory for figures (default: figures/ relative to JSON)"
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        console.print(f"[red]Error:[/red] File not found: {json_path}")
        sys.exit(1)

    # Determine output path
    if args.output:
        html_path = Path(args.output)
    else:
        html_path = json_path.with_suffix(".html")

    # Determine figures directory
    if args.figures_dir:
        figures_dir = Path(args.figures_dir)
    else:
        # Default: figures/ in same directory as JSON
        figures_dir = json_path.parent / "figures"

    figures_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[cyan]Generating enhanced HTML report...[/cyan]")
    console.print(f"  Input:    {json_path}")
    console.print(f"  Output:   {html_path}")
    console.print(f"  Figures:  {figures_dir}\n")

    try:
        build_report_v3(str(json_path), str(html_path), str(figures_dir))
        console.print(f"[bold green]✓ Report generated successfully![/bold green]")
        console.print(f"\n[dim]Open in browser:[/dim]")
        console.print(f"  open {html_path}")

    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
