---
name: cryptic-clue-composer
description: Develop and critique inventive British cryptic crossword clues with precise wordplay, natural misleading surfaces and diverse mechanisms. Use when composing, revising or reviewing clues.
---

# Cryptic clue composer

You are composing for experienced British cryptic solvers. Accessible vocabulary does **not** mean literal or easy clues. Seek delight through fair surprise.

## Working method

1. Read `editorial/clue-examples.json` and `editorial/example-library.md`. Treat these as **illustrations of transferable creative principles**, not patterns to copy. Prefer contrasting examples, including rejected ones.
2. Inspect the answer from multiple starting points: unusual meanings; letter patterns; cultural associations; plausible surface scenes; phonetics; typography; and conventional devices. **Do not begin every clue with a reversal or anagram.**
3. Generate genuinely distinct constructions: charades, containers, reversals, deletions, substitutions, anagrams, hidden words, alternate letters, homophones, double definitions, cryptic definitions, visual/lateral readings and hybrids. Do not force a quota for an individual answer.
4. For promising constructions, invent several *natural* surface readings. Aim for a little scene, plausible utterance, wry observation or unexpected connection. Every cryptic indicator should belong naturally to the surface.
5. For each candidate, record the exact parse, definition, indicator(s), surface story, misdirection and fairness risks. Verify letter operations using `scripts/wordplay_explorer.py` or `scripts/clue_composer.py` where supported. Semantic equivalence, indicators, definitions, visual tricks and surface quality require judgment.
6. Compare candidates blind where possible: would an experienced solver have a fair route to the answer, followed by a satisfying aha? Reject mechanical-but-obvious clues and strained surfaces.
7. Consider the **whole grid**: variety of mechanisms, humour, difficulty, clue lengths and pacing. Replace a poor answer rather than forcing a filler clue.
8. Leave `fairness_reviewed` false until independent human review. Never assert that automatic letter verification is editorial approval.

## Creative prompts

- What could this answer mean *outside* its usual context?
- Which fragments suggest another domain entirely (clothes, sport, cooking, politics, literature)?
- Could a reversal indicator read naturally as movement, reflection or a change of viewpoint?
- Could a containment indicator describe a person, object or action in a convincing scene?
- Could the whole clue be read as a rebus, visual joke or lateral observation?
- Can the definition hide in plain sight without being inaccurate?
- Is the surface better when the clue is shorter?
- Is this a new idea, or just a variation on the last clue we wrote?

## Reference material

- `editorial/clue-examples.json`: annotated, expandable examples (reference, draft, rejected).
- `editorial/example-library.md`: how to add and interpret examples.
- `editorial/clue-development-workflow.md`: full editorial workflow.
- `scripts/wordplay_explorer.py`: checks literal constructions.
- `scripts/clue_composer.py`: checks proposals and tracks diversity.
- `scripts/validate_clue_examples.py`: validates library structure, **not** clue quality.

## Learning from new clues

When the solver supplies a striking clue, analyse its **exact** letter-level construction before extracting a lesson. Add it as an annotated example with provenance and status. Record what is surprising about the mechanism and what makes the surface conceal it. If parsing is uncertain, mark it as a draft and ask rather than inventing an explanation. Do not overfit: the next clue should explore a different avenue where appropriate.

## Output for a composition trial

Show at least two meaningfully different candidate constructions where feasible, with concise exact parses and editorial criticism. Mark recommendations as provisional. Avoid publishing or merging unreviewed material.
