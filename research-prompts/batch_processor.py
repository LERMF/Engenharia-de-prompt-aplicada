#!/usr/bin/env python3
"""
ResearchForge v1.0 - Batch Processing System
Process multiple queries in parallel with progress tracking
"""

import json
from typing import List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from researchforge_v1 import (
    ResearchForge,
    ResearchQuery,
    format_output_json
)


class BatchProcessor:
    """Batch research query processor"""
    
    def __init__(self, max_workers: int = 4):
        self.forge = ResearchForge()
        self.max_workers = max_workers
        self.results = []
        self.errors = []
    
    def process_single(self, query_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process a single query"""
        try:
            start_time = time.time()
            
            query = ResearchQuery(
                query=query_data['query'],
                context_seed=query_data.get('context', ''),
                max_iterations=query_data.get('iterations', 4),
                target_tcr=query_data.get('tcr', 0.95)
            )
            
            result = self.forge.research(query)
            
            elapsed = time.time() - start_time
            
            return {
                'index': index,
                'success': True,
                'query': query_data['query'],
                'context': query_data.get('context', ''),
                'result': {
                    'findings': result.synthesized_results.get('key_findings', []),
                    'insight': result.surprise_insight,
                    'metrics': result.metrics,
                    'sources': result.sources,
                    'iterations_used': result.iterations_used
                },
                'elapsed_seconds': round(elapsed, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'index': index,
                'success': False,
                'query': query_data.get('query', 'Unknown'),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def process_batch(self, queries: List[Dict[str, Any]], 
                     parallel: bool = True,
                     verbose: bool = True) -> Dict[str, Any]:
        """
        Process multiple queries
        
        Args:
            queries: List of query dictionaries with 'query' and optional 'context'
            parallel: If True, process in parallel
            verbose: Show progress
        """
        total = len(queries)
        start_time = time.time()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🔬 Batch Processing: {total} queries")
            print(f"{'='*70}\n")
        
        results = []
        
        if parallel:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.process_single, query, i): i
                    for i, query in enumerate(queries, 1)
                }
                
                completed = 0
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if verbose:
                        status = "✅" if result['success'] else "❌"
                        progress = (completed / total) * 100
                        print(f"{status} [{completed}/{total}] ({progress:.1f}%) - "
                              f"{result['query'][:50]}...")
        else:
            # Sequential processing
            for i, query in enumerate(queries, 1):
                result = self.process_single(query, i)
                results.append(result)
                
                if verbose:
                    status = "✅" if result['success'] else "❌"
                    progress = (i / total) * 100
                    print(f"{status} [{i}/{total}] ({progress:.1f}%) - "
                          f"{result['query'][:50]}...")
        
        # Sort by index
        results.sort(key=lambda x: x['index'])
        
        # Calculate statistics
        elapsed = time.time() - start_time
        successful = sum(1 for r in results if r['success'])
        failed = total - successful
        
        avg_tcr = sum(
            r['result']['metrics']['TCR'] 
            for r in results if r['success']
        ) / max(successful, 1)
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"✅ Batch Complete: {successful} succeeded, {failed} failed")
            print(f"⏱️  Total Time: {elapsed:.2f}s | Avg: {elapsed/total:.2f}s per query")
            print(f"📊 Average TCR: {avg_tcr:.3f}")
            print(f"{'='*70}\n")
        
        return {
            'summary': {
                'total_queries': total,
                'successful': successful,
                'failed': failed,
                'avg_tcr': avg_tcr,
                'total_time_seconds': round(elapsed, 2),
                'avg_time_per_query': round(elapsed / total, 2)
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_from_file(self, input_file: str, output_file: str = None,
                         parallel: bool = True, verbose: bool = True) -> Dict[str, Any]:
        """
        Process queries from JSON file
        
        Input format:
        {
            "queries": [
                {"query": "...", "context": "...", "iterations": 4},
                {"query": "...", "context": "..."}
            ]
        }
        """
        # Read input
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        queries = data.get('queries', [])
        if not queries:
            raise ValueError("No queries found in input file")
        
        # Process
        result = self.process_batch(queries, parallel, verbose)
        
        # Save output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if verbose:
                print(f"💾 Results saved to: {output_file}")
        
        return result
    
    def generate_report(self, batch_result: Dict[str, Any], 
                       format: str = 'markdown') -> str:
        """Generate a report from batch results"""
        
        if format == 'markdown':
            md = "# 🔬 ResearchForge Batch Processing Report\n\n"
            
            # Summary
            summary = batch_result['summary']
            md += "## 📊 Summary\n\n"
            md += f"- **Total Queries**: {summary['total_queries']}\n"
            md += f"- **Successful**: {summary['successful']}\n"
            md += f"- **Failed**: {summary['failed']}\n"
            md += f"- **Average TCR**: {summary['avg_tcr']:.3f}\n"
            md += f"- **Total Time**: {summary['total_time_seconds']}s\n"
            md += f"- **Avg Time/Query**: {summary['avg_time_per_query']}s\n\n"
            
            # Individual results
            md += "## 📝 Individual Results\n\n"
            
            for result in batch_result['results']:
                if result['success']:
                    md += f"### Query {result['index']}: {result['query']}\n\n"
                    md += f"**TCR**: {result['result']['metrics']['TCR']:.3f} | "
                    md += f"**Time**: {result['elapsed_seconds']}s\n\n"
                    
                    md += "**Key Findings**:\n"
                    for finding in result['result']['findings'][:3]:
                        md += f"- {finding}\n"
                    
                    md += f"\n**Insight**: {result['result']['insight'][:150]}...\n\n"
                else:
                    md += f"### ❌ Query {result['index']}: {result['query']}\n\n"
                    md += f"**Error**: {result['error']}\n\n"
            
            md += f"\n---\n*Generated: {batch_result['timestamp']}*\n"
            return md
        
        else:  # JSON
            return json.dumps(batch_result, indent=2, ensure_ascii=False)


def main():
    """CLI interface for batch processor"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_processor.py <input.json> [output.json]")
        print("\nInput JSON format:")
        print('''{
  "queries": [
    {"query": "Your question 1", "context": "Optional context"},
    {"query": "Your question 2", "iterations": 6}
  ]
}''')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'batch_results.json'
    
    processor = BatchProcessor(max_workers=4)
    result = processor.process_from_file(input_file, output_file, parallel=True, verbose=True)
    
    # Generate markdown report
    report_file = output_file.replace('.json', '_report.md')
    report = processor.generate_report(result, format='markdown')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Report saved to: {report_file}")


if __name__ == '__main__':
    main()
