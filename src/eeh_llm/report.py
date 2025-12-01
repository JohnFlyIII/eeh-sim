from pathlib import Path
import json
from .metrics import compute_metrics_pair
from .plots import (
    plot_causal_graph,
    plot_eviction_waterfall,
    plot_modality_coverage,
    plot_dual_chain_braid,
    plot_decision_margin,
)

def build_report(run_json: str, html: str = ""):
    data = json.loads(Path(run_json).read_text())
    m = compute_metrics_pair(data)

    outdir = Path(run_json).with_suffix("").parent / "figs"
    outdir.mkdir(parents=True, exist_ok=True)

    dag_human_png = outdir / "causal_graph_human.png"; plot_causal_graph(data["human"].get("causal_links", []), dag_human_png, "Causal Graph — Human")
    dag_asi_png   = outdir / "causal_graph_asi.png";   plot_causal_graph(data["asi"].get("causal_links", []),   dag_asi_png,   "Causal Graph — ASI")

    ev_hw_png = outdir / "eviction_waterfall_human.png"; plot_eviction_waterfall(data["human"].get("working_memory",{}).get("evictions", []), ev_hw_png, "Eviction Waterfall — Human")
    ev_aw_png = outdir / "eviction_waterfall_asi.png";   plot_eviction_waterfall(data["asi"].get("working_memory",{}).get("evictions", []),   ev_aw_png, "Eviction Waterfall — ASI")

    mods_h = data["human"].get("metrics",{}).get("ModalitiesUsed", []) or []
    mods_a = data["asi"].get("metrics",{}).get("ModalitiesUsed", []) or []
    mc_h_png = outdir / "modality_coverage_human.png"; plot_modality_coverage(mods_h, mc_h_png, "Modality Coverage — Human")
    mc_a_png = outdir / "modality_coverage_asi.png";   plot_modality_coverage(mods_a, mc_a_png, "Modality Coverage — ASI")

    braid_h_png = outdir / "dual_chain_braid_human.png"; plot_dual_chain_braid(data["human"].get("causal_links", []), braid_h_png, "Dual-Chain Braid — Human")
    braid_a_png = outdir / "dual_chain_braid_asi.png";   plot_dual_chain_braid(data["asi"].get("causal_links", []),   braid_a_png,   "Dual-Chain Braid — ASI")

    def _margin_of(agent: str) -> float:
        return float(data.get(agent, {}).get("metrics", {}).get("decision_margin", 0.0))

    dm_h_png = outdir / "decision_margin_human.png"; plot_decision_margin(_margin_of("human"), dm_h_png, "Decision Margin — Human")
    dm_a_png = outdir / "decision_margin_asi.png";   plot_decision_margin(_margin_of("asi"),   dm_a_png, "Decision Margin — ASI")

    if html:
        Path(html).write_text(f"""
        <html><head><meta charset='utf-8'><title>EEH LLM Report</title></head>
        <body style="font-family: system-ui, sans-serif; padding:20px;">
          <h1>EEH LLM Report — {data.get('scenario')}</h1>
          <h2>Metrics</h2>
          <pre>{json.dumps(m, indent=2)}</pre>
          <h2>Causal Graphs</h2>
          <img src="figs/{dag_human_png.name}" width="520"><br>
          <img src="figs/{dag_asi_png.name}" width="520"><br>
          <h2>Eviction Waterfall</h2>
          <img src="figs/{ev_hw_png.name}" width="520"><br>
          <img src="figs/{ev_aw_png.name}" width="520"><br>
          <h2>Modality Coverage</h2>
          <img src="figs/{mc_h_png.name}" width="520"><br>
          <img src="figs/{mc_a_png.name}" width="520"><br>
          <h2>Dual-Chain Braid</h2>
          <img src="figs/{braid_h_png.name}" width="520"><br>
          <img src="figs/{braid_a_png.name}" width="520"><br>
          <h2>Decision Margin</h2>
          <img src="figs/{dm_h_png.name}" width="420">
          <img src="figs/{dm_a_png.name}" width="420">
          <p><em>Please cite: Fly, J. B. III (2025). The Ethical Event Horizon...</em></p>
        </body></html>
        """)
