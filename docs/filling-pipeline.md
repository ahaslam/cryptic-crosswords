# Crossword filling pipeline (work in progress)

The `generate_grid.py` script generates **empty 15×15 patterns**. `fill_grid.py` fills patterns using a supplied newline-separated dictionary. Neither script generates cryptic clues.

Example:

```sh
python scripts/generate_grid.py --seed 0 > /tmp/grid-output.txt
# Keep only the first 15 lines (the pattern), without the final entry-count line:
head -n 15 /tmp/grid-output.txt > /tmp/pattern.txt
python scripts/fill_grid.py /tmp/pattern.txt --dictionary /path/to/curated-words.txt --output /tmp/draft.json
python -m unittest discover -s scripts -p 'test_*.py'
```

The filler uses backtracking, most-constrained-first slot selection, crossing-letter constraints and no repeated answers. It has a configurable search budget (`--max-nodes`). A dense 15×15 grid may **not** fill successfully without a large, well-curated dictionary and further optimisation.

**Important:** a mechanically valid fill is not automatically a good crossword. Dictionaries can include obscure names, abbreviations, inflections and unsuitable answers. The current algorithm does not score word familiarity, thematic quality or clueability. The generated JSON deliberately uses `[CRYPTIC CLUE REQUIRED]` placeholders and refuses to write drafts into `site/puzzles/`. A later editorial stage must write and verify cryptic clues and validate the completed puzzle before publication.

Do not publish drafts or commit copyrighted dictionaries without appropriate permission.
