#!/usr/bin/env python3
"""
Build targeted arXiv search queries from validated keywords.
Session 50 - Part 3: Design keyword-targeted arXiv queries
"""

import json
from typing import Dict, List


# Good domains based on Session 46 audit (avg mechanism richness ≥3.5/10)
GOOD_DOMAINS = {
    "q-bio": ["q-bio.PE", "q-bio.CB", "q-bio.QM", "q-bio.MN"],
    "physics": ["physics.soc-ph", "physics.bio-ph", "cond-mat.stat-mech"],
    "cs": ["cs.AI", "cs.LG", "cs.SI", "cs.GT", "cs.MA"],
    "econ": ["econ.GN", "econ.TH", "q-fin.EC"],
    "nlin": ["nlin.CD", "nlin.AO"],
}


def load_validation_results(filepath: str) -> Dict:
    """Load keyword validation results."""
    with open(filepath, 'r') as f:
        return json.load(f)


def build_arxiv_queries(validation_results: Dict) -> List[Dict]:
    """Build targeted arXiv search queries from top discriminating keywords."""

    top_keywords = validation_results["top_10_discriminators"]

    queries = []

    # Query 1: Network dynamics in biology and social systems
    queries.append({
        "name": "network_dynamics",
        "description": "Network structure, topology, and dynamics in biological and social systems",
        "keywords": ["network", "network structure", "network topology", "centrality"],
        "domains": ["q-bio.*", "physics.soc-ph", "physics.bio-ph"],
        "query": "(abs:network OR abs:\"network structure\" OR abs:\"network topology\" OR abs:centrality) AND (cat:q-bio.* OR cat:physics.soc-ph OR cat:physics.bio-ph)",
        "expected_hit_rate": 0.355,  # Based on high-value hit rate for "network"
        "discrimination_power": 0.248,
        "rationale": "Network keywords show highest discrimination (24.8%). Biology and social physics are high-mechanism-richness domains."
    })

    # Query 2: Optimization and control in all good domains
    queries.append({
        "name": "optimization_control",
        "description": "Optimization, control, and regulation mechanisms across domains",
        "keywords": ["optimization", "optimize", "optimal", "control", "regulation"],
        "domains": ["q-bio.*", "cs.AI", "cs.LG", "econ.*"],
        "query": "(abs:optimization OR abs:optimize OR abs:optimal OR abs:control OR abs:regulation) AND (cat:q-bio.* OR cat:cs.AI OR cat:cs.LG OR cat:econ.*)",
        "expected_hit_rate": 0.386,  # Based on "optimization" high-value hit rate
        "discrimination_power": 0.246,
        "rationale": "Optimization has 24.6% discrimination. CS.AI, CS.LG, and economics focus on optimization problems."
    })

    # Query 3: Adaptive and evolutionary dynamics
    queries.append({
        "name": "adaptive_evolutionary",
        "description": "Adaptation, evolution, and selection mechanisms",
        "keywords": ["adaptation", "adaptive", "evolution", "evolutionary", "selection"],
        "domains": ["q-bio.*", "physics.bio-ph", "cs.LG"],
        "query": "(abs:adaptation OR abs:adaptive OR abs:evolution OR abs:evolutionary OR abs:selection) AND (cat:q-bio.* OR cat:physics.bio-ph OR cat:cs.LG)",
        "expected_hit_rate": 0.311,  # Based on "adaptation" high-value hit rate
        "discrimination_power": 0.237,
        "rationale": "Adaptation shows 23.7% discrimination. Evolutionary dynamics are rich in mechanisms."
    })

    # Query 4: Critical phenomena and phase transitions
    queries.append({
        "name": "critical_phenomena",
        "description": "Critical slowing, phase transitions, and bifurcations",
        "keywords": ["critical", "criticality", "bifurcation", "phase transition"],
        "domains": ["nlin.CD", "cond-mat.*", "physics.soc-ph", "q-bio.*"],
        "query": "(abs:critical OR abs:criticality OR abs:bifurcation OR abs:\"phase transition\") AND (cat:nlin.CD OR cat:cond-mat.* OR cat:physics.soc-ph OR cat:q-bio.*)",
        "expected_hit_rate": 0.263,  # Based on "criticality" high-value hit rate
        "discrimination_power": 0.194,
        "rationale": "Criticality shows 19.4% discrimination. Nonlinear dynamics papers are mechanism-rich."
    })

    # Query 5: Feedback and homeostasis in biological systems
    queries.append({
        "name": "feedback_homeostasis",
        "description": "Feedback loops, homeostasis, and regulatory circuits",
        "keywords": ["feedback", "homeostasis", "regulation", "regulatory"],
        "domains": ["q-bio.*", "physics.bio-ph"],
        "query": "(abs:feedback OR abs:homeostasis OR abs:regulation OR abs:regulatory) AND (cat:q-bio.* OR cat:physics.bio-ph)",
        "expected_hit_rate": 0.295,  # Estimated from feedback + regulation hit rates
        "discrimination_power": 0.180,
        "rationale": "Feedback and regulation are core biological mechanisms. Q-bio is highest-richness domain (4.5/10 avg)."
    })

    # Query 6: Coupling and synchronization
    queries.append({
        "name": "coupling_synchronization",
        "description": "Coupled systems, synchronization, and collective behavior",
        "keywords": ["coupling", "coupled", "synchronization", "collective"],
        "domains": ["nlin.*", "physics.soc-ph", "q-bio.*"],
        "query": "(abs:coupling OR abs:coupled OR abs:synchronization OR abs:collective) AND (cat:nlin.* OR cat:physics.soc-ph OR cat:q-bio.*)",
        "expected_hit_rate": 0.199,  # Based on "coupling" high-value hit rate
        "discrimination_power": 0.140,
        "rationale": "Coupling dynamics are central to complex systems. Nonlinear dynamics domain is mechanism-rich."
    })

    # Query 7: Heterogeneity and diversity effects
    queries.append({
        "name": "heterogeneity_diversity",
        "description": "Heterogeneity, diversity, and variance effects on system dynamics",
        "keywords": ["heterogeneity", "heterogeneous", "diversity", "variance"],
        "domains": ["q-bio.*", "physics.soc-ph", "econ.*"],
        "query": "(abs:heterogeneity OR abs:heterogeneous OR abs:diversity OR abs:variance) AND (cat:q-bio.* OR cat:physics.soc-ph OR cat:econ.*)",
        "expected_hit_rate": 0.147,  # Based on "heterogeneity" high-value hit rate
        "discrimination_power": 0.103,
        "rationale": "Heterogeneity creates rich structural dynamics. Economics and biology study population diversity."
    })

    # Query 8: Cooperation and competition
    queries.append({
        "name": "cooperation_competition",
        "description": "Cooperation, competition, and game-theoretic interactions",
        "keywords": ["cooperation", "competition", "coexistence", "game theory"],
        "domains": ["q-bio.*", "econ.*", "cs.GT"],
        "query": "(abs:cooperation OR abs:competition OR abs:coexistence OR abs:\"game theory\") AND (cat:q-bio.* OR cat:econ.* OR cat:cs.GT)",
        "expected_hit_rate": 0.220,  # Estimated from cooperation + competition
        "discrimination_power": 0.150,
        "rationale": "Game-theoretic dynamics generate rich mechanisms. Game theory and economics are natural targets."
    })

    return queries


