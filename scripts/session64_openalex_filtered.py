#!/usr/bin/env python3

"""
Session 64: OpenAlex Quality Test with Filtered Queries
Tests mechanism extraction quality on OpenAlex papers with abstracts
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import re

try:
    import pyalex
    from pyalex import Works
except ImportError:
    print("Error: pyalex not installed. Run: pip install pyalex")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
except ImportError:
    print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Configure pyalex
pyalex.config.email = "research@analog.quest"

class OpenAlexFilteredFetcher:
    def __init__(self):
        """Initialize the OpenAlex filtered fetcher"""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "papers_fetched": [],
            "statistics": {},
            "quality_assessment": {}
        }

        # Connect to PostgreSQL
        try:
            self.conn = psycopg2.connect(
                dbname="analog_quest",
                user="user",
                host="localhost",
                port=5432
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("✓ Connected to PostgreSQL")
        except Exception as e:
            print(f"✗ Failed to connect to PostgreSQL: {e}")
            sys.exit(1)

    def reconstruct_abstract(self, inverted_index: Optional[Dict]) -> str:
        """Reconstruct abstract from OpenAlex inverted index format"""
        if not inverted_index:
            return ""

        # Create a list of (word, position) tuples
        word_positions = []
        for word, positions in inverted_index.items():
            for position in positions:
                word_positions.append((position, word))

        # Sort by position and join words
        word_positions.sort(key=lambda x: x[0])
        abstract = " ".join([word for _, word in word_positions])

        return abstract

    def fetch_papers_with_abstracts(self, num_papers: int = 500) -> List[Dict]:
        """Fetch papers with abstracts using has_abstract filter"""
        print(f"\n=== Fetching {num_papers} Papers with Abstracts ===")

        papers = []
        batch_size = 100  # OpenAlex page size limit

        # Mix of mechanism-rich topics based on Session 50 analysis
        search_terms = [
            "network dynamics phase transition",
            "feedback control adaptation",
            "emergence self-organization",
            "evolutionary dynamics optimization",
            "critical phenomena synchronization",
            "coupling multi-scale",
            "collective behavior cooperation",
            "resource allocation learning"
        ]

        papers_per_query = num_papers // len(search_terms)

        for term in search_terms:
            print(f"\nFetching papers for: '{term}'")

            try:
                # Use has_abstract=True filter
                query = (Works()
                        .search(term)
                        .filter(has_abstract=True)
                        .filter(publication_year=2024)  # Recent papers
                        .sort(cited_by_count=False))  # Sort by citations (descending)

                batch_papers = query.get()[:papers_per_query]

                for paper in batch_papers:
                    # Reconstruct abstract
                    abstract = self.reconstruct_abstract(paper.get("abstract_inverted_index"))

                    if abstract:  # Double-check abstract exists
                        paper_data = {
                            "openalex_id": paper.get("id", "").replace("https://openalex.org/", ""),
                            "title": paper.get("title", ""),
                            "abstract": abstract,
                            "publication_date": paper.get("publication_date"),
                            "cited_by_count": paper.get("cited_by_count", 0),
                            "topics": paper.get("topics", []),
                            "search_term": term
                        }

                        # Extract primary topic
                        if paper_data["topics"]:
                            primary_topic = paper_data["topics"][0]
                            paper_data["primary_topic"] = primary_topic.get("display_name", "")
                            paper_data["topic_score"] = primary_topic.get("score", 0)

                        papers.append(paper_data)

                print(f"  ✓ Fetched {len(batch_papers)} papers")

            except Exception as e:
                print(f"  ✗ Error fetching for '{term}': {e}")
                continue

        print(f"\n✓ Total papers fetched: {len(papers)}")

        # Calculate statistics
        self.results["statistics"]["total_fetched"] = len(papers)
        self.results["statistics"]["abstracts_present"] = sum(1 for p in papers if p["abstract"])
        self.results["statistics"]["abstract_coverage"] = (
            self.results["statistics"]["abstracts_present"] / len(papers) * 100
            if papers else 0
        )

        # Topic distribution
        topic_counts = {}
        for paper in papers:
            topic = paper.get("primary_topic", "Unknown")
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        self.results["statistics"]["topic_distribution"] = dict(
            sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )

        return papers

    def import_to_postgresql(self, papers: List[Dict]) -> bool:
        """Import papers to PostgreSQL database"""
        print(f"\n=== Importing {len(papers)} Papers to PostgreSQL ===")

        imported_count = 0
        duplicate_count = 0

        for paper in papers:
            try:
                # Check if paper already exists (by title to avoid OpenAlex ID issues)
                self.cursor.execute(
                    "SELECT id FROM papers WHERE title = %s",
                    (paper["title"],)
                )

                if self.cursor.fetchone():
                    duplicate_count += 1
                    continue

                # Insert paper with domain="openalex" for tracking
                self.cursor.execute("""
                    INSERT INTO papers (
                        title, abstract, domain, subdomain,
                        published_date, mechanism_score
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    paper["title"],
                    paper["abstract"],
                    "openalex",  # Use "openalex" as domain for tracking
                    paper.get("primary_topic", "")[:50] if paper.get("primary_topic") else "",
                    paper.get("publication_date"),
                    0  # Score will be calculated next
                ))

                paper_id = self.cursor.fetchone()["id"]
                paper["db_id"] = paper_id
                imported_count += 1

            except Exception as e:
                print(f"  ✗ Error importing paper: {e}")
                self.conn.rollback()
                continue

        self.conn.commit()

        print(f"  ✓ Imported: {imported_count} papers")
        print(f"  ⚠ Duplicates skipped: {duplicate_count}")

        self.results["statistics"]["imported"] = imported_count
        self.results["statistics"]["duplicates"] = duplicate_count

        return imported_count > 0

    def score_papers(self, papers: List[Dict]) -> List[Dict]:
        """Score papers for mechanism richness using Session 48 algorithm"""
        print(f"\n=== Scoring {len(papers)} Papers for Mechanism Richness ===")

        # Structural keywords from Session 50 analysis
        structural_keywords = [
            "mechanism", "process", "system", "dynamics", "network", "feedback",
            "emergence", "control", "coupling", "adaptation", "optimization",
            "evolution", "selection", "equilibrium", "transition", "phase",
            "critical", "threshold", "cascade", "propagation", "diffusion",
            "synchronization", "oscillation", "bifurcation", "attractor",
            "trajectory", "stability", "convergence", "divergence", "flow",
            "interaction", "cooperation", "competition", "trade-off",
            "constraint", "resource", "allocation", "distribution",
            "hierarchy", "scale", "pattern", "structure", "topology",
            "modularity", "robustness", "resilience", "plasticity"
        ]

        # Negative indicators (reviews, surveys, meta-analyses)
        negative_keywords = [
            "review", "survey", "meta-analysis", "systematic review",
            "literature review", "bibliometric", "scientometric",
            "tutorial", "perspective", "commentary", "opinion"
        ]

        scored_papers = []

        for paper in papers:
            abstract = paper.get("abstract", "").lower()
            title = paper.get("title", "").lower()

            if not abstract:
                paper["score"] = 0
                scored_papers.append(paper)
                continue

            # Count structural keywords
            keyword_count = sum(1 for keyword in structural_keywords
                              if keyword in abstract or keyword in title)

            # Check for negative indicators
            is_review = any(neg in title or neg in abstract[:200]
                          for neg in negative_keywords)

            # Calculate score (0-10 scale)
            # Base score from keyword density
            abstract_words = len(abstract.split())
            keyword_density = keyword_count / max(abstract_words, 1) * 100

            # Score calculation similar to Session 48
            if keyword_density >= 8:
                score = 9
            elif keyword_density >= 6:
                score = 8
            elif keyword_density >= 4:
                score = 7
            elif keyword_density >= 3:
                score = 6
            elif keyword_density >= 2:
                score = 5
            elif keyword_density >= 1.5:
                score = 4
            elif keyword_density >= 1:
                score = 3
            elif keyword_density >= 0.5:
                score = 2
            else:
                score = 1

            # Penalty for reviews/surveys
            if is_review:
                score = max(1, score - 3)

            # Bonus for high-value topics (based on Session 46 audit)
            good_topics = ["network", "dynamics", "evolution", "optimization",
                          "emergence", "phase transition", "critical phenomena"]
            if any(topic in paper.get("primary_topic", "").lower() for topic in good_topics):
                score = min(10, score + 1)

            paper["score"] = score
            scored_papers.append(paper)

            # Update in database if paper was imported
            if "db_id" in paper:
                try:
                    self.cursor.execute(
                        "UPDATE papers SET mechanism_score = %s WHERE id = %s",
                        (score, paper["db_id"])
                    )
                except Exception as e:
                    print(f"  ✗ Error updating score: {e}")

        self.conn.commit()

        # Calculate score distribution
        score_dist = {}
        for paper in scored_papers:
            score = paper["score"]
            score_dist[score] = score_dist.get(score, 0) + 1

        avg_score = sum(p["score"] for p in scored_papers) / len(scored_papers) if scored_papers else 0
        high_value_count = sum(1 for p in scored_papers if p["score"] >= 5)

        print(f"\n  Score Distribution:")
        for score in sorted(score_dist.keys(), reverse=True):
            bar = "█" * (score_dist[score] // 5)
            print(f"    {score:2}/10: {score_dist[score]:3} papers {bar}")

        print(f"\n  ✓ Average score: {avg_score:.2f}/10")
        print(f"  ✓ High-value papers (≥5/10): {high_value_count} ({high_value_count/len(scored_papers)*100:.1f}%)")

        self.results["quality_assessment"]["score_distribution"] = score_dist
        self.results["quality_assessment"]["average_score"] = avg_score
        self.results["quality_assessment"]["high_value_count"] = high_value_count
        self.results["quality_assessment"]["high_value_percentage"] = (
            high_value_count / len(scored_papers) * 100 if scored_papers else 0
        )

        return scored_papers

    def compare_with_arxiv(self):
        """Compare score distribution with existing arXiv corpus"""
        print("\n=== Comparing with arXiv Corpus ===")

        try:
            # Get arXiv corpus statistics
            self.cursor.execute("""
                SELECT
                    AVG(mechanism_score) as avg_score,
                    COUNT(*) as total_papers,
                    SUM(CASE WHEN mechanism_score >= 5 THEN 1 ELSE 0 END) as high_value_count
                FROM papers
                WHERE domain != 'openalex'
            """)

            arxiv_stats = self.cursor.fetchone()

            print(f"\n  arXiv Corpus (n={arxiv_stats['total_papers']}):")
            print(f"    Average score: {arxiv_stats['avg_score']:.2f}/10")
            print(f"    High-value papers: {arxiv_stats['high_value_count']} ({arxiv_stats['high_value_count']/arxiv_stats['total_papers']*100:.1f}%)")

            print(f"\n  OpenAlex Test (n={self.results['statistics']['total_fetched']}):")
            print(f"    Average score: {self.results['quality_assessment']['average_score']:.2f}/10")
            print(f"    High-value papers: {self.results['quality_assessment']['high_value_count']} ({self.results['quality_assessment']['high_value_percentage']:.1f}%)")

            # Calculate differences
            score_diff = self.results['quality_assessment']['average_score'] - arxiv_stats['avg_score']
            high_value_diff = (self.results['quality_assessment']['high_value_percentage'] -
                              (arxiv_stats['high_value_count']/arxiv_stats['total_papers']*100))

            print(f"\n  Comparison:")
            print(f"    Score difference: {score_diff:+.2f}")
            print(f"    High-value difference: {high_value_diff:+.1f}%")

            self.results["quality_assessment"]["arxiv_comparison"] = {
                "arxiv_avg_score": float(arxiv_stats['avg_score']),
                "arxiv_high_value_pct": arxiv_stats['high_value_count']/arxiv_stats['total_papers']*100,
                "score_difference": score_diff,
                "high_value_difference": high_value_diff
            }

        except Exception as e:
            print(f"  ✗ Error comparing with arXiv: {e}")

    def select_top_papers(self, papers: List[Dict], top_n: int = 50) -> List[Dict]:
        """Select top papers by score for mechanism extraction"""
        print(f"\n=== Selecting Top {top_n} Papers for Extraction ===")

        # Sort by score descending
        sorted_papers = sorted(papers, key=lambda x: x["score"], reverse=True)
        top_papers = sorted_papers[:top_n]

        # Score distribution of top papers
        score_dist = {}
        for paper in top_papers:
            score = paper["score"]
            score_dist[score] = score_dist.get(score, 0) + 1

        print(f"\n  Top {top_n} Papers Score Distribution:")
        for score in sorted(score_dist.keys(), reverse=True):
            print(f"    {score}/10: {score_dist[score]} papers")

        avg_score = sum(p["score"] for p in top_papers) / len(top_papers) if top_papers else 0
        print(f"\n  ✓ Average score of top papers: {avg_score:.2f}/10")

        self.results["quality_assessment"]["top_papers_avg_score"] = avg_score
        self.results["quality_assessment"]["top_papers_scores"] = score_dist

        return top_papers

    def save_results(self, papers: List[Dict], top_papers: List[Dict]):
        """Save all results to JSON files"""
        print("\n=== Saving Results ===")

        # Save full results
        with open("examples/session64_openalex_papers.json", "w") as f:
            json.dump({
                "metadata": self.results,
                "papers": papers[:100]  # Save first 100 for reference
            }, f, indent=2, default=str)

        # Save top papers for extraction
        with open("examples/session64_top_papers_for_extraction.json", "w") as f:
            json.dump({
                "metadata": {
                    "total": len(top_papers),
                    "avg_score": self.results["quality_assessment"]["top_papers_avg_score"],
                    "score_distribution": self.results["quality_assessment"]["top_papers_scores"]
                },
                "papers": top_papers
            }, f, indent=2, default=str)

        # Save quality assessment
        with open("examples/session64_quality_assessment.json", "w") as f:
            json.dump(self.results["quality_assessment"], f, indent=2, default=str)

        print("  ✓ Results saved to examples/session64_*.json")

    def run(self):
        """Run the complete filtered fetch and quality test"""
        print("=" * 50)
        print("Session 64: OpenAlex Quality Test with Filtered Queries")
        print("=" * 50)

        # Step 1: Fetch papers with abstracts
        papers = self.fetch_papers_with_abstracts(num_papers=500)

        if not papers:
            print("\n✗ No papers fetched. Aborting.")
            return

        # Step 2: Import to PostgreSQL
        self.import_to_postgresql(papers)

        # Step 3: Score papers
        scored_papers = self.score_papers(papers)

        # Step 4: Compare with arXiv
        self.compare_with_arxiv()

        # Step 5: Select top papers
        top_papers = self.select_top_papers(scored_papers, top_n=50)

        # Step 6: Save results
        self.save_results(scored_papers, top_papers)

        # Step 7: Make recommendation
        print("\n" + "=" * 50)
        print("QUALITY ASSESSMENT SUMMARY")
        print("=" * 50)

        avg_score = self.results["quality_assessment"]["average_score"]
        high_value_pct = self.results["quality_assessment"]["high_value_percentage"]
        score_diff = self.results["quality_assessment"].get("arxiv_comparison", {}).get("score_difference", 0)

        print(f"\nOpenAlex Papers (n={len(papers)}):")
        print(f"  • Abstract coverage: 100% (filtered)")
        print(f"  • Average mechanism score: {avg_score:.2f}/10")
        print(f"  • High-value papers (≥5/10): {high_value_pct:.1f}%")
        print(f"  • Score vs arXiv: {score_diff:+.2f}")

        # Make go/no-go decision
        if avg_score >= 3.0 and high_value_pct >= 25:
            print(f"\n✅ RECOMMENDATION: PROCEED WITH OPENALEX")
            print(f"   Quality is comparable to arXiv corpus")
            print(f"   Speed advantage (2,626 papers/min) justifies slight quality tradeoff")
        elif avg_score >= 2.5 and high_value_pct >= 20:
            print(f"\n⚠️ RECOMMENDATION: PROCEED WITH CAUTION")
            print(f"   Quality is lower but acceptable")
            print(f"   Consider supplementing with arXiv for high-value papers")
        else:
            print(f"\n❌ RECOMMENDATION: DO NOT PROCEED")
            print(f"   Quality too low for mechanism extraction")
            print(f"   Test alternative sources (Semantic Scholar, arXiv S3)")

        print("\nNext step: Extract mechanisms from top 50 papers to validate hit rate")

        # Close database connection
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    fetcher = OpenAlexFilteredFetcher()
    fetcher.run()