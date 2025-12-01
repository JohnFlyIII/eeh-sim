from typing import Dict, Any, Optional, List, Tuple
import json, os, time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, TextGenerationPipeline
import torch

_DEFAULT_MODEL = os.getenv("EEH_HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
DO_SAMPLE = os.getenv("EEH_DO_SAMPLE", "0") in ("1","true","True","yes","on")
TEMP = float(os.getenv("EEH_TEMPERATURE", "0.6"))
TOP_P = float(os.getenv("EEH_TOP_P", "0.9"))
MAX_NEW = int(os.getenv("EEH_MAX_NEW_TOKENS", "384"))
FORCE_DTYPE = os.getenv("EEH_FORCE_DTYPE", "").lower()
PROMPT_MAX = int(os.getenv("EEH_PROMPT_MAX_TOKENS", "4096"))
EEH_DEVICE = os.getenv("EEH_DEVICE", "auto").lower()
LOAD4 = os.getenv("EEH_LOAD_IN_4BIT", "0") in ("1","true","True")
LOAD8 = os.getenv("EEH_LOAD_IN_8BIT", "0") in ("1","true","True")
DEVICE_MAP = os.getenv("EEH_DEVICE_MAP", "none").lower()  # "auto" or "none"

_tokenizer = None
_model = None
_pipe: Optional[TextGenerationPipeline] = None

def _truncate_prompt(tokenizer, text: str, max_tokens: int) -> str:
    enc = tokenizer(text, add_special_tokens=False, truncation=True, max_length=max_tokens, return_attention_mask=False)
    ids = enc.get("input_ids", [])
    return tokenizer.decode(ids, skip_special_tokens=True)

def _choose_dtype() -> Optional[torch.dtype]:
    if FORCE_DTYPE in ("float16","fp16"): return torch.float16
    if FORCE_DTYPE in ("bfloat16","bf16"): return torch.bfloat16
    if FORCE_DTYPE in ("float32","fp32"): return torch.float32
    if EEH_DEVICE == "cuda":
        return torch.bfloat16 if torch.cuda.is_available() else torch.float16
    if EEH_DEVICE == "mps":
        return torch.float16
    return None

def _place_model(model):
    if EEH_DEVICE == "cuda" and torch.cuda.is_available():
        model.to("cuda"); return
    if EEH_DEVICE == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        model.to("mps"); return
    model.to("cpu")

DELTA_GUIDE = """Return ONLY JSON with keys:
facts_new (string[]),
causal_new ({from:string,to:string,label:'ChainA'|'ChainB',cf?:boolean}[]),
modalities_new (string[]),
decision_provisional ('no-fault'|'shared-fault'|'driver-negligence'|'abstain'),
metrics (object with scoreA, scoreB, decision_margin, rationale)
JSON only, no prose, no backticks.
"""

def _ensure_loaded(model_name: str):
    global _tokenizer, _model, _pipe
    if _pipe is None:
        print(f"[HF] Loading model: {model_name} …")
        t0 = time.time()
        _tokenizer = AutoTokenizer.from_pretrained(model_name)

        dtype = _choose_dtype()
        kwargs = dict(torch_dtype=dtype, low_cpu_mem_usage=False)
        if LOAD4:
            kwargs.update(dict(load_in_4bit=True, device_map="auto"))
            print("[HF] load_in_4bit enabled")
        elif LOAD8:
            kwargs.update(dict(load_in_8bit=True, device_map="auto"))
            print("[HF] load_in_8bit enabled")
        else:
            if DEVICE_MAP == "auto":
                kwargs.update(dict(device_map="auto"))
            else:
                kwargs.update(dict(device_map=None))

        _model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)
        if DEVICE_MAP != "auto" and not LOAD4 and not LOAD8:
            _place_model(_model)
        else:
            print("[HF] Using accelerate device_map placement")

        _pipe = pipeline("text-generation", model=_model, tokenizer=_tokenizer, return_full_text=False)
        print(f"[HF] Model ready in {time.time()-t0:.1f}s")

def delta_prompt(system: str, user: str, facts, causal) -> str:
    prior = {"facts": facts[-200:], "causal_tail": causal[-200:]}
    return f"<|system|>\n{system}\n{DELTA_GUIDE}\n<|user|>\n{user}\nPRIOR_MEMORY:\n{json.dumps(prior, ensure_ascii=False)}\n<|assistant|>\n"

def _extract_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    s = text
    starts = [i for i,ch in enumerate(s) if ch == "{"]
    for st in starts:
        depth = 0
        for i in range(st, len(s)):
            if s[i] == "{": depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    chunk = s[st:i+1]
                    try:
                        return json.loads(chunk)
                    except Exception:
                        pass
    cleaned = text.strip().strip("`").replace("\u200b","").strip()
    return json.loads(cleaned)

def generate_json_with_raw(prompt: str, model_name: str = None, max_new_tokens: Optional[int] = None):
    name = model_name or _DEFAULT_MODEL
    _ensure_loaded(name)
    safe_prompt = _truncate_prompt(_tokenizer, prompt, int(os.getenv("EEH_PROMPT_MAX_TOKENS", "4096")))
    max_tokens = max_new_tokens if max_new_tokens is not None else MAX_NEW
    print(f"[HF] Generating (do_sample={DO_SAMPLE}, max_new_tokens={max_tokens}) …")
    t0 = time.time()
    try:
        out = _pipe(
            safe_prompt,
            max_new_tokens=max_tokens,
            do_sample=DO_SAMPLE,
            temperature=(float(os.getenv("EEH_TEMPERATURE","0.6")) if DO_SAMPLE else None),
            top_p=(float(os.getenv("EEH_TOP_P","0.9")) if DO_SAMPLE else None),
        )[0]["generated_text"]
    except Exception as e:
        print(f"[HF] Generation error: {e} — retrying safe CPU/no-sample.")
        model_fp32 = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32, torch_dtype=torch.float32, device_map=None)
        model_fp32.to("cpu")
        safe_pipe = pipeline("text-generation", model=model_fp32, tokenizer=_tokenizer, return_full_text=False)
        out = safe_pipe(safe_prompt, max_new_tokens=min(max_tokens,256), do_sample=False)[0]["generated_text"]
    dur = time.time()-t0
    print(f"[HF] Generation done in {dur:.1f}s — parsing JSON …")
    try:
        parsed = _extract_json(out)
        print("[HF] JSON parsed.")
    except Exception as e:
        print(f"[HF] JSON parse failed: {e}. Returning minimal delta.")
        parsed = {"facts_new": [], "causal_new": [], "modalities_new": [], "decision_provisional": "abstain", "metrics": {"parse_error": str(e)}}
    return out, parsed
