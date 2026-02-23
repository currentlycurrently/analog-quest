#!/usr/bin/env node

/**
 * MIGRATION SCRIPT: Curated Discoveries to PostgreSQL
 *
 * Migrates only high-quality, curated discoveries to the database
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://user@localhost:5432/analog_quest',
  ssl: false
});

async function migrateCuratedDiscoveries() {
  console.log('\n🚀 MIGRATING CURATED DISCOVERIES TO POSTGRESQL...\n');

  try {
    // Clear existing bad data
    console.log('⚠️  Clearing existing data...');
    await pool.query('TRUNCATE TABLE isomorphisms, isomorphism_papers CASCADE');

    // Load all curated discovery files
    const curatedFiles = [
      'examples/session75_curated_discoveries.json',
      'examples/session76_curated_discoveries.json',
      'examples/session77_curated_discoveries.json',
      'examples/session80_curated_discoveries.json',
      'examples/session81_curated_discoveries.json'
    ];

    let totalMigrated = 0;
    let discoveryId = 1;

    for (const file of curatedFiles) {
      const filePath = path.join(__dirname, '..', file);
      if (!fs.existsSync(filePath)) {
        console.log(`  ⚠️  File not found: ${file}`);
        continue;
      }

      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      const discoveries = data.discoveries || [];
      const sessionNum = file.match(/session(\d+)/)[1];

      console.log(`\n📄 Processing ${file}: ${discoveries.length} discoveries`);

      for (const discovery of discoveries) {
        try {
          const {
            paper_1,
            paper_2,
            similarity,
            rating,
            explanation,
            structural_explanation,
            pattern
          } = discovery;

          // Only migrate good and excellent discoveries
          if (rating !== 'excellent' && rating !== 'good') {
            console.log(`  ⚠️  Skipping weak discovery`);
            continue;
          }

          const result = await pool.query(`
            INSERT INTO isomorphisms (
              title,
              isomorphism_class,
              mathematical_structure,
              explanation,
              detailed_proof,
              confidence,
              verification_status,
              discovered_session,
              created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
          `, [
            `${paper_1?.domain || 'Unknown'} ↔ ${paper_2?.domain || 'Unknown'}: ${pattern || 'Structural Pattern'}`,
            pattern || 'structural_pattern',
            `${paper_1?.mechanism || 'Pattern 1'} ≈ ${paper_2?.mechanism || 'Pattern 2'}`,
            explanation || structural_explanation || 'Cross-domain structural similarity',
            JSON.stringify({
              paper_1: {
                title: paper_1?.title,
                domain: paper_1?.domain,
                arxiv_id: paper_1?.arxiv_id,
                mechanism: paper_1?.mechanism
              },
              paper_2: {
                title: paper_2?.title,
                domain: paper_2?.domain,
                arxiv_id: paper_2?.arxiv_id,
                mechanism: paper_2?.mechanism
              },
              similarity_score: similarity,
              original_rating: rating
            }),
            similarity || 0.75,
            rating === 'excellent' ? 'verified' : 'partial',
            parseInt(sessionNum),
            new Date()
          ]);

          totalMigrated++;
          console.log(`  ✅ Migrated discovery #${result.rows[0].id}: ${rating} (similarity: ${similarity?.toFixed(2)})`);

        } catch (error) {
          console.error(`  ❌ Failed to migrate discovery:`, error.message);
        }
      }
    }

    console.log(`\n✅ Migration complete!`);
    console.log(`  - Total migrated: ${totalMigrated} high-quality discoveries`);

    // Verify migration
    const finalCount = await pool.query('SELECT COUNT(*) FROM isomorphisms');
    const statusCount = await pool.query(`
      SELECT verification_status, COUNT(*)
      FROM isomorphisms
      GROUP BY verification_status
      ORDER BY COUNT(*) DESC
    `);

    console.log(`  - Total in database: ${finalCount.rows[0].count}`);
    console.log('\n📊 Status breakdown:');
    statusCount.rows.forEach(row => {
      console.log(`  - ${row.verification_status}: ${row.count}`);
    });

  } catch (error) {
    console.error('Migration failed:', error);
  } finally {
    await pool.end();
  }
}

async function main() {
  console.log('=' .repeat(60));
  console.log('   CURATED DISCOVERIES TO POSTGRESQL MIGRATION');
  console.log('=' .repeat(60));

  await migrateCuratedDiscoveries();

  console.log('\n' + '=' .repeat(60));
  console.log('   MIGRATION COMPLETE!');
  console.log('=' .repeat(60));

  console.log('\n📋 NEXT STEPS:');
  console.log('1. Verify the site displays the curated discoveries');
  console.log('2. Connect OpenAlex papers to isomorphisms');
  console.log('3. Remove old JSON files after verification');
}

main().catch(console.error);