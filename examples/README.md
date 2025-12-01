# EEH-LLM Example Runs

This directory contains reference runs demonstrating the EEH framework's capabilities across different hardware and model configurations.

## Example 1: Mac M1 Test Run

**Directory:** `example_1_mac_m1/`
**Date:** December 1, 2025
**Hardware:** MacBook Pro M1 (Apple Silicon)
**Researcher:** John B. Fly III

A complete test run on Apple Silicon demonstrating the EEH differential:
- **Human model:** Qwen/Qwen2.5-7B-Instruct (MPS, float16)
- **ASI model:** Qwen/Qwen2.5-14B-Instruct (MPS, float16)
- **Device:** MPS (Metal Performance Shaders)
- **HTML report** with side-by-side visualizations
- **Complete audit logs** for reproducibility

### Key Results

| Agent | Decision | Chain Depth | Temporal Span | Root Causes |
|-------|----------|-------------|---------------|-------------|
| **Human** | no-fault | 2 hops | 0 hours | 0 |
| **ASI** | driver-negligence | 4 hops | 5.2 hours | 4 |

**View:** Open `example_1_mac_m1/report.html` in a browser.

**Significance:** Demonstrates EEH framework works on consumer hardware (Mac M1) without CUDA, validating accessibility for researchers without specialized GPU infrastructure.

---

## Reference Run: DeepSeek R1 (Original)

**Directory:** `reference_run_deepseek_r1/`

Original reference run using DeepSeek-R1-Distill-Qwen-32B (reasoning specialist):
- **Model:** DeepSeek-R1-Distill-Qwen-32B (both modes, different constraints)
- **Device:** CUDA GPU with 4-bit quantization
- **HTML report** with visualizations
- **Complete JSON results** and audit logs

### Key Results

| Agent | Decision | Chain Depth | Temporal Span | Root Causes |
|-------|----------|-------------|---------------|-------------|
| **Human** | no-fault | 3 hops | 0 hours | 0 |
| **ASI** | driver-negligence | 4 hops | 5.2 hours | 4 |

**View:** Open `reference_run_deepseek_r1/report.html` in a browser.

**Significance:** Demonstrates EEH with reasoning-specialized model on CUDA infrastructure.

---

## Comparison

| Example | Hardware | Human Model | ASI Model | Runtime | EEH Demonstrated |
|---------|----------|-------------|-----------|---------|------------------|
| **Example 1** | Mac M1 MPS | Qwen-7B | Qwen-14B | ~2.5 hrs | ✅ Yes |
| **Reference** | CUDA GPU | DeepSeek-R1-32B | DeepSeek-R1-32B | ~20 min | ✅ Yes |

Both examples successfully demonstrate the Ethical Event Horizon phenomenon, showing the framework's robustness across different hardware platforms and model configurations.

---

## Usage

These examples serve as:
- **Validation** that the framework works correctly
- **Benchmarks** for comparing your own runs
- **Templates** for understanding expected output format
- **Documentation** of the EEH phenomenon in action
- **Hardware guidance** for different deployment scenarios

## Creating Your Own Examples

After running the framework:

```bash
# Run framework
./scripts/run_v3.sh

# Results appear in runs/run_TIMESTAMP/
# Copy to examples if desired:
cp -r runs/run_TIMESTAMP/ examples/my_example/
```

## For JOSS Reviewers

Both examples can be used to verify the framework:
- **Example 1:** Quick verification on Mac (no CUDA required)
- **Reference run:** Full power demonstration on CUDA GPU

Both show the same EEH phenomenon with different hardware/models.
