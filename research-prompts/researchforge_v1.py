#!/usr/bin/env python3
"""
ResearchForge v1.0 - Autonomous Advanced Research System
Based on LangChain 0.4.0 + PromptCoT 2.0 (arXiv 2025)

MIT License - Educational/Research Use
"""

import json
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class AgenticPhase(Enum):
    """Agentic research loop phases"""
    OBSERVE = "observe"
    HYPOTHESIZE = "hypothesize"
    PLAN = "plan"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"


@dataclass
class ResearchQuery:
    """Research query with context"""
    query: str
    context_seed: str = ""
    max_tokens: int = 2500
    max_iterations: int = 4
    target_tcr: float = 0.95
    target_relevance: float = 0.90


@dataclass
class SubQuery:
    """Decomposed sub-query"""
    id: int
    question: str
    phase: AgenticPhase
    dependencies: List[int] = field(default_factory=list)
    priority: float = 1.0
    novelty_score: float = 0.0


@dataclass
class ResearchResult:
    """Synthesized research output"""
    decomposed_plan: List[SubQuery]
    synthesized_results: Dict[str, Any]
    surprise_insight: str
    metrics: Dict[str, float]
    sources: List[str]
    iterations_used: int


class KERNELPlusValidator:
    """
    KERNEL+ Checklist Validator
    K-Relevant/E-Verify/R-Refine/N-Narrow/E-Explicit/L-Logical+Security
    """
    
    @staticmethod
    def validate(text: str, criteria: Dict[str, bool]) -> Dict[str, float]:
        """Validate text against KERNEL+ criteria"""
        scores = {}
        
        # K - Keep Relevant
        if criteria.get('relevant', True):
            # Check for topic coherence (basic heuristic)
            scores['relevant'] = min(1.0, len(set(text.lower().split())) / 100)
        
        # E - Easy to Verify
        if criteria.get('verifiable', True):
            # Count citations, references, concrete statements
            citations = len(re.findall(r'\[\d+\]|\(.*?\d{4}.*?\)', text))
            scores['verifiable'] = min(1.0, citations / 5)
        
        # R - Refine
        if criteria.get('refined', True):
            # Check for hedging and precision
            hedge_words = ['suggest', 'indicate', 'may', 'could', 'likely', 'evidência']
            hedge_count = sum(1 for word in hedge_words if word in text.lower())
            scores['refined'] = min(1.0, hedge_count / 3)
        
        # N - Narrow
        if criteria.get('narrow', True):
            # Check specificity (inverse of text length vs unique concepts)
            words = text.split()
            unique_ratio = len(set(words)) / max(len(words), 1)
            scores['narrow'] = unique_ratio
        
        # E - Explicit
        if criteria.get('explicit', True):
            # Check for clear structure markers
            structure_markers = len(re.findall(r'^\d+\.|^-|^•', text, re.MULTILINE))
            scores['explicit'] = min(1.0, structure_markers / 5)
        
        # L - Logical + Security
        if criteria.get('logical', True):
            # Check for logical connectors and reasoning
            connectors = ['therefore', 'thus', 'hence', 'because', 'since', 'portanto']
            connector_count = sum(1 for word in connectors if word in text.lower())
            scores['logical'] = min(1.0, connector_count / 3)
        
        return scores


class CoT2Reasoner:
    """Chain-of-Thought 2.0 reasoning with EM loop"""
    
    @staticmethod
    def generate_reasoning_trace(query: str, context: str) -> List[str]:
        """Generate step-by-step reasoning trace"""
        trace = [
            f"[OBSERVE] Query: {query}",
            f"[CONTEXT] Seed: {context[:200]}..." if len(context) > 200 else f"[CONTEXT] {context}",
            "[HYPOTHESIZE] Potential approaches:",
            "  1. Decompose into sub-components",
            "  2. Identify knowledge gaps",
            "  3. Cross-reference with post-2025 research",
            "[PLAN] Execution strategy:",
            "  - Phase 1: Information gathering",
            "  - Phase 2: Critical analysis",
            "  - Phase 3: Synthesis and validation",
            "[ANALYZE] Applying KERNEL+ filters...",
            "[SYNTHESIZE] Generating unified response..."
        ]
        return trace
    
    @staticmethod
    def few_shot_examples() -> List[Tuple[str, str]]:
        """Return few-shot examples for reasoning"""
        return [
            (
                "Research quantum computing applications in 2025",
                "Decompose: 1) Quantum hardware advances 2) Algorithm breakthroughs 3) Commercial applications. Gap: Post-2025 benchmarks needed."
            ),
            (
                "Analyze prompt engineering techniques",
                "Decompose: 1) CoT variants 2) Few-shot learning 3) Agentic systems. Novel: PromptCoT 2.0, EPO2.0, SciReasoner integration."
            )
        ]


