# Cryptic clue editorial workflow

**Goal:** publish one genuinely enjoyable, fair 15×15 British cryptic at Challenging difficulty, then use it to calibrate the levels.

## 1. Select a fill

Use the Exet Lufz scored dictionary and the reviewed-answer exclusions. A solver result with zero uncommon-word exceptions is **not** automatically editorially acceptable. Review all Across and Down answers together for everyday usage, awkward fragments, proper-name concentration and clueability. Keep draft output outside `site/puzzles`.

## 2. Construct each clue

For every answer, write a natural-sounding clue with a genuine definition and independently verifiable cryptic wordplay. Record:

```json
{
  "number": 1,
  "answer": "LISTEN",
  "text": "Example clue awaiting proper editorial construction",
  "editorial": {
    "device": "anagram",
    "definition": "hear attentively",
    "wordplay": "SILENT rearranged to LISTEN",
    "fairness_reviewed": false,
    "reviewer": null
  }
}
```

The example is **not a valid published clue**. Do not set `fairness_reviewed` until the actual clue has been independently checked for exact letter operations, grammar, definition, enumeration and surface reading.

## 3. Review and publish

Run `python scripts/clue_review.py draft.json` as an editorial pre-publication gate. It rejects missing explanations, placeholders, invalid devices, unsigned or unattributed approvals and duplicate answers. Its structural checks **cannot determine whether the wordplay is actually fair**. Human editorial review remains essential. Only after approval, add the puzzle to the published catalogue and test solving on mobile.

## Difficulty calibration

Start with the Sunday Times near the **Challenging** end of the scale. The current profiles adjust answer-vocabulary selection, **not** measured cryptic difficulty. Collect solver feedback on definition transparency, device variety, multi-step operations and solve time before claiming calibration.
