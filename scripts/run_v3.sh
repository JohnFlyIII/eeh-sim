#!/bin/bash
# EEH V3 Runner Script
# Mode-based deep reasoning implementation with improved prompts

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - Modify these as needed
# ============================================================================

# Model selection - IMPORTANT: Use 32B+ for deep reasoning!
# Recommended: Qwen/Qwen2.5-32B-Instruct (best balance of quality/speed)
# Alternative: meta-llama/Llama-3.1-70B-Instruct (requires more VRAM)
export EEH_HF_MODEL="${EEH_HF_MODEL:-Qwen/Qwen2.5-32B-Instruct}"

# Scenario and config files
SCENARIO="${1:-scenarios/no_fault_dual_v3.yaml}"
HUMAN_CONFIG="${2:-configs/pseudo_human_v2.yaml}"
ASI_CONFIG="${3:-configs/pseudo_asi_v2.yaml}"

# Create self-contained run directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RUN_DIR="${4:-runs/run_${TIMESTAMP}}"
mkdir -p "$RUN_DIR"
mkdir -p "$RUN_DIR/figures"
mkdir -p "$RUN_DIR/audit"

OUTPUT="$RUN_DIR/results.json"

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

# Device configuration
export EEH_DEVICE=cuda                    # Use CUDA (GPU)
export EEH_DEVICE_MAP=auto                # Auto device mapping
export EEH_FORCE_DTYPE=bfloat16           # Use BF16 (better for reasoning than FP16)

# Quantization (4-bit recommended for 32B models on 24GB VRAM)
export EEH_LOAD_IN_4BIT=1                 # Enable 4-bit quantization
# export EEH_LOAD_IN_8BIT=0               # Or use 8-bit if you have 48GB+ VRAM

# Sampling parameters - Differentiated by agent type
export EEH_DO_SAMPLE=1                    # Enable sampling
export EEH_TEMPERATURE=0.7                # Slightly higher for creative causal exploration
export EEH_TOP_P=0.95                     # Wider sampling for diverse reasoning paths

# Differentiated token limits per agent (NEW in v3)
# Maximum demonstration of EEH differential: 31x (16384 vs 512)
# Human: Constrained reflecting cognitive limitations
# ASI: Massive capacity enabling "decades of context" and "countless factors" (per paper vision)
export EEH_PROMPT_MAX_TOKENS=16384        # 16K context for rich evidence (ASI can process everything)
export EEH_MAX_NEW_TOKENS_HUMAN=512       # ~380 words, 5-8 causal links (constrained)
export EEH_MAX_NEW_TOKENS_ASI=16384       # ~12,000 words, 100-200+ causal links (31x differential)

# V3 doesn't use the old quota/reask system (single-shot generation)
# export EEH_MAX_REASK=0                  # Not used in v3

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
echo "EEH V3 Runner - Mode-Based Deep Reasoning"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Model:    $EEH_HF_MODEL"
echo "  Scenario: $SCENARIO"
echo "  Human:    $HUMAN_CONFIG"
echo "  ASI:      $ASI_CONFIG"
echo "  Run Dir:  $RUN_DIR"
echo "  Device:   $EEH_DEVICE (dtype: $EEH_FORCE_DTYPE, 4-bit: $EEH_LOAD_IN_4BIT)"
echo "  Sampling: temp=$EEH_TEMPERATURE, top_p=$EEH_TOP_P"
echo "  Token Limits (31x differential for maximum EEH demonstration):"
echo "    Context:  $EEH_PROMPT_MAX_TOKENS tokens (input/evidence)"
echo "    Human:    $EEH_MAX_NEW_TOKENS_HUMAN tokens output (constrained)"
echo "    ASI:      $EEH_MAX_NEW_TOKENS_ASI tokens output (expansive, 31x differential)"
echo ""

# Check if files exist
if [ ! -f "$SCENARIO" ]; then
    echo "ERROR: Scenario file not found: $SCENARIO"
    echo "Make sure you're using the v3 scenario: scenarios/no_fault_dual_v3.yaml"
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

# Warn if using small model
if [[ "$EEH_HF_MODEL" == *"7B"* ]] || [[ "$EEH_HF_MODEL" == *"8B"* ]]; then
    echo "WARNING: You're using a small model ($EEH_HF_MODEL)"
    echo "V3 requires 32B+ parameters for deep multi-hop reasoning."
    echo "Recommended: Qwen/Qwen2.5-32B-Instruct"
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

# Run using the new v3 runner (audit goes to RUN_DIR/audit)
python run_v3.py \
  --scenario "$SCENARIO" \
  --human "$HUMAN_CONFIG" \
  --asi "$ASI_CONFIG" \
  --model "$EEH_HF_MODEL" \
  --out "$OUTPUT" \
  --verbose \
  --audit-dir "$RUN_DIR/audit" \
  --n-samples 1

EXIT_CODE=$?

