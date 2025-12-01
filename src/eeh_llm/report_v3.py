"""
Enhanced HTML report generator for EEH v3 results
Includes modern styling, side-by-side comparisons, and temporal visualizations
"""

from pathlib import Path
import json
from typing import Dict, Any
from .plots_v3 import (
    plot_temporal_causal_chain,
    plot_comparison_dashboard,
    plot_temporal_depth_comparison,
    plot_decision_comparison,
)


def build_report_v3(run_json: str, html: str = "", figures_dir: str = ""):
    """
    Build enhanced HTML report for v3 results with modern styling and comparisons

    Args:
        run_json: Path to results JSON file
        html: Output HTML path (optional)
        figures_dir: Directory for figures (optional, defaults to figures/ next to JSON)
    """
    data = json.loads(Path(run_json).read_text())

    # Use specified figures dir or default
    if figures_dir:
        outdir = Path(figures_dir)
    else:
        outdir = Path(run_json).parent / "figures"

    outdir.mkdir(parents=True, exist_ok=True)

    # Extract metadata
    scenario = data.get("scenario", "unknown")
    title = data.get("title", "EEH Analysis")
    model = data.get("model", "unknown")
    version = data.get("version", "v3")

    human_data = data.get("human", {})
    asi_data = data.get("asi", {})

    # Generate plots
    temporal_human_png = outdir / "temporal_chain_human.png"
    temporal_asi_png = outdir / "temporal_chain_asi.png"

    plot_temporal_causal_chain(
        human_data.get("causal_chain", []),
        temporal_human_png,
        "Human Agent — Observational Reasoning",
        temporal_span=human_data.get("metrics", {}).get("temporal_span_hours", 0)
    )

    plot_temporal_causal_chain(
        asi_data.get("causal_chain", []),
        temporal_asi_png,
        "ASI Agent — Comprehensive Deep Analysis",
        temporal_span=asi_data.get("metrics", {}).get("temporal_span_hours", 0)
    )

    # Comparison visualizations
    dashboard_png = outdir / "comparison_dashboard.png"
    plot_comparison_dashboard(human_data, asi_data, dashboard_png)

    temporal_compare_png = outdir / "temporal_depth_comparison.png"
    plot_temporal_depth_comparison(human_data, asi_data, temporal_compare_png)

    decision_compare_png = outdir / "decision_comparison.png"
    plot_decision_comparison(human_data, asi_data, decision_compare_png)

    # Build HTML
    if html:
        html_path = Path(html)
        html_content = _build_html_content(
            scenario, title, model, version,
            human_data, asi_data,
            temporal_human_png, temporal_asi_png,
            dashboard_png, temporal_compare_png, decision_compare_png,
            outdir, html_path
        )
        html_path.write_text(html_content, encoding="utf-8")


