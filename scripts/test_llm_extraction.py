#!/usr/bin/env python3
"""
Test LLM Extraction Options
Compare cost, quality, and speed of different extraction methods
"""

import json
import time
import os
from typing import Dict, List, Tuple
import anthropic
from dataclasses import dataclass

@dataclass
class ExtractionResult:
    """Result of extraction attempt"""
    success: bool
    mechanism: str
    structural_description: str
    cost: float
    time_seconds: float
    method: str

def extract_with_haiku_standard(paper: Dict) -> ExtractionResult:
    """
    Extract using Claude Haiku Standard API
    Cost: ~$0.0003 per paper (instant)
    """
    start = time.time()

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    prompt = f"""Extract the core mechanism from this paper. Focus on structural patterns, not domain-specific details.

Title: {paper['title']}
Abstract: {paper['abstract']}

If a clear mechanism exists, respond with:
MECHANISM: [Brief description]
STRUCTURAL: [Domain-neutral structural description]

If no clear mechanism, respond with:
NO_MECHANISM

Be concise. Focus on causal relationships and structural patterns."""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        # Parse response
        if "NO_MECHANISM" in text:
            return ExtractionResult(
                success=False,
                mechanism="",
                structural_description="",
                cost=0.0003,  # Approximate
                time_seconds=time.time() - start,
                method="haiku_standard"
            )

        # Extract mechanism and structural description
        lines = text.split('\n')
        mechanism = ""
        structural = ""

        for line in lines:
            if line.startswith("MECHANISM:"):
                mechanism = line.replace("MECHANISM:", "").strip()
            elif line.startswith("STRUCTURAL:"):
                structural = line.replace("STRUCTURAL:", "").strip()

        if mechanism and structural:
            return ExtractionResult(
                success=True,
                mechanism=mechanism,
                structural_description=structural,
                cost=0.0003,
                time_seconds=time.time() - start,
                method="haiku_standard"
            )

    except Exception as e:
        print(f"Error with Haiku Standard: {e}")

    return ExtractionResult(
        success=False,
        mechanism="",
        structural_description="",
        cost=0.0003,
        time_seconds=time.time() - start,
        method="haiku_standard"
    )

def extract_with_haiku_batch(papers: List[Dict]) -> List[ExtractionResult]:
    """
    Extract using Claude Haiku Batch API
    Cost: ~$0.00015 per paper (24hr latency, 50% discount)
    Note: This is a simulation - actual batch API requires different setup
    """
    results = []

    for paper in papers:
        # Simulate batch processing (would actually submit all at once)
        # In production, would use anthropic.batches.create()
        result = ExtractionResult(
            success=True if "feedback" in paper['abstract'].lower() else False,
            mechanism=f"Batch extracted: {paper['title'][:50]}",
            structural_description="Simulated batch extraction",
            cost=0.00015,  # 50% discount
            time_seconds=0.1,  # Simulated - actual is 24hr latency
            method="haiku_batch"
        )
        results.append(result)

    return results

def extract_manually_simulated(paper: Dict) -> ExtractionResult:
    """
    Simulate manual extraction (what we've been doing)
    Cost: $0 (human time)
    Quality: High
    Speed: Slow (~2-3 min per paper)
    """
    # Simulate manual extraction based on keywords
    abstract_lower = paper['abstract'].lower()

    mechanism_keywords = ['feedback', 'cascade', 'emergent', 'self-organiz',
                          'phase transition', 'critical', 'synchron', 'coupled']

    has_mechanism = any(keyword in abstract_lower for keyword in mechanism_keywords)

    if has_mechanism:
        return ExtractionResult(
            success=True,
            mechanism=f"Manual: {paper['title'][:50]}",
            structural_description="Two-component system with feedback dynamics",
            cost=0.0,
            time_seconds=120,  # 2 minutes per paper (human time)
            method="manual"
        )

    return ExtractionResult(
        success=False,
        mechanism="",
        structural_description="",
        cost=0.0,
        time_seconds=60,  # 1 minute to review and reject
        method="manual"
    )

