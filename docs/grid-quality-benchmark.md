# British cryptic grid quality benchmark

## Purpose

Evaluate **properties**, not similarity to any particular published black-square
layout. The initial reference set comprises six user-provided Sunday Times grid
photographs (pages 73, 75, 76, 77, 87 and 91). These are reference observations,
not reusable templates. No photograph or copyrighted puzzle is vendored.

## Measurements

`scripts/rank_grids.py:metrics` reports entry count, Across/Down balance,
entry-length histogram, number of three-letter and 9+-letter entries,
block density, checked-letter ratio, and rotational symmetry.

The initial 26–30 entry target is a *working range*, not a conclusion that
all good British cryptics fall within it. We favour 27–28 but allow variation.

## Separate gates

1. Structural validation: size, connectivity, symmetry, minimum slot length,
   and checking rules.
2. Editorial ranking: soft preferences for balanced Across/Down counts,
   few three-letter answers, varied lengths, and sensible checking.
3. Fillability: complete CSP fill with acceptable vocabulary, reviewed by a
   human before publication.
4. Clue quality: independently review cryptic wordplay and surface readings.

A successful CI run establishes none of the editorial or clue-quality gates
on its own.

## Next experiment

Transcribe the six photographic grids into independent 15-row block patterns,
validate the transcription against visible numbering, and compute the same
metrics. Compare *distributions* against generated grids. Hold back at least
some examples for out-of-sample checks as more references arrive. Do not
hardcode their exact black-square arrangements into the generator.
