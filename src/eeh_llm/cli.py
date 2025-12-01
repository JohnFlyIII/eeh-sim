import json, os
from pathlib import Path
import typer
from rich import print
from rich.traceback import install as rich_traceback
from .config import load_config, load_scenario
from .reasoning.controller import run_agent
from .report import build_report

rich_traceback(show_locals=False)
app = typer.Typer(help="EEH LLM Demo (GPU-ready) — strict dual chains, cf, scoring, visuals")

def _fail(msg: str, code: int = 1):
    print(f"[red]Error:[/red] {msg}")
    raise typer.Exit(code)

@app.command()
def run(
    scenario: str = typer.Option(..., "--scenario", "-s", help="YAML scenario file"),
    human: str = typer.Option(..., "--human", help="YAML config for pseudo-human"),
    asi: str = typer.Option(..., "--asi", help="YAML config for pseudo-ASI"),
    out: str = typer.Option(..., "--out", help="Output JSON path"),
    model: str = typer.Option(None, "--model", help="HF model id (optional; otherwise EEH_HF_MODEL)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose run logging"),
    audit_dir: str = typer.Option("", "--audit-dir", help="Directory to store per-round prompts and raw outputs"),
    n_samples: int = typer.Option(3, "--n-samples", help="Generation samples to try per round; pick first that meets quotas"),
):
    scn_p = Path(scenario); human_p = Path(human); asi_p = Path(asi); out_p = Path(out)
    for p, label in [(scn_p,"scenario"),(human_p,"human config"),(asi_p,"asi config")]:
        if not p.exists(): _fail(f"{label} file not found: {p}")
    try:
        scn = load_scenario(str(scn_p)); human_cfg = load_config(str(human_p)); asi_cfg = load_config(str(asi_p))
    except Exception as e:
        _fail(f"Failed to load YAML: {e}")

    adir = Path(audit_dir) if audit_dir else None
    if adir:
        (adir / scn.get("id","scenario")).mkdir(parents=True, exist_ok=True)
        adir = adir / scn.get("id","scenario")

    model_eff = model or os.getenv("EEH_HF_MODEL") or None

    try:
        print("[cyan]Running agents (HF)…[/cyan]")
        human_out = run_agent(scn, human_cfg, agent_name=human_cfg.get("name","pseudo-human"),
                              model_name=model_eff, verbose=verbose,
                              audit_dir=(adir / "pseudo-human") if adir else None,
                              n_samples=n_samples)
        asi_out   = run_agent(scn, asi_cfg,   agent_name=asi_cfg.get("name","pseudo-asi"),
                              model_name=model_eff, verbose=verbose,
                              audit_dir=(adir / "pseudo-asi") if adir else None,
                              n_samples=n_samples)
    except KeyboardInterrupt:
        partial = {"scenario": scn.get("id")}
        if 'human_out' in locals(): partial["human"] = human_out
        if 'asi_out'   in locals(): partial["asi"]   = asi_out
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(partial, indent=2))
        _fail("Interrupted by user. Partial results saved.", code=2)
    except Exception as e:
        _fail(f"Run failed: {e}")

    def _extract_margin(agent_out):
        try:
            rounds = agent_out.get("working_memory", {}).get("rounds", [])
            if rounds:
                last = rounds[-1]
                mets = last.get("metrics", {}) if isinstance(last, dict) else {}
                if "decision_margin" in mets:
                    return mets["decision_margin"]
        except Exception:
            pass
        return None

    if _extract_margin(human_out) is not None:
        human_out.setdefault("metrics", {})["decision_margin"] = _extract_margin(human_out)  # type: ignore
    if _extract_margin(asi_out) is not None:
        asi_out.setdefault("metrics", {})["decision_margin"] = _extract_margin(asi_out)  # type: ignore

    summary = {"scenario": scn.get("id"), "human": human_out, "asi": asi_out}
    try:
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(summary, indent=2))
    except Exception as e:
        _fail(f"Failed to write output JSON: {e}")
    print(f"[green]Saved[/green] {out_p}")

@app.command()
def report(run_json: str = typer.Argument(..., help="Run JSON path"), html: str = typer.Option("", "--html", help="Optional HTML output file")):
    run_p = Path(run_json)
    if not run_p.exists(): _fail(f"Run JSON not found: {run_p}")
    try:
        build_report(str(run_p), html=html)
    except Exception as e:
        _fail(f"Report failed: {e}")
    print(f"[green]Report OK[/green]")
