#!/usr/bin/env python3
"""
Database validation script to catch data quality issues early.

Run this after major operations (fetching, extraction, matching) to ensure data integrity.
"""

import sqlite3
from utils import get_db

def validate_papers():
    """Validate papers table for common issues"""
    db = get_db()
    cursor = db.cursor()

    issues = []

    # Check 1: Papers with NULL or empty abstracts
    cursor.execute("SELECT COUNT(*) FROM papers WHERE abstract IS NULL OR abstract = ''")
    null_abstracts = cursor.fetchone()[0]
    if null_abstracts > 0:
        issues.append(f"⚠️  {null_abstracts} papers have NULL/empty abstracts")

    # Check 2: Papers with domain="unknown" or invalid domains
    cursor.execute("SELECT COUNT(*) FROM papers WHERE domain = 'unknown' OR domain = '--count'")
    invalid_domains = cursor.fetchone()[0]
    if invalid_domains > 0:
        issues.append(f"🚨 {invalid_domains} papers have invalid domains (unknown or --count)")

    # Check 3: Papers with subdomain containing "cat:" (should be stripped)
    cursor.execute("SELECT COUNT(*) FROM papers WHERE subdomain LIKE 'cat:%'")
    malformed_subdomains = cursor.fetchone()[0]
    if malformed_subdomains > 0:
        issues.append(f"⚠️  {malformed_subdomains} papers have malformed subdomains (cat: prefix)")

    # Check 4: Duplicate arXiv IDs
    cursor.execute("""
        SELECT arxiv_id, COUNT(*) as count
        FROM papers
        WHERE arxiv_id IS NOT NULL
        GROUP BY arxiv_id
        HAVING count > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        issues.append(f"🚨 {len(duplicates)} duplicate arXiv IDs found")

    # Check 5: Papers without patterns (hit rate check)
    cursor.execute("SELECT COUNT(*) FROM papers")
    total_papers = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT paper_id)
        FROM patterns
        WHERE paper_id IS NOT NULL
    """)
    papers_with_patterns = cursor.fetchone()[0]

    hit_rate = (papers_with_patterns / total_papers * 100) if total_papers > 0 else 0
    papers_without_patterns = total_papers - papers_with_patterns

    if hit_rate < 75:
        issues.append(f"🚨 Hit rate is {hit_rate:.1f}% (below 75% threshold)")
    elif hit_rate < 85:
        issues.append(f"⚠️  Hit rate is {hit_rate:.1f}% (below 85% target)")

    db.close()

    return issues, {
        'total_papers': total_papers,
        'papers_with_patterns': papers_with_patterns,
        'papers_without_patterns': papers_without_patterns,
        'hit_rate': hit_rate
    }

def validate_patterns():
    """Validate patterns table for common issues"""
    db = get_db()
    cursor = db.cursor()

    issues = []

    # Check 1: Orphaned patterns (paper_id doesn't exist)
    cursor.execute("""
        SELECT COUNT(*)
        FROM patterns
        WHERE paper_id NOT IN (SELECT id FROM papers)
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues.append(f"🚨 {orphaned} orphaned patterns (paper_id doesn't exist)")

    # Check 2: Patterns with NULL mechanism_type
    cursor.execute("SELECT COUNT(*) FROM patterns WHERE mechanism_type IS NULL")
    null_mechanisms = cursor.fetchone()[0]
    if null_mechanisms > 0:
        issues.append(f"⚠️  {null_mechanisms} patterns have NULL mechanism_type")

    # Check 3: Total pattern count
    cursor.execute("SELECT COUNT(*) FROM patterns")
    total_patterns = cursor.fetchone()[0]

    db.close()

    return issues, {'total_patterns': total_patterns}

def validate_isomorphisms():
    """Validate isomorphisms table for common issues"""
    db = get_db()
    cursor = db.cursor()

    issues = []

    # Check 1: Orphaned isomorphisms (pattern_id doesn't exist)
    cursor.execute("""
        SELECT COUNT(*)
        FROM isomorphisms
        WHERE pattern_1_id NOT IN (SELECT id FROM patterns)
           OR pattern_2_id NOT IN (SELECT id FROM patterns)
    """)
    orphaned = cursor.fetchone()[0]
    if orphaned > 0:
        issues.append(f"🚨 {orphaned} orphaned isomorphisms (pattern_id doesn't exist)")

    # Check 2: Self-matches (pattern_1_id = pattern_2_id)
    cursor.execute("""
        SELECT COUNT(*)
        FROM isomorphisms
        WHERE pattern_1_id = pattern_2_id
    """)
    self_matches = cursor.fetchone()[0]
    if self_matches > 0:
        issues.append(f"🚨 {self_matches} self-matching isomorphisms")

    # Check 3: Total isomorphism count
    cursor.execute("SELECT COUNT(*) FROM isomorphisms")
    total_isomorphisms = cursor.fetchone()[0]

    db.close()

    return issues, {'total_isomorphisms': total_isomorphisms}

def run_validation():
    """Run all validation checks and print results"""
    print("\n" + "="*60)
    print("DATABASE VALIDATION REPORT")
    print("="*60 + "\n")

    # Validate papers
    print("📄 PAPERS TABLE")
    paper_issues, paper_stats = validate_papers()
    print(f"   Total papers: {paper_stats['total_papers']}")
    print(f"   Papers with patterns: {paper_stats['papers_with_patterns']}")
    print(f"   Papers without patterns: {paper_stats['papers_without_patterns']}")
    print(f"   Hit rate: {paper_stats['hit_rate']:.1f}%")
    if paper_issues:
        for issue in paper_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No issues found")
    print()

    # Validate patterns
    print("🔍 PATTERNS TABLE")
    pattern_issues, pattern_stats = validate_patterns()
    print(f"   Total patterns: {pattern_stats['total_patterns']}")
    if pattern_issues:
        for issue in pattern_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No issues found")
    print()

    # Validate isomorphisms
    print("🔗 ISOMORPHISMS TABLE")
    iso_issues, iso_stats = validate_isomorphisms()
    print(f"   Total isomorphisms: {iso_stats['total_isomorphisms']}")
    if iso_issues:
        for issue in iso_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No issues found")
    print()

    # Summary
    total_issues = len(paper_issues) + len(pattern_issues) + len(iso_issues)
    print("="*60)
    if total_issues == 0:
        print("✅ VALIDATION PASSED - No issues found!")
    else:
        print(f"⚠️  VALIDATION FOUND {total_issues} ISSUE(S)")
        print("   Review issues above and fix before proceeding.")
    print("="*60 + "\n")

    return total_issues == 0

if __name__ == '__main__':
    success = run_validation()
    exit(0 if success else 1)
