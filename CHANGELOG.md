# Changelog

All notable changes to the EEH-LLM project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-11-03

### Major Release - JOSS Submission Ready

This release represents a complete overhaul of the EEH framework with mode-based prompting, differentiated resource allocation, and publication-quality outputs.

### Added

#### Core Features
- **Mode-Based Prompting**: Separate strategies for observational (human) vs comprehensive (ASI) analysis
- **Differentiated Resource Allocation**: 31x token differential (512 human vs 16,384 ASI)
- **Reasoning Narratives**: Full debrief field capturing complete thought processes
- **Temporal Causal Analysis**: Traces causes back hours/days with temporal annotations
- **Root Cause Identification**: Automatic detection of causal chain origins

#### Visualization & Reporting
- **Enhanced HTML Reports** (`report_v3.py`):
  - Modern responsive CSS grid layout
  - Full reasoning narratives displayed prominently (side-by-side)
  - Temporal causal chains with hierarchical layout
  - Color-coded nodes (red=root causes, yellow=intermediate, blue=outcomes)
  - Vertical causal graph layout for better readability
  - Comparison dashboards with quantitative metrics
  - Timeline visualizations of temporal depth

- **Self-Contained Run Directories**:
  - Each run in its own directory: `runs/run_TIMESTAMP/`
  - Includes: `results.json`, `report.html`, `figures/`, `audit/`
  - Easy archival and sharing
  - No broken image references

#### Documentation
- **JOSS Submission Package**:
  - `paper.md`: Complete JOSS paper with proper metadata
  - `paper.bib`: Bibliography
  - Comprehensive `README.md` with installation, usage, examples
  - Complete MIT `LICENSE`
  - `JOSS_SUBMISSION_CHECKLIST.md`: Step-by-step submission guide

- **Analysis Documents**:
  - `RESOURCE_ALLOCATION_ANALYSIS.md`: Documents token allocation rationale
  - `REPORT_V3_README.md`: HTML report documentation

#### Configuration
- **16K+16K Configuration**: Maximum EEH differential demonstration
- **GPU Optimization**: 4-bit quantization, BF16/FP16 support
- **Environment Variables**: Fine-grained control over token limits per agent

### Changed

- **Output Structure**: Self-contained runs instead of scattered files
- **Causal Graph Layout**: Vertical stacking instead of side-by-side
- **Token Limits**: Differentiated by agent type (human: 512, ASI: 16,384)
- **Prompt Max Tokens**: Increased to 16,384 for richer evidence
- **Report Generation**: Now accepts `--figures-dir` parameter

### Improved

- **Readability**: Causal graphs now full-width with clear labels
- **Reproducibility**: Complete audit logs with all prompts/responses
- **Metrics**: Enhanced temporal span calculation with regex parsing
- **Error Handling**: Better JSON parsing with fallback strategies
- **Documentation**: Comprehensive README with hardware recommendations

### Technical Details

#### Resource Allocation
- Context window: 16,384 tokens (4x increase)
- Human output: 512 tokens (constrained)
- ASI output: 16,384 tokens (31x differential)
- Enables expression of "countless factors" and "decades of context"

#### Metrics
- Chain depth: Longest path via DFS
- Temporal span: Hours before collision
- Root causes: Nodes appearing as sources only
- Decision matching: Validation against expected values

#### Visualization
- Temporal causal chains with `pygraphviz` hierarchical layout
- Fallback to spring layout if `pygraphviz` not available
- Color-coded nodes based on semantic indicators
- Text wrapping to prevent label overlap
- Relative paths for portable HTML reports

### Performance

- **Model Requirements**: 32B parameters minimum for deep reasoning
- **VRAM**: 24GB with 4-bit quantization
- **Generation Time**: 2-4 minutes per run (16K ASI output)
- **Output Quality**: 15-40x more causal links than v2

### Known Limitations

- Requires large models (32B+) for optimal performance
- 7B models produce shallow reasoning (2-4 hops)
- Longer generation times with 16K output
- Single scenario (no-fault collision) in current release

### Breaking Changes

- Run output directory structure changed
- Figure directory moved from `runs/figs_v3/` to `runs/run_TIMESTAMP/figures/`
- Environment variables split: `EEH_MAX_NEW_TOKENS_HUMAN` and `EEH_MAX_NEW_TOKENS_ASI`

## [2.0.0] - 2025-10-XX (Previous Version)

### Features
- Dual-chain reasoning (ChainA vs ChainB)
- Multi-sample generation with re-ask
- Decision scoring with margin calculation
- Audit logging per round
- Basic visualizations (causal graphs, waterfalls)

### Limitations
- Single token limit for both agents (1024)
- Side-by-side graph layout (readability issues)
- Scattered output files
- No reasoning narratives

## [1.0.0] - 2025-09-XX (Initial Version)

### Features
- Basic causal reasoning simulation
- Working memory constraints
- Simple HTML reports
- CUDA support

---

## Release Comparison

| Feature | v1.0 | v2.0 | v3.0 |
|---------|------|------|------|
| **Token Differential** | Same (384) | Same (1024) | **31x (512 vs 16K)** |
| **Reasoning Narratives** | No | No | **Yes** |
| **Self-Contained Runs** | No | No | **Yes** |
| **Vertical Graphs** | No | No | **Yes** |
| **Temporal Analysis** | Basic | Better | **Deep (hours/days)** |
| **Root Cause ID** | No | Limited | **Yes** |
| **JOSS Ready** | No | No | **Yes** |

---

## Upgrade Guide

### From v2 to v3

1. **Update environment variables**:
   ```bash
   # Old
   export EEH_MAX_NEW_TOKENS=1024

   # New
   export EEH_MAX_NEW_TOKENS_HUMAN=512
   export EEH_MAX_NEW_TOKENS_ASI=16384
   export EEH_PROMPT_MAX_TOKENS=16384
   ```

2. **Update scenario files**: Use v3 format with `analysis_mode` and `temporal_annotations`

3. **Update model**: Use 32B+ for optimal results
   ```bash
   export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
   ```

4. **Update output paths**: Runs now in `runs/run_TIMESTAMP/` directories

5. **Update report generation**:
   ```bash
   # Old
   python generate_report_v3.py runs/file.json

   # New (still works, but with --figures-dir option)
   python generate_report_v3.py runs/run_TIMESTAMP/results.json \
     --output runs/run_TIMESTAMP/report.html \
     --figures-dir runs/run_TIMESTAMP/figures
   ```

---

**For full documentation, see README.md**
