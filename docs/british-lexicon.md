# British cryptic crossword vocabulary

The goal is a conventional British-style cryptic, with familiar British English
answers and carefully selected uncommon entries.

## Candidate source

[Exet](https://github.com/viresh-ratnakar/exet) by Viresh Ratnakar offers
the Lufz English lexicon, derived from UKACD18 with additional words, phrases,
regional variants and Wikipedia-based popularity rankings. Exet also offers
the Will Nediger list, which has a different scoring scheme.

The Exet application is MIT-licensed. The underlying UKACD material has
additional copyright and attribution conditions. **Do not copy the Exet
lexicon into this repository until the precise data license, required notices
and export format have been verified.** Personal non-commercial use does not
automatically remove redistribution obligations for a public GitHub repo.

## Adapter contract

`scripts/crossword_lexicon.py` loads a **TSV export** with exactly two fields:

```text
COLOUR	92
King's Cross	81
```

Scores must be in the range 0–100, with larger values meaning more desirable
answers. This is an **adapter-specific score**, not a claim about the raw
Exet rank. Any future Exet exporter must explicitly convert its rankings to
this scale and document the conversion. Entries are normalized to A–Z for
the grid, and duplicates retain the highest score.

The adapter can emit the newline-delimited dictionary accepted by our existing
solver. It does not yet replace CMUdict in the production benchmark; doing
that before confirming the source format would create misleading results.

## Next experiment

1. Verify Lufz's serialization and attribution requirements.
2. Build a reproducible exporter for its entries and popularity ranks.
3. Benchmark matched grid seeds and node budgets against the current
   pronunciation dictionary.
4. Review actual filled answers for British usage and clueability.
