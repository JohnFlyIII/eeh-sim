#!/bin/bash
# EEH V2 Runner Script
# Full environment setup for running the dual-chain v2 implementation

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - Modify these as needed
# ============================================================================

# Model selection (use one of these)
# export EEH_HF_MODEL="Qwen/Qwen2.5-32B-Instruct"
# export EEH_HF_MODEL="meta-llama/Llama-3.1-70B-Instruct"
# export EEH_HF_MODEL="mistralai/Mistral-Nemo-Instruct-2407"
export EEH_HF_MODEL="${EEH_HF_MODEL:-Qwen/Qwen2.5-7B-Instruct}"  # Default to 7B if not set

# Scenario and config files
SCENARIO="${1:-scenarios/no_fault_dual_v2.yaml}"
HUMAN_CONFIG="${2:-configs/pseudo_human_v2.yaml}"
ASI_CONFIG="${3:-configs/pseudo_asi_v2.yaml}"
OUTPUT="${4:-runs/no_fault_v2_$(date +%Y%m%d_%H%M%S).json}"

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

# Device configuration
export EEH_DEVICE=cuda                    # Use CUDA (GPU)
export EEH_DEVICE_MAP=auto                # Auto device mapping
export EEH_FORCE_DTYPE=float16            # Use FP16 for faster inference

# Quantization (saves memory)
export EEH_LOAD_IN_4BIT=1                 # Enable 4-bit quantization
# export EEH_LOAD_IN_8BIT=0               # Or use 8-bit (better quality, more memory)

# Sampling parameters
export EEH_DO_SAMPLE=1                    # Enable sampling (vs greedy)
export EEH_TEMPERATURE=0.6                # Lower = more deterministic, higher = more creative
export EEH_TOP_P=0.9                      # Nucleus sampling threshold
export EEH_MAX_NEW_TOKENS=384             # Max output tokens per generation
export EEH_PROMPT_MAX_TOKENS=4096         # Max context window size

# Generation retry parameters
export EEH_MAX_REASK=3                    # Max retries if quotas not met

# HuggingFace Hub optimization
export HF_HUB_ENABLE_HF_TRANSFER=1        # Faster downloads

# System configuration
export TOKENIZERS_PARALLELISM=false       # Avoid tokenizer warnings
export MPLBACKEND=Agg                     # Matplotlib backend for headless
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128  # CUDA memory management

# ============================================================================
# VALIDATION
# ============================================================================

echo "=========================================="
echo "EEH V2 Runner"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Model:    $EEH_HF_MODEL"
echo "  Scenario: $SCENARIO"
echo "  Human:    $HUMAN_CONFIG"
echo "  ASI:      $ASI_CONFIG"
echo "  Output:   $OUTPUT"
echo "  Device:   $EEH_DEVICE (dtype: $EEH_FORCE_DTYPE, 4-bit: $EEH_LOAD_IN_4BIT)"
echo "  Sampling: temp=$EEH_TEMPERATURE, top_p=$EEH_TOP_P, max_tokens=$EEH_MAX_NEW_TOKENS"
echo ""

# Check if files exist
if [ ! -f "$SCENARIO" ]; then
    echo "ERROR: Scenario file not found: $SCENARIO"
    exit 1
fi

if [ ! -f "$HUMAN_CONFIG" ]; then
    echo "ERROR: Human config not found: $HUMAN_CONFIG"
    exit 1
fi

if [ ! -f "$ASI_CONFIG" ]; then
    echo "ERROR: ASI config not found: $ASI_CONFIG"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "WARNING: Virtual environment not activated!"
    echo "Run: source .venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============================================================================
# RUN
# ============================================================================

echo "Starting run at $(date)..."
echo ""

# Create audit directory
AUDIT_DIR="runs/audit_v2_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$AUDIT_DIR"

# Run the model
PYTHONPATH=./src python3 -m eeh_llm run \
  --scenario "$SCENARIO" \
  --human "$HUMAN_CONFIG" \
  --asi "$ASI_CONFIG" \
  --out "$OUTPUT" \
  --model "$EEH_HF_MODEL" \
  --verbose \
  --n-samples 3 \
  --audit-dir "$AUDIT_DIR"

EXIT_CODE=$?

# ============================================================================
# POST-RUN
# ============================================================================

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "SUCCESS!"
    echo "=========================================="
    echo ""
    echo "Results saved to: $OUTPUT"
    echo "Audit logs in:    $AUDIT_DIR"
    echo ""

    # Show quick summary if jq is available
    if command -v jq &> /dev/null; then
        echo "Quick Summary:"
        echo "  Human decision: $(jq -r '.human.decision' "$OUTPUT")"
        echo "  ASI decision:   $(jq -r '.asi.decision' "$OUTPUT")"
        echo ""
        echo "Generate report with:"
        echo "  PYTHONPATH=./src python3 -m eeh_llm report $OUTPUT --html ${OUTPUT%.json}.html"
    fi
else
    echo ""
    echo "=========================================="
    echo "FAILED (exit code: $EXIT_CODE)"
    echo "=========================================="
    echo ""
    echo "Check audit logs in: $AUDIT_DIR"
fi

exit $EXIT_CODE
