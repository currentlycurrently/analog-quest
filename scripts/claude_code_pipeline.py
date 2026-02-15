#!/usr/bin/env python3
"""
Claude Code Pipeline - Optimized for use WITH Claude Code agents
Session 70+ - Sustainable growth using Claude Code for extraction

This pipeline is designed to be run BY Claude Code agents multiple times
per session. It leverages the fact that Claude Code can do high-quality
extraction for free, rather than paying for external API calls.

Workflow:
1. Fetch papers from OpenAlex
2. Score them for mechanism richness
3. Claude Code manually extracts from high-value papers
4. Generate embeddings
5. Store in PostgreSQL
6. Repeat as many times as possible in a session
"""

import json
import os
import sys
import time
import yaml
import psycopg2
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from pyalex import Works

def load_config():
    """Load pipeline configuration"""
    with open('config/pipeline_config.yaml', 'r') as f:
        return yaml.safe_load(f)

def fetch_papers(num_papers: int = 20, batch_num: int = 1) -> List[Dict]:
    """
    Fetch a small batch of papers for Claude Code to process
    Keep batches small so Claude can extract in context
    """
    print(f"\n=== FETCHING {num_papers} PAPERS FROM OPENALEX ===\n")

    config = load_config()
    papers = []

    # Use diverse search terms, rotating based on batch number
    search_terms = config['search_terms']
    papers_per_term = max(2, num_papers // len(search_terms))

    # Rotate search terms based on batch number to get different papers each batch
    start_idx = ((batch_num - 1) * 10) % len(search_terms)
    rotated_terms = search_terms[start_idx:] + search_terms[:start_idx]

    for i, term in enumerate(rotated_terms):
        if len(papers) >= num_papers:
            break

        print(f"Searching: {term}")
        try:
            # Use pagination to get different papers in different batches
            # For batches 1-15, use page 1; for 16-30, page 2, etc.
            page_num = ((batch_num - 1) // len(search_terms)) + 1

            # Skip some results to get different papers
            skip_count = (batch_num - 1) * 2  # Skip 2 papers per batch number

            works_query = Works().search(term).filter(has_abstract=True)
            works = works_query.get()

            count = 0
            skipped = 0
            for work in works:
                if count >= papers_per_term or len(papers) >= num_papers:
                    break

                # Skip initial papers to get diversity across batches
                if skipped < skip_count:
                    skipped += 1
                    continue

                # Extract paper data
                paper = {
                    'title': work.get('title', ''),
                    'abstract': extract_abstract(work),
                    'openalex_id': work.get('id', ''),
                    'published_date': work.get('publication_date', ''),
                    'citations': work.get('cited_by_count', 0),
                    'topics': [t.get('display_name', '') for t in work.get('topics', [])]
                }

                if paper['title'] and paper['abstract']:
                    papers.append(paper)
                    count += 1

            print(f"  Found {count} papers")

        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal fetched: {len(papers)} papers")
    return papers

def extract_abstract(work: Dict) -> str:
    """Extract abstract from OpenAlex work"""
    inverted_index = work.get('abstract_inverted_index', {})
    if not inverted_index:
        return ""

    words = []
    for word, positions in inverted_index.items():
        for pos in positions:
            words.append((pos, word))
    words.sort()
    return ' '.join([word for _, word in words])

def score_papers(papers: List[Dict]) -> List[Dict]:
    """Score papers for mechanism richness"""
    print("\n=== SCORING PAPERS ===\n")

    strong_indicators = [
        'mechanism', 'feedback', 'cascade', 'emergent', 'self-organiz',
        'phase transition', 'critical', 'tipping point', 'bifurcation',
        'synchron', 'coupled', 'nonlinear', 'collective', 'propagat'
    ]

    moderate_indicators = [
        'dynamics', 'network', 'complex', 'adaptive', 'evolution',
        'diffusion', 'interaction', 'influence', 'spillover', 'contagion',
        'threshold', 'stability', 'equilibrium', 'oscillat', 'pattern'
    ]

    weak_indicators = [
        'model', 'system', 'process', 'behavior', 'effect',
        'relationship', 'distribution', 'flow', 'structure'
    ]

    for paper in papers:
        text = f"{paper['title']} {paper['abstract']}".lower()

        strong = sum(1 for ind in strong_indicators if ind in text)
        moderate = sum(1 for ind in moderate_indicators if ind in text)
        weak = sum(1 for ind in weak_indicators if ind in text)

        score = min(10, (strong * 3) + (moderate * 1.5) + (weak * 0.5))

        if strong >= 3:
            score = min(10, score + 2)

        if len(paper['abstract'].split()) < 50:
            score = max(0, score - 2)

        paper['mechanism_score'] = round(score, 1)

    # Sort by score
    papers.sort(key=lambda p: p['mechanism_score'], reverse=True)

    high_value = [p for p in papers if p['mechanism_score'] >= 5]
    print(f"High-value papers (≥5/10): {len(high_value)}/{len(papers)}")

    return papers

def save_for_extraction(papers: List[Dict], batch_num: int):
    """
    Save high-value papers for Claude Code to extract
    Keep only top papers that Claude can handle in context
    """
    # Filter high-value papers
    high_value = [p for p in papers if p['mechanism_score'] >= 5]

    # Limit to top 10 for manual extraction (Claude Code context limits)
    extraction_batch = high_value[:10]

    # Save to file for Claude Code to read
    filename = f'temp/extraction_batch_{batch_num}.json'
    os.makedirs('temp', exist_ok=True)

    with open(filename, 'w') as f:
        json.dump(extraction_batch, f, indent=2)

    print(f"\n=== READY FOR EXTRACTION ===")
    print(f"Saved {len(extraction_batch)} papers to {filename}")
    print(f"Top scores: {[p['mechanism_score'] for p in extraction_batch[:5]]}")

    # Print papers for Claude to see
    print("\n=== PAPERS FOR MANUAL EXTRACTION ===\n")
    for i, paper in enumerate(extraction_batch, 1):
        print(f"{i}. [{paper['mechanism_score']}/10] {paper['title'][:80]}...")

    return filename

def generate_embeddings(mechanisms: List[Dict]) -> List[Dict]:
    """Generate embeddings for mechanisms"""
    if not mechanisms:
        return mechanisms

    print(f"\n=== GENERATING EMBEDDINGS FOR {len(mechanisms)} MECHANISMS ===\n")

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    descriptions = [m['structural_description'] for m in mechanisms]
    embeddings = model.encode(descriptions)

    for mechanism, embedding in zip(mechanisms, embeddings):
        mechanism['embedding'] = embedding

    print(f"Generated {len(embeddings)} embeddings")
    return mechanisms

def store_to_postgresql(mechanisms: List[Dict], papers: List[Dict]):
    """Store mechanisms and papers in PostgreSQL"""
    if not mechanisms:
        print("No mechanisms to store")
        return

    print(f"\n=== STORING {len(mechanisms)} MECHANISMS TO DATABASE ===\n")

    config = load_config()

    try:
        conn = psycopg2.connect(
            host=config['database']['host'],
            port=config['database']['port'],
            database=config['database']['name'],
            user=config['database']['user']
        )
        cursor = conn.cursor()

        stored_count = 0

        for mechanism in mechanisms:
            # First store the paper if needed
            paper = next((p for p in papers if p['title'] in mechanism.get('paper_title', '')), None)
            if paper:
                cursor.execute("""
                    INSERT INTO papers (title, abstract, domain, subdomain, arxiv_id,
                                      published_date, mechanism_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (title) DO UPDATE SET mechanism_score = EXCLUDED.mechanism_score
                    RETURNING id
                """, (
                    paper['title'],
                    paper['abstract'],
                    paper.get('topics', ['unknown'])[0] if paper.get('topics') else 'unknown',
                    '',
                    paper.get('openalex_id', ''),
                    paper.get('published_date', ''),
                    paper.get('mechanism_score', 0)
                ))

                result = cursor.fetchone()
                if result:
                    paper_id = result[0]

                    # Store mechanism
                    cursor.execute("""
                        INSERT INTO mechanisms (paper_id, description, structural_description,
                                              mechanism_type, domain, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        paper_id,
                        mechanism['description'],
                        mechanism['structural_description'],
                        mechanism.get('mechanism_type', ''),
                        mechanism.get('domain', 'unknown'),
                        mechanism['embedding'].tolist() if 'embedding' in mechanism else None
                    ))
                    stored_count += 1

        conn.commit()
        print(f"Successfully stored {stored_count} mechanisms")

    except Exception as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def run_batch(batch_num: int):
    """
    Run one batch of the pipeline
    Designed to be called multiple times per session
    """
    print(f"\n{'='*60}")
    print(f"BATCH {batch_num} - Claude Code Pipeline")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    # 1. Fetch small batch of papers
    papers = fetch_papers(num_papers=20, batch_num=batch_num)

    # 2. Score them
    papers = score_papers(papers)

    # 3. Save for Claude Code extraction
    extraction_file = save_for_extraction(papers, batch_num)

    # 4. Return info for Claude Code
    high_value = [p for p in papers if p['mechanism_score'] >= 5]

    stats = {
        'batch_num': batch_num,
        'papers_fetched': len(papers),
        'high_value_papers': len(high_value),
        'extraction_file': extraction_file,
        'avg_score': round(sum(p['mechanism_score'] for p in papers) / len(papers), 1) if papers else 0,
        'top_scores': [p['mechanism_score'] for p in papers[:5]]
    }

    print(f"\n=== BATCH {batch_num} COMPLETE ===")
    print(f"Papers: {stats['papers_fetched']}")
    print(f"High-value: {stats['high_value_papers']}")
    print(f"Avg score: {stats['avg_score']}")
    print(f"\nNow Claude Code should:")
    print(f"1. Read {extraction_file}")
    print(f"2. Extract mechanisms manually")
    print(f"3. Save to temp/mechanisms_batch_{batch_num}.json")
    print(f"4. Run: python3 scripts/claude_code_pipeline.py --store {batch_num}")

    return stats

def store_batch(batch_num: int):
    """
    Store mechanisms after Claude Code extraction
    Called with --store flag after manual extraction
    """
    mechanisms_file = f'temp/mechanisms_batch_{batch_num}.json'
    papers_file = f'temp/extraction_batch_{batch_num}.json'

    if not os.path.exists(mechanisms_file):
        print(f"No mechanisms found at {mechanisms_file}")
        print("Claude Code needs to extract and save mechanisms first")
        return

    # Load mechanisms and papers
    with open(mechanisms_file, 'r') as f:
        mechanisms = json.load(f)

    with open(papers_file, 'r') as f:
        papers = json.load(f)

    print(f"Loaded {len(mechanisms)} mechanisms from batch {batch_num}")

    # Generate embeddings
    mechanisms = generate_embeddings(mechanisms)

    # Store to PostgreSQL
    store_to_postgresql(mechanisms, papers)

    # Save stats
    stats_file = f'temp/batch_{batch_num}_stats.json'
    stats = {
        'batch_num': batch_num,
        'mechanisms_extracted': len(mechanisms),
        'timestamp': datetime.now().isoformat()
    }

    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\nBatch {batch_num} fully processed!")
    print(f"Ready to run next batch")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--store' and len(sys.argv) > 2:
            # Store mode: process extracted mechanisms
            batch_num = int(sys.argv[2])
            store_batch(batch_num)
        elif sys.argv[1] == '--batch' and len(sys.argv) > 2:
            # Run specific batch number
            batch_num = int(sys.argv[2])
            run_batch(batch_num)
        else:
            print("Usage:")
            print("  python3 claude_code_pipeline.py --batch N  # Run batch N")
            print("  python3 claude_code_pipeline.py --store N  # Store batch N after extraction")
    else:
        # Default: run next batch
        # Find last batch number
        batch_num = 1
        if os.path.exists('temp'):
            existing = [f for f in os.listdir('temp') if f.startswith('extraction_batch_')]
            if existing:
                numbers = [int(f.split('_')[2].split('.')[0]) for f in existing]
                batch_num = max(numbers) + 1

        run_batch(batch_num)

if __name__ == "__main__":
    main()