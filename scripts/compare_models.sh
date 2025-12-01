#!/bin/bash
# Compare multiple models for EEH demonstration
# This script runs the same scenario with different models and generates comparison reports

set -e

# Models to compare
MODELS=(
    "Qwen/Qwen2.5-32B-Instruct"
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
)

MODEL_NAMES=(
    "qwen25_32b"
    "deepseek_r1_32b"
)

echo "=========================================="
echo "EEH Model Comparison Runner"
echo "=========================================="
echo ""
echo "Will run ${#MODELS[@]} models:"
for i in "${!MODELS[@]}"; do
    echo "  $((i+1)). ${MODELS[$i]} (${MODEL_NAMES[$i]})"
done
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Create comparison directory
COMPARISON_DIR="runs/comparison_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$COMPARISON_DIR"

echo ""
echo "Results will be saved to: $COMPARISON_DIR"
echo ""

# Run each model
for i in "${!MODELS[@]}"; do
    MODEL="${MODELS[$i]}"
    NAME="${MODEL_NAMES[$i]}"

    echo ""
    echo "=========================================="
    echo "Running Model $((i+1))/${#MODELS[@]}: $MODEL"
    echo "=========================================="
    echo ""

    # Set model
    export EEH_HF_MODEL="$MODEL"

    # Create model-specific directory
    RUN_DIR="$COMPARISON_DIR/${NAME}"
    mkdir -p "$RUN_DIR"

    # Run simulation
    if ./scripts/run_v3.sh "$@" 2>&1 | tee "$RUN_DIR/run.log"; then
        # Move latest run to comparison directory
        LATEST_RUN=$(ls -td runs/run_* | head -1)
        if [ -d "$LATEST_RUN" ]; then
            cp -r "$LATEST_RUN"/* "$RUN_DIR/"
            echo ""
            echo "✓ Model $NAME completed successfully"
            echo "  Results: $RUN_DIR"
        fi
    else
        echo ""
        echo "✗ Model $NAME failed"
        echo "  Check logs: $RUN_DIR/run.log"
    fi

    echo ""
done

echo ""
echo "=========================================="
echo "All models completed!"
echo "=========================================="
echo ""

# Generate comparison summary
SUMMARY="$COMPARISON_DIR/COMPARISON_SUMMARY.md"

cat > "$SUMMARY" <<'EOF'
# Model Comparison Summary

## Models Tested

EOF

for i in "${!MODELS[@]}"; do
    NAME="${MODEL_NAMES[$i]}"
    MODEL="${MODELS[$i]}"
    echo "- **${NAME}**: \`${MODEL}\`" >> "$SUMMARY"
done

cat >> "$SUMMARY" <<'EOF'

## Results

| Model | Chain Depth | Temporal Span | Root Causes | Decision | Tokens Generated |
|-------|-------------|---------------|-------------|----------|------------------|
EOF

# Extract metrics from each run
for i in "${!MODELS[@]}"; do
    NAME="${MODEL_NAMES[$i]}"
    RESULTS_JSON="$COMPARISON_DIR/${NAME}/results.json"

    if [ -f "$RESULTS_JSON" ]; then
        ASI_DEPTH=$(jq -r '.asi.metrics.chain_depth' "$RESULTS_JSON")
        ASI_TEMPORAL=$(jq -r '.asi.metrics.temporal_span_hours' "$RESULTS_JSON")
        ASI_ROOTS=$(jq -r '.asi.root_causes | length' "$RESULTS_JSON")
        ASI_DECISION=$(jq -r '.asi.decision' "$RESULTS_JSON")

        # Estimate tokens from reasoning narrative length
        NARRATIVE=$(jq -r '.asi.reasoning_narrative' "$RESULTS_JSON")
        WORD_COUNT=$(echo "$NARRATIVE" | wc -w)
        TOKEN_EST=$((WORD_COUNT * 13 / 10))  # ~1.3 tokens per word

        echo "| ${NAME} | ${ASI_DEPTH} | ${ASI_TEMPORAL}h | ${ASI_ROOTS} | ${ASI_DECISION} | ~${TOKEN_EST} |" >> "$SUMMARY"
    else
        echo "| ${NAME} | ERROR | ERROR | ERROR | ERROR | ERROR |" >> "$SUMMARY"
    fi
done

cat >> "$SUMMARY" <<'EOF'

## Analysis

### Chain Depth
- Higher is better (indicates deeper causal reasoning)
- Expected: 7-10 hops for 32B models

### Temporal Span
- Higher is better (traces causes further back in time)
- Expected: 5-6 hours for no-fault scenario

### Root Causes
- More is better (identifies multiple causal origins)
- Expected: 3-4 root causes (bar, sleep, time pressure, etc.)

### Decision
- Should be "driver-negligence" for ASI (comprehensive analysis)
- "no-fault" or "shared-fault" would indicate shallow reasoning

### Tokens Generated
- More tokens = more detailed reasoning narrative
- Expected: 5,000-12,000 tokens for ASI with 16K limit

## HTML Reports

EOF

for i in "${!MODELS[@]}"; do
    NAME="${MODEL_NAMES[$i]}"
    echo "- [${NAME} Report](${NAME}/report.html)" >> "$SUMMARY"
done

cat >> "$SUMMARY" <<'EOF'

## Conclusion

[Review the HTML reports and metrics above to determine which model performs best for the EEH demonstration.]

---

Generated: $(date)
EOF

echo "Comparison summary: $SUMMARY"
echo ""
echo "View reports:"
for i in "${!MODELS[@]}"; do
    NAME="${MODEL_NAMES[$i]}"
    echo "  open $COMPARISON_DIR/${NAME}/report.html"
done
echo ""
echo "View summary:"
echo "  cat $SUMMARY"
