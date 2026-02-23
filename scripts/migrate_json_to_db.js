#!/usr/bin/env node

/**
 * MIGRATION SCRIPT: JSON to PostgreSQL
 *
 * Migrates all discoveries from JSON files to PostgreSQL database
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

// Fix SSL issue for local database
const pool = new Pool({
  connectionString: process.env.POSTGRES_URL || 'postgresql://user@localhost:5432/analog_quest',
  ssl: false // Disable SSL for local connection
});

async function migrateDiscoveries() {
  console.log('\n🚀 STARTING MIGRATION FROM JSON TO POSTGRESQL...\n');

  try {
    // Read the main discoveries.json file
    const discoveriesPath = path.join(__dirname, '../app/data/discoveries.json');
    const data = JSON.parse(fs.readFileSync(discoveriesPath, 'utf-8'));
    const discoveries = data.discoveries || data;

    console.log(`Found ${discoveries.length} discoveries in JSON to migrate`);

    // Check current isomorphisms in database
    const currentCount = await pool.query('SELECT COUNT(*) FROM isomorphisms');
    console.log(`Current isomorphisms in database: ${currentCount.rows[0].count}`);

    // Clear existing data (be careful!)
    console.log('\n⚠️  Clearing existing isomorphisms...');
    await pool.query('TRUNCATE TABLE isomorphisms, isomorphism_papers CASCADE');

    let migrated = 0;
    let failed = 0;

    for (const discovery of discoveries) {
      try {
        // Extract data from discovery
        const {
          id,
          paper_1,
          paper_2,
          similarity,
          rating,
          explanation,
          structural_explanation,
          discovered_in_session
        } = discovery;

        // Insert into isomorphisms table
        const result = await pool.query(`
          INSERT INTO isomorphisms (
            id,
            title,
            isomorphism_class,
            mathematical_structure,
            explanation,
            detailed_proof,
            confidence,
            verification_status,
            discovered_session,
            created_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
          RETURNING id
        `, [
          id || migrated + 1,
          `${paper_1?.domain || 'unknown'} ↔ ${paper_2?.domain || 'unknown'}: ${discovery.pattern || 'Isomorphism'}`,
          discovery.pattern || 'structural_pattern',
          discovery.mathematical_structure || 'Cross-domain pattern',
          explanation || structural_explanation || 'Cross-domain structural similarity',
          JSON.stringify({
            paper_1_title: paper_1?.title,
            paper_2_title: paper_2?.title,
            paper_1_domain: paper_1?.domain,
            paper_2_domain: paper_2?.domain,
            paper_1_arxiv_id: paper_1?.arxiv_id,
            paper_2_arxiv_id: paper_2?.arxiv_id,
            mechanism_1: paper_1?.mechanism,
            mechanism_2: paper_2?.mechanism,
            original_json_id: discovery.id
          }),
          similarity || 0.7,
          rating === 'excellent' ? 'verified' : rating === 'good' ? 'partial' : 'unverified',
          discovered_in_session || null,
          new Date()
        ]);

        migrated++;

        // If we have paper details, try to connect to papers table
        if (paper_1?.arxiv_id || paper_2?.arxiv_id) {
          // TODO: Match with papers table and create isomorphism_papers entries
          console.log(`  ✓ Migrated discovery #${result.rows[0].id} (${rating})`);
        }

      } catch (error) {
        console.error(`  ✗ Failed to migrate discovery ${discovery.id}:`, error.message);
        failed++;
      }
    }

    console.log(`\n✅ Migration complete!`);
    console.log(`  - Migrated: ${migrated} discoveries`);
    console.log(`  - Failed: ${failed} discoveries`);

    // Verify migration
    const finalCount = await pool.query('SELECT COUNT(*) FROM isomorphisms');
    console.log(`  - Total in database: ${finalCount.rows[0].count}`);

  } catch (error) {
    console.error('Migration failed:', error);
  } finally {
    await pool.end();
  }
}

async function cleanupJsonFiles() {
  console.log('\n🗑️  CLEANUP OLD JSON FILES...\n');

  const filesToDelete = [
    'app/data/discoveries_backup.json',
    'app/data/discoveries_backup_20260218_022913.json',
    'app/data/discovered_pairs.json',
    'app/data/real_isomorphisms.json',
    'app/data/verified_isomorphisms.json',
    'app/data/discovery_stats.json',
    'app/data/rebuild_status.json'
  ];

  for (const file of filesToDelete) {
    const filePath = path.join(__dirname, '..', file);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`  ✓ Deleted ${file}`);
    }
  }

  // Keep discoveries.json temporarily as backup
  console.log('\n  ⚠️  Keeping discoveries.json as backup (delete manually after verification)');
  console.log('  ✅ Keeping discoveries_editorial.json for editorial content');
}

async function cleanupArchives() {
  console.log('\n🗑️  CLEANUP ARCHIVE FOLDERS...\n');

  const foldersToClean = [
    'archive',
    'scripts/archive',
    'examples'
  ];

  for (const folder of foldersToClean) {
    const folderPath = path.join(__dirname, '..', folder);
    if (fs.existsSync(folderPath)) {
      // Count files first
      const files = fs.readdirSync(folderPath);
      const sessionFiles = files.filter(f => f.includes('session'));

      if (sessionFiles.length > 0) {
        console.log(`  Found ${sessionFiles.length} session files in ${folder}/`);

        // Delete session files
        for (const file of sessionFiles) {
          fs.unlinkSync(path.join(folderPath, file));
        }
        console.log(`  ✓ Deleted session files from ${folder}/`);
      }
    }
  }

  // Clean up backup page files
  const pageBackups = [
    'app/discoveries/[id]/page-simple-backup.tsx',
    'app/discoveries/[id]/page-simplified.tsx'
  ];

  for (const file of pageBackups) {
    const filePath = path.join(__dirname, '..', file);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`  ✓ Deleted ${file}`);
    }
  }
}

async function main() {
  console.log('=' .repeat(60));
  console.log('   JSON TO POSTGRESQL MIGRATION');
  console.log('=' .repeat(60));

  await migrateDiscoveries();
  await cleanupJsonFiles();
  await cleanupArchives();

  console.log('\n' + '=' .repeat(60));
  console.log('   MIGRATION COMPLETE!');
  console.log('=' .repeat(60));

  console.log('\n📋 NEXT STEPS:');
  console.log('1. Verify the site still works with database data');
  console.log('2. Connect OpenAlex papers to isomorphisms');
  console.log('3. Delete discoveries.json after verification');
  console.log('4. Remove any remaining archive folders');
}

main().catch(console.error);