# ============================================================================
# POST-RUN ANALYSIS
# ============================================================================

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "SUCCESS!"
    echo "=========================================="
    echo ""
    echo "Results saved to: $RUN_DIR"
    echo "  ├─ results.json"
    echo "  ├─ report.html (generating...)"
    echo "  ├─ figures/"
    echo "  └─ audit/"
    echo ""

    # Show detailed summary if jq is available
    if command -v jq &> /dev/null; then
        echo "Detailed Results:"
        echo ""
        echo "HUMAN AGENT (Observational Mode):"
        echo "  Decision:       $(jq -r '.human.decision' "$OUTPUT")"
        echo "  Expected:       $(jq -r '.human.metrics.expected_decisions | join(" or ")' "$OUTPUT")"
        echo "  Match:          $(jq -r '.human.metrics.decision_matches' "$OUTPUT")"
        echo "  Chain depth:    $(jq -r '.human.metrics.chain_depth' "$OUTPUT") (expected: $(jq -r '.human.metrics.expected_depth' "$OUTPUT"))"
        echo "  Temporal span:  $(jq -r '.human.metrics.temporal_span_hours' "$OUTPUT")h"
        echo ""
        echo "ASI AGENT (Comprehensive Mode):"
        echo "  Decision:       $(jq -r '.asi.decision' "$OUTPUT")"
        echo "  Expected:       $(jq -r '.asi.metrics.expected_decisions | join(" or ")' "$OUTPUT")"
        echo "  Match:          $(jq -r '.asi.metrics.decision_matches' "$OUTPUT")"
        echo "  Chain depth:    $(jq -r '.asi.metrics.chain_depth' "$OUTPUT") (expected: $(jq -r '.asi.metrics.expected_depth' "$OUTPUT"))"
        echo "  Temporal span:  $(jq -r '.asi.metrics.temporal_span_hours' "$OUTPUT")h"
        echo "  Root causes:    $(jq -r '.asi.root_causes | length' "$OUTPUT") identified"
        echo ""

        # Check if both matched expectations
        HUMAN_MATCH=$(jq -r '.human.metrics.decision_matches' "$OUTPUT")
        ASI_MATCH=$(jq -r '.asi.metrics.decision_matches' "$OUTPUT")

        if [ "$HUMAN_MATCH" = "true" ] && [ "$ASI_MATCH" = "true" ]; then
            echo "✓ SUCCESS: Both agents produced expected decisions!"
            echo ""
            echo "This demonstrates the Ethical Event Horizon:"
            echo "  - Human: Limited to observable evidence → $(jq -r '.human.decision' "$OUTPUT")"
            echo "  - ASI: Deep causal analysis → $(jq -r '.asi.decision' "$OUTPUT")"
        else
            echo "⚠ PARTIAL: One or both agents didn't match expectations"
            echo ""
            if [ "$HUMAN_MATCH" != "true" ]; then
                echo "  Human agent: Expected $(jq -r '.human.metrics.expected_decisions | join(" or ")' "$OUTPUT"), got $(jq -r '.human.decision' "$OUTPUT")"
            fi
            if [ "$ASI_MATCH" != "true" ]; then
                echo "  ASI agent: Expected $(jq -r '.asi.metrics.expected_decisions | join(" or ")' "$OUTPUT"), got $(jq -r '.asi.decision' "$OUTPUT")"
                echo ""
                echo "  Possible issues:"
                echo "    - Model too small (need 32B+)"
                echo "    - Temperature too low/high"
                echo "    - Check audit logs for prompt/response"
            fi
        fi

        echo ""
        echo "View full causal chains with:"
        echo "  jq '.human.causal_chain' $OUTPUT"
        echo "  jq '.asi.causal_chain' $OUTPUT"
    else
        echo "Install jq for detailed summary: sudo yum install jq"
    fi

    # Generate enhanced HTML report
    echo ""
    echo "Generating enhanced HTML report..."
    HTML_REPORT="$RUN_DIR/report.html"
    if python generate_report_v3.py "$OUTPUT" --output "$HTML_REPORT" --figures-dir "$RUN_DIR/figures" 2>/dev/null; then
        echo "✓ HTML report: $HTML_REPORT"
        echo ""
        echo "View report with:"
        echo "  open $HTML_REPORT   # macOS"
        echo "  xdg-open $HTML_REPORT   # Linux"
    else
        echo "⚠ HTML report generation failed (requires matplotlib)"
    fi
else
    echo ""
    echo "=========================================="
    echo "FAILED (exit code: $EXIT_CODE)"
    echo "=========================================="
    echo ""
    echo "Check audit logs in: $AUDIT_DIR"
    echo ""
    echo "Common issues:"
    echo "  - Model too large for VRAM → Enable 4-bit: export EEH_LOAD_IN_4BIT=1"
    echo "  - Model not found → Check EEH_HF_MODEL is correct"
    echo "  - CUDA out of memory → Reduce EEH_MAX_NEW_TOKENS or use smaller model"
fi

exit $EXIT_CODE
