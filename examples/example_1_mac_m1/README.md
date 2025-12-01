# Example 1: Mac M1 Test Run

**Date:** December 1, 2025
**Hardware:** MacBook Pro M1 (Apple Silicon)
**Researcher:** John B. Fly III

## Configuration

**System:**
- Device: MPS (Metal Performance Shaders)
- Precision: float16
- Quantization: Disabled (not available on MPS)

**Models:**
- **Human mode:** Qwen/Qwen2.5-7B-Instruct
- **ASI mode:** Qwen/Qwen2.5-14B-Instruct

**Token Limits:**
- **Human:** 512 tokens (constrained)
- **ASI:** 4,096 tokens (8x differential)

**Scenario:** No-fault collision paradox (pedestrian-vehicle collision)

## Results Summary

### Human Agent (Observational Mode)
- **Decision:** `no-fault` ✅
- **Chain depth:** 2 hops
- **Temporal span:** 0.0 hours
- **Root causes identified:** 0
- **Reasoning:** "Based on observable evidence at the scene, this appears to be an unfortunate accident. The traffic light transitioning from green to yellow allowed the vehicle to maintain its speed as it was legally permitted to proceed."

### ASI Agent (Comprehensive Mode)
- **Decision:** `driver-negligence` ✅
- **Chain depth:** 4 hops
- **Temporal span:** 5.2 hours
- **Root causes identified:** 4
- **Reasoning:** "Through comprehensive multi-modal analysis, I can trace the causal chain back 5.2 hours before the collision to identify the root causes. The driver's visit to an alcohol-serving venue late at night (confirmed by payment records and venue video at 2:15 AM) initiated a cascade of impairments."

### EEH Differential

| Metric | Human | ASI | Differential |
|--------|-------|-----|--------------|
| **Decision** | no-fault | driver-negligence | Different conclusions |
| **Chain Depth** | 2 hops | 4 hops | 2x deeper |
| **Temporal Span** | 0 hours | 5.2 hours | ASI traces back |
| **Root Causes** | 0 | 4 | ASI identifies sources |

## Interpretation

This run successfully demonstrates the **Ethical Event Horizon** phenomenon:

1. **Same evidence:** Both agents analyzed the identical collision scenario
2. **Different reasoning horizons:** Human limited to scene-level evidence, ASI accessed temporal and multi-modal data
3. **Different ethical conclusions:** Human concluded "no-fault accident", ASI determined "driver negligence" with identifiable root causes

The ASI agent traced the causal chain back 5.2 hours to identify:
- Late-night alcohol venue visit
- Sleep deprivation (4.2 hours)
- Morning time pressure
- Microsleep event (2 seconds before collision)

These factors were invisible to the human agent's observational analysis, demonstrating a measurable intelligence differential in ethical reasoning.

## Performance Notes

**Generation times on Mac M1:**
- Human mode (7B, 512 tokens): ~12 minutes (first generation)
- ASI mode (14B, 4096 tokens): ~149 minutes (2.5 hours)

**Note:** First-time generation on MPS includes PyTorch compilation overhead. Subsequent runs are significantly faster (~5-10 minutes total).

## Files

- `results.json` - Complete structured output
- `report.html` - Visual report with side-by-side causal graphs
- `figures/` - PNG visualizations (5 files)
- `audit/` - Full prompt/response logs for reproducibility

## Viewing Results

```bash
# View in browser
open report.html

# View JSON summary
cat results.json | jq '{
  human: .human.decision,
  asi: .asi.decision,
  differential: "Different conclusions from same evidence"
}'

# View full reasoning
cat results.json | jq '.human.reasoning_narrative'
cat results.json | jq '.asi.reasoning_narrative'
```

## Reproducibility

To reproduce this example:

```bash
# Configure for Mac M1
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"
export EEH_HF_MODEL_ASI="Qwen/Qwen2.5-14B-Instruct"
export EEH_DEVICE=mps
export EEH_FORCE_DTYPE=float16
export EEH_LOAD_IN_4BIT=0
export EEH_MAX_NEW_TOKENS_HUMAN=512
export EEH_MAX_NEW_TOKENS_ASI=4096

# Run
./scripts/run_v3.sh
```

Or use the automated test script:
```bash
./test_eeh_differential.sh
```

## Citation

If using this example in research:

```bibtex
@misc{EEH_Example1_2025,
  author = {Fly, John B., III},
  title = {EEH-LLM Example Run: Mac M1 Demonstration},
  howpublished = {Example run from EEH-LLM framework},
  month = {December},
  year = {2025},
  note = {Demonstrates intelligence differential in ethical reasoning using Qwen models on Apple Silicon}
}
```

---

**Validated:** December 1, 2025
**Framework Version:** v3.0.0