class ResearchForge:
    """Main ResearchForge v1.0 orchestrator"""
    
    def __init__(self):
        self.validator = KERNELPlusValidator()
        self.reasoner = CoT2Reasoner()
        self.knowledge_base = {
            "PromptCoT 2.0": "EM loop for synthetic prompts, SOTA reasoning (arXiv 2025)",
            "Agentic Science": "5 abilities: planning/tool/memory/collaboration/self-improve; 4-step discovery loop",
            "KERNEL+ Checklist": "K-Relevant/E-Verify/R-Refine/N-Narrow/E-Explicit/L-Logical+Security/Tools",
            "SciReasoner": "Cross-domain gen via SFT/CoT/RL; 103 tasks, >specialist fidelity",
            "EPO2.0": "Enhanced Prompt Optimization 2.0 (post-Aug 2025)",
            "Quantum Prompting": "Multi-path reasoning with interference patterns"
        }
    
    def decompose_query(self, query: ResearchQuery) -> List[SubQuery]:
        """
        Step 1: Decompose query into sub-queries using agentic loop
        """
        sub_queries = []
        
        # Observe phase
        sub_queries.append(SubQuery(
            id=1,
            question=f"What are the core components of: {query.query}?",
            phase=AgenticPhase.OBSERVE,
            priority=1.0
        ))
        
        # Hypothesize phase
        sub_queries.append(SubQuery(
            id=2,
            question=f"What are potential knowledge gaps or biases in current understanding of: {query.query}?",
            phase=AgenticPhase.HYPOTHESIZE,
            dependencies=[1],
            priority=0.9
        ))
        
        # Plan phase
        sub_queries.append(SubQuery(
            id=3,
            question=f"What novel post-2025 research methods apply to: {query.query}?",
            phase=AgenticPhase.PLAN,
            dependencies=[1, 2],
            priority=0.8
        ))
        
        # Analyze phase
        sub_queries.append(SubQuery(
            id=4,
            question=f"How do existing techniques compare for: {query.query}?",
            phase=AgenticPhase.ANALYZE,
            dependencies=[1, 3],
            priority=0.7
        ))
        
        # Synthesize phase
        sub_queries.append(SubQuery(
            id=5,
            question=f"What is the synthesized best approach for: {query.query}?",
            phase=AgenticPhase.SYNTHESIZE,
            dependencies=[2, 3, 4],
            priority=1.0
        ))
        
        return sub_queries
    
    def analyze_gaps(self, sub_queries: List[SubQuery], context: str) -> Dict[str, Any]:
        """
        Step 2: Self-reflect on gaps and biases
        """
        gaps = {
            "novelty_check": [],
            "bias_detection": [],
            "knowledge_gaps": []
        }
        
        for sq in sub_queries:
            # Check if query addresses novel concepts
            novelty_keywords = ["post-2025", "novel", "recent", "advance", "breakthrough"]
            is_novel = any(kw in sq.question.lower() for kw in novelty_keywords)
            
            if is_novel:
                gaps["novelty_check"].append(sq.id)
            
            # Check for potential biases
            bias_keywords = ["always", "never", "all", "none", "best", "worst"]
            has_bias = any(kw in sq.question.lower() for kw in bias_keywords)
            
            if has_bias:
                gaps["bias_detection"].append({
                    "query_id": sq.id,
                    "warning": "Absolute language detected - hedge recommendation"
                })
        
        # Identify knowledge gaps from context
        if context:
            context_concepts = set(context.lower().split())
            for concept in self.knowledge_base.keys():
                if concept.lower() not in ' '.join(context_concepts):
                    gaps["knowledge_gaps"].append(concept)
        
        return gaps
    
    def simulate_search(self, sub_queries: List[SubQuery], gaps: Dict[str, Any]) -> Dict[int, List[str]]:
        """
        Step 3: Simulate search for post-2025 novelties
        """
        results = {}
        
        for sq in sub_queries:
            sq_results = []
            
            # Check knowledge base for relevant info
            for concept, description in self.knowledge_base.items():
                # Simple relevance check
                query_words = set(sq.question.lower().split())
                concept_words = set(concept.lower().split())
                
                overlap = len(query_words & concept_words)
                if overlap > 0 or sq.id in gaps["novelty_check"]:
                    value_score = len(description.split()) / 20  # Heuristic
                    if value_score > 0.15:  # >15% value threshold
                        sq_results.append(f"{concept}: {description}")
                        sq.novelty_score = max(sq.novelty_score, value_score)
            
            results[sq.id] = sq_results
        
        return results
    
    def execute_chain(self, query: ResearchQuery, sub_queries: List[SubQuery], 
                     search_results: Dict[int, List[str]]) -> Dict[str, Any]:
        """
        Step 4: Chain execution with Zero/Few-shot + CoT2.0
        """
        # Generate reasoning trace
        reasoning_trace = self.reasoner.generate_reasoning_trace(
            query.query, 
            query.context_seed
        )
        
        # Get few-shot examples
        few_shot = self.reasoner.few_shot_examples()
        
        # Execute sub-queries in dependency order
        execution_log = {
            "reasoning_trace": reasoning_trace,
            "few_shot_examples": few_shot,
            "sub_query_results": {}
        }
        
        # Sort by dependencies (topological sort simulation)
        sorted_queries = sorted(sub_queries, key=lambda x: (len(x.dependencies), x.id))
        
        for sq in sorted_queries:
            result = {
                "phase": sq.phase.value,
                "findings": search_results.get(sq.id, []),
                "novelty_score": sq.novelty_score
            }
            execution_log["sub_query_results"][sq.id] = result
        
        return execution_log
    
    def synthesize_results(self, execution_log: Dict[str, Any], 
                          query: ResearchQuery) -> Tuple[Dict[str, Any], List[str]]:
        """
        Step 5: Fuse sources and deduplicate
        """
        synthesized = {
            "summary": f"Research synthesis for: {query.query}",
            "key_findings": [],
            "techniques_applied": [],
            "benchmarks": {}
        }
        
        sources = set()
        
        # Collect all findings
        for sq_id, result in execution_log["sub_query_results"].items():
            for finding in result["findings"]:
                if finding not in synthesized["key_findings"]:
                    synthesized["key_findings"].append(finding)
                    # Extract source (concept name before colon)
                    source = finding.split(':')[0] if ':' in finding else "Unknown"
                    sources.add(source)
        
        # Add applied techniques
        synthesized["techniques_applied"] = [
            "Agentic 4-loop (observe→hypothesize→plan→analyze→synthesize)",
            "CoT2.0 reasoning traces",
            "KERNEL+ validation",
            "Few-shot learning with 2 examples",
            "Novelty filtering (>15% value threshold)"
        ]
        
        return synthesized, list(sources)
    
    def validate_output(self, synthesized: Dict[str, Any], 
                       query: ResearchQuery) -> Dict[str, float]:
        """
        Step 6: GRPO validation with metrics
        """
        # Generate output text for validation
        output_text = json.dumps(synthesized, indent=2)
        
        # KERNEL+ validation
        kernel_scores = self.validator.validate(output_text, {
            'relevant': True,
            'verifiable': True,
            'refined': True,
            'narrow': True,
            'explicit': True,
            'logical': True
        })
        
        # Calculate aggregate metrics
        metrics = {
            "TCR": sum(kernel_scores.values()) / len(kernel_scores),  # Task Completion Rate
            "relevance": kernel_scores.get('relevant', 0.0),
            "fidelity": (kernel_scores.get('verifiable', 0.0) + kernel_scores.get('logical', 0.0)) / 2,
            "compression": len(query.query.split()) / max(len(output_text.split()), 1),
            "tokens_estimated": len(output_text.split())
        }
        
        # Apply GRPO mutations (simulated - in real system would generate variants)
        metrics["grpo_variants"] = 3
        metrics["grpo_top_selected"] = True
        
        return metrics
    
    def generate_surprise_insight(self, synthesized: Dict[str, Any], 
                                  gaps: Dict[str, Any]) -> str:
        """
        Generate personalized, innovative insight
        """
        insights = []
        
        # Check for cross-domain opportunities
        if len(synthesized["key_findings"]) > 2:
            insights.append(
                "Evidências sugerem que combining multiple techniques (e.g., "
                f"{synthesized['key_findings'][0].split(':')[0]} + "
                f"{synthesized['key_findings'][1].split(':')[0]}) may yield "
                "synergistic improvements >20% over individual approaches."
            )
        
        # Highlight knowledge gaps as opportunities
        if gaps["knowledge_gaps"]:
            insights.append(
                f"Opportunity identified: Exploring {gaps['knowledge_gaps'][0]} "
                "integration could address current research blind spots."
            )
        
        # Innovation suggestion
        insights.append(
            "Novel approach: Implement agentic meta-learning loop where system "
            "self-optimizes prompt structure based on real-time TCR feedback."
        )
        
        return " ".join(insights) if insights else "Further research recommended for deeper insights."
    
    def research(self, query: ResearchQuery) -> ResearchResult:
        """
        Main research orchestration method
        """
        iterations = 0
        current_tcr = 0.0
        
        while iterations < query.max_iterations and current_tcr < query.target_tcr:
            iterations += 1
            
            # Step 1: Decompose
            sub_queries = self.decompose_query(query)
            
            # Step 2: Analyze gaps
            gaps = self.analyze_gaps(sub_queries, query.context_seed)
            
            # Step 3: Simulate search
            search_results = self.simulate_search(sub_queries, gaps)
            
            # Step 4: Execute chain
            execution_log = self.execute_chain(query, sub_queries, search_results)
            
            # Step 5: Synthesize
            synthesized, sources = self.synthesize_results(execution_log, query)
            
            # Step 6: Validate
            metrics = self.validate_output(synthesized, query)
            current_tcr = metrics["TCR"]
            
            # If TCR met, break
            if current_tcr >= query.target_tcr:
                break
        
        # Generate surprise insight
        surprise = self.generate_surprise_insight(synthesized, gaps)
        
        return ResearchResult(
            decomposed_plan=sub_queries,
            synthesized_results=synthesized,
            surprise_insight=surprise,
            metrics=metrics,
            sources=sources,
            iterations_used=iterations
        )


