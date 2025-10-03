# 🚀 ResearchForge v1.0 - Quick Start Guide

Get started with autonomous advanced research in 5 minutes!

## ⚡ Installation

No installation required! ResearchForge uses only Python 3.7+ standard library.

```bash
# Verify Python version
python --version  # Should be 3.7 or higher

# Navigate to research-prompts directory
cd research-prompts

# Make scripts executable (Linux/Mac)
chmod +x *.py examples/*.py
```

## 🎯 Your First Research Query

### Command Line (Easiest)

```bash
# Simple query
python cli.py "What are the best prompt engineering techniques?"

# With context
python cli.py "LLM optimization strategies" \
  --context "Focus on memory efficiency and latency"

# Save to file
python cli.py "Agentic AI systems" \
  --format markdown \
  --output my_research.md
```

### Python Script

Create `my_research.py`:

```python
from researchforge_v1 import ResearchForge, ResearchQuery

# Initialize
forge = ResearchForge()

# Create query
query = ResearchQuery(
    query="How to reduce LLM inference latency?",
    context_seed="Edge devices, resource constraints"
)

# Run research
result = forge.research(query)

# Display results
print(f"✅ TCR: {result.metrics['TCR']:.3f}")
print(f"📊 Found {len(result.sources)} sources")
print(f"💡 {result.surprise_insight}")
```

Run it:
```bash
python my_research.py
```

## 📖 Common Use Cases

### 1. Literature Review

```bash
python cli.py "Recent advances in transformer architectures" \
  --context "Post-2024, focus on efficiency improvements" \
  --iterations 6 \
  --tcr 0.98
```

### 2. Technique Comparison

```bash
python cli.py "Compare Chain-of-Thought vs Tree-of-Thoughts" \
  --context "Performance benchmarks and use cases" \
  --format both \
  --output comparison
```

### 3. System Design Research

```bash
python cli.py "Design distributed LLM inference system" \
  --context "High availability, load balancing, fault tolerance" \
  --verbose
```

### 4. Quick Facts

```bash
# Fast query with relaxed requirements
python cli.py "What is PromptCoT 2.0?" \
  --iterations 2 \
  --tcr 0.85
```

## 🔧 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--context`, `-c` | Context seed for research | "" |
| `--format`, `-f` | Output format: markdown, json, both | markdown |
| `--output`, `-o` | Output file path | stdout |
| `--iterations`, `-i` | Max research iterations | 4 |
| `--tcr`, `-t` | Target Task Completion Rate | 0.95 |
| `--verbose`, `-v` | Show progress indicators | false |

## 📊 Understanding Results

### Markdown Output Structure

```markdown
## 1️⃣ Plano Decomposto
[Shows how your query was broken down into research phases]

## 2️⃣ Resultados Sintetizados
[Key findings from knowledge base and reasoning]

## 3️⃣ Surpresa Insight
[Novel cross-domain insight generated from analysis]

## 📈 Metrics & Validation
[Quality scores: TCR, relevance, fidelity]
```

### Key Metrics Explained

- **TCR (Task Completion Rate)**: Overall quality score (target: >0.95)
- **Relevance**: Topic coherence (target: >0.90)
- **Fidelity**: Citation quality and logical reasoning
- **Iterations Used**: Number of refinement loops

## 🎓 Examples

Run the included examples to learn more:

```bash
# Basic usage
python examples/example_basic.py

# Advanced features (multi-query, custom knowledge)
python examples/example_advanced.py

# Integration patterns (API, streaming, validation)
python examples/example_integration.py
```

## 🔬 Test Your Installation

```bash
# Run system tests
python test_system.py

# Should show: "🎉 All tests passed!"
```

## 💡 Pro Tips

1. **Better Context = Better Results**: Provide specific context to guide research
   ```bash
   --context "Focus on production systems, not theoretical"
   ```

2. **Adjust Iterations for Quality**: More iterations = higher quality
   ```bash
   --iterations 6 --tcr 0.98  # High quality
   --iterations 2 --tcr 0.85  # Fast results
   ```

3. **Use JSON for Automation**: Pipe JSON output to other tools
   ```bash
   python cli.py "query" --format json | jq '.metrics.TCR'
   ```

4. **Verbose Mode for Debugging**: See what's happening
   ```bash
   python cli.py "query" --verbose
   ```

## 🐛 Troubleshooting

### Python Version Error
```bash
# Error: Python 3.6 or older
python --version  # Check version
# Solution: Upgrade to Python 3.7+
```

### Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Make sure you're in the research-prompts directory
cd research-prompts
python cli.py "query"
```

### Low TCR Scores
```bash
# TCR < 0.95 after 4 iterations
# Solution: Increase max iterations
python cli.py "query" --iterations 6
```

## 🚀 Next Steps

1. ✅ Read full documentation: [`README.md`](README.md)
2. ✅ Explore the code: [`researchforge_v1.py`](researchforge_v1.py)
3. ✅ Customize knowledge base: Add your own entries
4. ✅ Build integrations: REST API, VS Code extension

## 📞 Need Help?

- **Documentation**: [README.md](README.md)
- **Examples**: [examples/](examples/)
- **Metadata**: [metadata.json](metadata.json)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

**Happy Researching! 🔬**
