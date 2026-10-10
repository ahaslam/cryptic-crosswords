"""Load scored British crossword vocabulary from an explicitly exported TSV.

The Exet Lufz source is a JavaScript lexicon, not a plain word list.
Do not assume its internal serialization format or silently copy its data.
An export should contain one entry per line: ANSWER<TAB>POPULARITY_SCORE.
"""
import csv
from pathlib import Path

def normalize_answer(value):
    """Return a grid answer (letters only), preserving British spelling."""
    return ''.join(c for c in value.upper() if 'A' <= c <= 'Z')

def load_scored_tsv(path, min_length=3, max_length=15):
    """Return {ANSWER: score}; reject malformed records instead of guessing."""
    scores={}
    with Path(path).open(encoding='utf-8-sig', newline='') as source:
        for line_no, row in enumerate(csv.reader(source, delimiter='\t'), 1):
            if not row or (len(row)==1 and not row[0].strip()):
                continue
            if row[0].lstrip().startswith('#'):
                continue
            if len(row)!=2:
                raise ValueError(f'Line {line_no}: expected answer and score')
            raw, value=row
            if not raw.strip():
                raise ValueError(f'Line {line_no}: empty answer')
            answer=normalize_answer(raw)
            if not min_length<=len(answer)<=max_length:
                continue
            try:
                score=float(value)
            except ValueError as exc:
                raise ValueError(f'Line {line_no}: invalid score') from exc
            if not 0<=score<=100:
                raise ValueError(f'Line {line_no}: score outside 0..100')
            scores[answer]=max(score,scores.get(answer,0))
    return scores

def export_solver_dictionary(scores, path, minimum_score=0):
    """Write a newline-delimited file compatible with fill_grid.fill."""
    selected=sorted(word for word,score in scores.items() if score>=minimum_score)
    Path(path).write_text(chr(10).join(selected)+chr(10),encoding='utf-8')
    return len(selected)
