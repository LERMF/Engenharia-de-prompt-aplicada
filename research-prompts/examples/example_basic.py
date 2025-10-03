#!/usr/bin/env python3
"""
ResearchForge v1.0 - Basic Example
Simple research query with default parameters
"""

import sys
sys.path.insert(0, '..')

from researchforge_v1 import (
    ResearchForge,
    ResearchQuery,
    format_output_markdown
)


def main():
    print("🔬 ResearchForge v1.0 - Basic Example\n")
    print("=" * 60)
    
    # Initialize ResearchForge
    forge = ResearchForge()
    
    # Create a simple research query
    query = ResearchQuery(
        query="What are the most effective prompt engineering techniques for LLMs?",
        context_seed="Focus on techniques that improve reasoning and reduce hallucinations",
        max_iterations=4,
        target_tcr=0.95
    )
    
    print(f"\n📝 Research Query: {query.query}")
    print(f"🎯 Context: {query.context_seed}")
    print(f"🔄 Max Iterations: {query.max_iterations}")
    print(f"📊 Target TCR: {query.target_tcr}\n")
    print("⏳ Running research...\n")
    
    # Execute research
    result = forge.research(query)
    
    # Display results
    print("✅ Research Completed!\n")
    print("=" * 60)
    print(f"\n📈 Performance Metrics:")
    print(f"  - TCR: {result.metrics['TCR']:.3f}")
    print(f"  - Relevance: {result.metrics['relevance']:.3f}")
    print(f"  - Fidelity: {result.metrics['fidelity']:.3f}")
    print(f"  - Iterations Used: {result.iterations_used}/{query.max_iterations}")
    print(f"  - Estimated Tokens: {result.metrics['tokens_estimated']}")
    
    print(f"\n📚 Sources Referenced: {len(result.sources)}")
    for i, source in enumerate(result.sources, 1):
        print(f"  {i}. {source}")
    
    print(f"\n💡 Surprise Insight:")
    print(f"  {result.surprise_insight}\n")
    
    print("=" * 60)
    print("\n📄 Full Markdown Report:\n")
    print(format_output_markdown(result))


if __name__ == "__main__":
    main()
