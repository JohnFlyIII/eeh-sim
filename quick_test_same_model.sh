#!/bin/bash
# FASTEST test - uses same 7B model for both modes
# Shows differential from prompting/tokens alone
# Takes ~2-3 minutes total

set -e

echo "Quick EEH Test (Same Model, Different Constraints)"
echo "==================================================="
echo ""

# Use same small model for both (fastest)
export EEH_HF_MODEL="Qwen/Qwen2.5-7B-Instruct"

# Auto-detect device and configure appropriately
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use MPS (Apple Silicon) or CPU
    if python3 -c "import torch; exit(0 if torch.backends.mps.is_available() else 1)" 2>/dev/null; then
        export EEH_DEVICE=mps
        export EEH_FORCE_DTYPE=float16  # MPS doesn't support bfloat16
        export EEH_LOAD_IN_4BIT=0       # Quantization not available on MPS
        echo "Using MPS (Apple Silicon GPU)"
    else
        export EEH_DEVICE=cpu
        export EEH_FORCE_DTYPE=float32
        export EEH_LOAD_IN_4BIT=0
        echo "Using CPU (no GPU detected - will be slow)"
    fi
else
    # Linux - use CUDA if available
    export EEH_DEVICE=cuda
    export EEH_FORCE_DTYPE=bfloat16
    export EEH_LOAD_IN_4BIT=1
    echo "Using CUDA GPU"
fi

export EEH_DEVICE_MAP=auto

# Token differential
export EEH_MAX_NEW_TOKENS_HUMAN=256    # Very constrained
export EEH_MAX_NEW_TOKENS_ASI=2048     # 8x more

# Quick sampling
export EEH_TEMPERATURE=0.7
export EEH_TOP_P=0.95
export EEH_DO_SAMPLE=1

export TOKENIZERS_PARALLELISM=false
export MPLBACKEND=Agg

# Output
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_DIR="runs/quick_test_${TIMESTAMP}"
mkdir -p "$TEST_DIR"

echo "Model: $EEH_HF_MODEL (both modes)"
echo "Human tokens: $EEH_MAX_NEW_TOKENS_HUMAN"
echo "ASI tokens:   $EEH_MAX_NEW_TOKENS_ASI"
echo ""
echo "Running..."
echo ""

# Run
python run_v3.py \
  --scenario scenarios/no_fault_dual_v3.yaml \
  --human configs/pseudo_human_v2.yaml \
  --asi configs/pseudo_asi_v2.yaml \
  --out "$TEST_DIR/results.json" \
  --audit-dir "$TEST_DIR/audit" \
  --verbose

echo ""
echo "Results: $TEST_DIR/results.json"
echo ""
echo "View results:"
echo "  cat $TEST_DIR/results.json | jq '.human.decision, .asi.decision'"
echo ""
