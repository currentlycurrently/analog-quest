#!/bin/bash
# Backup critical data files
# Run daily or before major changes

BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting backup to $BACKUP_DIR..."

# Critical files to backup
cp app/data/discovered_pairs.json "$BACKUP_DIR/" 2>/dev/null && echo "✓ discovered_pairs.json"
cp app/data/discoveries.json "$BACKUP_DIR/" 2>/dev/null && echo "✓ discoveries.json"
cp examples/session74_candidates.json "$BACKUP_DIR/" 2>/dev/null && echo "✓ session74_candidates.json"
cp database/papers.db "$BACKUP_DIR/" 2>/dev/null && echo "✓ papers.db (SQLite)"

# Backup recent discovery files
mkdir -p "$BACKUP_DIR/recent_discoveries"
cp examples/session7[5-9]_curated_discoveries.json "$BACKUP_DIR/recent_discoveries/" 2>/dev/null
cp examples/session8[0-9]_curated_discoveries.json "$BACKUP_DIR/recent_discoveries/" 2>/dev/null
echo "✓ Recent discovery files"

# Create manifest
echo "Backup created on $(date)" > "$BACKUP_DIR/manifest.txt"
echo "Total discoveries: $(grep -o '"paper_1_id"' app/data/discovered_pairs.json | wc -l)" >> "$BACKUP_DIR/manifest.txt"

# Keep only last 7 backups
echo "🧹 Cleaning old backups..."
ls -dt backups/* | tail -n +8 | xargs rm -rf 2>/dev/null

echo "✅ Backup complete!"
echo "📁 Location: $BACKUP_DIR"
echo "📊 Files backed up: $(ls -1 $BACKUP_DIR | wc -l)"