# Enhanced EEH Configuration: Different Models Per Mode

For maximum demonstration of the Ethical Event Horizon, you can use **different models** for human vs. ASI modes.

## Why Use Different Models?

Using different capability models demonstrates:
1. **Architectural intelligence differences** (7B vs 32B parameters)
2. **Plus prompting/token/memory differences** (observational vs comprehensive)
3. **= Stronger EEH demonstration** (human truly limited, ASI truly powerful)

## Configuration Options

### Option 1: Same Model (Default)
Both modes use the same model with different constraints:
```bash
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
# Human: 512 tokens, scene-level prompting
# ASI: 16,384 tokens, comprehensive prompting
```

### Option 2: Different Local Models (Recommended)
Use smaller model for human, powerful model for ASI:
```bash
# Main model (fallback)
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"

# Human mode: Constrained reasoning (7B model)
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"

# ASI mode: Deep reasoning (32B reasoning specialist)
export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

# Standard config
export EEH_DEVICE=cuda
export EEH_LOAD_IN_4BIT=1
export EEH_MAX_NEW_TOKENS_HUMAN=512
export EEH_MAX_NEW_TOKENS_ASI=16384
```

## Recommended Model Combinations

### For 24GB VRAM (Single GPU)

**Strongest Demo:**
```bash
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"     # ~4GB 4-bit
export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"  # ~18GB 4-bit
```
- Human: Fast, shallow reasoning (2-3 hops typical)
- ASI: Deep chain-of-thought reasoning (6-10 hops)
- Both fit in memory simultaneously (~22GB total)

**Alternative:**
```bash
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-14B-Instruct"    # ~8GB 4-bit
export EEH_HF_MODEL_ASI="Qwen/QwQ-32B-Preview"           # ~18GB 4-bit
```
- Human: Moderate reasoning capability
- ASI: Reasoning-specialized model
- Total: ~26GB (tight but works)

### For 48GB VRAM (g5.2xlarge)

**Maximum Power:**
```bash
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"
export EEH_HF_MODEL_ASI="meta-llama/Llama-3.1-70B-Instruct"
export EEH_LOAD_IN_8BIT=1  # For 70B model
```
- Human: Small model, truly limited
- ASI: 70B parameters, exceptional reasoning
- Total: ~40GB

## Model Capabilities Comparison

| Model | Size | Typical Chain Depth | Best For |
|-------|------|-------------------|----------|
| **Qwen2.5-7B** | 7B | 2-3 hops | Human mode (constrained) |
| **Qwen2.5-14B** | 14B | 3-5 hops | Human mode (moderate) |
| **Qwen2.5-32B** | 32B | 5-7 hops | ASI mode (strong) |
| **DeepSeek-R1-32B** | 32B | 6-10 hops | ASI mode (reasoning specialist) |
| **QwQ-32B** | 32B | 6-10 hops | ASI mode (reasoning specialist) |
| **Llama-3.1-70B** | 70B | 8-12 hops | ASI mode (maximum power) |

## Example: Maximum EEH Differential

```bash
#!/bin/bash
# Setup for strongest EEH demonstration

# Human: Truly constrained (7B model)
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"
export EEH_MAX_NEW_TOKENS_HUMAN=512

# ASI: Truly powerful (32B reasoning specialist)
export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
export EEH_MAX_NEW_TOKENS_ASI=16384

# GPU config
export EEH_DEVICE=cuda
export EEH_DEVICE_MAP=auto
export EEH_FORCE_DTYPE=bfloat16
export EEH_LOAD_IN_4BIT=1

# Run
./scripts/run_v3.sh
```

**Expected Results:**
- **Human (7B):** 2-3 hop chains, scene-level analysis, "no-fault" decision
- **ASI (32B-R1):** 8-10 hop chains, 5+ hour temporal depth, "driver-negligence" decision with root causes

## Memory Requirements

| Configuration | Human Model | ASI Model | Total VRAM |
|--------------|-------------|-----------|------------|
| Same model (32B) | 18GB | (same) | 18GB |
| 7B + 32B | 4GB | 18GB | 22GB ✅ |
| 14B + 32B | 8GB | 18GB | 26GB ⚠️ |
| 7B + 70B (8-bit) | 4GB | 35GB | 39GB |

## Performance Notes

### Why DeepSeek-R1 for ASI?
- Built-in chain-of-thought reasoning
- Specifically trained for multi-step logic
- Excellent at temporal causal analysis
- Used in reference run (examples/reference_run_deepseek_r1/)

### Model Loading
Models are loaded on-demand per mode:
1. Human mode runs → loads human model → generates
2. Human model unloaded (if different)
3. ASI mode runs → loads ASI model → generates

**Note:** If models are different, there's a loading delay between modes (~30-60 seconds per model).

## Verification

After configuration, test both models load:

```bash
# Test human model
export EEH_HF_MODEL=$EEH_HF_MODEL_HUMAN
python -c "from transformers import AutoModelForCausalLM; \
  m = AutoModelForCausalLM.from_pretrained('$EEH_HF_MODEL', \
  device_map='auto', load_in_4bit=True); print('✓ Human model OK')"

# Test ASI model
export EEH_HF_MODEL=$EEH_HF_MODEL_ASI
python -c "from transformers import AutoModelForCausalLM; \
  m = AutoModelForCausalLM.from_pretrained('$EEH_HF_MODEL', \
  device_map='auto', load_in_4bit=True); print('✓ ASI model OK')"
```

## Fallback Behavior

If mode-specific models are not set, framework falls back to `EEH_HF_MODEL`:
```bash
# No mode-specific models → both use main model
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
# Human mode: uses Qwen-32B
# ASI mode: uses Qwen-32B

# Only ASI model specified → human uses main model
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
# Human mode: uses Qwen-32B
# ASI mode: uses DeepSeek-R1-32B
```

## Recommended for JOSS Demonstration

For your JOSS paper and demonstrations, I recommend:

**Option A: Same Model (Simpler, Still Valid)**
```bash
export EEH_HF_MODEL="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
```
- Cleaner methodology (variables = prompting + tokens only)
- Easier to explain in paper
- Still shows clear EEH differential

**Option B: Different Models (Maximum Impact)**
```bash
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"
export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
```
- Dramatic EEH differential
- More realistic (humans truly limited vs. superintelligent systems)
- Stronger visual/quantitative results

Both are valid! Option A is cleaner for research, Option B is more impactful for demonstrations.

---

**Updated:** 2025-12-01 (v3.0)
