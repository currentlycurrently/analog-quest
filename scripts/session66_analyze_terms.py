#!/usr/bin/env python3
"""
Session 66: Analyze Session 65 search term performance
"""

import json
import numpy as np

# Load fetch stats
with open('../examples/session65_fetch_stats.json', 'r') as f:
    stats = json.load(f)

papers_per_term = stats['papers_per_term']

# Sort terms by paper count
sorted_terms = sorted(papers_per_term.items(), key=lambda x: x[1], reverse=True)

# Analyze top and bottom performers
top_20 = sorted_terms[:20]
bottom_20 = sorted_terms[-20:]

print("SESSION 66: Search Term Performance Analysis")
print("=" * 70)

print("\nTOP 20 PERFORMERS (most papers):")
for term, count in top_20:
    print(f"  {count:2} papers: {term}")

print("\nBOTTOM 20 PERFORMERS (fewest papers):")
for term, count in bottom_20:
    print(f"  {count:2} papers: {term}")

# Analyze patterns in high performers
print("\n" + "=" * 70)
print("PATTERN ANALYSIS:")

# Keywords that appear in top performers
top_keywords = {}
for term, count in sorted_terms[:50]:  # Top third
    for word in term.split():
        if word not in ['the', 'and', 'or', 'in', 'of']:
            top_keywords[word] = top_keywords.get(word, 0) + count

# Sort keywords by total paper contribution
sorted_keywords = sorted(top_keywords.items(), key=lambda x: x[1], reverse=True)

print("\nMost productive keywords (in top 50 terms):")
for keyword, total in sorted_keywords[:20]:
    avg_papers = total / sum(1 for t, _ in sorted_terms[:50] if keyword in t)
    print(f"  {keyword:20} → {total:3} total papers (avg {avg_papers:.1f} per term)")

# Category analysis
categories = {
    'feedback': [],
    'dynamics': [],
    'coupling': [],
    'network': [],
    'synchronization': [],
    'optimization': [],
    'stability': [],
    'learning': [],
    'diffusion': [],
    'emergence': []
}

for term, count in papers_per_term.items():
    for category in categories:
        if category in term.lower():
            categories[category].append(count)

print("\nCategory Performance:")
for category, counts in sorted(categories.items(), key=lambda x: np.mean(x[1]) if x[1] else 0, reverse=True):
    if counts:
        print(f"  {category:15} → avg {np.mean(counts):.1f} papers, total {sum(counts)} from {len(counts)} terms")

# Recommendations
print("\n" + "=" * 70)
print("RECOMMENDATIONS FOR SESSION 66:")
print("\n1. Focus on compound terms with these high-value words:")
print("   - feedback, learning, synchronization, coupling")
print("   - cross-scale, homeostatic, metastable")
print("\n2. Avoid single-word or overly specific terms")
print("\n3. Add modifiers to boost quality:")
print("   - 'mathematical model'")
print("   - 'theoretical analysis'")
print("   - 'mechanism'")
print("\n4. Combine successful patterns:")
print("   - [mechanism] + 'feedback' + [domain]")
print("   - 'coupled' + [process] + 'dynamics'")

# Stats summary
avg_papers = np.mean(list(papers_per_term.values()))
std_papers = np.std(list(papers_per_term.values()))

print("\n" + "=" * 70)
print(f"Overall Statistics:")
print(f"  Average papers per term: {avg_papers:.1f}")
print(f"  Standard deviation: {std_papers:.1f}")
print(f"  Total unique terms: {len(papers_per_term)}")
print(f"  Terms with 20+ papers: {sum(1 for _, c in papers_per_term.items() if c >= 20)}")
print(f"  Terms with <10 papers: {sum(1 for _, c in papers_per_term.items() if c < 10)}")