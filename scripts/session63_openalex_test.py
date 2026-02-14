#!/usr/bin/env python3

"""
Session 63: OpenAlex Testing for Bulk Data Ingestion
Tests OpenAlex API for feasibility of fetching 50K papers
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import sys

try:
    import pyalex
    from pyalex import Works
except ImportError as e:
    print(f"Error importing pyalex: {e}")
    print("Trying alternate import...")
    try:
        import pyalex
        Works = pyalex.Works
    except ImportError:
        print("Error: pyalex not installed. Run: pip install pyalex")
        sys.exit(1)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

# Configure pyalex (email is polite but not required)
pyalex.config.email = "research@analog.quest"

class OpenAlexTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "basic_test": {},
            "data_quality": {},
            "speed_test": {},
            "database_test": {},
            "feasibility": {}
        }

    def test_basic_connection(self):
        """Test basic OpenAlex connection and queries"""
        print("\n=== Testing Basic Connection ===")

        try:
            # Test simple query
            start_time = time.time()
            works = Works().search("network dynamics").get()[:5]
            query_time = time.time() - start_time

            print(f"✓ Basic query successful ({query_time:.2f}s)")
            print(f"  Found {len(works)} works")

            self.results["basic_test"]["status"] = "success"
            self.results["basic_test"]["query_time"] = query_time
            self.results["basic_test"]["works_found"] = len(works)

            # Check data structure
            if works:
                sample_work = works[0]
                fields = list(sample_work.keys())
                print(f"  Available fields: {', '.join(fields[:10])}...")

                # Check critical fields
                critical_fields = ["id", "title", "abstract_inverted_index", "publication_date", "topics"]
                missing = [f for f in critical_fields if f not in sample_work]
                if missing:
                    print(f"  ⚠️ Missing critical fields: {missing}")
                else:
                    print(f"  ✓ All critical fields present")

                self.results["basic_test"]["fields"] = fields
                self.results["basic_test"]["missing_critical"] = missing

            return True

        except Exception as e:
            print(f"✗ Connection failed: {e}")
            self.results["basic_test"]["status"] = "failed"
            self.results["basic_test"]["error"] = str(e)
            return False

    def test_data_quality(self, num_papers: int = 100):
        """Test data quality by fetching papers with mechanism-relevant keywords"""
        print(f"\n=== Testing Data Quality (n={num_papers}) ===")

        # Mechanism-relevant keywords from Session 50 analysis
        keywords = [
            "network dynamics", "feedback control", "emergence",
            "phase transition", "optimization", "adaptation",
            "evolutionary dynamics", "coupling", "synchronization",
            "critical phenomena"
        ]

        all_papers = []
        papers_with_abstracts = 0
        papers_with_topics = 0
        total_fetch_time = 0

        print(f"Fetching papers with keywords: {', '.join(keywords[:3])}...")

        for keyword in keywords[:3]:  # Test first 3 keywords
            try:
                start_time = time.time()
                # Filter for recent papers - note: has_abstract filter may not work as expected
                # OpenAlex abstract filtering may need different approach
                query = (Works()
                    .search(keyword)
                    .filter(from_publication_date="2023-01-01"))

                # Fetch in batches using pagination
                papers = []
                for page in query.paginate(per_page=25):
                    papers.extend(page)
                    if len(papers) >= num_papers // 3:
                        break

                fetch_time = time.time() - start_time
                total_fetch_time += fetch_time

                print(f"  {keyword}: {len(papers)} papers ({fetch_time:.2f}s)")

                for paper in papers:
                    # Check if abstract_inverted_index exists and has content
                    abstract_index = paper.get("abstract_inverted_index")
                    abstract_text = self._extract_abstract(abstract_index) if abstract_index else ""

                    paper_data = {
                        "id": paper.get("id"),
                        "title": paper.get("title"),
                        "abstract": abstract_text,
                        "abstract_available": bool(abstract_index and len(abstract_index) > 0),
                        "publication_date": paper.get("publication_date"),
                        "topics": paper.get("topics", []),
                        "keyword": keyword
                    }

                    all_papers.append(paper_data)
                    if paper_data["abstract_available"]:
                        papers_with_abstracts += 1
                    if paper_data["topics"]:
                        papers_with_topics += 1

            except Exception as e:
                print(f"  ✗ Error fetching '{keyword}': {e}")

        # Calculate quality metrics
        total = len(all_papers)
        if total > 0:
            abstract_rate = papers_with_abstracts / total * 100
            topic_rate = papers_with_topics / total * 100

            print(f"\nQuality Metrics:")
            print(f"  Total papers: {total}")
            print(f"  With abstracts: {papers_with_abstracts} ({abstract_rate:.1f}%)")
            print(f"  With topics: {papers_with_topics} ({topic_rate:.1f}%)")
            print(f"  Avg fetch time: {total_fetch_time/len(keywords[:3]):.2f}s per keyword")

            self.results["data_quality"] = {
                "total_papers": total,
                "with_abstracts": papers_with_abstracts,
                "abstract_rate": abstract_rate,
                "with_topics": papers_with_topics,
                "topic_rate": topic_rate,
                "fetch_time": total_fetch_time,
                "sample_papers": all_papers[:5]  # Store first 5 as sample
            }

            # Save sample papers for review
            with open("examples/session63_sample_papers.json", "w") as f:
                json.dump(all_papers[:20], f, indent=2, default=str)
            print(f"  Sample papers saved to examples/session63_sample_papers.json")

            return abstract_rate >= 80  # Success if 80%+ have abstracts

        return False

    def test_ingestion_speed(self, num_papers: int = 1000):
        """Test ingestion speed for larger batch"""
        print(f"\n=== Testing Ingestion Speed (n={num_papers}) ===")

        # Use broad query to get many papers quickly
        print("Fetching papers on 'machine learning'...")

        try:
            start_time = time.time()

            query = (Works()
                .search("machine learning")
                .filter(from_publication_date="2024-01-01")
                .filter(has_abstract=True))

            papers = []
            batch_times = []

            # Fetch in batches
            for page_num, page in enumerate(query.paginate(per_page=100)):
                batch_start = time.time()
                papers.extend(page)
                batch_time = time.time() - batch_start
                batch_times.append(batch_time)

                print(f"  Batch {page_num+1}: {len(page)} papers ({batch_time:.2f}s)")

                if len(papers) >= num_papers:
                    break

            total_time = time.time() - start_time
            papers_fetched = len(papers[:num_papers])

            # Calculate metrics
            avg_batch_time = sum(batch_times) / len(batch_times) if batch_times else 0
            papers_per_second = papers_fetched / total_time if total_time > 0 else 0
            papers_per_minute = papers_per_second * 60
            time_for_50k = 50000 / papers_per_second / 60 if papers_per_second > 0 else float('inf')

            print(f"\nSpeed Metrics:")
            print(f"  Total papers: {papers_fetched}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Avg batch time: {avg_batch_time:.2f}s")
            print(f"  Papers/second: {papers_per_second:.1f}")
            print(f"  Papers/minute: {papers_per_minute:.1f}")
            print(f"  Est. time for 50K papers: {time_for_50k:.1f} minutes")

            self.results["speed_test"] = {
                "papers_fetched": papers_fetched,
                "total_time": total_time,
                "papers_per_second": papers_per_second,
                "papers_per_minute": papers_per_minute,
                "est_time_50k_minutes": time_for_50k,
                "batch_times": batch_times
            }

            # Save for database test
            self.test_papers = papers[:100]  # Keep first 100 for DB test

            return papers_per_minute >= 100  # Success if > 100 papers/min

        except Exception as e:
            print(f"✗ Speed test failed: {e}")
            self.results["speed_test"]["error"] = str(e)
            return False

    def test_database_integration(self):
        """Test importing papers into PostgreSQL"""
        print("\n=== Testing Database Integration ===")

        if not hasattr(self, 'test_papers') or not self.test_papers:
            print("✗ No test papers available. Run speed test first.")
            return False

        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                dbname="analog_quest",
                user="user",
                host="localhost",
                port=5432
            )
            cur = conn.cursor(cursor_factory=RealDictCursor)

            print("✓ Connected to PostgreSQL")

            # Test insert with deduplication
            inserted = 0
            duplicates = 0
            errors = 0

            start_time = time.time()

            for paper in self.test_papers[:10]:  # Test with first 10
                try:
                    # Extract data
                    openalex_id = paper.get("id", "").split("/")[-1]  # Extract ID from URL
                    title = paper.get("title", "")[:500]  # Truncate if needed
                    abstract = self._extract_abstract(paper.get("abstract_inverted_index"))

                    if not title or not abstract:
                        errors += 1
                        continue

                    # Check for duplicate
                    cur.execute(
                        "SELECT id FROM papers WHERE title = %s",
                        (title,)
                    )

                    if cur.fetchone():
                        duplicates += 1
                    else:
                        # Insert new paper (without ON CONFLICT since arxiv_id may not have constraint)
                        cur.execute("""
                            INSERT INTO papers (title, abstract, domain, published_date, arxiv_id)
                            VALUES (%s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            title,
                            abstract[:2000] if abstract else "",  # Truncate abstract if needed
                            "openalex",  # Mark as from OpenAlex
                            paper.get("publication_date"),
                            f"openalex_{openalex_id}"  # Use OpenAlex ID as arxiv_id
                        ))

                        if cur.fetchone():
                            inserted += 1

                except Exception as e:
                    print(f"  Error inserting paper: {e}")
                    errors += 1
                    conn.rollback()  # Rollback on error
                    continue

            import_time = time.time() - start_time

            # Commit changes if any successful inserts
            if inserted > 0:
                conn.commit()

            print(f"\nDatabase Results:")
            print(f"  Inserted: {inserted}")
            print(f"  Duplicates: {duplicates}")
            print(f"  Errors: {errors}")
            print(f"  Import time: {import_time:.2f}s")
            print(f"  Avg time per paper: {import_time/10:.3f}s")

            self.results["database_test"] = {
                "inserted": inserted,
                "duplicates": duplicates,
                "errors": errors,
                "import_time": import_time,
                "avg_time_per_paper": import_time/10
            }

            cur.close()
            conn.close()

            return inserted > 0

        except Exception as e:
            print(f"✗ Database test failed: {e}")
            self.results["database_test"]["error"] = str(e)
            return False

    def _extract_abstract(self, inverted_index: Optional[Dict]) -> str:
        """Convert OpenAlex inverted index to abstract text"""
        if not inverted_index:
            return ""

        # Reconstruct abstract from inverted index
        words = []
        for word, positions in inverted_index.items():
            for pos in positions:
                words.append((pos, word))

        # Sort by position and join
        words.sort(key=lambda x: x[0])
        return " ".join(word[1] for word in words)

    def assess_feasibility(self):
        """Overall feasibility assessment"""
        print("\n=== Feasibility Assessment ===")

        # Check all test results
        basic_ok = self.results["basic_test"].get("status") == "success"
        quality_ok = self.results["data_quality"].get("abstract_rate", 0) >= 80
        speed_ok = self.results["speed_test"].get("papers_per_minute", 0) >= 100
        db_ok = self.results["database_test"].get("inserted", 0) > 0

        # Calculate time estimates
        papers_per_minute = self.results["speed_test"].get("papers_per_minute", 0)
        if papers_per_minute > 0:
            time_50k = 50000 / papers_per_minute
            time_50k_hours = time_50k / 60
        else:
            time_50k_hours = float('inf')

        print(f"Test Results:")
        print(f"  Basic connection: {'✓' if basic_ok else '✗'}")
        print(f"  Data quality (>80% abstracts): {'✓' if quality_ok else '✗'}")
        print(f"  Speed (>100 papers/min): {'✓' if speed_ok else '✗'}")
        print(f"  Database integration: {'✓' if db_ok else '✗'}")

        print(f"\nProjections for 50K papers:")
        print(f"  Estimated time: {time_50k_hours:.1f} hours")
        print(f"  Abstract availability: {self.results['data_quality'].get('abstract_rate', 0):.1f}%")
        print(f"  Topic coverage: {self.results['data_quality'].get('topic_rate', 0):.1f}%")

        # Overall recommendation
        all_tests_pass = all([basic_ok, quality_ok, speed_ok, db_ok])

        if all_tests_pass and time_50k_hours <= 1:
            recommendation = "HIGHLY FEASIBLE - OpenAlex meets all requirements"
            status = "highly_feasible"
        elif all_tests_pass and time_50k_hours <= 3:
            recommendation = "FEASIBLE - OpenAlex suitable, may take 1-3 hours"
            status = "feasible"
        elif quality_ok and db_ok:
            recommendation = "PARTIALLY FEASIBLE - Consider smaller batches or filtering"
            status = "partially_feasible"
        else:
            recommendation = "NOT FEASIBLE - Consider alternative sources"
            status = "not_feasible"

        print(f"\n{'='*50}")
        print(f"RECOMMENDATION: {recommendation}")
        print(f"{'='*50}")

        self.results["feasibility"] = {
            "all_tests_pass": all_tests_pass,
            "time_50k_hours": time_50k_hours,
            "recommendation": recommendation,
            "status": status,
            "basic_ok": basic_ok,
            "quality_ok": quality_ok,
            "speed_ok": speed_ok,
            "db_ok": db_ok
        }

        return status in ["highly_feasible", "feasible"]

    def save_results(self):
        """Save test results to JSON"""
        output_path = "examples/session63_openalex_results.json"
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults saved to {output_path}")

        return self.results

def main():
    print("="*50)
    print("Session 63: OpenAlex Testing for Bulk Data Ingestion")
    print("="*50)

    tester = OpenAlexTester()

    # Run tests in sequence
    if tester.test_basic_connection():
        tester.test_data_quality(num_papers=100)
        tester.test_ingestion_speed(num_papers=1000)
        tester.test_database_integration()

    # Final assessment
    feasible = tester.assess_feasibility()

    # Save results
    results = tester.save_results()

    return feasible, results

if __name__ == "__main__":
    feasible, results = main()
    sys.exit(0 if feasible else 1)