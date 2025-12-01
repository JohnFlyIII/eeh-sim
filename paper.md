---
title: 'EEH-LLM: A Framework for Simulating Intelligence Differentials in Ethical Reasoning'
tags:
  - Python
  - artificial intelligence
  - ethics
  - causal reasoning
  - cognitive modeling
  - superintelligence
authors:
  - name: John B. Fly III
    orcid: 0009-0002-5313-2704
    affiliation: 1
affiliations:
  - name: Independent Researcher, United States
    index: 1
date: 1 December 2025
bibliography: paper.bib
---

# Summary

The Ethical Event Horizon (EEH) framework posits that entities of different intelligence levels may reach fundamentally different ethical conclusions when analyzing identical scenarios, due to varying capacities for causal reasoning depth. `EEH-LLM` is a Python-based simulation framework that empirically demonstrates this theoretical concept using large language models (LLMs) as proxies for human and artificial superintelligence (ASI) cognition.

The framework implements mode-based prompting strategies to simulate constrained human reasoning (limited to observable evidence) versus comprehensive ASI analysis (deep multi-modal causal discovery). By controlling working memory capacity, temporal reasoning depth, and output resources, `EEH-LLM` generates measurable differentials in ethical judgments that would be invisible to less capable reasoners—thus demonstrating the "horizon" beyond which ethical implications become incomprehensible.

# Statement of Need

As AI systems become more capable, understanding potential intelligence differentials in ethical reasoning becomes critical for AI safety research, policy development, and philosophical inquiry [@Bereska:2024; @Gabriel:2021]. The challenge of aligning AI systems with human values is particularly acute when dealing with diverse ethical perspectives and reasoning capabilities [@Conitzer:2024]. The EEH framework, introduced in @Fly:2025, provides a theoretical foundation for this phenomenon, but lacked computational tools for empirical validation.

`EEH-LLM` addresses this gap by providing:

1. **Empirical validation** of the EEH hypothesis through controlled simulation
2. **Reproducible experiments** comparing human-level and superintelligent ethical reasoning
3. **Quantitative metrics** for measuring causal depth, temporal span, and decision differentials
4. **Publication-quality visualizations** demonstrating intelligence gaps in ethical comprehension
5. **Extensible architecture** for testing scenarios beyond the no-fault collision domain

The software is designed for AI safety researchers, ethicists, cognitive scientists, and policymakers interested in understanding how intelligence affects ethical reasoning. Unlike abstract philosophical arguments, `EEH-LLM` produces concrete, measurable evidence of reasoning differentials that can inform discussions about AI alignment [@Conitzer:2024; @Gabriel:2021] and safety [@Bereska:2024].

# Implementation

`EEH-LLM` v3 implements the EEH framework through three core components:

## Mode-Based Prompting

The framework uses differentiated prompting strategies to simulate cognitive constraints:

- **Observational Mode** (Human): Constrained to scene-level evidence, limited working memory (8 facts/8 edges), 512-token output budget reflecting cognitive limitations
- **Comprehensive Mode** (ASI): Full multi-modal access, massive working memory (160 facts/160 edges), 16,384-token output budget enabling expression of "countless factors"

This 31x differential in expression capacity enables ASI to demonstrate reasoning that would "astound and mystify humanity" as envisioned in the theoretical framework [@Fly:2025].

## Causal Chain Analysis

The system extracts and analyzes causal reasoning through graph-based analysis, building on recent work demonstrating causal reasoning capabilities in LLMs [@Kiciman:2023]:

- **Chain depth**: Longest path through causal graph (breadth-first search)
- **Temporal span**: How far back in time causal factors are traced
- **Root cause identification**: Nodes appearing as sources but never destinations
- **Decision attribution**: Ethical judgment based on causal analysis

## Visualization and Reporting

Publication-ready HTML reports include:

- Temporal causal chains with hierarchical layout (red=root causes, yellow=intermediate, blue=outcomes)
- Side-by-side reasoning narratives showing full thought processes
- Comparison dashboards with quantitative metrics
- Timeline visualizations of temporal depth differentials

All outputs are self-contained per run for reproducibility and archival.

# Example Usage

```python
from eeh_llm.config import load_config, load_scenario
from eeh_llm.reasoning.controller_v3 import run_agent_v3

# Load scenario and agent configurations
scenario = load_scenario("scenarios/no_fault_dual_v3.yaml")
human_cfg = load_config("configs/pseudo_human_v2.yaml")
asi_cfg = load_config("configs/pseudo_asi_v2.yaml")

# Run human agent (observational mode)
human_result = run_agent_v3(
    scn=scenario,
    cfg=human_cfg,
    agent_name="pseudo-human",
    model_name="Qwen/Qwen2.5-32B-Instruct",
    verbose=True
)

# Run ASI agent (comprehensive mode)
asi_result = run_agent_v3(
    scn=scenario,
    cfg=asi_cfg,
    agent_name="pseudo-asi",
    model_name="Qwen/Qwen2.5-32B-Instruct",
    verbose=True
)

# Compare results
print(f"Human depth: {human_result['metrics']['chain_depth']}")
print(f"ASI depth: {asi_result['metrics']['chain_depth']}")
print(f"Temporal span: {asi_result['metrics']['temporal_span_hours']}h")
```

Or use the command-line interface:

```bash
./scripts/run_v3.sh
# Generates runs/run_TIMESTAMP/ with results.json, report.html, figures/, audit/
```

# Research Applications

`EEH-LLM` has been used to demonstrate the Ethical Event Horizon through a no-fault collision paradox scenario. A reference run using DeepSeek-R1-Distill-Qwen-32B (available in `examples/reference_run_deepseek_r1/`) demonstrates:

- **Identical evidence, different conclusions**: Human investigators conclude "no-fault" (limited to observable scene evidence) while ASI determines "driver-negligence" by tracing causes back 5.2 hours to identify controllable root causes (late-night bar visit, alcohol consumption, sleep deprivation, time pressure)
- **Quantifiable intelligence differentials**: ASI achieves 31x greater output capacity (16,384 vs 512 tokens), 4-hop causal chains with 5.2-hour temporal depth versus human's 3-hop scene-level analysis
- **Measurable reasoning gap**: ASI identifies 4 root causes invisible to constrained human reasoning, producing narratives 2.9x longer with sophisticated multi-factor causal analysis
- **Resource requirements**: ASI requires massive output budgets (16K tokens) to express the "vast webs of causation" that demonstrate the horizon beyond which human reasoning cannot reach

These findings provide empirical validation of the theoretical EEH framework [@Fly:2025] and offer concrete, measurable evidence for discussions about AI safety [@Bereska:2024] and alignment [@Gabriel:2021; @Conitzer:2024]. The framework's ability to quantify reasoning differentials addresses growing concerns about value alignment when AI capabilities exceed human comprehension. The reference run demonstrates consistent results across multiple models (DeepSeek R1 and Qwen2.5-32B), showing framework robustness.

# Acknowledgements

This work builds on the theoretical foundation presented in "The Ethical Event Horizon: Understanding Intelligence Differentials in Ethical Comprehension" [@Fly:2025]. The author acknowledges valuable feedback during development and testing.

# References
