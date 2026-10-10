# Cryptic clue development: generate, disguise, verify, select

**Purpose:** Produce fair, delightful Sunday Times-style cryptic clues for experienced solvers. Do not equate an accessible answer with an easy clue.

## Workflow for every answer

1. **Enumerate distinct constructions.** Explore reversals, anagrams, containers, deletions, charades, hidden answers, homophones, double definitions, cryptic definitions and lateral mechanisms. Some require semantic knowledge and cannot be verified by letter arithmetic alone. Record at least three *genuinely different* possibilities where available; do not force three if the answer cannot support them.
2. **Identify semantic hooks.** For each fodder word, indicator and definition, find plausible non-cryptic meanings. Seek a setting where all three seem to belong together. The misleading surface must be a natural sentence, question or phrase; it should tell a tiny story or evoke a concrete scene.
3. **Compose competing surfaces.** Draft several clues per promising construction. Prefer ones where the indicator is an ordinary part of the scene, not a conspicuous instruction. Do not make the answer obvious in the surface.
4. **Verify the parse.** Check every letter operation; check abbreviations, synonyms, direction and indicator convention. The provided `scripts/wordplay_explorer.py` verifies literal operations but **cannot validate semantic fairness**. For multi-step constructions, verify each step and final assembly.
5. **Critique blind.** Try solving the clue without the answer. Rate surface naturalness, misdirection, economy, fairness, originality and aha moment separately. A mechanically sound clue may still be rejected.
6. **Select for the grid.** Balance device types, difficulty and tone across the *whole puzzle*. Do not artificially force a quota of devices. Replace stubborn answers rather than publishing filler.
7. **Independent review.** Keep `fairness_reviewed=false` until a human editor checks the clue. Do not publish or merge on an AI-only assessment.

## Calibration examples (provided by solver)

- **Lush large visor, as it were (2,2,5)** — SOT (lush) + OS (outsize) + PEAK (visor part) = SO TO SPEAK; definition “as it were”.
- **Greet large cook outside (6)** — SAUTE (“cook”) around L (“large”) = SALUTE; definition “greet”.
- **H I J K L M N O (5)** — H to O = H2O = WATER; lateral visual construction.
- **2 girls on each knee (7)** — PAT + ELLA = PATELLA; definition “knee” used loosely for kneecap.
- **Under tops looking back is a stain (4)** — TOPS reversed = SPOT; definition “a stain”. Surface evokes dirty clothing. **Working draft**: indicator placement and naturalness require further review.

The first four are calibration examples, not automatically licensed puzzle content. The fifth is a solver/assistant working draft, not signed off.

## Prototype: actual run on SPOT

```bash
python scripts/wordplay_explorer.py SPOT --words TOPS POTS POST STOP --json
python -m unittest discover -s tests -p 'test_wordplay_explorer.py'
```

The tool discovers and checks reversals and anagrams from the supplied words. It does **not** write finished clues or fabricate semantic relationships. A later stage should add semantic fodder discovery, surface generation and blinded editorial ranking, while preserving the same mechanical verification boundary.

## Editorial trial records

For each candidate, record `answer`, `clue`, `definition`, `mechanism`, `fodder`, `indicator`, `exact_parse`, `surface_story`, `misdirection`, `fairness_risks`, `editorial_status` and `reviewer`. Reject a clue if its exact parse fails, even if its surface is delightful.
