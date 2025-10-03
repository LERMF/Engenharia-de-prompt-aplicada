#!/usr/bin/env python3
"""
ResearchForge v1.0 - Quick System Test
Verify all components are working correctly
"""

import sys
from researchforge_v1 import (
    ResearchForge,
    ResearchQuery,
    KERNELPlusValidator,
    CoT2Reasoner,
    format_output_markdown,
    format_output_json
)
import json


def test_imports():
    """Test 1: Verify all imports work"""
    print("✓ Test 1: All imports successful")
    return True


def test_basic_research():
    """Test 2: Run basic research query"""
    forge = ResearchForge()
    query = ResearchQuery(
        query="Test query for system validation",
        context_seed="Minimal test context",
        max_iterations=2,
        target_tcr=0.80
    )
    
    result = forge.research(query)
    
    assert result is not None
    assert result.metrics['TCR'] > 0
    assert len(result.sources) > 0
    assert result.iterations_used <= query.max_iterations
    
    print(f"✓ Test 2: Basic research completed (TCR: {result.metrics['TCR']:.3f})")
    return True


def test_kernel_validation():
    """Test 3: Test KERNEL+ validator"""
    validator = KERNELPlusValidator()
    
    test_text = "Research suggests [1] that prompt engineering improves performance."
    scores = validator.validate(test_text, {
        'relevant': True,
        'verifiable': True,
        'refined': True
    })
    
    assert len(scores) > 0
    assert all(0 <= v <= 1 for v in scores.values())
    
    print(f"✓ Test 3: KERNEL+ validation working (avg score: {sum(scores.values())/len(scores):.3f})")
    return True


def test_cot_reasoner():
    """Test 4: Test CoT2.0 reasoner"""
    reasoner = CoT2Reasoner()
    
    trace = reasoner.generate_reasoning_trace("test query", "test context")
    assert len(trace) > 0
    
    examples = reasoner.few_shot_examples()
    assert len(examples) == 2
    
    print(f"✓ Test 4: CoT2.0 reasoner working ({len(trace)} trace steps)")
    return True


def test_output_formats():
    """Test 5: Test output formatters"""
    forge = ResearchForge()
    query = ResearchQuery(
        query="Format test",
        max_iterations=1
    )
    result = forge.research(query)
    
    # Test markdown format
    md = format_output_markdown(result)
    assert len(md) > 0
    assert "# 🔬 ResearchForge v1.0" in md
    
    # Test JSON format
    json_str = format_output_json(result)
    parsed = json.loads(json_str)
    assert "metrics" in parsed
    assert "decomposed_plan" in parsed
    
    print(f"✓ Test 5: Output formatters working (MD: {len(md)} chars, JSON: {len(json_str)} chars)")
    return True


def test_knowledge_base():
    """Test 6: Verify knowledge base"""
    forge = ResearchForge()
    
    assert len(forge.knowledge_base) > 0
    assert "PromptCoT 2.0" in forge.knowledge_base
    assert "Agentic Science" in forge.knowledge_base
    
    print(f"✓ Test 6: Knowledge base loaded ({len(forge.knowledge_base)} entries)")
    return True


def test_agentic_loop():
    """Test 7: Test agentic loop phases"""
    forge = ResearchForge()
    query = ResearchQuery(query="Agentic loop test", max_iterations=1)
    
    # Test decomposition
    sub_queries = forge.decompose_query(query)
    assert len(sub_queries) == 5  # 5 phases
    
    # Test gap analysis
    gaps = forge.analyze_gaps(sub_queries, "test context")
    assert "novelty_check" in gaps
    assert "bias_detection" in gaps
    
    # Test search
    search_results = forge.simulate_search(sub_queries, gaps)
    assert len(search_results) > 0
    
    print(f"✓ Test 7: Agentic loop operational ({len(sub_queries)} phases)")
    return True


def main():
    print("=" * 70)
    print("🔬 ResearchForge v1.0 - System Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_imports,
        test_basic_research,
        test_kernel_validation,
        test_cot_reasoner,
        test_output_formats,
        test_knowledge_base,
        test_agentic_loop
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! ResearchForge v1.0 is fully operational.")
    else:
        print(f"⚠️  {failed} test(s) failed. Please check the implementation.")
        sys.exit(1)
    
    print("=" * 70)


if __name__ == "__main__":
    main()
