"""
Unit tests for controller_v3 core logic
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from eeh_llm.reasoning.controller_v3 import (
    _compute_chain_depth,
    _compute_temporal_span,
    _identify_root_causes,
    _compute_root_cause_score
)


def test_chain_depth_simple():
    """Test chain depth calculation with simple linear chain"""
    chain = [
        {"from": "A", "to": "B"},
        {"from": "B", "to": "C"}
    ]
    depth = _compute_chain_depth(chain)
    # A→B→C means 3 levels (A at depth 1, B at 2, C at 3)
    assert depth == 3, f"Expected depth 3, got {depth}"


def test_chain_depth_branching():
    """Test chain depth with branching structure"""
    chain = [
        {"from": "A", "to": "B"},
        {"from": "A", "to": "C"},
        {"from": "B", "to": "D"},
        {"from": "C", "to": "D"}
    ]
    depth = _compute_chain_depth(chain)
    assert depth >= 2, f"Expected depth >= 2, got {depth}"


def test_chain_depth_empty():
    """Test chain depth with empty chain"""
    assert _compute_chain_depth([]) == 0


def test_chain_depth_single():
    """Test chain depth with single link"""
    chain = [{"from": "A", "to": "B"}]
    depth = _compute_chain_depth(chain)
    # A→B means 2 levels (A at depth 1, B at 2)
    assert depth == 2, f"Expected depth 2, got {depth}"


def test_temporal_span_hours():
    """Test temporal span extraction from causal chain"""
    chain = [
        {"from": "Event at t=-5.2h", "to": "Next event"},
        {"from": "Another at t=-3h", "to": "Final"}
    ]
    span = _compute_temporal_span(chain)
    assert span == 5.2, f"Expected 5.2 hours, got {span}"


def test_temporal_span_no_temporal_info():
    """Test temporal span with no temporal markers"""
    chain = [
        {"from": "Event A", "to": "Event B"},
        {"from": "Event B", "to": "Event C"}
    ]
    span = _compute_temporal_span(chain)
    assert span == 0.0, f"Expected 0.0 hours, got {span}"


def test_temporal_span_empty():
    """Test temporal span with empty chain"""
    assert _compute_temporal_span([]) == 0.0


def test_identify_root_causes_simple():
    """Test root cause identification"""
    chain = [
        {"from": "Root1", "to": "B"},
        {"from": "Root2", "to": "C"},
        {"from": "B", "to": "D"},
        {"from": "C", "to": "D"}
    ]
    roots = _identify_root_causes(chain)
    assert "Root1" in roots
    assert "Root2" in roots
    assert "D" not in roots  # D is only a destination
    assert "B" not in roots  # B appears as destination


def test_identify_root_causes_empty():
    """Test root cause identification with empty chain"""
    roots = _identify_root_causes([])
    assert roots == []


def test_root_cause_score_observational():
    """Test root cause scoring for observational mode"""
    chain = [{"from": "Yellow light", "to": "Collision"}]
    score = _compute_root_cause_score(chain, "observational")
    assert score == 1.0  # Should return neutral score for human


def test_root_cause_score_comprehensive_with_indicators():
    """Test root cause scoring for comprehensive mode with indicators"""
    chain = [
        {"from": "Venue visit late-night", "to": "Alcohol consumption"},
        {"from": "Alcohol consumption", "to": "Sleep deprivation"},
        {"from": "Sleep deprivation", "to": "Collision"}
    ]
    score = _compute_root_cause_score(chain, "comprehensive")
    assert score > 0, f"Expected score > 0, got {score}"


def test_root_cause_score_comprehensive_no_indicators():
    """Test root cause scoring without deep indicators"""
    chain = [
        {"from": "Event A", "to": "Event B"},
        {"from": "Event B", "to": "Event C"}
    ]
    score = _compute_root_cause_score(chain, "comprehensive")
    assert score >= 0, f"Expected score >= 0, got {score}"


if __name__ == "__main__":
    # Run tests manually
    tests = [
        test_chain_depth_simple,
        test_chain_depth_branching,
        test_chain_depth_empty,
        test_chain_depth_single,
        test_temporal_span_hours,
        test_temporal_span_no_temporal_info,
        test_temporal_span_empty,
        test_identify_root_causes_simple,
        test_identify_root_causes_empty,
        test_root_cause_score_observational,
        test_root_cause_score_comprehensive_with_indicators,
        test_root_cause_score_comprehensive_no_indicators,
    ]

    print("Running tests...")
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
