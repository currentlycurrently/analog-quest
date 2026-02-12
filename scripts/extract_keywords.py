#!/usr/bin/env python3
"""
Extract structural keywords from mechanism descriptions.
Session 50 - Part 1: Keyword extraction from 104 mechanisms
"""

import json
import re
from collections import Counter
from typing import Dict, List, Tuple

# Structural keywords to look for (process, relationship, dynamics)
STRUCTURAL_KEYWORDS = {
    # Process words - fundamental dynamics
    "feedback": ["feedback", "feedback loop", "positive feedback", "negative feedback"],
    "coevolution": ["coevolve", "coevolution", "co-evolution", "coevolving"],
    "cascade": ["cascade", "cascading"],
    "oscillation": ["oscillate", "oscillation", "oscillating", "oscillatory"],
    "equilibrium": ["equilibrium", "nash equilibrium"],
    "bifurcation": ["bifurcation"],
    "criticality": ["critical", "criticality", "critical slowing"],
    "emergence": ["emerge", "emergence", "emergent"],
    "self-organization": ["self-organization", "self-organizing"],
    "homeostasis": ["homeostasis", "homeostatic"],

    # Relationship/structure words
    "threshold": ["threshold", "critical threshold"],
    "heterogeneity": ["heterogeneity", "heterogeneous"],
    "trade-off": ["trade-off", "tradeoff", "trade off"],
    "complementarity": ["complementarity", "complementarities", "complementary"],
    "coupling": ["coupling", "coupled", "decoupling"],
    "synchronization": ["synchronization", "synchronize", "synchronized"],

    # Network/spatial concepts
    "network": ["network", "network structure", "network topology"],
    "centrality": ["centrality", "central"],
    "diffusion": ["diffusion", "diffuse", "diffusing"],
    "spatial": ["spatial", "spatial structure"],
    "cascade": ["cascade", "cascading"],
    "contagion": ["contagion", "contagious"],
    "propagation": ["propagate", "propagation"],

    # Evolutionary/adaptive dynamics
    "selection": ["selection", "selected", "selecting"],
    "adaptation": ["adaptation", "adaptive", "adapting", "adapt"],
    "cooperation": ["cooperation", "cooperative", "cooperate"],
    "competition": ["competition", "competitive", "compete", "competing"],
    "coexistence": ["coexistence", "coexist"],

    # Optimization/control
    "optimization": ["optimization", "optimize", "optimal"],
    "control": ["control", "controlled"],
    "regulation": ["regulation", "regulate", "regulatory"],

    # Stochastic/variability
    "stochastic": ["stochastic", "stochasticity"],
    "noise": ["noise", "noisy"],
    "variability": ["variability", "variable", "variance"],
    "fluctuation": ["fluctuation", "fluctuating", "fluctuate"],

    # Phase/state transitions
    "phase_transition": ["phase transition", "phase transitions"],
    "bistability": ["bistability", "bistable"],
    "metastability": ["metastability", "metastable"],
    "hysteresis": ["hysteresis"],

    # System properties
    "nonlinearity": ["nonlinear", "nonlinearity", "non-linear"],
    "scaling": ["scaling", "scale"],
    "universality": ["universality", "universal"],
    "robustness": ["robustness", "robust"],

    # Specific mechanisms
    "allee_effect": ["allee effect", "allee effects"],
    "prisoner_dilemma": ["prisoner's dilemma", "prisoner dilemma", "cooperation dilemma"],
    "free_rider": ["free-rider", "free rider", "free riding"],
    "spillover": ["spillover", "spillovers"],
}


