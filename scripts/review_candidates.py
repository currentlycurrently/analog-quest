#!/usr/bin/env python3
"""
Review candidates from Session 37 and identify verified isomorphisms.
"""
import json
import sqlite3
from pathlib import Path

def load_candidates():
    """Load candidates from JSON file."""
    candidates_file = Path(__file__).parent.parent / "examples" / "session37_candidates_for_review.json"
    with open(candidates_file, 'r') as f:
        data = json.load(f)
    return data

def display_candidate(candidate, index, total):
    """Display a candidate for review."""
    print(f"\n{'='*80}")
    print(f"CANDIDATE {index}/{total} (ID: {candidate['candidate_id']}, Similarity: {candidate['similarity']:.4f})")
    print(f"{'='*80}")

    print(f"\n[PAPER 1] {candidate['paper_1']['domain'].upper()}")
    print(f"Title: {candidate['paper_1']['title']}")
    print(f"Mechanism:\n{candidate['paper_1']['mechanism']}")

    print(f"\n[PAPER 2] {candidate['paper_2']['domain'].upper()}")
    print(f"Title: {candidate['paper_2']['title']}")
    print(f"Mechanism:\n{candidate['paper_2']['mechanism']}")
    print()

def rate_candidate(candidate, index, total):
    """Rate a single candidate interactively."""
    display_candidate(candidate, index, total)

    print("Rating options:")
    print("  e = excellent (clear structural isomorphism)")
    print("  g = good (solid structural similarity)")
    print("  w = weak (some similarity, not convincing)")
    print("  f = false (no real structural connection)")
    print("  s = skip (review later)")
    print("  q = quit and save")

    while True:
        rating_input = input("\nRating [e/g/w/f/s/q]: ").strip().lower()

        if rating_input == 'q':
            return 'quit'
        elif rating_input == 's':
            return 'skip'
        elif rating_input in ['e', 'g', 'w', 'f']:
            rating_map = {'e': 'excellent', 'g': 'good', 'w': 'weak', 'f': 'false'}
            rating = rating_map[rating_input]

            # For excellent/good ratings, ask for notes
            notes = ""
            if rating in ['excellent', 'good']:
                print("\nBrief structural explanation (Enter to skip):")
                notes = input("> ").strip()

            candidate['rating'] = rating
            candidate['notes'] = notes if notes else None
            candidate['review_status'] = 'reviewed'

            return 'continue'
        else:
            print("Invalid input. Please enter e/g/w/f/s/q")

def save_progress(data, output_file):
    """Save current progress."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✓ Progress saved to {output_file}")

def review_all_candidates():
    """Main review loop."""
    print("Loading candidates...")
    data = load_candidates()
    candidates = data['candidates']
    total = len(candidates)

    output_file = Path(__file__).parent.parent / "examples" / "session37_candidates_reviewed.json"

    print(f"\n{total} candidates loaded")
    print(f"Starting review from the top (highest similarity)...")

    for i, candidate in enumerate(candidates, 1):
        # Skip already reviewed
        if candidate.get('review_status') == 'reviewed' and candidate.get('rating'):
            continue

        result = rate_candidate(candidate, i, total)

        if result == 'quit':
            print("\n\nQuitting and saving progress...")
            save_progress(data, output_file)
            break
        elif result == 'skip':
            continue

        # Auto-save every 10 reviews
        if i % 10 == 0:
            save_progress(data, output_file)

    else:
        # Completed all reviews
        save_progress(data, output_file)
        print("\n\n" + "="*80)
        print("ALL CANDIDATES REVIEWED!")
        print("="*80)

        # Show summary
        ratings_count = {}
        for c in candidates:
            rating = c.get('rating')
            if rating:
                ratings_count[rating] = ratings_count.get(rating, 0) + 1

        print("\nSummary:")
        for rating in ['excellent', 'good', 'weak', 'false']:
            count = ratings_count.get(rating, 0)
            print(f"  {rating.capitalize()}: {count}")

        print(f"\nReviewed file: {output_file}")

if __name__ == "__main__":
    review_all_candidates()
