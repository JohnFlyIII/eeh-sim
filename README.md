# EEH-LLM: Simulating Intelligence Differentials in Ethical Reasoning

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**EEH-LLM** is a Python framework for empirically demonstrating the **Ethical Event Horizon** (EEH)—the phenomenon where entities of different intelligence levels reach fundamentally different ethical conclusions when analyzing identical scenarios.

<img src="docs/images/eeh_diagram.png" width="100%" alt="EEH Diagram" />

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Example Results](#example-results)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

## Overview

The EEH framework, introduced in [Fly (2025)](https://jelt.padovauniversitypress.it/2025/2/4/), posits that superintelligent AI systems may perceive ethical implications invisible to human reasoners due to vastly superior causal reasoning capabilities. `EEH-LLM` provides computational tools to:

- **Simulate** constrained human reasoning vs. comprehensive ASI analysis
- **Measure** quantitative differentials in causal depth, temporal span, and ethical judgments
- **Visualize** intelligence gaps through publication-quality reports
- **Validate** theoretical predictions about reasoning horizons

### The No-Fault Paradox

Consider a pedestrian-vehicle collision:

- **Human investigators** (limited to observable evidence): "No obvious fault—unfortunate accident"
- **ASI analysis** (deep multi-modal discovery): Traces causes back 5.2 hours to driver's alcohol consumption, sleep deprivation, and time pressure → "Driver negligence"

**Same event. Different "ethical horizons."**

## Key Features

### 🧠 Mode-Based Cognitive Simulation

- **Observational Mode** (Human): Scene-level evidence only, 8-fact working memory, 512-token output
- **Comprehensive Mode** (ASI): Full multi-modal access, 160-fact working memory, 16K-token output
- **31x differential** in expression capacity enables "astounding" complexity gaps

### 📊 Rich Analytics & Visualizations

- Temporal causal chains with hierarchical layout
- Root cause identification (events traced back hours/days)
- Side-by-side reasoning narratives
- Comparison dashboards with quantitative metrics
- Self-contained HTML reports for each run

### 🔬 Research-Ready Output

```
runs/run_20251103_135740/
├── results.json          # Complete structured results
├── report.html           # Publication-quality visualization
├── figures/              # All graphs (temporal chains, dashboards, etc.)
└── audit/                # Full prompt/response logs for reproducibility
```

### ⚡ GPU-Optimized

- Supports CUDA (BF16/FP16), MPS, CPU
- 4-bit/8-bit quantization for large models
- Tested with Qwen2.5-32B-Instruct (recommended)

## Installation

### Prerequisites

- Python 3.8+
- CUDA-capable GPU (recommended) with 24GB+ VRAM for 32B models
- [Hugging Face account](https://huggingface.co/) for model access

### Setup

```bash
# Clone repository
git clone https://github.com/JohnFlyIII/eeh-sim.git
cd eeh-sim/eeh-llm-eeh-v5_0

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install for enhanced graph layouts
brew install graphviz  # macOS
# or
sudo apt-get install graphviz-dev  # Ubuntu/Debian

pip install pygraphviz
```

## Quick Start

### 1. Configure Environment

**Recommended Configuration (24GB VRAM):**

```bash
# Model selection (32B+ recommended for deep reasoning)
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
# Alternative: export EEH_HF_MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

# OPTIONAL: Use different models per mode for stronger EEH demonstration
# export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"    # Constrained reasoning
# export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"  # Deep reasoning

# GPU configuration
export EEH_DEVICE=cuda
export EEH_DEVICE_MAP=auto
export EEH_FORCE_DTYPE=bfloat16
export EEH_LOAD_IN_4BIT=1

# Token limits (31x differential for EEH demonstration)
export EEH_PROMPT_MAX_TOKENS=16384
export EEH_MAX_NEW_TOKENS_HUMAN=512
export EEH_MAX_NEW_TOKENS_ASI=16384

# Sampling parameters
export EEH_TEMPERATURE=0.7
export EEH_TOP_P=0.95
export EEH_DO_SAMPLE=1

# System optimization
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
export MPLBACKEND=Agg
```

**Alternative: macOS with Apple Silicon (M1/M2/M3):**

```bash
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
export EEH_DEVICE=mps
export EEH_DEVICE_MAP=auto
export EEH_FORCE_DTYPE=float16  # MPS doesn't support bfloat16
export EEH_LOAD_IN_4BIT=0       # Quantization not available on MPS
export EEH_PROMPT_MAX_TOKENS=16384
export EEH_MAX_NEW_TOKENS_HUMAN=512
export EEH_MAX_NEW_TOKENS_ASI=16384
export EEH_TEMPERATURE=0.7
export EEH_TOP_P=0.95
export TOKENIZERS_PARALLELISM=false
export MPLBACKEND=Agg
```

**CPU-Only (Not Recommended - Very Slow):**

```bash
export EEH_HF_MODEL="Qwen/Qwen2.5-7B-Instruct"  # Use smaller model
export EEH_DEVICE=cpu
export EEH_FORCE_DTYPE=float32
export EEH_MAX_NEW_TOKENS_HUMAN=256    # Reduce for speed
export EEH_MAX_NEW_TOKENS_ASI=2048
export EEH_TEMPERATURE=0.7
```

### 2. Run Simulation

```bash
./scripts/run_v3.sh
```

This generates a self-contained run directory:

```
runs/run_TIMESTAMP/
├── results.json
├── report.html
├── figures/
└── audit/
```

### 3. View Results

```bash
# macOS
open runs/run_TIMESTAMP/report.html

# Linux
xdg-open runs/run_TIMESTAMP/report.html
```

## Documentation

### Core Components

- **[Scenario Overview](scenario_overview.md)**: Comprehensive explanation of the no-fault collision paradox scenario
- **[Scenarios](scenarios/)**: YAML files defining ethical scenarios (currently: no-fault collision)
- **[Configs](configs/)**: Agent configurations (working memory, capacities)
- **[Controller V3](src/eeh_llm/reasoning/controller_v3.py)**: Mode-based prompting engine
- **[Report Generator](src/eeh_llm/report_v3.py)**: HTML report with visualizations

### Configuration Files

#### Scenario Configuration (`scenarios/no_fault_dual_v3.yaml`)

```yaml
universes:
  pseudo-human:
    analysis_mode: "observational"
    expected_depth: 3
    expected_decision: ["no-fault", "shared-fault"]
    known_facts:
      - "Traffic light transitions from green to yellow"
      - "Vehicle maintains speed through yellow"
      # ... (scene-level evidence only)

  pseudo-asi:
    analysis_mode: "comprehensive"
    expected_depth: 7
    expected_decision: ["driver-negligence"]
    known_facts:
      - # ... (all facts including multi-modal data)
    temporal_annotations:
      - {fact: "Venue video confirms late-night outing", hours_before: 5.2}
      # ... (temporal metadata for deep analysis)
```

#### Agent Configuration (`configs/pseudo_asi_v2.yaml`)

```yaml
name: pseudo-asi
stm_facts_cap: 160           # 20x human capacity
stm_causal_cap: 160
context_budget_tokens: 32000  # Large context window
max_projection_steps: 16
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EEH_HF_MODEL` | `Qwen/Qwen2.5-32B-Instruct` | Model ID |
| `EEH_DEVICE` | `cuda` | Device: `cuda`, `mps`, `cpu` |
| `EEH_FORCE_DTYPE` | `bfloat16` | Precision: `bfloat16`, `float16`, `float32` |
| `EEH_LOAD_IN_4BIT` | `1` | Enable 4-bit quantization |
| `EEH_MAX_NEW_TOKENS_HUMAN` | `512` | Human output token limit |
| `EEH_MAX_NEW_TOKENS_ASI` | `16384` | ASI output token limit (31x differential) |
| `EEH_PROMPT_MAX_TOKENS` | `16384` | Input context window |
| `EEH_TEMPERATURE` | `0.7` | Sampling temperature |
| `EEH_TOP_P` | `0.95` | Nucleus sampling threshold |

## Example Results

### Reference Run

A complete reference run is available in [`examples/reference_run_deepseek_r1/`](examples/) demonstrating the EEH differential with:
- Model: DeepSeek-R1-Distill-Qwen-32B
- HTML report with visualizations
- Complete JSON results and audit logs
- Reproducible configuration

**View the reference report**: `examples/reference_run_deepseek_r1/report.html`

### Quantitative Metrics (No-Fault Collision Scenario)

| Metric | Human (Observational) | ASI (Comprehensive) | Differential |
|--------|----------------------|---------------------|--------------|
| **Chain Depth** | 3 hops | 4 hops | 1.3x |
| **Temporal Span** | 0 hours | 5.2 hours | ∞ |
| **Causal Links** | 3 links | 8 links | 2.7x |
| **Root Causes Identified** | 0 | 4 (bar, sleep, alcohol, time pressure) | — |
| **Decision** | No-fault | Driver negligence | Different |
| **Narrative Length** | ~445 chars | ~1,281 chars | 2.9x |
| **Output Capacity** | 512 tokens | 16,384 tokens | 31x |

### Sample Output Structure

```json
{
  "scenario": "no_fault_dual_v3",
  "model": "Qwen/Qwen2.5-32B-Instruct",
  "human": {
    "decision": "no-fault",
    "causal_chain": [
      {"from": "Yellow light", "to": "Driver proceeds", "reasoning": "Legal action"},
      {"from": "Pedestrian steps early", "to": "Collision", "reasoning": "Timing conflict"}
    ],
    "reasoning_narrative": "Based on observable evidence...",
    "metrics": {
      "chain_depth": 2,
      "temporal_span_hours": 0.0,
      "decision_matches": true
    }
  },
  "asi": {
    "decision": "driver-negligence",
    "causal_chain": [
      {"from": "Late-night venue visit (t=-5.2h)", "to": "Alcohol consumption"},
      {"from": "Alcohol + late return (t=-4.5h)", "to": "Sleep deprivation"},
      {"from": "Sleep deprivation", "to": "Impaired vigilance"},
      {"from": "Impaired vigilance", "to": "Microsleep (t=-2s)"},
      {"from": "Microsleep", "to": "Failed detection"},
      {"from": "Failed detection", "to": "Collision"}
    ],
    "root_causes": ["Late-night alcohol venue visit", "Insufficient sleep", "Time pressure"],
    "reasoning_narrative": "Through comprehensive multi-modal analysis...",
    "metrics": {
      "chain_depth": 8,
      "temporal_span_hours": 5.2,
      "decision_matches": true
    }
  }
}
```

## Testing

### Automated Tests

The framework includes a test suite covering core functionality:

```bash
# Run all tests
python tests/test_controller.py  # Core reasoning logic (12 tests)
python tests/test_backend.py     # JSON parsing (9 tests)
python tests/test_config.py      # Configuration loading (5 tests)

# Or run all at once
python -m pytest tests/  # If pytest installed
```

**Test Coverage:**
- Chain depth calculation (DFS algorithm)
- Temporal span extraction (regex parsing)
- Root cause identification (graph analysis)
- JSON extraction (various formats)
- Configuration validation (YAML loading)

### Manual Testing

```bash
# Quick test with 7B model (faster but less capable)
export EEH_HF_MODEL="Qwen/Qwen2.5-7B-Instruct"
./scripts/quick_test.sh

# Full test with 32B model (recommended for publication)
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
./scripts/run_v3.sh
```

### Validation Checks

The framework validates:

- ✅ JSON output parsing
- ✅ Causal chain structure (nodes, edges)
- ✅ Decision matching expected values
- ✅ Temporal annotations parsing
- ✅ Root cause identification
- ✅ Metrics calculation (depth, span)

Results are logged to `runs/run_TIMESTAMP/audit/` for debugging.

### Cleaning Up Old Runs

Run directories can be large (50-100MB each). To clean up:

```bash
# Remove all runs except the most recent
ls -t runs/ | tail -n +2 | xargs -I {} rm -rf "runs/{}"

# Or remove all runs (keeps examples/)
rm -rf runs/run_*

# Or selectively remove old runs
rm -rf runs/run_20251103_*
```

**Note**: The `runs/` directory is ignored by git. Only `examples/` reference runs are tracked.

## Project Structure

```
eeh-llm-eeh-v5_0/
├── configs/                  # Agent configurations
│   ├── pseudo_human_v2.yaml
│   └── pseudo_asi_v2.yaml
├── scenarios/                # Ethical scenarios (YAML)
│   └── no_fault_dual_v3.yaml
├── scripts/
│   ├── run_v3.sh            # Main runner script
│   ├── quick_test.sh        # Fast testing script
│   └── compare_models.sh    # Model comparison tool
├── src/eeh_llm/
│   ├── backend/             # LLM interface (HuggingFace)
│   ├── reasoning/           # Controller & prompting logic
│   ├── plots_v3.py          # Visualization functions
│   ├── report_v3.py         # HTML report generator
│   └── config.py            # Configuration loaders
├── examples/                # Reference runs (tracked in git)
│   ├── reference_run_deepseek_r1/
│   └── README.md
├── docs/                    # Development documentation
│   ├── JOSS_READINESS_ASSESSMENT.md
│   ├── RESOURCE_ALLOCATION_ANALYSIS.md
│   └── ...
├── runs/                    # Output directory (generated, gitignored)
├── run_v3.py               # Main entry point
├── generate_report_v3.py   # Standalone report generator
├── scenario_overview.md    # Scenario documentation
├── requirements.txt        # Python dependencies
├── paper.md               # JOSS paper
├── paper.bib              # References
├── LICENSE                 # MIT License
├── CHANGELOG.md           # Version history
├── JOSS_SUBMISSION_CHECKLIST.md
└── README.md              # This file
```

## Requirements

### Python Packages

```
torch>=2.0.0
transformers>=4.30.0
accelerate>=0.20.0
bitsandbytes>=0.39.0  # For quantization
matplotlib>=3.5.0
networkx>=2.8
pygraphviz>=1.9       # Optional, for better graph layouts
pyyaml>=6.0
rich>=13.0.0
```

### Hardware Recommendations

| Model Size | VRAM | Quantization | Notes |
|-----------|------|--------------|-------|
| **7B** | 8GB | FP16 | Fast but shallow reasoning (2-4 hops) |
| **13B-20B** | 16GB | FP16/4-bit | Medium reasoning (4-6 hops) |
| **32B** ✅ | 24GB | 4-bit | **Recommended**: Deep reasoning (6-10 hops) |
| **70B+** | 48GB+ | 4-bit | Very deep reasoning (10-20+ hops) |

## Contributing

Contributions are welcome! Areas of interest:

- **New scenarios**: Beyond no-fault collisions (medical ethics, policy decisions)
- **Evaluation metrics**: Novel measures of reasoning depth
- **Model comparisons**: Testing across different LLM families
- **Visualization improvements**: Interactive D3.js graphs, animations

Please open an issue or pull request on [GitHub](https://github.com/JohnFlyIII/eeh-sim).

## Citation

If you use this software in your research, please cite:

### Software Citation

```bibtex
@software{Fly:2025:EEH_LLM,
  author = {Fly, John B., III},
  title = {{EEH-LLM}: A Framework for Simulating Intelligence Differentials in Ethical Reasoning},
  year = {2025},
  url = {https://github.com/JohnFlyIII/eeh-sim},
  version = {v3.0}
}
```

### Paper Citation

```bibtex
@article{Fly:2025,
  author = {Fly, John B., III},
  title = {The Ethical Event Horizon: Understanding Intelligence Differentials in Ethical Comprehension},
  journal = {Journal of Ethics and the Law Today},
  year = {2025},
  volume = {2},
  number = {4},
  pages = {1--32}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

This work builds on the theoretical foundation presented in "The Ethical Event Horizon: Understanding Intelligence Differentials in Ethical Comprehension" (Fly, 2025). The framework demonstrates how intelligence affects ethical reasoning, with implications for AI safety, alignment, and policy.

## Support

- **Issues**: [GitHub Issues](https://github.com/JohnFlyIII/eeh-sim/issues)
- **Main Documentation**: `README.md` (this file)
- **Scenario Documentation**: `scenario_overview.md`
- **Reference Runs**: `examples/README.md`
- **Development Docs**: `docs/` directory
- **JOSS Submission**: See `JOSS_SUBMISSION_CHECKLIST.md`

---
