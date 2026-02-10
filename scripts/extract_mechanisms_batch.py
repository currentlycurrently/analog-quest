#!/usr/bin/env python3
"""
Extract mechanisms from Session 34 sample papers.

This script processes papers and extracts structural mechanisms using
the LLM approach validated in Session 33.
"""

import json

# Manually extracted mechanisms following the Session 33 prompt template
EXTRACTED_MECHANISMS = {
    # ECOLOGY PAPERS (q-bio.PE)
    448: {
        "mechanism": "Plants facilitate neighboring growth through local resource modification. "
                    "Facilitation competes with resource competition. When precipitation is intermittent, "
                    "facilitation-competition balance creates spatial vegetation patterns. Below threshold "
                    "density, vegetation collapses due to weakened facilitation (spatial Allee effect).",
        "mechanism_type": "threshold_dynamics,feedback_loop,network_effect",
        "quality": "excellent"
    },

    450: {
        "mechanism": "Tumor cells release antigens that activate immune T-cells. T-cells attack tumor reducing "
                    "growth. Tumor evolves PD-L1 expression to suppress T-cell response (escape mechanism). "
                    "Anti-PD-L1 therapy blocks suppression restoring immune attack. Vaccine increases antigen "
                    "presentation boosting T-cell activation. Combination creates feedback where immune response "
                    "selects for tumor variants.",
        "mechanism_type": "feedback_loop,evolutionary_dynamics,threshold_dynamics",
        "quality": "excellent"
    },

    451: {
        "mechanism": "Resource stock accumulates from production flow. Exploitation (flow out) versus conservation "
                    "(stock maintenance) tradeoff. Maximum sustainable yield occurs at intermediate stock level. "
                    "Over-exploitation depletes stock below replenishment threshold causing collapse. Under-exploitation "
                    "leaves unexploited surplus.",
        "mechanism_type": "flow_stock_transformation,threshold_dynamics,optimization",
        "quality": "excellent"
    },

    452: {
        "mechanism": "Transmission rate increases with infected density (frequency-dependent contact). "
                    "Recovery rate decreases infection duration. When transmission exceeds recovery (R0>1), "
                    "epidemic spreads exponentially. Vaccination reduces susceptible population shifting R0 below 1, "
                    "stopping spread. Spatial heterogeneity creates local pockets where R0 varies.",
        "mechanism_type": "threshold_dynamics,network_effect,diffusion_process",
        "quality": "excellent"
    },

    # ECONOMICS PAPERS (econ.GN)
    77: {
        "mechanism": "Firms collaborate forming innovation network. Central firms access diverse knowledge from "
                    "multiple partners enhancing innovation output. Peripheral firms limited by fewer connections. "
                    "Network structure (centrality) determines innovation capacity. Over time, successful innovators "
                    "attract more partners (preferential attachment) reinforcing centrality advantage.",
        "mechanism_type": "network_effect,feedback_loop,scaling",
        "quality": "excellent"
    },

    83: {
        "mechanism": "Agents share common resource. Individual optimization leads to overexploitation. "
                    "Without coordination, tragedy of commons occurs: individual incentives conflict with collective "
                    "benefit. Institutional rules (quotas, sanctions) change payoff structure. When sanctions exceed "
                    "exploitation benefit, cooperation becomes dominant strategy shifting equilibrium.",
        "mechanism_type": "strategic_interaction,equilibrium,threshold_dynamics",
        "quality": "excellent"
    },

    87: {
        "mechanism": "Agent productivity depends on network position (centrality). Information flows through network "
                    "with distance decay. Centrally located agents receive information faster and from more sources. "
                    "Information advantage translates to performance advantage. Network structure creates persistent "
                    "productivity inequality.",
        "mechanism_type": "network_effect,diffusion_process,scaling",
        "quality": "excellent"
    },

    100: {
        "mechanism": "Agents observe others' past contributions. Conditional cooperators increase contributions "
                    "when others contribute (reciprocity). Free-riders reduce contributions to exploit cooperators. "
                    "Reciprocity creates feedback: high average contribution sustains cooperation, low average triggers "
                    "collapse to non-cooperation. System exhibits bistability with cooperation and defection as stable states.",
        "mechanism_type": "strategic_interaction,feedback_loop,threshold_dynamics",
        "quality": "excellent"
    },

    # BIOLOGY PAPERS (q-bio.*)
    106: {
        "mechanism": "Mathematical model generates predictions about system behavior. Experimental tests validate "
                    "or reject predictions. Model parameters updated based on experimental results. Updated model "
                    "generates refined predictions creating iterative feedback loop. Prediction accuracy improves "
                    "over iterations as model incorporates empirical constraints.",
        "mechanism_type": "feedback_loop,convergence",
        "quality": "good"
    },

    157: {
        "mechanism": "Sound wave energy dissipates through damping. Damping rate depends on frequency. "
                    "High-frequency components decay faster creating frequency selectivity. This selective damping "
                    "forms natural filter: initial broadband signal evolves to narrowband output. Feedback between "
                    "sound level and damping creates tunable frequency response.",
        "mechanism_type": "feedback_loop,diffusion_process,frequency_selectivity",
        "quality": "good"
    },

    164: {
        "mechanism": "Daily infection events (incidence flow) add to pool of infected individuals (active cases stock). "
                    "Recovery rate determines outflow from infected stock. Stock level reflects cumulative incidence "
                    "minus cumulative recoveries. When incidence exceeds recovery, stock grows; when recovery exceeds "
                    "incidence, stock declines. Stock-flow dynamics determine epidemic trajectory.",
        "mechanism_type": "flow_stock_transformation,diffusion_process",
        "quality": "good"
    },

    168: {
        "mechanism": "Competitive exclusion principle limits coexistence: stronger competitor eliminates weaker ones. "
                    "Deterministic systems follow exclusion strictly. Chaotic dynamics introduce temporal variability "
                    "in competitive advantages. When chaos shifts advantage faster than elimination occurs, multiple "
                    "competitors persist. Chaos enables coexistence beyond deterministic limit.",
        "mechanism_type": "threshold_dynamics,chaotic_dynamics,equilibrium",
        "quality": "excellent"
    },

    # Add more as extracted...
}

