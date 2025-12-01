"""
Enhanced plotting functions for EEH v3 with temporal visualizations and better layouts
"""

from pathlib import Path
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import re


def plot_temporal_causal_chain(
    causal_chain: List[Dict],
    outpng: Path,
    title: str,
    temporal_span: float = 0.0
):
    """
    Plot causal chain with hierarchical layout (left-to-right temporal flow)
    Color-coded by node type: root causes, intermediate, outcomes
    """
    if not causal_chain:
        _plot_empty_chain(outpng, title)
        return

    G = nx.DiGraph()

    # Extract temporal information and build graph
    for i, link in enumerate(causal_chain):
        from_node = link.get("from", f"node_{i}")
        to_node = link.get("to", f"node_{i+1}")

        # Add edges
        G.add_edge(from_node, to_node)

    # Use hierarchical layout (left to right for temporal flow)
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR')
    except:
        # Fallback to spring layout if graphviz not available
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Classify nodes (root causes, intermediate, outcomes)
    root_indicators = ['bar', 'alcohol', 'venue', 'drinking', 'late-night', 'outing',
                       'sleep', 'deprivation', 'alarm', 'baseline']

    outcome_indicators = ['collision', 'contact', 'failed detection', 'microsleep episode']

    node_colors = []
    for node in G.nodes():
        node_lower = node.lower()
        if any(ind in node_lower for ind in root_indicators):
            node_colors.append('#ef4444')  # Red for root causes
        elif any(ind in node_lower for ind in outcome_indicators):
            node_colors.append('#3b82f6')  # Blue for outcomes
        else:
            node_colors.append('#fbbf24')  # Yellow for intermediate

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor('#f9fafb')
    fig.patch.set_facecolor('white')

    # Draw edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color='#9ca3af',
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        width=2,
        connectionstyle='arc3,rad=0.1'
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors,
        node_size=3000,
        alpha=0.9,
        edgecolors='white',
        linewidths=2
    )

    # Draw labels with text wrapping
    labels = {}
    for node in G.nodes():
        wrapped = _wrap_text(node, width=20)
        labels[node] = wrapped

    nx.draw_networkx_labels(
        G, pos, labels, ax=ax,
        font_size=8,
        font_weight='500',
        font_family='sans-serif'
    )

    # Add title and temporal span
    ax.set_title(
        f"{title}\nTemporal Span: {temporal_span:.1f} hours",
        fontsize=14,
        fontweight='bold',
        pad=20
    )

    # Add legend
    legend_elements = [
        mpatches.Patch(color='#ef4444', label='Root Causes'),
        mpatches.Patch(color='#fbbf24', label='Intermediate Factors'),
        mpatches.Patch(color='#3b82f6', label='Outcomes')
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)

    ax.axis('off')
    plt.tight_layout()
    fig.savefig(outpng, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_comparison_dashboard(
    human_data: Dict,
    asi_data: Dict,
    outpng: Path
):
    """
    Create comprehensive comparison dashboard showing key metrics
    """
    human_metrics = human_data.get("metrics", {})
    asi_metrics = asi_data.get("metrics", {})

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Human vs ASI Agent Comparison', fontsize=16, fontweight='bold')

    # 1. Chain Depth Comparison
    ax = axes[0, 0]
    human_depth = human_metrics.get("chain_depth", 0)
    asi_depth = asi_metrics.get("chain_depth", 0)
    human_exp = human_metrics.get("expected_depth", 0)
    asi_exp = asi_metrics.get("expected_depth", 0)

    x = [0, 1]
    actual = [human_depth, asi_depth]
    expected = [human_exp, asi_exp]

    ax.bar([i-0.2 for i in x], actual, width=0.4, label='Actual', color='#3b82f6')
    ax.bar([i+0.2 for i in x], expected, width=0.4, label='Expected', color='#e5e7eb', edgecolor='#6b7280')
    ax.set_xticks(x)
    ax.set_xticklabels(['Human', 'ASI'])
    ax.set_ylabel('Chain Depth (hops)')
    ax.set_title('Causal Chain Depth')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # 2. Temporal Span Comparison
    ax = axes[0, 1]
    human_temporal = human_metrics.get("temporal_span_hours", 0)
    asi_temporal = asi_metrics.get("temporal_span_hours", 0)

    bars = ax.barh(['Human', 'ASI'], [human_temporal, asi_temporal], color=['#60a5fa', '#3b82f6'])
    ax.set_xlabel('Hours Before Collision')
    ax.set_title('Temporal Depth')
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}h', va='center', fontweight='bold')

    # 3. Decision Match
    ax = axes[0, 2]
    human_match = 1 if human_metrics.get("decision_matches") else 0
    asi_match = 1 if asi_metrics.get("decision_matches") else 0

    colors = ['#10b981' if m else '#ef4444' for m in [human_match, asi_match]]
    ax.bar(['Human', 'ASI'], [human_match, asi_match], color=colors)
    ax.set_ylim(0, 1.2)
    ax.set_ylabel('Decision Match')
    ax.set_title('Expected Decision Match')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['✗ No', '✓ Yes'])
    ax.grid(axis='y', alpha=0.3)

    # 4. Root Causes Identified
    ax = axes[1, 0]
    human_roots = len(human_data.get("root_causes", []))
    asi_roots = len(asi_data.get("root_causes", []))

    ax.bar(['Human', 'ASI'], [human_roots, asi_roots], color=['#60a5fa', '#3b82f6'])
    ax.set_ylabel('Count')
    ax.set_title('Root Causes Identified')
    ax.grid(axis='y', alpha=0.3)

    # 5. Decision Text
    ax = axes[1, 1]
    ax.axis('off')
    human_decision = human_data.get("decision", "N/A")
    asi_decision = asi_data.get("decision", "N/A")

    decision_text = f"Human Decision:\n{human_decision}\n\nASI Decision:\n{asi_decision}"
    ax.text(0.5, 0.5, decision_text,
            ha='center', va='center',
            fontsize=11,
            bbox=dict(boxstyle='round,pad=1', facecolor='#f3f4f6', edgecolor='#d1d5db'))

    # 6. Overall Status
    ax = axes[1, 2]
    ax.axis('off')

    both_match = human_match and asi_match
    status_color = '#10b981' if both_match else '#f59e0b'
    status_text = "✓ SUCCESS\nEEH Demonstrated" if both_match else "⚠ PARTIAL\nReview Required"

    ax.text(0.5, 0.5, status_text,
            ha='center', va='center',
            fontsize=14,
            fontweight='bold',
            color='white',
            bbox=dict(boxstyle='round,pad=1', facecolor=status_color))

    plt.tight_layout()
    fig.savefig(outpng, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_temporal_depth_comparison(
    human_data: Dict,
    asi_data: Dict,
    outpng: Path
):
    """
    Visualize temporal depth difference with timeline
    """
    human_temporal = human_data.get("metrics", {}).get("temporal_span_hours", 0)
    asi_temporal = asi_data.get("metrics", {}).get("temporal_span_hours", 0)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Timeline visualization
    max_time = max(asi_temporal, 6)  # At least 6 hours

    # Human timeline
    ax.barh(1, human_temporal, left=-human_temporal, height=0.3,
            color='#60a5fa', alpha=0.7, label='Human Temporal Span')
    ax.text(-human_temporal/2 if human_temporal > 0 else -0.1, 1,
            f'{human_temporal:.1f}h', ha='center', va='center', fontweight='bold')

    # ASI timeline
    ax.barh(0, asi_temporal, left=-asi_temporal, height=0.3,
            color='#3b82f6', alpha=0.7, label='ASI Temporal Span')
    ax.text(-asi_temporal/2, 0,
            f'{asi_temporal:.1f}h', ha='center', va='center', fontweight='bold')

    # Collision point
    ax.axvline(0, color='#ef4444', linewidth=3, linestyle='--', label='Collision (t=0)')

    # Format
    ax.set_xlim(-max_time-1, 1)
    ax.set_ylim(-0.5, 1.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['ASI Agent\n(Comprehensive)', 'Human Agent\n(Observational)'])
    ax.set_xlabel('Time Before Collision (hours)', fontsize=12)
    ax.set_title('Temporal Causal Depth Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='lower left')
    ax.grid(axis='x', alpha=0.3)

    # Annotations
    if asi_temporal > 5:
        ax.annotate('Deep root cause analysis\n(bar, drinking, sleep deprivation)',
                   xy=(-asi_temporal, 0), xytext=(-asi_temporal-1, -0.3),
                   arrowprops=dict(arrowstyle='->', color='#6b7280'),
                   fontsize=9, color='#374151', ha='right')

    if human_temporal == 0:
        ax.annotate('Observable evidence only\n(scene-level analysis)',
                   xy=(0, 1), xytext=(0.5, 1.3),
                   arrowprops=dict(arrowstyle='->', color='#6b7280'),
                   fontsize=9, color='#374151', ha='left')

    plt.tight_layout()
    fig.savefig(outpng, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_decision_comparison(
    human_data: Dict,
    asi_data: Dict,
    outpng: Path
):
    """
    Compare decisions side by side with expected values
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    human_decision = human_data.get("decision", "N/A")
    asi_decision = asi_data.get("decision", "N/A")

    human_expected = human_data.get("metrics", {}).get("expected_decisions", [])
    asi_expected = asi_data.get("metrics", {}).get("expected_decisions", [])

    human_match = human_data.get("metrics", {}).get("decision_matches", False)
    asi_match = asi_data.get("metrics", {}).get("decision_matches", False)

    # Create comparison visualization
    agents = ['Human Agent\n(Observational)', 'ASI Agent\n(Comprehensive)']
    y_pos = [1, 0]

    colors = [
        '#10b981' if human_match else '#f59e0b',
        '#10b981' if asi_match else '#f59e0b'
    ]

    ax.barh(y_pos, [1, 1], color=colors, alpha=0.3, height=0.6)

    # Add decision text
    ax.text(0.1, 1, f"Decision: {human_decision}\n\nExpected: {' or '.join(human_expected)}",
            va='center', fontsize=11, fontweight='bold')

    ax.text(0.1, 0, f"Decision: {asi_decision}\n\nExpected: {' or '.join(asi_expected)}",
            va='center', fontsize=11, fontweight='bold')

    # Add match indicators
    match_symbols = ['✓' if human_match else '✗', '✓' if asi_match else '✗']
    for i, symbol in enumerate(match_symbols):
        ax.text(0.9, y_pos[i], symbol, va='center', ha='center',
                fontsize=24, fontweight='bold',
                color='#10b981' if (i == 0 and human_match) or (i == 1 and asi_match) else '#ef4444')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(agents)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title('Decision Attribution Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    fig.savefig(outpng, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def _wrap_text(text: str, width: int = 20) -> str:
    """Wrap text to specified width"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return '\n'.join(lines)


def _plot_empty_chain(outpng: Path, title: str):
    """Plot placeholder for empty causal chain"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.5, 'No causal chain data available',
            ha='center', va='center', fontsize=14, color='#6b7280')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(outpng, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
