#!/usr/bin/env python3
"""
ResearchForge v1.0 - Integration Example
Shows how to integrate ResearchForge with existing systems
"""

import sys
sys.path.insert(0, '..')

from researchforge_v1 import ResearchForge, ResearchQuery
from typing import Dict, Any
import json


class ResearchAPI:
    """Wrapper class for easy integration"""
    
    def __init__(self):
        self.forge = ResearchForge()
        self.history = []
    
    def query(self, question: str, context: str = "", **kwargs) -> Dict[str, Any]:
        """Simple query interface"""
        query = ResearchQuery(
            query=question,
            context_seed=context,
            **kwargs
        )
        
        result = self.forge.research(query)
        
        # Store in history
        self.history.append({
            "query": question,
            "context": context,
            "tcr": result.metrics['TCR'],
            "iterations": result.iterations_used
        })
        
        return {
            "success": True,
            "findings": result.synthesized_results.get("key_findings", []),
            "insight": result.surprise_insight,
            "metrics": result.metrics,
            "sources": result.sources
        }
    
    def batch_query(self, questions: list) -> list:
        """Process multiple queries"""
        return [self.query(q) for q in questions]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.history:
            return {"queries": 0}
        
        return {
            "total_queries": len(self.history),
            "avg_tcr": sum(h['tcr'] for h in self.history) / len(self.history),
            "avg_iterations": sum(h['iterations'] for h in self.history) / len(self.history),
            "history": self.history[-5:]  # Last 5 queries
        }


def demo_simple_integration():
    """Demo: Simple API usage"""
    print("🔹 Demo 1: Simple Integration\n")
    
    api = ResearchAPI()
    
    result = api.query(
        "Best practices for prompt engineering in production systems",
        context="Focus on error handling, fallbacks, and monitoring"
    )
    
    print(f"✅ Success: {result['success']}")
    print(f"📊 TCR: {result['metrics']['TCR']:.3f}")
    print(f"💡 Insight: {result['insight'][:80]}...")
    print(f"📚 Findings: {len(result['findings'])} key points\n")


def demo_batch_processing():
    """Demo: Batch query processing"""
    print("🔹 Demo 2: Batch Processing\n")
    
    api = ResearchAPI()
    
    questions = [
        "How to reduce LLM inference latency?",
        "Techniques for improving LLM accuracy?",
        "Memory optimization strategies for LLMs?"
    ]
    
    results = api.batch_query(questions)
    
    print(f"✅ Processed {len(results)} queries")
    for i, result in enumerate(results, 1):
        print(f"  {i}. TCR={result['metrics']['TCR']:.3f}, "
              f"Sources={len(result['sources'])}")
    
    stats = api.get_stats()
    print(f"\n📊 Average TCR: {stats['avg_tcr']:.3f}")
    print(f"🔄 Average Iterations: {stats['avg_iterations']:.1f}\n")


def demo_streaming_integration():
    """Demo: Simulated streaming for web APIs"""
    print("🔹 Demo 3: Streaming Simulation\n")
    
    forge = ResearchForge()
    query = ResearchQuery(
        query="Real-time AI inference optimization techniques",
        context_seed="Edge devices, low-latency requirements"
    )
    
    # Simulate streaming by yielding progress
    def stream_research():
        # Decompose
        yield {"stage": "decompose", "progress": 20}
        sub_queries = forge.decompose_query(query)
        
        # Analyze
        yield {"stage": "analyze", "progress": 40}
        gaps = forge.analyze_gaps(sub_queries, query.context_seed)
        
        # Search
        yield {"stage": "search", "progress": 60}
        search_results = forge.simulate_search(sub_queries, gaps)
        
        # Execute
        yield {"stage": "execute", "progress": 80}
        execution_log = forge.execute_chain(query, sub_queries, search_results)
        
        # Synthesize
        yield {"stage": "synthesize", "progress": 90}
        synthesized, sources = forge.synthesize_results(execution_log, query)
        
        # Validate
        yield {"stage": "validate", "progress": 100}
        metrics = forge.validate_output(synthesized, query)
        
        yield {
            "stage": "complete",
            "progress": 100,
            "tcr": metrics['TCR'],
            "sources": len(sources)
        }
    
    # Consume stream
    for update in stream_research():
        stage = update.get('stage', 'unknown')
        progress = update.get('progress', 0)
        print(f"  [{stage.upper():12s}] {'█' * (progress // 5)}{' ' * (20 - progress // 5)} {progress}%")
    
    print()


def demo_custom_validation():
    """Demo: Custom validation rules"""
    print("🔹 Demo 4: Custom Validation\n")
    
    from researchforge_v1 import KERNELPlusValidator
    
    validator = KERNELPlusValidator()
    
    test_text = """
    Research suggests that Chain-of-Thought prompting [1] improves reasoning by 15-30%.
    Evidence indicates that few-shot examples (2-5) yield optimal results.
    Therefore, combining CoT with few-shot may provide synergistic benefits.
    
    [1] Wei et al., 2022, arXiv:2201.11903
    """
    
    scores = validator.validate(test_text, {
        'relevant': True,
        'verifiable': True,
        'refined': True,
        'logical': True
    })
    
    print("📊 KERNEL+ Validation Scores:")
    for criterion, score in scores.items():
        bar = '█' * int(score * 20)
        print(f"  {criterion:12s} [{bar:20s}] {score:.3f}")
    
    avg_score = sum(scores.values()) / len(scores)
    print(f"\n✅ Average Score: {avg_score:.3f}\n")


def main():
    print("=" * 70)
    print("🔬 ResearchForge v1.0 - Integration Examples")
    print("=" * 70)
    print()
    
    demo_simple_integration()
    demo_batch_processing()
    demo_streaming_integration()
    demo_custom_validation()
    
    print("=" * 70)
    print("✅ All integration demos completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
