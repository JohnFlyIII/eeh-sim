# Testing the EEH Differential

Three ways to test the framework, from fastest to most powerful:

## Option 1: Quickest Test (~2-3 minutes)

**Same model, different constraints only:**

```bash
./quick_test_same_model.sh
```

**Uses:**
- Model: Qwen/Qwen2.5-7B-Instruct (both modes)
- Human: 256 tokens
- ASI: 2048 tokens (8x differential)

**Shows:** Differential from prompting + token limits alone

**Expected:**
- Human: 2-3 hop chains, scene-level
- ASI: 4-5 hop chains (limited by model capability)

---

## Option 2: Full Test with Different Models (~5-10 minutes)

**Different models, maximum differential:**

```bash
./test_eeh_differential.sh
```

**Uses:**
- Human: Qwen/Qwen2.5-7B-Instruct (~4GB)
- ASI: Qwen/Qwen2.5-14B-Instruct (~8GB)
- Human: 512 tokens
- ASI: 4096 tokens

**Shows:** Architectural + prompting + token differential

**Expected:**
- Human: 2-3 hop chains, "no-fault"
- ASI: 5-7 hop chains, deeper temporal analysis

---

## Option 3: Maximum Power (~10-20 minutes, requires 24GB VRAM)

**Production configuration:**

```bash
# Configure
export EEH_HF_MODEL_HUMAN="Qwen/Qwen2.5-7B-Instruct"
export EEH_HF_MODEL_ASI="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
export EEH_DEVICE=cuda
export EEH_LOAD_IN_4BIT=1
export EEH_MAX_NEW_TOKENS_HUMAN=512
export EEH_MAX_NEW_TOKENS_ASI=16384

# Run
./scripts/run_v3.sh
```

**Uses:**
- Human: 7B model, 512 tokens
- ASI: 32B reasoning specialist, 16K tokens
- Total: ~22GB VRAM

**Shows:** Maximum EEH differential

**Expected:**
- Human: 2-3 hop chains, "no-fault" or "shared-fault"
- ASI: 8-10 hop chains, 5+ hour temporal depth, "driver-negligence" with root causes

---

## What to Look For

### In Terminal Output

```
HUMAN Agent:
  Decision: no-fault (expected: ['no-fault', 'shared-fault'])
  Match: ✓
  Depth: 3 (expected: 3)
  Temporal span: 0.0h

ASI Agent:
  Decision: driver-negligence (expected: ['driver-negligence'])
  Match: ✓
  Depth: 8 (expected: 7)
  Temporal span: 5.2h
  Root causes: 4
```

**Key indicators of EEH:**
- ✅ Different decisions (human: "no-fault", ASI: "driver-negligence")
- ✅ ASI deeper chain (8 vs 3 hops)
- ✅ ASI looks back in time (5.2 hours vs 0)
- ✅ ASI identifies root causes (4 vs 0)

### In JSON Results

```bash
# View decisions
cat runs/test_*/results.json | jq '{
  human_decision: .human.decision,
  asi_decision: .asi.decision,
  human_depth: .human.metrics.chain_depth,
  asi_depth: .asi.metrics.chain_depth,
  human_temporal: .human.metrics.temporal_span_hours,
  asi_temporal: .asi.metrics.temporal_span_hours
}'
```

**Expected output:**
```json
{
  "human_decision": "no-fault",
  "asi_decision": "driver-negligence",
  "human_depth": 3,
  "asi_depth": 8,
  "human_temporal": 0,
  "asi_temporal": 5.2
}
```

### In Audit Logs

**Human reasoning** (`audit/no_fault_dual_v3/pseudo-human/sample_1.json`):
```json
{
  "causal_chain": [
    {"from": "Yellow light appears", "to": "Driver proceeds through intersection"},
    {"from": "Pedestrian begins crossing", "to": "Collision occurs"}
  ],
  "reasoning_narrative": "Based on the observable evidence at the scene, both parties followed normal patterns. The driver proceeded through a yellow light, which is legal. The pedestrian began crossing within their right. The collision appears to be an unfortunate timing conflict with no clear negligence."
}
```

