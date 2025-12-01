# Model Recommendations for EEH V3 (g5.xlarge / 24GB VRAM)

## TL;DR - Best Model for Your Use Case

**Qwen/Qwen2.5-32B-Instruct** in 4-bit quantization
- Best reasoning capability for multi-hop causal chains
- Excellent instruction following
- Fits comfortably in 24GB with 4-bit quant (~18GB)
- Strong performance on complex logical tasks

## Why Model Choice Matters for EEH

Your framework requires:
1. **Multi-hop reasoning**: Trace 6-8 causal links
2. **Temporal reasoning**: Connect events across hours
3. **Instruction following**: Stick to JSON format, follow constraints
4. **Counterfactual thinking**: Evaluate "what if" scenarios
5. **Long-form output**: Generate detailed causal chains

Small models (7B-12B) **struggle** with #1 and #2. They default to shallow proximate-cause reasoning.

## Recommended Models (Ranked)

### 🏆 #1: Qwen/Qwen2.5-32B-Instruct (BEST CHOICE)
- **Size**: 32B parameters
- **VRAM**: ~18GB in 4-bit, ~36GB in fp16 (use 4-bit)
- **Strengths**:
  - Excellent multi-hop reasoning
  - Strong instruction adherence
  - Good at temporal/causal analysis
  - Handles long outputs well
- **Setup**:
  ```bash
  pip install bitsandbytes
  export EEH_HF_MODEL=Qwen/Qwen2.5-32B-Instruct
  export EEH_DEVICE=cuda
  export EEH_FORCE_DTYPE=bfloat16
  export EEH_LOAD_IN_4BIT=1
  export EEH_MAX_NEW_TOKENS=1024
  ```

### 🥈 #2: meta-llama/Llama-3.1-70B-Instruct (8-bit)
- **Size**: 70B parameters
- **VRAM**: ~35GB in 8-bit, ~70GB in fp16 (TIGHT FIT in 8-bit)
- **Strengths**:
  - Superior reasoning over smaller models
  - Excellent at complex logic
  - Strong safety/instruction tuning
- **Caution**: May not fit in 24GB even with 8-bit. Test carefully.
- **Setup**:
  ```bash
  export EEH_HF_MODEL=meta-llama/Llama-3.1-70B-Instruct
  export EEH_LOAD_IN_8BIT=1
  export EEH_MAX_NEW_TOKENS=1024
  ```

### 🥉 #3: Qwen/QwQ-32B-Preview (Reasoning Specialist)
- **Size**: 32B parameters
- **VRAM**: ~18GB in 4-bit
- **Strengths**:
  - Specifically trained for reasoning tasks
  - Built-in chain-of-thought
  - May produce longer reasoning traces
- **Caution**: Preview model, may have quirks
- **Setup**: Same as Qwen2.5-32B above

### #4: mistralai/Mistral-Small-Instruct-2409 (24B)
- **Size**: 24B parameters
- **VRAM**: ~14GB in 4-bit, ~48GB in fp16
- **Strengths**:
  - Fits comfortably in 24GB
  - Good general capabilities
  - Fast inference
- **Weaknesses**:
  - Less capable at deep reasoning than Qwen 32B
  - May still produce shallow chains
- **Setup**:
  ```bash
  export EEH_HF_MODEL=mistralai/Mistral-Small-Instruct-2409
  export EEH_LOAD_IN_4BIT=1
  ```

## NOT Recommended (Too Small)

❌ **Qwen/Qwen2.5-7B-Instruct** - What you tested
- Too small for deep multi-hop reasoning
- Defaults to shallow 2-3 hop chains even when prompted for depth

❌ **mistralai/Mistral-Nemo-Instruct-2407** (12B)
- Better than 7B but still struggles with 6+ hop chains

❌ **meta-llama/Llama-3.2-11B-Vision-Instruct**
- Small parameter count limits reasoning depth

## Installation for 4-bit Quantization

```bash
# Install bitsandbytes for quantization
pip install bitsandbytes accelerate

# Verify CUDA is working
python -c "import torch; print(torch.cuda.is_available())"
```

## Testing Your Model

Quick test to see if a model can do deep reasoning:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "Qwen/Qwen2.5-32B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    load_in_4bit=True
)

prompt = """Build a causal chain with at least 6 hops:
Event: Person has car accident
Task: Trace back to root causes 5 hours before

Output format:
1. Root cause → 2. Effect → 3. Effect → ... → 7. Accident
"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

Look for:
- ✓ At least 6 distinct causal steps
- ✓ Temporal reasoning ("5 hours earlier...")
- ✓ Concrete not abstract steps

## Memory Optimization Tips

### If you hit OOM (Out of Memory):

1. **Enable 4-bit quantization** (saves ~50% memory):
   ```bash
   export EEH_LOAD_IN_4BIT=1
   ```

2. **Reduce context window**:
   ```bash
   export EEH_PROMPT_MAX_TOKENS=3072
   ```

3. **Reduce max output tokens**:
   ```bash
   export EEH_MAX_NEW_TOKENS=768
   ```

4. **Use gradient checkpointing** (in backend/hf.py):
   ```python
   model.gradient_checkpointing_enable()
   ```

5. **Try smaller model**:
   - Qwen2.5-14B-Instruct (if it exists)
   - Mistral-Small-22B

## Recommended Sampling Parameters

For deep reasoning tasks:

```bash
# More creative for causal exploration
export EEH_TEMPERATURE=0.7
export EEH_TOP_P=0.95
export EEH_DO_SAMPLE=1

# OR: More deterministic for consistency
export EEH_TEMPERATURE=0.3
export EEH_TOP_P=0.9
export EEH_DO_SAMPLE=1
```

## Performance Expectations

### Qwen2.5-32B-Instruct (4-bit):
- **Speed**: ~15-30 tokens/sec on g5.xlarge
- **Quality**: Should achieve 6-8 hop chains consistently
- **VRAM**: ~18GB peak
- **Cost**: $1.01/hour on AWS g5.xlarge

### Llama-3.1-70B (8-bit):
- **Speed**: ~8-15 tokens/sec
- **Quality**: Best reasoning, most consistent depth
- **VRAM**: ~35GB (may require g5.2xlarge with 48GB)
- **Cost**: $1.52/hour on AWS g5.2xlarge

## Final Recommendation

**Start with Qwen/Qwen2.5-32B-Instruct in 4-bit.**

If results are good but you want better:
→ Upgrade to g5.2xlarge (48GB) and use Llama-3.1-70B in 8-bit

If OOM issues:
→ Try Mistral-Small-24B-Instruct in 4-bit

If still getting shallow reasoning:
→ Problem is likely in prompt design, not model size. Review prompt templates in scenario YAML.

## Verification Command

After setup, verify your model loads correctly:

```bash
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
model_name = '$EEH_HF_MODEL'
print(f'Loading {model_name}...')
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map='auto',
    load_in_4bit=True
)
print(f'✓ Model loaded successfully')
print(f'✓ VRAM used: {torch.cuda.memory_allocated()/1e9:.2f}GB')
"
```
