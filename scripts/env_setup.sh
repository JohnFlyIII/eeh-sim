#!/bin/bash
# Common environment setup for EEH runs
# Source this file to set up environment variables
# Usage: source scripts/env_setup.sh

# ============================================================================
# MODEL SELECTION
# ============================================================================
# Uncomment the model you want to use:

# Recommended for V3 (deep reasoning) - 32B parameters
export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"

# Alternative: Larger model (70B) - requires more VRAM
# export EEH_HF_MODEL="meta-llama/Llama-3.1-70B-Instruct"

# Smaller models (NOT recommended for V3)
# export EEH_HF_MODEL="Qwen/Qwen2.5-7B-Instruct"
# export EEH_HF_MODEL="mistralai/Mistral-Nemo-Instruct-2407"

# ============================================================================
# DEVICE & QUANTIZATION
# ============================================================================
export EEH_DEVICE=cuda
export EEH_DEVICE_MAP=auto
export EEH_FORCE_DTYPE=bfloat16           # Use bfloat16 for better reasoning

# Quantization (use 4-bit for 32B+ models on 24GB VRAM)
export EEH_LOAD_IN_4BIT=1
# export EEH_LOAD_IN_8BIT=0               # Use if you have 48GB+ VRAM

# ============================================================================
# SAMPLING PARAMETERS
# ============================================================================
export EEH_DO_SAMPLE=1
export EEH_TEMPERATURE=0.7                # 0.6-0.8 good range
export EEH_TOP_P=0.95
export EEH_MAX_NEW_TOKENS=1024            # Increase for longer chains
export EEH_PROMPT_MAX_TOKENS=4096

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================
export HF_HUB_ENABLE_HF_TRANSFER=1
export TOKENIZERS_PARALLELISM=false
export MPLBACKEND=Agg
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# ============================================================================
# OPTIONAL: HuggingFace Token (for gated models)
# ============================================================================
# Uncomment and set if using gated models like Llama
# export HF_TOKEN="your_token_here"

echo "Environment configured:"
echo "  Model: $EEH_HF_MODEL"
echo "  Device: $EEH_DEVICE"
echo "  Dtype: $EEH_FORCE_DTYPE"
echo "  4-bit: $EEH_LOAD_IN_4BIT"
echo "  Temp: $EEH_TEMPERATURE"
echo "  Max tokens: $EEH_MAX_NEW_TOKENS"