**ASI reasoning** (`audit/no_fault_dual_v3/pseudo-asi/sample_1.json`):
```json
{
  "causal_chain": [
    {"from": "Late-night venue visit (t=-5.2h)", "to": "Alcohol consumption"},
    {"from": "Alcohol consumption", "to": "Sleep deprivation (t=-4.5h)"},
    {"from": "Sleep deprivation", "to": "Impaired vigilance"},
    {"from": "Morning time pressure (t=-30min)", "to": "Rushed departure"},
    {"from": "Impaired vigilance + time pressure", "to": "Microsleep event (t=-2s)"},
    {"from": "Microsleep", "to": "Failed to detect pedestrian"},
    {"from": "Failed detection", "to": "Collision"}
  ],
  "reasoning_narrative": "Through comprehensive multi-modal analysis including venue transactions, mobile data, and vehicle telemetry, we can trace the collision to controllable root causes hours before the event. The driver's late-night alcohol venue visit at t=-5.2h led to insufficient sleep (4.2 hours), combined with morning time pressure, resulted in impaired cognitive function. A brief microsleep 2 seconds before impact prevented pedestrian detection. While the proximate cause appears accidental, the deeper causal chain reveals driver choices that created the conditions for this outcome."
}
```

---

## Generate Visual Report

After running any test:

```bash
# Generate HTML report with visualizations
python generate_report_v3.py runs/test_*/results.json runs/test_*/report.html

# View
open runs/test_*/report.html  # macOS
xdg-open runs/test_*/report.html  # Linux
```

The report shows:
- Side-by-side causal graphs (human vs ASI)
- Color-coded nodes (red=root causes, yellow=intermediate, blue=outcomes)
- Full reasoning narratives
- Comparison dashboard with metrics
- Temporal depth visualization

---

## Troubleshooting

### "CUDA out of memory"

Try smaller models or reduce tokens:
```bash
export EEH_HF_MODEL_ASI="Qwen/Qwen2.5-14B-Instruct"  # Instead of 32B
export EEH_MAX_NEW_TOKENS_ASI=4096  # Instead of 16384
```

### "Model not found"

Ensure you have internet access for first download:
```bash
# Models are downloaded from HuggingFace on first use
# They cache to ~/.cache/huggingface/
```

### "No GPU / MPS not available"

Use CPU mode (very slow):
```bash
export EEH_DEVICE=cpu
export EEH_FORCE_DTYPE=float32
export EEH_LOAD_IN_4BIT=0
```

### "Shallow chains even with 32B model"

Check that ASI mode is using the right model:
```bash
# Should see different models in output:
# [bold]Agent:[/bold] pseudo-human
# [bold]Model:[/bold] Qwen/Qwen2.5-7B-Instruct  ← Human model
#
# [bold]Agent:[/bold] pseudo-asi
# [bold]Model:[/bold] deepseek-ai/DeepSeek-R1-Distill-Qwen-32B  ← ASI model
```

---

## For JOSS Reviewers

To verify the framework works:

```bash
# Quick test (2-3 minutes)
./quick_test_same_model.sh

# Verify results exist
ls runs/quick_test_*/results.json

# Check JSON is valid
cat runs/quick_test_*/results.json | jq .

# Verify different decisions
cat runs/quick_test_*/results.json | jq '{human: .human.decision, asi: .asi.decision}'
```

Expected: Human and ASI reach different ethical conclusions from the same evidence.

---

## Performance Benchmarks

| Configuration | Time | VRAM | Quality |
|--------------|------|------|---------|
| Quick (7B same) | 2-3 min | 4GB | Basic demo ⭐⭐ |
| Full (7B + 14B) | 5-10 min | 12GB | Good demo ⭐⭐⭐⭐ |
| Max (7B + 32B-R1) | 10-20 min | 22GB | Excellent ⭐⭐⭐⭐⭐ |

---

**Last Updated:** 2025-12-01