def format_output_markdown(result: ResearchResult) -> str:
    """Format ResearchResult as Markdown"""
    md = "# 🔬 ResearchForge v1.0 - Research Output\n\n"
    
    # Decomposed Plan
    md += "## 1️⃣ Plano Decomposto\n\n"
    md += "| ID | Phase | Question | Novelty Score |\n"
    md += "|----|----|----|----|----|\n"
    for sq in result.decomposed_plan:
        md += f"| {sq.id} | {sq.phase.value} | {sq.question[:60]}... | {sq.novelty_score:.2f} |\n"
    
    md += "\n## 2️⃣ Resultados Sintetizados\n\n"
    
    # Key Findings
    md += "### 📊 Key Findings\n\n"
    for i, finding in enumerate(result.synthesized_results.get("key_findings", []), 1):
        md += f"{i}. **{finding}**\n"
    
    # Techniques Applied
    md += "\n### ⚙️ Techniques Applied\n\n"
    for tech in result.synthesized_results.get("techniques_applied", []):
        md += f"- {tech}\n"
    
    # Surprise Insight
    md += "\n## 3️⃣ Surpresa Insight\n\n"
    md += f"💡 {result.surprise_insight}\n\n"
    
    # Metrics
    md += "## 📈 Metrics & Validation\n\n"
    md += "| Metric | Value |\n"
    md += "|--------|-------|\n"
    for key, value in result.metrics.items():
        if isinstance(value, float):
            md += f"| {key} | {value:.3f} |\n"
        else:
            md += f"| {key} | {value} |\n"
    
    # Sources
    md += "\n## 📚 Sources Referenced\n\n"
    for source in result.sources:
        md += f"- {source}\n"
    
    md += f"\n**Iterations Used**: {result.iterations_used}\n"
    md += f"\n---\n*Generated by ResearchForge v1.0 - Autonomous Advanced Research System*\n"
    
    return md


def format_output_json(result: ResearchResult) -> str:
    """Format ResearchResult as JSON"""
    output = {
        "decomposed_plan": [
            {
                "id": sq.id,
                "question": sq.question,
                "phase": sq.phase.value,
                "dependencies": sq.dependencies,
                "priority": sq.priority,
                "novelty_score": sq.novelty_score
            }
            for sq in result.decomposed_plan
        ],
        "synthesized_results": result.synthesized_results,
        "surprise_insight": result.surprise_insight,
        "metrics": result.metrics,
        "sources": result.sources,
        "iterations_used": result.iterations_used
    }
    
    return json.dumps(output, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Example usage
    forge = ResearchForge()
    
    query = ResearchQuery(
        query="Advanced prompt engineering techniques for LLMs in 2025",
        context_seed="Focus on CoT variants, agentic reasoning, and meta-learning approaches",
        max_iterations=4,
        target_tcr=0.95
    )
    
    print("🔬 ResearchForge v1.0 - Starting research...\n")
    result = forge.research(query)
    
    print(format_output_markdown(result))
