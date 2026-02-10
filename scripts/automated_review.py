#!/usr/bin/env python3
"""
Automated review of Session 37 candidates using AI judgment.
Displays candidates in batches for systematic review.
"""
import json
from pathlib import Path

def load_candidates():
    """Load candidates from JSON file."""
    candidates_file = Path(__file__).parent.parent / "examples" / "session37_candidates_for_review.json"
    with open(candidates_file, 'r') as f:
        data = json.load(f)
    return data

def display_batch(candidates, start_idx, batch_size=10):
    """Display a batch of candidates for review."""
    end_idx = min(start_idx + batch_size, len(candidates))

    print(f"\n{'='*90}")
    print(f"REVIEWING CANDIDATES {start_idx+1}-{end_idx} (Batch of {end_idx - start_idx})")
    print(f"{'='*90}\n")

    for i in range(start_idx, end_idx):
        candidate = candidates[i]
        print(f"\n{'─'*90}")
        print(f"#{i+1} | ID: {candidate['candidate_id']} | Similarity: {candidate['similarity']:.4f}")
        print(f"{'─'*90}")

        p1 = candidate['paper_1']
        p2 = candidate['paper_2']

        print(f"\n📄 PAPER 1 [{p1['domain'].upper()}]: {p1['title']}")
        print(f"   Mechanism: {p1['mechanism'][:200]}..." if len(p1['mechanism']) > 200 else f"   Mechanism: {p1['mechanism']}")

        print(f"\n📄 PAPER 2 [{p2['domain'].upper()}]: {p2['title']}")
        print(f"   Mechanism: {p2['mechanism'][:200]}..." if len(p2['mechanism']) > 200 else f"   Mechanism: {p2['mechanism']}")
        print()

def show_statistics(data):
    """Show overall statistics."""
    print("\n" + "="*90)
    print("DATASET STATISTICS")
    print("="*90)
    print(f"Total candidates: {data['metadata']['total_candidates']}")
    print(f"Similarity range: {data['statistics']['similarity_min']:.4f} - {data['statistics']['similarity_max']:.4f}")
    print(f"Mean similarity: {data['statistics']['similarity_mean']:.4f}")
    print(f"Median similarity: {data['statistics']['similarity_median']:.4f}")
    print(f"\nTop domain pairs:")
    for pair, count in sorted(data['statistics']['domain_pairs'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {pair}: {count} pairs")

def main():
    """Main review display function."""
    print("Loading Session 37 candidates...")
    data = load_candidates()
    candidates = data['candidates']

    show_statistics(data)

    # Ask how many to review
    print("\n" + "="*90)
    print("BATCH REVIEW OPTIONS")
    print("="*90)
    print("Enter number of candidates to review (or 'all' for all 165)")
    print("Recommended: Start with top 50, then review more based on findings")

    choice = input("\nHow many candidates to display? [default: 50]: ").strip()

    if choice.lower() == 'all':
        num_to_review = len(candidates)
    elif choice.isdigit():
        num_to_review = int(choice)
    else:
        num_to_review = 50

    # Display in batches of 10
    batch_size = 10
    for start_idx in range(0, min(num_to_review, len(candidates)), batch_size):
        display_batch(candidates, start_idx, batch_size)

        if start_idx + batch_size < min(num_to_review, len(candidates)):
            input("\nPress Enter to see next batch...")

    print("\n" + "="*90)
    print(f"Displayed {min(num_to_review, len(candidates))} candidates")
    print("="*90)
    print("\nNext steps:")
    print("1. Review the displayed candidates")
    print("2. Rate them in the JSON file manually or using another script")
    print("3. Export the best 20-30 for launch")

if __name__ == "__main__":
    main()
