"""
Unit tests for backend JSON extraction
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eeh_llm.backend.hf import _extract_json


def test_extract_json_clean():
    """Test extracting clean JSON"""
    text = '{"decision": "no-fault", "confidence": "HIGH"}'
    result = _extract_json(text)
    assert result["decision"] == "no-fault"
    assert result["confidence"] == "HIGH"


def test_extract_json_with_markdown():
    """Test extracting JSON from markdown code blocks"""
    text = """```json
{
    "decision": "driver-negligence",
    "causal_chain": [
        {"from": "A", "to": "B"}
    ]
}
```"""
    result = _extract_json(text)
    assert result["decision"] == "driver-negligence"
    assert len(result["causal_chain"]) == 1


def test_extract_json_with_prose():
    """Test extracting JSON embedded in prose"""
    text = """Here is my analysis:
{
    "decision": "shared-fault",
    "reasoning_narrative": "Both parties contributed"
}
Additional commentary here."""
    result = _extract_json(text)
    assert result["decision"] == "shared-fault"


def test_extract_json_nested():
    """Test extracting complex nested JSON"""
    text = """{
    "decision": "no-fault",
    "causal_chain": [
        {"from": "Light turns yellow", "to": "Driver proceeds"},
        {"from": "Pedestrian crosses", "to": "Collision"}
    ],
    "metrics": {
        "chain_depth": 2,
        "temporal_span": 0
    }
}"""
    result = _extract_json(text)
    assert result["decision"] == "no-fault"
    assert len(result["causal_chain"]) == 2
    assert result["metrics"]["chain_depth"] == 2


def test_extract_json_with_unicode():
    """Test extracting JSON with unicode characters"""
    text = '{"decision": "no-fault", "narrative": "Analysis → conclusion"}'
    result = _extract_json(text)
    assert result["decision"] == "no-fault"
    assert "→" in result["narrative"]


def test_extract_json_multiple_objects():
    """Test extracting first valid JSON from multiple objects"""
    text = """{invalid}
{
    "decision": "driver-negligence",
    "valid": true
}
{
    "second": "object"
}"""
    result = _extract_json(text)
    assert result["decision"] == "driver-negligence"


def test_extract_json_with_backticks():
    """Test extracting JSON with backticks"""
    text = '```{"decision": "no-fault"}```'
    result = _extract_json(text)
    assert result["decision"] == "no-fault"


def test_extract_json_empty_array():
    """Test extracting JSON with empty arrays"""
    text = '{"causal_chain": [], "decision": "abstain"}'
    result = _extract_json(text)
    assert result["causal_chain"] == []
    assert result["decision"] == "abstain"


def test_extract_json_multiline_strings():
    """Test extracting JSON with multiline strings"""
    text = """{
    "decision": "driver-negligence",
    "reasoning_narrative": "This is a long reasoning that spans multiple lines"
}"""
    result = _extract_json(text)
    assert result["decision"] == "driver-negligence"
    assert "reasoning" in result["reasoning_narrative"]


if __name__ == "__main__":
    # Run tests manually
    tests = [
        test_extract_json_clean,
        test_extract_json_with_markdown,
        test_extract_json_with_prose,
        test_extract_json_nested,
        test_extract_json_with_unicode,
        test_extract_json_multiple_objects,
        test_extract_json_with_backticks,
        test_extract_json_empty_array,
        test_extract_json_multiline_strings,
    ]

    print("Running backend tests...")
    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