def load_mechanisms(filepath: str) -> List[Dict]:
    """Load mechanisms from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def extract_text(mechanism: Dict) -> str:
    """Extract mechanism description text from mechanism object."""
    # Handle both "mechanism" and "mechanism_description" fields
    text = mechanism.get("mechanism", "")
    if not text:
        text = mechanism.get("mechanism_description", "")
    return text.lower()


def count_keyword_occurrences(mechanisms: List[Dict], keywords: Dict[str, List[str]]) -> Dict[str, Dict]:
    """Count how many mechanisms contain each keyword category."""
    total_mechanisms = len(mechanisms)
    keyword_stats = {}

    for category, patterns in keywords.items():
        matching_mechanisms = set()
        matching_examples = []

        for i, mech in enumerate(mechanisms):
            text = extract_text(mech)

            # Check if any pattern matches
            matched = False
            for pattern in patterns:
                if pattern in text:
                    matched = True
                    break

            if matched:
                matching_mechanisms.add(i)
                if len(matching_examples) < 3:  # Store up to 3 examples
                    matching_examples.append(mech.get("paper_id", i))

        count = len(matching_mechanisms)
        percentage = (count / total_mechanisms) * 100

        keyword_stats[category] = {
            "term": category.replace("_", " "),
            "count": count,
            "percentage": round(percentage, 1),
            "patterns": patterns,
            "example_paper_ids": matching_examples
        }

    return keyword_stats


def categorize_keywords(keyword_stats: Dict) -> Dict[str, List[str]]:
    """Group keywords into semantic categories."""
    categories = {
        "feedback_systems": ["feedback", "homeostasis", "regulation", "control"],
        "network_effects": ["network", "centrality", "coupling", "synchronization", "propagation", "contagion", "cascade"],
        "evolutionary_dynamics": ["selection", "adaptation", "cooperation", "competition", "coexistence", "coevolution"],
        "phase_transitions": ["phase_transition", "bifurcation", "criticality", "bistability", "metastability", "hysteresis"],
        "spatial_dynamics": ["spatial", "diffusion"],
        "stochastic_processes": ["stochastic", "noise", "variability", "fluctuation"],
        "optimization": ["optimization", "trade-off"],
        "structural_properties": ["heterogeneity", "threshold", "complementarity", "scaling", "nonlinearity"],
        "emergent_phenomena": ["emergence", "self-organization", "oscillation", "universality"],
        "specific_mechanisms": ["allee_effect", "prisoner_dilemma", "free_rider", "spillover", "robustness"]
    }
    return categories


def main():
    # Load mechanisms
    mechanisms = load_mechanisms("examples/session48_all_mechanisms.json")
    print(f"Loaded {len(mechanisms)} mechanisms")

    # Count keyword occurrences
    keyword_stats = count_keyword_occurrences(mechanisms, STRUCTURAL_KEYWORDS)

    # Sort by frequency
    sorted_keywords = sorted(
        keyword_stats.values(),
        key=lambda x: x["count"],
        reverse=True
    )

    # Categorize
    categories = categorize_keywords(keyword_stats)

    # Prepare output
    output = {
        "total_mechanisms": len(mechanisms),
        "extraction_date": "2026-02-12",
        "keywords": sorted_keywords,
        "categories": {}
    }

    # Build category structure
    for cat_name, keyword_list in categories.items():
        output["categories"][cat_name] = [
            kw for kw in sorted_keywords
            if any(term in kw["term"] for term in keyword_list)
        ]

    # Summary statistics
    high_frequency = [kw for kw in sorted_keywords if kw["percentage"] >= 30]
    medium_frequency = [kw for kw in sorted_keywords if 10 <= kw["percentage"] < 30]
    low_frequency = [kw for kw in sorted_keywords if kw["percentage"] < 10]

    output["summary"] = {
        "high_frequency": len(high_frequency),
        "medium_frequency": len(medium_frequency),
        "low_frequency": len(low_frequency),
        "top_10_keywords": [kw["term"] for kw in sorted_keywords[:10]]
    }

    # Save output
    with open("examples/session50_structural_keywords.json", 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Extracted {len(sorted_keywords)} structural keywords")
    print(f"  - High frequency (≥30%): {len(high_frequency)}")
    print(f"  - Medium frequency (10-30%): {len(medium_frequency)}")
    print(f"  - Low frequency (<10%): {len(low_frequency)}")
    print(f"\nTop 10 keywords:")
    for i, kw in enumerate(sorted_keywords[:10], 1):
        print(f"  {i}. {kw['term']}: {kw['count']}/104 ({kw['percentage']}%)")

    print(f"\n✓ Output saved to: examples/session50_structural_keywords.json")


if __name__ == "__main__":
    main()
