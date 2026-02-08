"""
Calculate precision from reviewed validation sample.
Session 19.5 - Methodology Hardening
"""

import json


def calculate_precision():
    """Calculate precision from reviewed validation sample."""

    with open('examples/validation_sample_reviewed.json', 'r') as f:
        samples = json.load(f)

    buckets = {}

    for item in samples:
        if not item.get('manual_rating'):
            continue

        bucket = item['bucket']
        if bucket not in buckets:
            buckets[bucket] = {'total': 0, 'excellent': 0, 'good': 0, 'weak': 0, 'fp': 0}

        buckets[bucket]['total'] += 1
        rating = item['manual_rating']

        if rating == 'excellent':
            buckets[bucket]['excellent'] += 1
        elif rating == 'good':
            buckets[bucket]['good'] += 1
        elif rating == 'weak':
            buckets[bucket]['weak'] += 1
        elif rating == 'false_positive':
            buckets[bucket]['fp'] += 1

    # Print results
    print("\n" + "="*80)
    print("PRECISION BY BUCKET (Session 19.5)")
    print("="*80 + "\n")

    for bucket in sorted(buckets.keys()):
        counts = buckets[bucket]
        if counts['total'] == 0:
            continue

        good_count = counts['excellent'] + counts['good']
        precision = (good_count / counts['total']) * 100

        print(f"{bucket}:")
        print(f"  Total: {counts['total']}")
        print(f"  Excellent: {counts['excellent']} ({counts['excellent']/counts['total']*100:.1f}%)")
        print(f"  Good: {counts['good']} ({counts['good']/counts['total']*100:.1f}%)")
        print(f"  Weak: {counts['weak']} ({counts['weak']/counts['total']*100:.1f}%)")
        print(f"  False Positive: {counts['fp']} ({counts['fp']/counts['total']*100:.1f}%)")
        print(f"  → Precision: {precision:.1f}%\n")

    # Overall
    total_all = sum(b['total'] for b in buckets.values())
    excellent_all = sum(b['excellent'] for b in buckets.values())
    good_all = sum(b['good'] for b in buckets.values())
    weak_all = sum(b['weak'] for b in buckets.values())
    fp_all = sum(b['fp'] for b in buckets.values())
    good_count_all = excellent_all + good_all

    if total_all > 0:
        print(f"OVERALL:")
        print(f"  Total reviewed: {total_all}")
        print(f"  Excellent: {excellent_all} ({excellent_all/total_all*100:.1f}%)")
        print(f"  Good: {good_all} ({good_all/total_all*100:.1f}%)")
        print(f"  Weak: {weak_all} ({weak_all/total_all*100:.1f}%)")
        print(f"  False Positive: {fp_all} ({fp_all/total_all*100:.1f}%)")
        print(f"  → OVERALL PRECISION: {good_count_all}/{total_all} = {good_count_all/total_all*100:.1f}%")

    # Save results
    with open('examples/precision_by_bucket_19.5.json', 'w') as f:
        json.dump({
            'buckets': buckets,
            'overall': {
                'total': total_all,
                'excellent': excellent_all,
                'good': good_all,
                'weak': weak_all,
                'false_positive': fp_all,
                'precision': good_count_all/total_all if total_all > 0 else 0
            }
        }, f, indent=2)

    print(f"\n✓ Results saved to examples/precision_by_bucket_19.5.json")
    print("="*80)


if __name__ == "__main__":
    calculate_precision()
