#!/bin/bash
# Quick test to demonstrate EEH differential with different models
# This uses small models for fast testing

set -e

echo "=========================================="
echo "EEH Differential Test"
echo "=========================================="
echo ""
echo "This will run both human and ASI modes and show the difference."
echo "Using smaller models for faster testing (~5-10 minutes total)."
echo ""

# Configuration
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"
export EEH_HF_MODEL_ASI="Qwen/Qwen2.5-14B-Instruct"  # Using 14B for speed (still shows differential)

# Auto-detect device and configure appropriately
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use MPS (Apple Silicon) or CPU
    if python3 -c "import torch; exit(0 if torch.backends.mps.is_available() else 1)" 2>/dev/null; then
        export EEH_DEVICE=mps
        export EEH_FORCE_DTYPE=float16  # MPS doesn't support bfloat16
        export EEH_LOAD_IN_4BIT=0       # Quantization not available on MPS
        echo "Detected: macOS with Apple Silicon (MPS)"
    else
        export EEH_DEVICE=cpu
        export EEH_FORCE_DTYPE=float32
        export EEH_LOAD_IN_4BIT=0
        echo "Detected: macOS without GPU (CPU only - will be slow)"
    fi
else
    # Linux - use CUDA if available
    export EEH_DEVICE=cuda
    export EEH_FORCE_DTYPE=bfloat16
    export EEH_LOAD_IN_4BIT=1
    echo "Detected: Linux with CUDA"
fi

export EEH_DEVICE_MAP=auto

# Token limits
export EEH_MAX_NEW_TOKENS_HUMAN=512
export EEH_MAX_NEW_TOKENS_ASI=4096  # Using 4K instead of 16K for speed

# Sampling
export EEH_TEMPERATURE=0.7
export EEH_TOP_P=0.95
export EEH_DO_SAMPLE=1

# System
export TOKENIZERS_PARALLELISM=false
export MPLBACKEND=Agg

# Create test output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_DIR="runs/test_${TIMESTAMP}"
mkdir -p "$TEST_DIR"

echo "Configuration:"
echo "  Human model: $EEH_HF_MODEL_HUMAN"
echo "  ASI model:   $EEH_HF_MODEL_ASI"
echo "  Device:      $EEH_DEVICE"
echo "  Output:      $TEST_DIR"
echo ""
echo "Starting test run..."
echo ""

# Run the test
python run_v3.py \
  --scenario scenarios/no_fault_dual_v3.yaml \
  --human configs/pseudo_human_v2.yaml \
  --asi configs/pseudo_asi_v2.yaml \
  --out "$TEST_DIR/results.json" \
  --audit-dir "$TEST_DIR/audit" \
  --verbose

echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Results saved to: $TEST_DIR"
echo ""

# Extract and display key metrics
echo "COMPARISON:"
echo ""
python3 << PYTHON_SCRIPT
import json
import sys

results_path = "${TEST_DIR}/results.json"
try:
    with open(results_path) as f:
        data = json.load(f)

    human = data.get("human", {})
    asi = data.get("asi", {})

    h_metrics = human.get("metrics", {})
    a_metrics = asi.get("metrics", {})

    print("HUMAN MODE:")
    print(f"  Decision:      {human.get('decision', 'N/A')}")
    print(f"  Chain depth:   {h_metrics.get('chain_depth', 'N/A')} hops")
    print(f"  Temporal span: {h_metrics.get('temporal_span_hours', 0):.1f} hours")
    print(f"  Root causes:   {len(human.get('root_causes', []))}")
    print("")

    print("ASI MODE:")
    print(f"  Decision:      {asi.get('decision', 'N/A')}")
    print(f"  Chain depth:   {a_metrics.get('chain_depth', 'N/A')} hops")
    print(f"  Temporal span: {a_metrics.get('temporal_span_hours', 0):.1f} hours")
    print(f"  Root causes:   {len(asi.get('root_causes', []))}")
    print("")

    depth_diff = a_metrics.get('chain_depth', 0) - h_metrics.get('chain_depth', 0)
    print(f"EEH DIFFERENTIAL:")
    print(f"  Chain depth:   {depth_diff:+d} hops (ASI deeper)")
    print(f"  Temporal span: {a_metrics.get('temporal_span_hours', 0):.1f}h (ASI looks back further)")
    print(f"  Decision diff: {'YES - Different conclusions!' if human.get('decision') != asi.get('decision') else 'Same'}")

except Exception as e:
    print(f"Could not parse results: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo ""
echo "To view detailed results:"
echo "  Results JSON:  cat $TEST_DIR/results.json | jq ."
echo "  Human output:  cat $TEST_DIR/audit/no_fault_dual_v3/pseudo-human/sample_1.json | jq ."
echo "  ASI output:    cat $TEST_DIR/audit/no_fault_dual_v3/pseudo-asi/sample_1.json | jq ."
echo ""
echo "Generate HTML report:"
echo "  python generate_report_v3.py $TEST_DIR/results.json $TEST_DIR/report.html"
echo "  open $TEST_DIR/report.html"
echo ""