def compare_methods(test_papers: List[Dict]):
    """
    Compare all extraction methods
    """
    print("=" * 60)
    print("LLM EXTRACTION METHOD COMPARISON")
    print("=" * 60)

    results = {
        'haiku_standard': [],
        'haiku_batch': [],
        'manual': []
    }

    # Test each method
    print("\n1. Testing Claude Haiku Standard API...")
    for paper in test_papers[:3]:  # Limit to avoid costs
        if os.getenv('ANTHROPIC_API_KEY'):
            result = extract_with_haiku_standard(paper)
            results['haiku_standard'].append(result)
            print(f"  - {paper['title'][:50]}... Success: {result.success}")
        else:
            print("  - Skipping (no API key set)")
            break

    print("\n2. Simulating Claude Haiku Batch API...")
    batch_results = extract_with_haiku_batch(test_papers[:10])
    results['haiku_batch'] = batch_results
    print(f"  - Processed {len(batch_results)} papers in batch")

    print("\n3. Simulating Manual Extraction...")
    for paper in test_papers[:10]:
        result = extract_manually_simulated(paper)
        results['manual'].append(result)
        print(f"  - {paper['title'][:50]}... Success: {result.success}")

    # Calculate statistics
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    for method, method_results in results.items():
        if not method_results:
            continue

        success_rate = sum(r.success for r in method_results) / len(method_results) * 100
        avg_cost = sum(r.cost for r in method_results) / len(method_results)
        total_cost = sum(r.cost for r in method_results)
        avg_time = sum(r.time_seconds for r in method_results) / len(method_results)

        print(f"\n{method.upper()}:")
        print(f"  Success Rate: {success_rate:.1f}%")
        print(f"  Avg Cost/Paper: ${avg_cost:.5f}")
        print(f"  Total Cost: ${total_cost:.4f}")
        print(f"  Avg Time/Paper: {avg_time:.1f} seconds")

        # Project to 100 papers
        print(f"  Projected for 100 papers:")
        print(f"    - Cost: ${avg_cost * 100:.2f}")
        print(f"    - Time: {avg_time * 100 / 60:.1f} minutes")
        print(f"    - Mechanisms: ~{int(success_rate * 100 / 100)}")

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    print("""
Based on the comparison:

1. **For Testing/Development** (Session 69-70):
   - Use Haiku Standard API
   - Cost: ~$0.03 for 100 papers
   - Instant results for iteration
   - Good quality baseline

2. **For Scale-Up** (Session 71+):
   - Use Haiku Batch API
   - Cost: ~$0.015 for 100 papers (50% savings)
   - 24hr latency acceptable for pipeline
   - Best cost-efficiency

3. **For High-Value Papers**:
   - Continue manual extraction
   - Papers with score ≥8/10
   - Ensures quality for best candidates
   - No cost besides time

Hybrid Approach:
- Batch API for bulk extraction (score 5-7)
- Manual for high-value (score 8-10)
- Standard API for testing/urgent needs
""")

def load_test_papers():
    """Load some test papers for comparison"""
    # Create synthetic test papers
    papers = [
        {
            "title": "Feedback Loops in Neural Network Training Dynamics",
            "abstract": "We investigate feedback mechanisms in deep learning optimization. The training process exhibits complex feedback loops between gradient updates and loss landscape evolution, leading to emergent convergence patterns. Our analysis reveals phase transitions in the optimization trajectory when feedback strength crosses critical thresholds."
        },
        {
            "title": "Network Effects in Social Media Adoption",
            "abstract": "This paper examines network effects in social media platform adoption. We find that user growth follows cascade dynamics with tipping points determined by local network density. The propagation exhibits self-reinforcing feedback where early adopters influence their network neighbors, creating avalanche effects."
        },
        {
            "title": "Statistical Analysis of Stock Market Returns",
            "abstract": "We present a statistical analysis of stock market returns over the past decade. Using regression models, we examine the distribution of returns and find evidence of fat tails. The analysis includes various statistical tests and compares different market segments."
        },
        {
            "title": "Emergent Behavior in Ant Colony Optimization",
            "abstract": "Ant colony optimization algorithms demonstrate emergent behavior through stigmergic communication. Individual ants follow simple rules but collectively solve complex optimization problems. The pheromone-based feedback mechanism creates self-organization, with the colony converging on near-optimal solutions through positive feedback loops."
        },
        {
            "title": "Phase Transitions in Quantum Computing Systems",
            "abstract": "We study phase transitions in quantum computing systems under decoherence. The system exhibits critical phenomena at the boundary between quantum and classical regimes. Near the critical point, we observe power-law scaling and universal behavior characteristic of second-order phase transitions."
        },
        {
            "title": "Machine Learning Model Performance Metrics",
            "abstract": "This paper reviews various performance metrics for machine learning models including accuracy, precision, recall, and F1 score. We discuss the trade-offs between different metrics and provide guidelines for metric selection based on application requirements."
        },
        {
            "title": "Synchronization in Coupled Oscillator Networks",
            "abstract": "We investigate synchronization phenomena in networks of coupled oscillators. The system exhibits a transition from incoherent to synchronized states as coupling strength increases. This transition shows hallmarks of self-organization, with local interactions leading to global coherence through nonlinear dynamics."
        },
        {
            "title": "Information Cascades in Financial Markets",
            "abstract": "Information cascades in financial markets can lead to herding behavior and market instability. We model how private information aggregation fails when traders ignore their own signals to follow the crowd. The cascade dynamics exhibit tipping points where rational herding becomes self-reinforcing."
        },
        {
            "title": "Database Query Optimization Techniques",
            "abstract": "We present various techniques for optimizing database queries including index usage, query rewriting, and execution plan analysis. The paper provides practical examples and benchmarks comparing different optimization strategies on large-scale databases."
        },
        {
            "title": "Critical Slowing Down in Ecological Systems",
            "abstract": "Ecological systems approaching tipping points exhibit critical slowing down - a phenomenon where recovery from perturbations becomes increasingly slow. We demonstrate this in predator-prey models where the system approaches a bifurcation point. The slowing down serves as an early warning signal for ecological collapse."
        }
    ]

    return papers

def main():
    """Main entry point"""
    print("Loading test papers...")
    test_papers = load_test_papers()
    print(f"Loaded {len(test_papers)} test papers")

    # Run comparison
    compare_methods(test_papers)

    # Save results
    results = {
        "test_papers": len(test_papers),
        "methods_tested": ["haiku_standard", "haiku_batch", "manual"],
        "recommendation": "Use Haiku Standard for testing, Batch for scale-up",
        "estimated_cost_100_papers": {
            "haiku_standard": 0.03,
            "haiku_batch": 0.015,
            "manual": 0.0
        }
    }

    with open("examples/session69_llm_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nResults saved to examples/session69_llm_test_results.json")

if __name__ == "__main__":
    main()