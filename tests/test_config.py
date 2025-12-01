"""
Unit tests for configuration loading and validation
"""

import sys
from pathlib import Path
import tempfile
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eeh_llm.config import load_config, load_scenario


def test_load_valid_config():
    """Test loading valid configuration file"""
    config_content = """
name: test-agent
stm_facts_cap: 10
stm_causal_cap: 10
max_projection_steps: 4
max_factors: 20
max_causal_links: 30
context_budget_tokens: 2000
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        config = load_config(f.name)
        assert config["name"] == "test-agent"
        assert config["stm_facts_cap"] == 10
        Path(f.name).unlink()


def test_load_config_invalid_type():
    """Test configuration with invalid integer type"""
    config_content = """
name: test-agent
stm_facts_cap: "not_a_number"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        f.flush()
        try:
            config = load_config(f.name)
            # Should raise ValueError for non-integer
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        finally:
            Path(f.name).unlink()


def test_load_scenario_v3_format():
    """Test loading v3 scenario format with prompt_templates"""
    scenario_content = """
id: test_scenario
title: Test Scenario
prompt_templates:
  human_observational: "Analyze as human"
  asi_comprehensive: "Analyze as ASI"
universes:
  pseudo-human:
    analysis_mode: observational
    expected_depth: 3
    expected_decision: ["no-fault"]
    known_facts:
      - "Fact 1"
      - "Fact 2"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(scenario_content)
        f.flush()
        scenario = load_scenario(f.name)
        assert scenario["id"] == "test_scenario"
        assert "prompt_templates" in scenario
        assert "universes" in scenario
        Path(f.name).unlink()


def test_load_scenario_missing_required_keys():
    """Test scenario with missing required keys"""
    scenario_content = """
title: Test Scenario
# Missing 'id'
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(scenario_content)
        f.flush()
        try:
            scenario = load_scenario(f.name)
            assert False, "Should have raised ValueError for missing 'id'"
        except ValueError as e:
            assert "missing keys" in str(e).lower()
        finally:
            Path(f.name).unlink()


def test_load_scenario_v2_format():
    """Test loading v2 scenario format with single prompt"""
    scenario_content = """
id: test_scenario_v2
title: Test Scenario V2
prompt: "Single prompt for both agents"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(scenario_content)
        f.flush()
        scenario = load_scenario(f.name)
        assert scenario["id"] == "test_scenario_v2"
        assert "prompt" in scenario
        Path(f.name).unlink()


if __name__ == "__main__":
    # Run tests manually
    tests = [
        test_load_valid_config,
        test_load_config_invalid_type,
        test_load_scenario_v3_format,
        test_load_scenario_missing_required_keys,
        test_load_scenario_v2_format,
    ]

    print("Running config tests...")
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