def main():
    # Load validation results
    validation_results = load_validation_results("examples/session50_keyword_validation.json")

    # Build queries
    queries = build_arxiv_queries(validation_results)

    # Prepare output
    output = {
        "generation_date": "2026-02-12",
        "total_queries": len(queries),
        "query_templates": queries,
        "usage_notes": [
            "Use arXiv API with these queries to fetch targeted papers",
            "expected_hit_rate is based on keyword presence in high-value papers (≥7/10)",
            "discrimination_power shows keyword effectiveness (high vs low value papers)",
            "Target recent papers (2024-2025) for maximum relevance",
            "Combine multiple queries to diversify mechanism types"
        ],
        "arxiv_api_example": {
            "base_url": "http://export.arxiv.org/api/query",
            "parameters": {
                "search_query": "(query from above)",
                "start": 0,
                "max_results": 30,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
        },
        "validation_summary": {
            "total_keywords_tested": validation_results["total_keywords"],
            "overall_discrimination": validation_results["overall_validation"]["discrimination_power"],
            "high_value_coverage": validation_results["overall_validation"]["high_value"]["hit_rate"],
            "low_value_coverage": validation_results["overall_validation"]["low_value"]["hit_rate"]
        }
    }

    # Save output
    with open("examples/session50_search_queries.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Built {len(queries)} targeted arXiv search queries")
    print(f"\nQuery templates:")
    for i, q in enumerate(queries, 1):
        print(f"\n{i}. {q['name']}")
        print(f"   Description: {q['description']}")
        print(f"   Expected hit rate: {q['expected_hit_rate']*100:.1f}%")
        print(f"   Discrimination: {q['discrimination_power']*100:.1f}%")
        print(f"   Query: {q['query'][:100]}...")

    print(f"\n✓ Output saved to: examples/session50_search_queries.json")


if __name__ == "__main__":
    main()
