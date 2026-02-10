#!/usr/bin/env python3
"""
LLM-based mechanism extraction for Session 34.

This script extracts structural mechanisms from abstracts using an LLM approach.
For Session 34, we process 100 mechanism-rich papers and measure precision.
"""

import json
import sys

# Prompt template from Session 33
MECHANISM_EXTRACTION_PROMPT = """Read this abstract and extract the core MECHANISM being described.

A mechanism is a causal process: what affects what, and how.

Describe in 2-3 sentences using domain-neutral language:
- Use generic terms (population, resource, agent, system, component)
- Avoid field-specific jargon and technique names
- Focus on causal relationships (A causes B, B affects C)
- Include feedback loops if present (A → B → A)
- Include thresholds if present (when X crosses Y, then Z)

GOOD: "Resource abundance allows population growth. Growing population depletes resources. Creates oscillating cycle."
BAD: "This paper uses Lotka-Volterra equations for predator-prey."

Abstract: {abstract}

Mechanism (2-3 sentences):"""

def extract_mechanism_manual(paper):
    """
    Manual mechanism extraction for demonstration.

    In production, this would use Claude API to extract mechanisms.
    For Session 34, we'll manually extract from a sample to demonstrate quality.
    """

    # This is where Claude API would be called in production:
    # response = anthropic.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     messages=[{"role": "user", "content": MECHANISM_EXTRACTION_PROMPT.format(abstract=paper['abstract'])}]
    # )
    # return response.content[0].text

    # For now, return a placeholder that prompts manual extraction
    return {
        'paper_id': paper['id'],
        'title': paper['title'],
        'domain': paper['domain'],
        'subdomain': paper['subdomain'],
        'abstract': paper['abstract'],
        'mechanism': None,  # To be filled in manually or via API
        'extraction_method': 'manual_placeholder'
    }


def process_papers(input_file, output_file, manual_mode=True):
    """Process papers and extract mechanisms."""

    with open(input_file, 'r') as f:
        papers = json.load(f)

    print(f"Loaded {len(papers)} papers")
    print(f"Processing with {'manual extraction' if manual_mode else 'API extraction'}")

    results = []
    for i, paper in enumerate(papers):
        print(f"Processing paper {i+1}/{len(papers)}: {paper['title'][:60]}...")

        if manual_mode:
            result = extract_mechanism_manual(paper)
        else:
            # Would use Claude API here
            pass

        results.append(result)

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nExtracted {len(results)} mechanisms to {output_file}")
    print(f"\nNext step: Fill in 'mechanism' fields manually using the prompt template,")
    print(f"or integrate Claude API for automated extraction.")


if __name__ == '__main__':
    input_file = 'examples/session34_selected_papers.json'
    output_file = 'examples/session34_llm_mechanisms.json'

    process_papers(input_file, output_file, manual_mode=True)

    print("\n" + "="*80)
    print("PROMPT TEMPLATE FOR MANUAL EXTRACTION:")
    print("="*80)
    print(MECHANISM_EXTRACTION_PROMPT.replace("{abstract}", "[ABSTRACT TEXT]"))
