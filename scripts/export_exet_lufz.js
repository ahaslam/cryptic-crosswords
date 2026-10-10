#!/usr/bin/env node
/**
 * Convert an Exet Lufz JavaScript lexicon to scored TSV.
 *
 * Usage: node scripts/export_exet_lufz.js path/to/lufz-en-lexicon.js output.tsv
 * Obtain the source from https://github.com/viresh-ratnakar/exet.
 * The source lexicon is not vendored in this repository.
 */
const fs = require('node:fs');
const vm = require('node:vm');

function exportLexicon(source, destination) {
  // Exet's generated source populates exetLexicon with lexicon and importance.
  const context = vm.createContext({ exetLexicon: {} });
  vm.runInContext(fs.readFileSync(source, 'utf8'), context, {
    filename: source, timeout: 30000,
  });
  const data = context.exetLexicon;
  if (!Array.isArray(data.lexicon) || !Array.isArray(data.importance) ||
      data.lexicon.length !== data.importance.length) {
    throw new Error('Unsupported Exet lexicon format: missing aligned lexicon/importance arrays');
  }
  const rows = [];
  const values = [];
  for (let i = 1; i < data.lexicon.length; i++) {
    const word = data.lexicon[i];
    const importance = Number(data.importance[i]);
    if (typeof word !== 'string' || !Number.isFinite(importance)) continue;
    const answer = word.toUpperCase().replace(/[^A-Z]/g, '');
    if (answer.length < 3 || answer.length > 15) continue;
    rows.push({ word, importance });
    values.push(importance);
  }
  // Wikipedia importance is a rank-like quantity (lower means more popular).
  // Derive a monotonic 0..100 percentile score without assuming rank range.
  const ordered = [...values].sort((a, b) => a - b);
  const rank = new Map();
  ordered.forEach((value, index) => { if (!rank.has(value)) rank.set(value, index); });
  const n = Math.max(1, ordered.length - 1);
  const lines = rows.map(({ word, importance }) => {
    const score = Math.round(100 * (1 - rank.get(importance) / n));
    return word.replace(/[\t\r\n]/g, ' ') + '\t' + score;
  });
  fs.writeFileSync(destination, lines.join('\n') + '\n', 'utf8');
  return lines.length;
}

if (require.main === module) {
  if (process.argv.length !== 4) {
    console.error('Usage: node export_exet_lufz.js input.js output.tsv');
    process.exit(2);
  }
  console.log('Exported', exportLexicon(process.argv[2], process.argv[3]), 'entries');
}
module.exports = { exportLexicon };
