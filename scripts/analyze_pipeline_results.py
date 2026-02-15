#!/usr/bin/env python3
"""
Analyze Pipeline Results for Session 69
Calculate detailed metrics and success rates
"""

import json
import os
from typing import Dict, Any

def load_metrics() -> Dict[str, Any]:
    """Load pipeline metrics from JSON file"""
    with open('pipeline_metrics.json', 'r') as f:
        return json.load(f)

def load_checkpoint() -> Dict[str, Any]:
    """Load checkpoint data if available"""
    if os.path.exists('pipeline_checkpoint.json'):
        with open('pipeline_checkpoint.json', 'r') as f:
            return json.load(f)
    return {}

def analyze_results():
    """Analyze pipeline results and calculate success rates"""
    metrics = load_metrics()
    checkpoint = load_checkpoint()

    print("=" * 60)
    print("PIPELINE RESULTS ANALYSIS - Session 69")
    print("=" * 60)

    # Overall Performance
    print("\n### OVERALL PERFORMANCE ###")
    print(f"Total Papers Fetched: {metrics['papers_fetched']}")
    print(f"Total Papers Scored: {metrics['papers_scored']}")
    print(f"High-Value Papers (≥5/10): {metrics['high_value_papers']}")
    print(f"Mechanisms Extracted: {metrics['mechanisms_extracted']}")
    print(f"Embeddings Generated: {metrics['embeddings_generated']}")
    print(f"Candidates Generated: {metrics['candidates_generated']}")
    print(f"Total Time: {metrics['time_elapsed']:.1f} seconds")
    print(f"Total Cost: ${metrics['total_cost']:.4f}")

    # Success Rates
    print("\n### SUCCESS RATES ###")

    # Fetch success rate
    if metrics['papers_fetched'] > 0:
        fetch_rate = metrics['papers_scored'] / metrics['papers_fetched'] * 100
        print(f"Fetch Success Rate: {fetch_rate:.1f}%")

    # Quality rate
    if metrics['papers_scored'] > 0:
        quality_rate = metrics['high_value_papers'] / metrics['papers_scored'] * 100
        print(f"High-Value Rate: {quality_rate:.1f}%")

    # Extraction rate
    if metrics['high_value_papers'] > 0:
        extraction_rate = metrics['mechanisms_extracted'] / metrics['high_value_papers'] * 100
        print(f"Extraction Rate: {extraction_rate:.1f}%")

    # Embedding success
    if metrics['mechanisms_extracted'] > 0:
        embedding_rate = metrics['embeddings_generated'] / metrics['mechanisms_extracted'] * 100
        print(f"Embedding Success: {embedding_rate:.1f}%")

    # Efficiency Metrics
    print("\n### EFFICIENCY METRICS ###")

    # Papers per minute
    if metrics['time_elapsed'] > 0:
        papers_per_minute = metrics['papers_fetched'] / (metrics['time_elapsed'] / 60)
        print(f"Papers per Minute: {papers_per_minute:.1f}")

    # Cost per paper
    if metrics['papers_fetched'] > 0:
        cost_per_paper = metrics['total_cost'] / metrics['papers_fetched']
        print(f"Cost per Paper: ${cost_per_paper:.5f}")

    # Cost per mechanism
    if metrics['mechanisms_extracted'] > 0:
        cost_per_mechanism = metrics['total_cost'] / metrics['mechanisms_extracted']
        print(f"Cost per Mechanism: ${cost_per_mechanism:.4f}")

    # Time per phase
    print("\n### PHASE BREAKDOWN (Estimated) ###")
    fetch_time = metrics['time_elapsed'] * 0.6  # ~60% for fetching
    score_time = metrics['time_elapsed'] * 0.02  # ~2% for scoring
    extract_time = metrics['time_elapsed'] * 0.05  # ~5% for extraction
    embed_time = metrics['time_elapsed'] * 0.3  # ~30% for embedding
    store_time = metrics['time_elapsed'] * 0.03  # ~3% for storage

    print(f"Fetch Phase: ~{fetch_time:.1f}s ({fetch_time/metrics['time_elapsed']*100:.0f}%)")
    print(f"Score Phase: ~{score_time:.1f}s ({score_time/metrics['time_elapsed']*100:.0f}%)")
    print(f"Extract Phase: ~{extract_time:.1f}s ({extract_time/metrics['time_elapsed']*100:.0f}%)")
    print(f"Embed Phase: ~{embed_time:.1f}s ({embed_time/metrics['time_elapsed']*100:.0f}%)")
    print(f"Store Phase: ~{store_time:.1f}s ({store_time/metrics['time_elapsed']*100:.0f}%)")

    # Projections
    print("\n### PROJECTIONS FOR SCALE-UP ###")

    # For 1,000 papers
    scale_factor_1k = 1000 / metrics['papers_fetched']
    print(f"\nFor 1,000 papers:")
    print(f"  Expected Time: {metrics['time_elapsed'] * scale_factor_1k / 60:.1f} minutes")
    print(f"  Expected Cost: ${metrics['total_cost'] * scale_factor_1k:.2f}")
    print(f"  Expected Mechanisms: ~{int(metrics['mechanisms_extracted'] * scale_factor_1k)}")
    print(f"  Expected High-Value: ~{int(metrics['high_value_papers'] * scale_factor_1k)}")

    # For 10,000 papers
    scale_factor_10k = 10000 / metrics['papers_fetched']
    print(f"\nFor 10,000 papers:")
    print(f"  Expected Time: {metrics['time_elapsed'] * scale_factor_10k / 3600:.1f} hours")
    print(f"  Expected Cost: ${metrics['total_cost'] * scale_factor_10k:.2f}")
    print(f"  Expected Mechanisms: ~{int(metrics['mechanisms_extracted'] * scale_factor_10k)}")
    print(f"  Expected High-Value: ~{int(metrics['high_value_papers'] * scale_factor_10k)}")

    # Quality Assessment
    print("\n### QUALITY ASSESSMENT ###")

    # Based on historical data
    print("Historical Benchmarks:")
    print("  Manual extraction: 60-90% hit rate")
    print("  Simulated extraction: 10-13% hit rate")
    print("  High-value paper rate: 40-60% typical")

    current_extraction = metrics['mechanisms_extracted'] / metrics['high_value_papers'] * 100 if metrics['high_value_papers'] > 0 else 0
    current_quality = metrics['high_value_papers'] / metrics['papers_scored'] * 100 if metrics['papers_scored'] > 0 else 0

    print(f"\nCurrent Performance:")
    print(f"  Extraction rate: {current_extraction:.1f}% {'⚠️ Below manual rate' if current_extraction < 60 else '✓'}")
    print(f"  High-value rate: {current_quality:.1f}% {'✓ Within expected range' if 40 <= current_quality <= 60 else '⚠️'}")

    # Errors Analysis
    if metrics.get('errors'):
        print("\n### ERRORS ENCOUNTERED ###")
        for i, error in enumerate(metrics['errors'][:5], 1):
            print(f"{i}. {error.strip()}")

    # Recommendations
    print("\n### RECOMMENDATIONS ###")

    if current_extraction < 20:
        print("• Extraction rate is low - consider:")
        print("  - Using actual LLM API instead of simulation")
        print("  - Adjusting extraction thresholds")
        print("  - Manual extraction for high-value papers")

    if current_quality > 70:
        print("• High-value rate is excellent - search terms working well")
    elif current_quality < 40:
        print("• High-value rate is low - consider:")
        print("  - Refining search terms")
        print("  - Adding more mechanism-specific keywords")

    if metrics['total_cost'] < 0.01:
        print("• Cost is very low - can afford to scale up")
        print("  - Consider batch processing 200-500 papers per session")

    if metrics.get('errors'):
        print("• Database errors detected - fix before production:")
        print("  - Check PostgreSQL schema")
        print("  - Ensure proper constraints and indexes")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"""
Pipeline Status: {'✓ Working' if metrics['mechanisms_extracted'] > 0 else '⚠️ Needs fixes'}
Ready for Scale: {'Yes' if not metrics.get('errors') else 'No - fix database issues first'}
Cost Efficiency: {'Excellent' if metrics['total_cost'] < 0.05 else 'Good'}
Time Efficiency: {'Good' if metrics['time_elapsed'] < 60 else 'Acceptable'}

Key Achievements:
✓ Modular pipeline design implemented
✓ Fetched {metrics['papers_fetched']} papers from OpenAlex
✓ Generated {metrics['embeddings_generated']} embeddings
✓ Total cost only ${metrics['total_cost']:.4f}
✓ Process completed in {metrics['time_elapsed']:.0f} seconds

Next Steps:
1. Fix database storage issues (ON CONFLICT clause)
2. Implement actual LLM extraction (not simulation)
3. Test with larger batch (200-500 papers)
4. Add progress monitoring and resumability
5. Create automated daily runs
""")

    # Save analysis
    analysis = {
        'session': 69,
        'timestamp': metrics.get('timestamp'),
        'papers_fetched': metrics['papers_fetched'],
        'mechanisms_extracted': metrics['mechanisms_extracted'],
        'total_cost': metrics['total_cost'],
        'extraction_rate_pct': current_extraction,
        'high_value_rate_pct': current_quality,
        'papers_per_minute': papers_per_minute if metrics['time_elapsed'] > 0 else 0,
        'cost_per_paper': cost_per_paper if metrics['papers_fetched'] > 0 else 0,
        'ready_for_scale': not bool(metrics.get('errors')),
        'recommendations': [
            'Fix database storage issues',
            'Implement actual LLM extraction',
            'Test with larger batches',
            'Add progress monitoring'
        ]
    }

    with open('examples/session69_pipeline_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    print("\nAnalysis saved to examples/session69_pipeline_analysis.json")

if __name__ == "__main__":
    analyze_results()