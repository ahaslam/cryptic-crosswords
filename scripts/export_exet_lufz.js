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
  if (!Array.isArray(data.lexicon) || data.lexicon.length < 2) {
    throw new Error('Unsupported Exet lexicon format: missing ranked lexicon array');
  }
  // Lufz entries are ordered by descending Wikipedia popularity, with a
  // sentinel empty string at index 0. No importance/scores array is supplied.
  const count = data.lexicon.length - 1;
  const lines = [];
  for (let i = 1; i < data.lexicon.length; i++) {
    const word = data.lexicon[i];
    if (typeof word !== 'string') continue;
    const answer = word.toUpperCase().replace(/[^A-Z]/g, '');
    if (answer.length < 3 || answer.length > 15) continue;
    const score = Math.round(100 * (1 - (i - 1) / Math.max(1, count - 1)));
    lines.push(word.replace(/[\t\r\n]/g, ' ') + '\t' + score);
  }
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