def main():
    """Extract mechanisms from sample papers."""

    # Load sample papers
    with open('/tmp/session34_sample_papers.json', 'r') as f:
        papers = json.load(f)

    print(f"Loaded {len(papers)} papers")
    print(f"Extracted mechanisms for {len(EXTRACTED_MECHANISMS)} papers so far")

    # Build output
    results = []
    extracted_count = 0
    skipped_count = 0

    for paper in papers:
        paper_id = paper['id']

        if paper_id in EXTRACTED_MECHANISMS:
            mech_data = EXTRACTED_MECHANISMS[paper_id]
            results.append({
                'paper_id': paper_id,
                'title': paper['title'],
                'domain': paper['domain'],
                'subdomain': paper['subdomain'],
                'arxiv_id': paper['arxiv_id'],
                'abstract': paper['abstract'],
                'mechanism': mech_data['mechanism'],
                'mechanism_type': mech_data['mechanism_type'],
                'extraction_quality': mech_data['quality'],
                'extraction_method': 'manual_following_session33_prompt'
            })
            extracted_count += 1
        else:
            # Paper not yet processed
            results.append({
                'paper_id': paper_id,
                'title': paper['title'],
                'domain': paper['domain'],
                'subdomain': paper['subdomain'],
                'arxiv_id': paper['arxiv_id'],
                'abstract': paper['abstract'],
                'mechanism': None,
                'mechanism_type': None,
                'extraction_quality': None,
                'extraction_method': 'pending'
            })
            skipped_count += 1

    # Save results
    output_file = 'examples/session34_llm_mechanisms.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved {len(results)} papers to {output_file}")
    print(f"  - Extracted: {extracted_count}")
    print(f"  - Pending: {skipped_count}")

    # Show extraction breakdown by domain
    domain_stats = {}
    for result in results:
        domain = result['subdomain'] if result['subdomain'] else result['domain']
        if domain not in domain_stats:
            domain_stats[domain] = {'total': 0, 'extracted': 0}
        domain_stats[domain]['total'] += 1
        if result['mechanism']:
            domain_stats[domain]['extracted'] += 1

    print("\nExtraction progress by domain:")
    for domain in sorted(domain_stats.keys()):
        stats = domain_stats[domain]
        pct = 100.0 * stats['extracted'] / stats['total'] if stats['total'] > 0 else 0
        print(f"  {domain}: {stats['extracted']}/{stats['total']} ({pct:.0f}%)")


if __name__ == '__main__':
    main()
