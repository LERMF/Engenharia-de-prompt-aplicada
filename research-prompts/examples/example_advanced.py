#!/usr/bin/env python3
"""
ResearchForge v1.0 - Advanced Example
Custom knowledge base, multiple queries, comparative analysis
"""

import sys
sys.path.insert(0, '..')

from researchforge_v1 import (
    ResearchForge,
    ResearchQuery,
    format_output_json
)
import json


def main():
    print("🔬 ResearchForge v1.0 - Advanced Example\n")
    print("=" * 60)
    
    # Initialize ResearchForge
    forge = ResearchForge()
    
    # Extend knowledge base with custom entries
    print("\n📚 Extending Knowledge Base...")
    forge.knowledge_base.update({
        "ReAct": "Reasoning + Acting; interleaved thought-action-observation loops; SOTA on ALFWorld",
        "Reflexion": "Self-reflection with episodic memory; learns from mistakes; improves over iterations",
        "Tree-of-Thoughts": "BFS/DFS exploration of reasoning paths; deliberate problem solving; 74% on Game of 24",
        "AutoGPT": "Autonomous agent with planning, tool use, and memory; continuous task execution",
        "LangChain Agents": "Modular agent framework; tool integration; ReAct-inspired reasoning"
    })
    print(f"✅ Knowledge base extended: {len(forge.knowledge_base)} entries\n")
    
    # Define multiple research queries for comparison
    queries = [
        ResearchQuery(
            query="Compare agentic reasoning frameworks for autonomous AI systems",
            context_seed="Focus on ReAct, Reflexion, and Tree-of-Thoughts performance",
            max_iterations=6,
            target_tcr=0.98
        ),
        ResearchQuery(
            query="Optimal memory architectures for LLM agents",
            context_seed="Compare episodic vs semantic memory, retrieval strategies",
            max_iterations=5,
            target_tcr=0.96
        ),
        ResearchQuery(
            query="Tool integration patterns in agentic systems",
            context_seed="API calling, function invocation, error handling",
            max_iterations=4,
            target_tcr=0.95
        )
    ]
    
    results = []
    
    # Execute each research query
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"🔍 Research Query #{i}/{len(queries)}")
        print(f"{'=' * 60}")
        print(f"\n📝 Query: {query.query}")
        print(f"🎯 Context: {query.context_seed}")
        print(f"⏳ Processing...\n")
        
        result = forge.research(query)
        results.append(result)
        
        print(f"✅ Completed in {result.iterations_used} iterations")
        print(f"📊 TCR: {result.metrics['TCR']:.3f} | Relevance: {result.metrics['relevance']:.3f}")
        print(f"💡 Insight: {result.surprise_insight[:100]}...")
    
    # Comparative analysis
    print(f"\n\n{'=' * 60}")
    print("📊 COMPARATIVE ANALYSIS")
    print(f"{'=' * 60}\n")
    
    print("| Query | TCR | Relevance | Fidelity | Iterations | Sources |")
    print("|-------|-----|-----------|----------|------------|---------|")
    
    for i, result in enumerate(results, 1):
        print(
            f"| #{i} | {result.metrics['TCR']:.3f} | "
            f"{result.metrics['relevance']:.3f} | "
            f"{result.metrics['fidelity']:.3f} | "
            f"{result.iterations_used} | "
            f"{len(result.sources)} |"
        )
    
    # Average metrics
    avg_tcr = sum(r.metrics['TCR'] for r in results) / len(results)
    avg_rel = sum(r.metrics['relevance'] for r in results) / len(results)
    avg_fid = sum(r.metrics['fidelity'] for r in results) / len(results)
    avg_iter = sum(r.iterations_used for r in results) / len(results)
    
    print(f"\n**Averages**: TCR={avg_tcr:.3f}, Relevance={avg_rel:.3f}, "
          f"Fidelity={avg_fid:.3f}, Iterations={avg_iter:.1f}")
    
    # Export combined results to JSON
    print(f"\n\n{'=' * 60}")
    print("💾 Exporting Results")
    print(f"{'=' * 60}\n")
    
    combined_output = {
        "timestamp": "2025-10-03T00:00:00Z",
        "total_queries": len(queries),
        "knowledge_base_size": len(forge.knowledge_base),
        "average_metrics": {
            "TCR": avg_tcr,
            "relevance": avg_rel,
            "fidelity": avg_fid,
            "iterations": avg_iter
        },
        "results": []
    }
    
    for i, (query, result) in enumerate(zip(queries, results), 1):
        combined_output["results"].append({
            "query_id": i,
            "query": query.query,
            "context": query.context_seed,
            "synthesized_results": result.synthesized_results,
            "surprise_insight": result.surprise_insight,
            "metrics": result.metrics,
            "sources": result.sources,
            "iterations_used": result.iterations_used
        })
    
    output_file = "advanced_research_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_output, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results exported to: {output_file}")
    print(f"📦 File size: {len(json.dumps(combined_output))} bytes")
    
    print("\n" + "=" * 60)
    print("🎉 Advanced Research Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
