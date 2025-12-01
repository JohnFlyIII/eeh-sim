from pathlib import Path
from typing import Dict, Any
import yaml

REQUIRED_SCENARIO_KEYS_BASE = {"id", "title"}

def load_yaml(path: str):
    return yaml.safe_load(Path(path).read_text())

def load_config(path: str) -> Dict[str, Any]:
    cfg = load_yaml(path)
    if not isinstance(cfg, dict):
        raise ValueError("config must be a YAML mapping")
    for k in ["max_causal_links","max_projection_steps","max_factors","stm_facts_cap","stm_causal_cap"]:
        if k in cfg and (not isinstance(cfg[k], int) or cfg[k] <= 0):
            raise ValueError(f"{k} must be positive int")
    return cfg

def load_scenario(path: str) -> Dict[str, Any]:
    scn = load_yaml(path)
    if not isinstance(scn, dict):
        raise ValueError("scenario must be a YAML mapping")

    # Check base required keys
    missing = REQUIRED_SCENARIO_KEYS_BASE - set(scn.keys())
    if missing:
        raise ValueError(f"scenario missing keys: {sorted(missing)}")

    # V2 format: single "prompt" field
    # V3 format: "prompt_templates" dict with human_observational/asi_comprehensive
    has_v2_prompt = "prompt" in scn
    has_v3_prompts = "prompt_templates" in scn

    if not has_v2_prompt and not has_v3_prompts:
        raise ValueError("scenario must have either 'prompt' (v2) or 'prompt_templates' (v3)")

    # Validate v2 format
    if has_v2_prompt:
        if not isinstance(scn["prompt"], str) or not scn["prompt"].strip():
            raise ValueError("scenario.prompt must be a non-empty string")

    # Validate v3 format
    if has_v3_prompts:
        if not isinstance(scn["prompt_templates"], dict):
            raise ValueError("prompt_templates must be a mapping")
        # Check for expected template keys (not strictly required, but helpful)
        templates = scn["prompt_templates"]
        if not any(k in templates for k in ["human_observational", "asi_comprehensive"]):
            # Allow flexibility but warn about typical keys
            pass

    # Validate universes if present
    if "universes" in scn and not isinstance(scn["universes"], dict):
        raise ValueError("universes must be a mapping of agent-name -> settings")

    return scn
