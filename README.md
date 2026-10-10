# Cryptic Crosswords

A dependency-free, mobile-friendly crossword player designed for static hosting on Cloudflare Pages.

## Deployment

Connect this GitHub repository to **Cloudflare Pages**. Use production branch `main`, framework **None**, build command `exit 0`, output directory `site`.

## Puzzle files

Published puzzles live in `site/puzzles/`. The catalogue is `site/puzzles/index.json`. Each puzzle JSON has `id`, `title`, `size`, `grid` (uppercase solution letters, # for black squares) and `clues.across` / `clues.down` arrays. Each clue has `number`, zero-based `row` and `col`, `answer` and `text`. Answers are included in public JSON to enable browser-side checking.

## Validate and preview

```sh
python3 scripts/validate.py
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000. GitHub Actions runs the validator on every push and pull request.

The included **3×3 puzzle is a technical demonstration only**, not a proper cryptic crossword. Next milestones are a reviewed 15×15 puzzle, dictionary-backed grid generator, editorial clue review and an approved publishing workflow. Do not commit API tokens or private drafts.
