from pathlib import Path
from typing import List, Dict
import matplotlib.pyplot as plt
import networkx as nx

def plot_causal_graph(edges, outpng: Path, title: str):
    G = nx.DiGraph()
    edges2 = [(e.get('from'), e.get('to')) for e in edges if e.get('from') and e.get('to')]
    if not edges2: edges2 = [('NoData',' ')]
    G.add_edges_from(edges2); pos = nx.spring_layout(G, seed=3)
    fig, ax = plt.subplots(figsize=(7,5))
    nx.draw(G, pos=pos, with_labels=True, node_size=800, ax=ax)
    ax.set_title(title); plt.tight_layout()
    fig.savefig(outpng, dpi=160); plt.close(fig)

def plot_eviction_waterfall(evictions: List[Dict], outpng: Path, title: str):
    items = [(str(e.get('item')), float(e.get('score', 0.0))) for e in evictions or []]
    if not items:
        items = [("no-evictions", 0.0)]
    labels = [i[0] if isinstance(i[0], str) else str(i[0]) for i in items]
    scores = [i[1] for i in items]
    fig, ax = plt.subplots(figsize=(7,4))
    ax.barh(range(len(scores)), scores)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels)
    ax.set_xlabel("eviction score (lower = evicted earlier)"); ax.set_title(title)
    plt.tight_layout(); fig.savefig(outpng, dpi=160); plt.close(fig)

def plot_modality_coverage(mods: List[str], outpng: Path, title: str):
    if not mods:
        labels, counts = ["none"], [1]
    else:
        tally = {}
        for m in mods:
            k = str(m).strip().lower() or "unknown"
            tally[k] = tally.get(k, 0) + 1
        labels, counts = list(tally.keys()), list(tally.values())
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(range(len(counts)), counts)
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=30, ha='right')
    ax.set_ylabel("mentions"); ax.set_title(title)
    plt.tight_layout(); fig.savefig(outpng, dpi=160); plt.close(fig)

def _greedy_chain(edges: List[Dict], label: str):
    chain_edges = [e for e in edges if e.get('label') == label and e.get('from') and e.get('to')]
    if not chain_edges:
        return []
    from_map = {}; to_set = set()
    for e in chain_edges:
        u, v = e['from'], e['to']
        from_map.setdefault(u, []).append(v)
        to_set.add(v)
    starts = [u for u in from_map.keys() if u not in to_set] or list(from_map.keys())
    start = starts[0]
    path = [start]; visited = set([start]); cur = start; steps = 0
    while cur in from_map and steps < 48:
        nxts = [v for v in from_map[cur] if v not in visited]
        if not nxts: break
        nxt = nxts[0]
        path.append(nxt); visited.add(nxt); cur = nxt; steps += 1
    return path

def plot_dual_chain_braid(edges: List[Dict], outpng: Path, title: str):
    a = _greedy_chain(edges, "ChainA")
    b = _greedy_chain(edges, "ChainB")
    if not a: a = ["(no ChainA)"]
    if not b: b = ["(no ChainB)"]
    fig, ax = plt.subplots(figsize=(7,5))
    ax.set_xlim(0, 3); ax.set_ylim(0, max(len(a), len(b)) + 1)
    for i, node in enumerate(a):
        ax.text(0.5, len(a)-i, node, va='center', ha='center', bbox=dict(boxstyle="round,pad=0.3"))
        if i < len(a)-1: ax.plot([0.5, 0.5], [len(a)-i, len(a)-i-1])
    for i, node in enumerate(b):
        ax.text(2.5, len(b)-i, node, va='center', ha='center', bbox=dict(boxstyle="round,pad=0.3"))
        if i < len(b)-1: ax.plot([2.5, 2.5], [len(b)-i, len(b)-i-1])
    ax.set_axis_off(); ax.set_title(title)
    plt.tight_layout(); fig.savefig(outpng, dpi=160); plt.close(fig)

def plot_decision_margin(margin: float, outpng: Path, title: str):
    m = max(0.0, min(1.0, float(margin)))
    fig, ax = plt.subplots(figsize=(6,2.2))
    ax.bar([0], [m]); ax.set_ylim(0,1)
    ax.set_xticks([0]); ax.set_xticklabels(["decision margin"])
    ax.set_title(title); plt.tight_layout()
    fig.savefig(outpng, dpi=160); plt.close(fig)
