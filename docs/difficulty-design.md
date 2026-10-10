# Crossword difficulty: generator and editorial specification

Status: proposed implementation specification. Difficulty is a **puzzle-level generation input**, not a post-hoc label.

## Levels

| Level | Audience | Answer selection | Clue construction |
|---|---|---|---|
| accessible | Newer cryptic solvers | Common, familiar British English; very few proper nouns | Transparent definitions; conventional anagrams, containers, reversals, charades and hidden words; fewer nested operations |
| standard | Regular solvers | Broad familiar vocabulary; occasional fair specialist reference | Varied devices and moderate surface misdirection; occasional multi-step construction |
| challenging | Experienced solvers | Still fair and clueable; broader vocabulary without arbitrary obscurity | Greater semantic misdirection, sophisticated surfaces and well-signalled multi-step wordplay |

## Contract

- `difficulty` must be a required, validated property of every *newly published* puzzle, with values `accessible`, `standard`, `challenging`. Legacy demo puzzles may default to `standard` until migrated.
- The generation command accepts `--difficulty`, records the requested level in the unpublished draft and the benchmark report, and never infers it solely from a dictionary score.
- Difficulty-specific answer preferences (frequency floor, proper-name budget, abbreviations, multiword expressions) are separate from difficulty-specific clue constraints (wordplay devices, steps, definition transparency, misdirection).
- An editor can reject an answer at **any** level. Higher difficulty is not a licence for unguessable names, vague definitions or unfair wordplay.
- The clue-writing process records device type, definition, construction, and editorial assessment for each clue. A puzzle-level review checks the mix, not just individual clues.
- The website exposes a level selector for discovering puzzles, shows the level before solving, and does not silently change difficulty while a puzzle is in progress.
- Solvers should be able to choose difficulty without knowing crossword jargon. A short description of each level is sufficient.
- Do not claim calibrated difficulty until real solvers have tested multiple puzzles. Record solver feedback and adjust the bands empirically.

## Suggested initial tuning (not yet calibrated)

Accessible: preferred Lufz score >= 85, uncommon-answer budget <= 2.
Standard: preferred score >= 80, uncommon-answer budget <= 5.
Challenging: preferred score >= 75, uncommon-answer budget <= 6.

These numbers are **starting hypotheses**, not guarantees of clue quality or objective difficulty. Keep an independent editorial veto over awkward answers.

## Acceptance tests

1. CLI rejects an unknown difficulty and records a valid one in draft/report metadata.
2. Same seed and settings are reproducible; different levels may produce different fills.
3. Published puzzle validation rejects missing/unknown levels for new puzzles.
4. The site shows and filters puzzle difficulty without losing a solver's progress.
5. Editorial test cases distinguish hard-but-fair clues from obscure or defective clues.
