#!/usr/bin/env python3
"""
Sustainable Pipeline for Analog Quest
Session 69 - Build for long-term continuous research

This pipeline is designed to run repeatedly, adding value incrementally
each session rather than racing toward arbitrary endpoints.
"""

import os
import sys
import json
import yaml
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer
import requests
from pyalex import Works

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Paper:
    """Paper data structure"""
    title: str
    abstract: str
    openalex_id: str
    domain: str
    subdomain: str
    published_date: str
    citations: int
    mechanism_score: Optional[float] = None

@dataclass
class Mechanism:
    """Mechanism data structure"""
    paper_id: int
    description: str
    structural_description: str
    mechanism_type: str
    domain: str
    embedding: Optional[np.ndarray] = None

@dataclass
class PipelineMetrics:
    """Metrics for tracking pipeline performance"""
    papers_fetched: int = 0
    papers_scored: int = 0
    high_value_papers: int = 0
    mechanisms_extracted: int = 0
    embeddings_generated: int = 0
    candidates_generated: int = 0
    total_cost: float = 0.0
    time_elapsed: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class PipelineCheckpoint:
    """Handle checkpoint saving and loading for resumability"""

    def __init__(self, checkpoint_file: str):
        self.checkpoint_file = checkpoint_file
        self.state = {}
        self.load()

    def load(self):
        """Load checkpoint from file"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    self.state = json.load(f)
                logger.info(f"Loaded checkpoint: {self.state}")
            except Exception as e:
                logger.warning(f"Could not load checkpoint: {e}")
                self.state = {}

    def save(self):
        """Save checkpoint to file"""
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.debug("Checkpoint saved")
        except Exception as e:
            logger.error(f"Could not save checkpoint: {e}")

    def get(self, key: str, default=None):
        """Get value from checkpoint"""
        return self.state.get(key, default)

    def set(self, key: str, value: Any):
        """Set value in checkpoint"""
        self.state[key] = value
        self.save()

class SustainablePipeline:
    """
    Main pipeline class - designed for sustainability and repeatability
    """

    def __init__(self, config_path: str = "config/pipeline_config.yaml"):
        """Initialize pipeline with configuration"""
        self.config = self._load_config(config_path)
        self.metrics = PipelineMetrics()
        self.checkpoint = PipelineCheckpoint(self.config['progress']['checkpoint_file'])
        self.embedding_model = None
        self.db_conn = None
        self.start_time = time.time()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def _connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user']
            )
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def _close_db(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            logger.info("Database connection closed")

    # ========== PHASE 1: FETCH PAPERS ==========

    def fetch_papers(self, num_papers: int = 100) -> List[Paper]:
        """
        Fetch papers from OpenAlex with mechanism-relevant search terms
        """
        logger.info(f"=== PHASE 1: Fetching {num_papers} papers from OpenAlex ===")

        papers = []
        search_terms = self.config['search_terms']
        papers_per_term = num_papers // len(search_terms)

        for term in search_terms:
            try:
                logger.info(f"Searching for: {term}")

                # Use OpenAlex API
                works = Works().search(term).filter(has_abstract=True).get()

                count = 0
                for work in works:
                    if count >= papers_per_term:
                        break

                    # Extract paper data
                    paper = Paper(
                        title=work.get('title', ''),
                        abstract=self._extract_abstract(work),
                        openalex_id=work.get('id', ''),
                        domain=self._extract_domain(work),
                        subdomain='',
                        published_date=work.get('publication_date', ''),
                        citations=work.get('cited_by_count', 0)
                    )

                    if paper.title and paper.abstract:
                        papers.append(paper)
                        count += 1

                logger.info(f"  Fetched {count} papers for '{term}'")

            except Exception as e:
                logger.error(f"Error fetching papers for '{term}': {e}")
                self.metrics.errors.append(f"Fetch error: {term}: {str(e)}")

        self.metrics.papers_fetched = len(papers)
        logger.info(f"Total papers fetched: {len(papers)}")

        # Save papers to checkpoint
        self.checkpoint.set('fetched_papers', [asdict(p) for p in papers])

        return papers

    def _extract_abstract(self, work: Dict) -> str:
        """Extract abstract from OpenAlex work object"""
        inverted_index = work.get('abstract_inverted_index', {})
        if not inverted_index:
            return ""

        # Reconstruct abstract from inverted index
        words = []
        for word, positions in inverted_index.items():
            for pos in positions:
                words.append((pos, word))
        words.sort()
        return ' '.join([word for _, word in words])

    def _extract_domain(self, work: Dict) -> str:
        """Extract domain from OpenAlex work topics"""
        topics = work.get('topics', [])
        if topics and len(topics) > 0:
            return topics[0].get('display_name', 'unknown')
        return 'unknown'

    # ========== PHASE 2: SCORE PAPERS ==========

    def score_papers(self, papers: List[Paper]) -> List[Paper]:
        """
        Score papers for mechanism richness (0-10 scale)
        """
        logger.info("=== PHASE 2: Scoring papers for mechanism richness ===")

        for paper in papers:
            try:
                score = self._calculate_mechanism_score(paper)
                paper.mechanism_score = score

                if score >= self.config['quality']['min_mechanism_score']:
                    self.metrics.high_value_papers += 1

            except Exception as e:
                logger.error(f"Error scoring paper: {e}")
                paper.mechanism_score = 0.0

        self.metrics.papers_scored = len(papers)

        # Sort by score
        papers.sort(key=lambda p: p.mechanism_score or 0, reverse=True)

        logger.info(f"Scored {len(papers)} papers")
        logger.info(f"High-value papers (≥{self.config['quality']['min_mechanism_score']}): {self.metrics.high_value_papers}")

        # Save to checkpoint
        self.checkpoint.set('scored_papers', [asdict(p) for p in papers])

        return papers

    def _calculate_mechanism_score(self, paper: Paper) -> float:
        """
        Calculate mechanism richness score (0-10)
        Based on presence of mechanism-indicating keywords
        """
        abstract_lower = paper.abstract.lower()
        title_lower = paper.title.lower()
        combined = f"{title_lower} {abstract_lower}"

        # Mechanism indicators
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

        # Count indicators
        strong_count = sum(1 for ind in strong_indicators if ind in combined)
        moderate_count = sum(1 for ind in moderate_indicators if ind in combined)
        weak_count = sum(1 for ind in weak_indicators if ind in combined)

        # Calculate score
        score = min(10, (strong_count * 3) + (moderate_count * 1.5) + (weak_count * 0.5))

        # Boost for multiple strong indicators
        if strong_count >= 3:
            score = min(10, score + 2)

        # Penalty for too short
        if len(abstract_lower.split()) < 50:
            score = max(0, score - 2)

        return round(score, 1)

    # ========== PHASE 3: EXTRACT MECHANISMS ==========

    def extract_mechanisms(self, papers: List[Paper]) -> List[Mechanism]:
        """
        Extract mechanisms from high-value papers using LLM
        For Session 69: Start with manual simulation, test API costs
        """
        logger.info("=== PHASE 3: Extracting mechanisms from papers ===")

        # Filter high-value papers
        high_value_papers = [
            p for p in papers
            if p.mechanism_score and p.mechanism_score >= self.config['quality']['min_mechanism_score']
        ]

        logger.info(f"Extracting from {len(high_value_papers)} high-value papers")

        mechanisms = []

        # For Session 69: Simulate extraction with realistic hit rates
        # In production: Use actual LLM API
        for paper in high_value_papers[:10]:  # Limit to 10 for testing
            try:
                mechanism = self._extract_mechanism_from_paper(paper)
                if mechanism:
                    mechanisms.append(mechanism)
                    self.metrics.mechanisms_extracted += 1

            except Exception as e:
                logger.error(f"Error extracting from paper: {e}")
                self.metrics.errors.append(f"Extraction error: {str(e)}")

        logger.info(f"Extracted {len(mechanisms)} mechanisms")

        # Calculate cost
        if self.config['llm']['provider'] == 'anthropic':
            # Haiku pricing: $0.25 per million input tokens, $1.25 per million output tokens
            # Estimate: 500 tokens in, 200 tokens out per paper
            input_tokens = len(mechanisms) * 500
            output_tokens = len(mechanisms) * 200
            cost = (input_tokens * 0.25 + output_tokens * 1.25) / 1_000_000
            self.metrics.total_cost += cost
            logger.info(f"Estimated extraction cost: ${cost:.4f}")

        # Save to checkpoint
        self.checkpoint.set('extracted_mechanisms', [asdict(m) for m in mechanisms])

        return mechanisms

    def _extract_mechanism_from_paper(self, paper: Paper) -> Optional[Mechanism]:
        """
        Extract mechanism from a single paper
        For Session 69: Return simulated mechanism
        In production: Call actual LLM API
        """
        # Simulate extraction (60% hit rate based on historical data)
        if np.random.random() < 0.6:
            return Mechanism(
                paper_id=0,  # Will be set when storing to DB
                description=f"Mechanism from: {paper.title[:50]}...",
                structural_description="Two-component system where A increases B and B decreases A, creating oscillatory dynamics",
                mechanism_type="feedback_loop",
                domain=paper.domain
            )
        return None

    # ========== PHASE 4: GENERATE EMBEDDINGS ==========

    def generate_embeddings(self, mechanisms: List[Mechanism]) -> List[Mechanism]:
        """
        Generate semantic embeddings for mechanisms
        """
        logger.info("=== PHASE 4: Generating embeddings ===")

        if not self.embedding_model:
            self.embedding_model = SentenceTransformer(self.config['embeddings']['model'])
            logger.info(f"Loaded embedding model: {self.config['embeddings']['model']}")

        # Extract descriptions for embedding
        descriptions = [m.structural_description for m in mechanisms]

        if descriptions:
            # Generate embeddings
            embeddings = self.embedding_model.encode(descriptions)

            # Attach to mechanisms
            for mechanism, embedding in zip(mechanisms, embeddings):
                mechanism.embedding = embedding
                self.metrics.embeddings_generated += 1

        logger.info(f"Generated {self.metrics.embeddings_generated} embeddings")

        return mechanisms

    # ========== PHASE 5: STORE IN DATABASE ==========

    def store_to_database(self, papers: List[Paper], mechanisms: List[Mechanism]) -> bool:
        """
        Store papers and mechanisms in PostgreSQL
        """
        logger.info("=== PHASE 5: Storing to database ===")

        try:
            self._connect_db()
            cursor = self.db_conn.cursor()

            # Store papers
            papers_stored = 0
            for paper in papers:
                if paper.mechanism_score and paper.mechanism_score >= self.config['quality']['min_mechanism_score']:
                    cursor.execute("""
                        INSERT INTO papers (title, abstract, domain, subdomain, arxiv_id, published_date, mechanism_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (title) DO NOTHING
                        RETURNING id
                    """, (
                        paper.title,
                        paper.abstract,
                        paper.domain,
                        paper.subdomain,
                        paper.openalex_id,
                        paper.published_date,
                        paper.mechanism_score
                    ))

                    result = cursor.fetchone()
                    if result:
                        paper_id = result[0]
                        papers_stored += 1

                        # Store associated mechanisms
                        for mechanism in [m for m in mechanisms if paper.title in m.description]:
                            if mechanism.embedding is not None:
                                cursor.execute("""
                                    INSERT INTO mechanisms (paper_id, description, structural_description,
                                                          mechanism_type, domain, embedding)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (
                                    paper_id,
                                    mechanism.description,
                                    mechanism.structural_description,
                                    mechanism.mechanism_type,
                                    mechanism.domain,
                                    mechanism.embedding.tolist()
                                ))

            self.db_conn.commit()
            logger.info(f"Stored {papers_stored} papers and {len(mechanisms)} mechanisms")

            return True

        except Exception as e:
            logger.error(f"Database storage error: {e}")
            self.metrics.errors.append(f"Storage error: {str(e)}")
            if self.db_conn:
                self.db_conn.rollback()
            return False

        finally:
            self._close_db()

    # ========== PHASE 6: GENERATE CANDIDATES ==========

    def generate_candidates(self) -> int:
        """
        Generate cross-domain candidate pairs using pgvector
        """
        logger.info("=== PHASE 6: Generating candidate pairs ===")

        try:
            self._connect_db()
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)

            # Query for similar mechanisms across domains
            cursor.execute("""
                SELECT
                    m1.id as id1,
                    m2.id as id2,
                    m1.domain as domain1,
                    m2.domain as domain2,
                    1 - (m1.embedding <=> m2.embedding) as similarity
                FROM mechanisms m1, mechanisms m2
                WHERE m1.id < m2.id
                    AND m1.domain != m2.domain
                    AND 1 - (m1.embedding <=> m2.embedding) >= %s
                ORDER BY similarity DESC
                LIMIT 1000
            """, (self.config['quality']['min_similarity'],))

            candidates = cursor.fetchall()
            self.metrics.candidates_generated = len(candidates)

            logger.info(f"Generated {len(candidates)} candidate pairs")

            # Save top candidates to file for review
            if candidates:
                with open('examples/session69_candidates.json', 'w') as f:
                    json.dump(candidates[:100], f, indent=2, default=str)
                logger.info("Saved top 100 candidates to examples/session69_candidates.json")

            return len(candidates)

        except Exception as e:
            logger.error(f"Candidate generation error: {e}")
            self.metrics.errors.append(f"Candidate error: {str(e)}")
            return 0

        finally:
            self._close_db()

    # ========== MAIN PIPELINE EXECUTION ==========

    def run(self, num_papers: int = None):
        """
        Run the complete pipeline
        """
        logger.info("="*60)
        logger.info("STARTING SUSTAINABLE PIPELINE - Session 69")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info("="*60)

        if num_papers is None:
            num_papers = self.config['quality']['batch_size']

        try:
            # Phase 1: Fetch papers
            papers = self.fetch_papers(num_papers)

            # Phase 2: Score papers
            papers = self.score_papers(papers)

            # Phase 3: Extract mechanisms
            mechanisms = self.extract_mechanisms(papers)

            # Phase 4: Generate embeddings
            mechanisms = self.generate_embeddings(mechanisms)

            # Phase 5: Store to database
            success = self.store_to_database(papers, mechanisms)

            # Phase 6: Generate candidates
            if success:
                self.generate_candidates()

            # Calculate final metrics
            self.metrics.time_elapsed = time.time() - self.start_time

            # Save metrics
            self._save_metrics()

            # Print summary
            self._print_summary()

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            logger.error(traceback.format_exc())
            self.metrics.errors.append(f"Pipeline failure: {str(e)}")
            self._save_metrics()
            sys.exit(1)

    def _save_metrics(self):
        """Save metrics to file"""
        metrics_dict = asdict(self.metrics)
        metrics_dict['timestamp'] = datetime.now().isoformat()

        with open(self.config['progress']['metrics_file'], 'w') as f:
            json.dump(metrics_dict, f, indent=2)

        logger.info(f"Metrics saved to {self.config['progress']['metrics_file']}")

    def _print_summary(self):
        """Print pipeline summary"""
        logger.info("="*60)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*60)
        logger.info(f"Papers fetched: {self.metrics.papers_fetched}")
        logger.info(f"Papers scored: {self.metrics.papers_scored}")
        logger.info(f"High-value papers: {self.metrics.high_value_papers}")
        logger.info(f"Mechanisms extracted: {self.metrics.mechanisms_extracted}")
        logger.info(f"Embeddings generated: {self.metrics.embeddings_generated}")
        logger.info(f"Candidates generated: {self.metrics.candidates_generated}")
        logger.info(f"Total cost: ${self.metrics.total_cost:.4f}")
        logger.info(f"Time elapsed: {self.metrics.time_elapsed:.1f} seconds")

        if self.metrics.errors:
            logger.warning(f"Errors encountered: {len(self.metrics.errors)}")
            for error in self.metrics.errors[:5]:  # Show first 5 errors
                logger.warning(f"  - {error}")

        # Success rate
        if self.metrics.high_value_papers > 0:
            extraction_rate = self.metrics.mechanisms_extracted / self.metrics.high_value_papers * 100
            logger.info(f"Extraction rate: {extraction_rate:.1f}%")

        logger.info("="*60)

def main():
    """Main entry point"""
    pipeline = SustainablePipeline()

    # Check cost limit
    if pipeline.checkpoint.get('total_cost_today', 0) > pipeline.config['cost']['max_per_session']:
        logger.warning("Daily cost limit reached. Exiting.")
        sys.exit(1)

    # Run pipeline
    pipeline.run(num_papers=100)

if __name__ == "__main__":
    main()