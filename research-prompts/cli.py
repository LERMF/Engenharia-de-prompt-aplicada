#!/usr/bin/env python3
"""
ResearchForge v1.0 - Command Line Interface
Run research queries from terminal with various output formats
"""

import argparse
import sys
from pathlib import Path
from researchforge_v1 import (
    ResearchForge,
    ResearchQuery,
    format_output_markdown,
    format_output_json
)


def main():
    parser = argparse.ArgumentParser(
        description="ResearchForge v1.0 - Autonomous Advanced Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic research query
  python cli.py "prompt engineering techniques 2025"
  
  # With context seed
  python cli.py "quantum computing" --context "Focus on hardware and algorithms"
  
  # JSON output to file
  python cli.py "AI safety" --format json --output results.json
  
  # Custom parameters
  python cli.py "LLM optimization" --iterations 6 --tcr 0.98
        """
    )
    
    parser.add_argument(
        "query",
        type=str,
        help="Research query to investigate"
    )
    
    parser.add_argument(
        "-c", "--context",
        type=str,
        default="",
        help="Context seed for research (optional)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "-i", "--iterations",
        type=int,
        default=4,
        help="Maximum research iterations (default: 4)"
    )
    
    parser.add_argument(
        "-t", "--tcr",
        type=float,
        default=0.95,
        help="Target Task Completion Rate (default: 0.95)"
    )
    
    parser.add_argument(
        "-r", "--relevance",
        type=float,
        default=0.90,
        help="Target relevance threshold (default: 0.90)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2500,
        help="Maximum output tokens (default: 2500)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with progress indicators"
    )
    
    args = parser.parse_args()
    
    # Initialize ResearchForge
    forge = ResearchForge()
    
    # Create research query
    query = ResearchQuery(
        query=args.query,
        context_seed=args.context,
        max_tokens=args.max_tokens,
        max_iterations=args.iterations,
        target_tcr=args.tcr,
        target_relevance=args.relevance
    )
    
    # Execute research
    if args.verbose:
        print("🔬 ResearchForge v1.0 - Initializing...", file=sys.stderr)
        print(f"📝 Query: {args.query}", file=sys.stderr)
        print(f"🎯 Target TCR: {args.tcr}", file=sys.stderr)
        print(f"🔄 Max Iterations: {args.iterations}\n", file=sys.stderr)
    
    result = forge.research(query)
    
    if args.verbose:
        print(f"✅ Research completed in {result.iterations_used} iterations", file=sys.stderr)
        print(f"📊 Final TCR: {result.metrics['TCR']:.3f}\n", file=sys.stderr)
    
    # Format output
    outputs = {}
    
    if args.format in ["markdown", "both"]:
        outputs["markdown"] = format_output_markdown(result)
    
    if args.format in ["json", "both"]:
        outputs["json"] = format_output_json(result)
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        
        if args.format == "both":
            # Write both formats with different extensions
            md_path = output_path.with_suffix('.md')
            json_path = output_path.with_suffix('.json')
            
            md_path.write_text(outputs["markdown"], encoding='utf-8')
            json_path.write_text(outputs["json"], encoding='utf-8')
            
            print(f"✅ Output written to:\n  - {md_path}\n  - {json_path}")
        else:
            output_path.write_text(outputs[args.format], encoding='utf-8')
            print(f"✅ Output written to: {output_path}")
    else:
        # Print to stdout
        if args.format == "both":
            print("=== MARKDOWN OUTPUT ===\n")
            print(outputs["markdown"])
            print("\n=== JSON OUTPUT ===\n")
            print(outputs["json"])
        else:
            print(outputs[args.format])


if __name__ == "__main__":
    main()