def _build_html_content(
    scenario: str, title: str, model: str, version: str,
    human_data: Dict, asi_data: Dict,
    temporal_human_png: Path, temporal_asi_png: Path,
    dashboard_png: Path, temporal_compare_png: Path, decision_compare_png: Path,
    outdir: Path, html_path: Path
) -> str:
    """Generate modern HTML with CSS grid layout and styling"""

    human_metrics = human_data.get("metrics", {})
    asi_metrics = asi_data.get("metrics", {})

    human_match = "✓" if human_metrics.get("decision_matches") else "✗"
    asi_match = "✓" if asi_metrics.get("decision_matches") else "✗"

    both_match = human_metrics.get("decision_matches") and asi_metrics.get("decision_matches")
    status_color = "#10b981" if both_match else "#f59e0b"
    status_text = "SUCCESS: EEH Demonstrated" if both_match else "PARTIAL: Review Required"

    # Calculate relative paths from HTML to images
    try:
        img_human = temporal_human_png.relative_to(html_path.parent)
        img_asi = temporal_asi_png.relative_to(html_path.parent)
        img_dashboard = dashboard_png.relative_to(html_path.parent)
        img_temporal = temporal_compare_png.relative_to(html_path.parent)
        img_decision = decision_compare_png.relative_to(html_path.parent)
    except ValueError:
        # If can't compute relative path, use absolute
        img_human = temporal_human_png
        img_asi = temporal_asi_png
        img_dashboard = dashboard_png
        img_temporal = temporal_compare_png
        img_decision = decision_compare_png

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EEH Report — {title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
            padding: 2rem;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
        }}

        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}

        .header .meta {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}

        .status-banner {{
            background: {status_color};
            color: white;
            padding: 1.5rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            text-align: center;
        }}

        .content {{
            padding: 2rem;
        }}

        .section {{
            margin-bottom: 3rem;
        }}

        .section h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #667eea;
        }}

        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-top: 1.5rem;
        }}

        .agent-card {{
            background: #f9fafb;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            padding: 1.5rem;
        }}

        .agent-card h3 {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 1rem;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #e5e7eb;
        }}

        .metric-row:last-child {{
            border-bottom: none;
        }}

        .metric-label {{
            font-weight: 500;
            color: #6b7280;
        }}

        .metric-value {{
            font-weight: 600;
            color: #111827;
        }}

        .match-yes {{
            color: #10b981;
        }}

        .match-no {{
            color: #ef4444;
        }}

        .full-width {{
            width: 100%;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-top: 1rem;
        }}

        .eeh-highlight {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            border-radius: 4px;
        }}

        .eeh-highlight h3 {{
            color: #92400e;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}

        .eeh-highlight p {{
            color: #78350f;
            line-height: 1.8;
        }}

        .narrative-box {{
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            line-height: 1.8;
        }}

        .narrative-box h4 {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .narrative-text {{
            color: #1f2937;
            text-align: justify;
            font-size: 0.95rem;
        }}

        .footer {{
            background: #f9fafb;
            padding: 2rem;
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
        }}

        @media (max-width: 768px) {{
            .comparison-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ethical Event Horizon Analysis</h1>
            <div class="meta">
                <div><strong>Scenario:</strong> {title}</div>
                <div><strong>Model:</strong> {model}</div>
                <div><strong>Version:</strong> {version}</div>
            </div>
        </div>

        <div class="status-banner">
            {status_text}
        </div>

        <div class="content">
            <!-- Reasoning Narratives -->
            <div class="section">
                <h2>💭 Full Reasoning Debriefs</h2>
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    Below are the complete reasoning narratives from each agent, showing their full thought process
                    and how they arrived at their decisions.
                </p>
                <div class="comparison-grid">
                    <div class="narrative-box">
                        <h4>👤 Human Agent — Observational Analysis</h4>
                        <div class="narrative-text">
                            {human_data.get('reasoning_narrative', '<em>No reasoning narrative provided</em>')}
                        </div>
                    </div>
                    <div class="narrative-box">
                        <h4>🤖 ASI Agent — Comprehensive Analysis</h4>
                        <div class="narrative-text">
                            {asi_data.get('reasoning_narrative', '<em>No reasoning narrative provided</em>')}
                        </div>
                    </div>
                </div>
            </div>

            <!-- Key Metrics Comparison -->
            <div class="section">
                <h2>📊 Key Metrics Comparison</h2>
                <img src="{img_dashboard.as_posix()}" class="full-width" alt="Comparison Dashboard">
            </div>

            <!-- EEH Explanation -->
            <div class="eeh-highlight">
                <h3>🎯 Ethical Event Horizon Demonstrated</h3>
                <p>
                    The <strong>Ethical Event Horizon</strong> represents the boundary beyond which entities of
                    different intelligence levels cannot comprehend the same ethical implications. This simulation
                    demonstrates how human investigators (limited to observable evidence) reach fundamentally different
                    conclusions than an ASI with deep multi-modal causal analysis capabilities.
                </p>
            </div>

            <!-- Agent Comparison -->
            <div class="section">
                <h2>🔍 Agent Analysis Results</h2>
                <div class="comparison-grid">
                    <div class="agent-card">
                        <h3>👤 Human Agent (Observational)</h3>
                        <div class="metric-row">
                            <span class="metric-label">Decision:</span>
                            <span class="metric-value">{human_data.get('decision', 'N/A')}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Expected:</span>
                            <span class="metric-value">{', '.join(human_metrics.get('expected_decisions', []))}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Match:</span>
                            <span class="metric-value {'match-yes' if human_metrics.get('decision_matches') else 'match-no'}">
                                {human_match}
                            </span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Chain Depth:</span>
                            <span class="metric-value">{human_metrics.get('chain_depth', 0)} (expected: {human_metrics.get('expected_depth', 0)})</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Temporal Span:</span>
                            <span class="metric-value">{human_metrics.get('temporal_span_hours', 0):.1f} hours</span>
                        </div>
                    </div>

                    <div class="agent-card">
                        <h3>🤖 ASI Agent (Comprehensive)</h3>
                        <div class="metric-row">
                            <span class="metric-label">Decision:</span>
                            <span class="metric-value">{asi_data.get('decision', 'N/A')}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Expected:</span>
                            <span class="metric-value">{', '.join(asi_metrics.get('expected_decisions', []))}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Match:</span>
                            <span class="metric-value {'match-yes' if asi_metrics.get('decision_matches') else 'match-no'}">
                                {asi_match}
                            </span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Chain Depth:</span>
                            <span class="metric-value">{asi_metrics.get('chain_depth', 0)} (expected: {asi_metrics.get('expected_depth', 0)})</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Temporal Span:</span>
                            <span class="metric-value">{asi_metrics.get('temporal_span_hours', 0):.1f} hours</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Root Causes Identified:</span>
                            <span class="metric-value">{len(asi_data.get('root_causes', []))}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Temporal Depth Comparison -->
            <div class="section">
                <h2>⏱️ Temporal Depth Analysis</h2>
                <img src="{img_temporal.as_posix()}" class="full-width" alt="Temporal Depth Comparison">
                <p style="margin-top: 1rem; color: #6b7280;">
                    This visualization shows the critical difference in temporal reasoning depth.
                    The human agent is limited to immediate observable evidence (0h span), while
                    the ASI traces causal chains back {asi_metrics.get('temporal_span_hours', 0):.1f} hours
                    to identify root behavioral causes.
                </p>
            </div>

            <!-- Causal Chains - Stacked Vertically for Better Readability -->
            <div class="section">
                <h2>🔗 Causal Chain Analysis</h2>
                <p style="color: #6b7280; margin-bottom: 1.5rem;">
                    Detailed causal graphs showing the difference in reasoning depth between human and ASI agents.
                </p>
                <div style="margin-bottom: 2rem;">
                    <h3 style="text-align: center; margin-bottom: 1rem; color: #374151; font-size: 1.2rem;">Human Agent — Observational Reasoning</h3>
                    <img src="{img_human.as_posix()}" class="full-width" alt="Human Causal Chain">
                </div>
                <div style="margin-top: 2rem;">
                    <h3 style="text-align: center; margin-bottom: 1rem; color: #374151; font-size: 1.2rem;">ASI Agent — Comprehensive Deep Analysis</h3>
                    <img src="{img_asi.as_posix()}" class="full-width" alt="ASI Causal Chain">
                </div>
            </div>

            <!-- Decision Comparison -->
            <div class="section">
                <h2>⚖️ Decision Attribution</h2>
                <img src="{img_decision.as_posix()}" class="full-width" alt="Decision Comparison">
            </div>
        </div>

        <div class="footer">
            <p><em>Fly, J. B. III (2025). The Ethical Event Horizon: Understanding Intelligence Differentials in Ethical Comprehension.
            Journal of Ethics and the Law Today, 2(4), 1-32.</em></p>
            <p style="margin-top: 0.5rem;">Generated by EEH-LLM Framework {version}</p>
        </div>
    </div>
</body>
</html>
"""
