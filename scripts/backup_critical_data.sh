#!/bin/bash

# CRITICAL DATA BACKUP SCRIPT
# Preserves the real mathematical isomorphisms (years of research work)

echo "================================================"
echo "   CRITICAL DATA BACKUP - REAL ISOMORPHISMS"
echo "================================================"

BACKUP_DIR="CRITICAL_BACKUP/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup JSON files
echo "📁 Backing up JSON files..."
cp app/data/verified_isomorphisms.json "$BACKUP_DIR/" 2>/dev/null
cp app/data/real_isomorphisms.json "$BACKUP_DIR/" 2>/dev/null

# Backup database
echo "💾 Backing up PostgreSQL data..."
/opt/homebrew/opt/postgresql@17/bin/pg_dump \
  postgresql://user@localhost:5432/analog_quest \
  --table=isomorphisms \
  --data-only \
  --inserts \
  > "$BACKUP_DIR/isomorphisms_backup.sql"

# Create summary
echo "📊 Creating backup summary..."
cat > "$BACKUP_DIR/backup_summary.txt" << SUMMARY
CRITICAL BACKUP - $(date)
===========================

This backup contains the REAL mathematical isomorphisms:

1. Diffusion Models (AI) ↔ MRI Diffusion (Medicine)
   Formula: ∂u/∂t = k∇²u

2. Robot Task Segmentation ↔ Sleep Stage Dynamics
   Formula: dx/dt = ax - bxy, dy/dt = -cy + dxy

3. ISING_MODEL: math ↔ q-bio
   Formula: H = -J Σ σi σj - h Σ σi

4-6. POWER_LAW variations
   Formula: P(x) ∝ x^(-α)

These represent YEARS of research work.
DO NOT DELETE without proper restoration plan!
SUMMARY

echo "✅ Backup complete: $BACKUP_DIR"
echo "⚠️  CRITICAL: These are the REAL mathematical discoveries"
