#!/usr/bin/env python3
"""
Session 37: Extract mechanisms from all 2,021 papers using LLM approach.

Expected hit rate: ~22.5% (based on Session 34)
Expected output: ~450 mechanisms from mechanism-rich papers
"""

import sqlite3
import json
import os
from anthropic import Anthropic

# Initialize Claude API
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# LLM extraction prompt (from Session 33/34)
EXTRACTION_PROMPT = """Read this abstract and extract the core MECHANISM being described.

A mechanism is a causal process: what affects what, and how.

Describe in 2-3 sentences using domain-neutral language:
- Use generic terms (population, resource, agent, system, component, network)
- Avoid field-specific jargon and technique names
- Focus on causal relationships (A causes B, B affects C)
- Include feedback loops if present (A → B → A)
- Include thresholds if present (when X crosses Y, then Z)

If the paper does NOT describe a mechanism (e.g., pure ML/technique, empirical study, survey), respond with exactly: "NO_MECHANISM"

Only describe mechanisms if the paper explains HOW or WHY something works, not just WHAT was done or measured.

Abstract:
{abstract}

Mechanism:"""

def extract_mechanism(abstract, paper_id):
    """Extract mechanism from abstract using Claude API."""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT.format(abstract=abstract)
            }]
        )

        mechanism = message.content[0].text.strip()

        # Check if no mechanism found
        if mechanism == "NO_MECHANISM" or mechanism.startswith("NO_MECHANISM"):
            return None

        return mechanism

    except Exception as e:
        print(f"Error extracting mechanism for paper {paper_id}: {e}")
        return None

def main():
    # Connect to database
    conn = sqlite3.connect('database/papers.db')
    cursor = conn.cursor()

    # Get all papers
    cursor.execute("""
        SELECT id, arxiv_id, title, abstract, domain, subdomain
        FROM papers
        ORDER BY id
    """)

    papers = cursor.fetchall()
    print(f"Total papers to process: {len(papers)}")

    # Load existing results if any (for resuming)
    output_file = 'examples/session37_all_mechanisms.json'
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_results = json.load(f)
        print(f"Resuming from {len(existing_results)} existing results")
        processed_ids = {r['paper_id'] for r in existing_results}
    else:
        existing_results = []
        processed_ids = set()

    results = list(existing_results)
    batch_size = 50
    save_interval = 10  # Save every 10 papers

    for i, (paper_id, arxiv_id, title, abstract, domain, subdomain) in enumerate(papers):
        # Skip if already processed
        if paper_id in processed_ids:
            continue

        # Skip papers without abstracts
        if not abstract or len(abstract.strip()) < 50:
            continue

        print(f"\n[{i+1}/{len(papers)}] Processing paper {paper_id} ({domain})...")

        # Extract mechanism
        mechanism = extract_mechanism(abstract, paper_id)

        if mechanism:
            result = {
                "paper_id": paper_id,
                "domain": domain,
                "subdomain": subdomain,
                "arxiv_id": arxiv_id,
                "title": title,
                "mechanism": mechanism,
                "batch": (i // batch_size) + 1
            }
            results.append(result)
            print(f"  ✓ Mechanism extracted ({len(mechanism)} chars)")
        else:
            print(f"  ✗ No mechanism found")

        # Save intermediate results every 10 papers
        if (i + 1) % save_interval == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Saved {len(results)} mechanisms so far...")

    # Final save
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    conn.close()

    # Print statistics
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total papers processed: {len(papers)}")
    print(f"Mechanisms extracted: {len(results)}")
    print(f"Hit rate: {len(results)/len(papers)*100:.1f}%")
    print(f"Output file: {output_file}")

    # Domain breakdown
    domain_counts = {}
    for r in results:
        domain = r['domain']
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print(f"\nMechanisms by domain:")
    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: {count}")

if __name__ == "__main__":
    main()
