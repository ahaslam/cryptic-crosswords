const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { exportLexicon } = require('./export_exet_lufz');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'lufz-export-'));
try {
  const input = path.join(dir, 'source.js');
  const output = path.join(dir, 'export.tsv');
  fs.writeFileSync(input,
    "exetLexicon = {lexicon: ['', 'colour', 'King\'s Cross', 'obscurity'], importance: [0, 100, 70, 1]};");
  assert.equal(exportLexicon(input, output), 3);
  const scores = new Map(fs.readFileSync(output, 'utf8').trim().split('\n')
    .map(line => { const [word, score] = line.split('\t'); return [word, Number(score)]; }));
  assert.ok(scores.get('colour') > scores.get('obscurity'));
  assert.ok(scores.get("King's Cross") > scores.get('obscurity'));
  assert.throws(() => {
    fs.writeFileSync(input, 'exetLexicon = {lexicon: ["x"]};');
    exportLexicon(input, output);
  }, /Unsupported Exet lexicon format/);
  console.log('Lufz exporter tests passed');
} finally {
  fs.rmSync(dir, { recursive: true, force: true });
}
