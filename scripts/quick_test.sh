#!/bin/bash
# Quick test script - runs a fast test with minimal tokens
# Useful for verifying setup before full runs

set -e

echo "=========================================="
echo "EEH Quick Test"
echo "=========================================="
echo ""
echo "This is a quick test with reduced tokens."
echo "For full runs, use run_v2.sh or run_v3.sh"
echo ""

# Quick test settings
export EEH_DEVICE=cuda
export EEH_DEVICE_MAP=auto
export EEH_FORCE_DTYPE=bfloat16
export EEH_LOAD_IN_4BIT=1
export EEH_DO_SAMPLE=1
export EEH_TEMPERATURE=0.7
export EEH_TOP_P=0.9
export EEH_MAX_NEW_TOKENS=256            # Reduced for quick test
export EEH_PROMPT_MAX_TOKENS=2048        # Reduced for quick test
export HF_HUB_ENABLE_HF_TRANSFER=1
export TOKENIZERS_PARALLELISM=false
export MPLBACKEND=Agg

# Use provided model or default
export EEH_HF_MODEL="${1:-Qwen/Qwen2.5-32B-Instruct}"

echo "Model: $EEH_HF_MODEL"
echo "Running quick test..."
echo ""

# Test v3 (newer implementation)
python run_v3.py \
  --scenario scenarios/no_fault_dual_v3.yaml \
  --human configs/pseudo_human_v2.yaml \
  --asi configs/pseudo_asi_v2.yaml \
  --model "$EEH_HF_MODEL" \
  --out runs/quick_test.json \
  --verbose \
  --n-samples 1

echo ""
echo "Quick test complete!"
echo "Results: runs/quick_test.json"
echo ""
echo "For full runs with proper token limits:"
echo "  ./scripts/run_v3.sh"
