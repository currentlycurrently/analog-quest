#!/usr/bin/env node

/**
 * MASSIVE CLEANUP AND MIGRATION SCRIPT
 *
 * This script will:
 * 1. Audit what data we have in JSON vs Database
 * 2. Migrate all JSON data to PostgreSQL
 * 3. Connect OpenAlex papers properly
 * 4. Clean up all the mess
 */

const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://user@localhost:5432/analog_quest',
  ssl: process.env.DATABASE_URL?.includes('localhost') ? false : { rejectUnauthorized: false }
});

async function auditCurrentState() {
  console.log('\n🔍 AUDITING CURRENT STATE...\n');

  try {
    // Check database tables
    const tables = await pool.query(`
      SELECT table_name,
             pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
      FROM information_schema.tables
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `);

    console.log('📊 Database Tables:');
    for (const table of tables.rows) {
      const countResult = await pool.query(`SELECT COUNT(*) FROM ${table.table_name}`);
      console.log(`  - ${table.table_name}: ${countResult.rows[0].count} rows (${table.size})`);
    }

    // Check JSON files
    console.log('\n📄 JSON Data Files:');
    const dataDir = path.join(__dirname, '../app/data');
    const jsonFiles = fs.readdirSync(dataDir).filter(f => f.endsWith('.json'));

    for (const file of jsonFiles) {
      const filePath = path.join(dataDir, file);
      const stats = fs.statSync(filePath);
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      const count = Array.isArray(data) ? data.length :
                    data.discoveries ? data.discoveries.length :
                    data.data ? data.data.length : 'N/A';
      console.log(`  - ${file}: ${count} items (${(stats.size / 1024).toFixed(1)} KB)`);
    }

    // Check OpenAlex papers
    const openalex = await pool.query(`
      SELECT COUNT(*) as total,
             COUNT(DISTINCT domain) as domains,
             MIN(published_date) as earliest,
             MAX(published_date) as latest
      FROM papers
      WHERE arxiv_id IS NOT NULL OR doi IS NOT NULL
    `);
    console.log('\n🔬 OpenAlex Papers in Database:');
    console.log(`  - Total papers: ${openalex.rows[0].total}`);
    console.log(`  - Unique domains: ${openalex.rows[0].domains}`);
    console.log(`  - Date range: ${openalex.rows[0].earliest?.toISOString().split('T')[0]} to ${openalex.rows[0].latest?.toISOString().split('T')[0]}`);

    // Check isomorphisms
    const isos = await pool.query(`
      SELECT COUNT(*) as total,
             COUNT(DISTINCT verification_status) as statuses
      FROM isomorphisms
    `);
    console.log('\n🔗 Isomorphisms in Database:');
    console.log(`  - Total: ${isos.rows[0].total}`);

    // Check archive folders
    console.log('\n📁 Archive/Session Folders:');
    const archiveDirs = ['archive', 'examples', 'scripts/archive'];
    for (const dir of archiveDirs) {
      const fullPath = path.join(__dirname, '..', dir);
      if (fs.existsSync(fullPath)) {
        const files = fs.readdirSync(fullPath, { withFileTypes: true });
        const fileCount = files.filter(f => f.isFile()).length;
        const dirCount = files.filter(f => f.isDirectory()).length;
        console.log(`  - ${dir}/: ${fileCount} files, ${dirCount} subdirs`);
      }
    }

  } catch (error) {
    console.error('Error during audit:', error);
  }
}

async function connectOpenAlexPapers() {
  console.log('\n🔌 CONNECTING OPENALEX PAPERS TO ISOMORPHISMS...\n');

  try {
    // First, let's see what papers we have
    const papers = await pool.query(`
      SELECT id, title, domain, arxiv_id, doi
      FROM papers
      WHERE arxiv_id IS NOT NULL
      LIMIT 20
    `);

    console.log(`Found ${papers.rows.length} papers with arXiv IDs`);

    // Check if we have any isomorphism_papers connections
    const connections = await pool.query(`
      SELECT COUNT(*) FROM isomorphism_papers
    `);

    if (connections.rows[0].count === '0') {
      console.log('⚠️  No papers connected to isomorphisms yet!');
      console.log('TODO: Need to match papers to existing isomorphisms based on titles/domains');
    } else {
      console.log(`✅ Found ${connections.rows[0].count} paper-isomorphism connections`);
    }

  } catch (error) {
    console.error('Error connecting papers:', error);
  }
}

async function migrateJsonToDb() {
  console.log('\n🚀 MIGRATING JSON DATA TO DATABASE...\n');

  try {
    // Read the main discoveries.json
    const discoveriesPath = path.join(__dirname, '../app/data/discoveries.json');
    if (fs.existsSync(discoveriesPath)) {
      const data = JSON.parse(fs.readFileSync(discoveriesPath, 'utf-8'));
      const discoveries = data.discoveries || data;

      console.log(`Found ${discoveries.length} discoveries in JSON`);

      // TODO: Actually migrate these to the database
      console.log('⚠️  Migration logic needs to be implemented');
      console.log('   - Need to convert JSON format to isomorphisms table format');
      console.log('   - Need to handle duplicate detection');
      console.log('   - Need to preserve ratings and metadata');
    }

  } catch (error) {
    console.error('Error during migration:', error);
  }
}

async function cleanupFiles() {
  console.log('\n🗑️  CLEANUP RECOMMENDATIONS...\n');

  const toDelete = [
    'app/data/discoveries.json (after migration)',
    'app/data/discovered_pairs.json',
    'app/data/discoveries_backup*.json',
    'app/data/real_isomorphisms.json',
    'app/data/verified_isomorphisms.json',
    'archive/ (entire folder)',
    'examples/session*.json',
    'scripts/archive/',
    'scripts/session*.py',
    'app/discoveries/[id]/page-*.tsx (backup files)',
  ];

  console.log('Files and folders to delete:');
  toDelete.forEach(f => console.log(`  ❌ ${f}`));

  console.log('\nFiles to keep:');
  console.log('  ✅ app/data/discoveries_editorial.json (for editorial content)');
  console.log('  ✅ Current working scripts');
  console.log('  ✅ Database connection files');
}

async function main() {
  console.log('=' * 60);
  console.log('   ANALOG QUEST - CLEANUP AND MIGRATION');
  console.log('=' * 60);

  await auditCurrentState();
  await connectOpenAlexPapers();
  await migrateJsonToDb();
  await cleanupFiles();

  console.log('\n' + '=' * 60);
  console.log('   SUMMARY');
  console.log('=' * 60);

  console.log('\n📋 NEXT STEPS:');
  console.log('1. Implement the migration logic to move JSON data to PostgreSQL');
  console.log('2. Connect OpenAlex papers to isomorphisms properly');
  console.log('3. Update all API routes to use database only');
  console.log('4. Delete all the redundant JSON files');
  console.log('5. Remove archive folders');

  await pool.end();
}

main().catch(console.error);