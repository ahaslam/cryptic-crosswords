#!/usr/bin/env python3
"""Editorial checks for cryptic clue drafts. Never auto-approves clue fairness."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

DIFFICULTIES = ('accessible', 'standard', 'challenging')
DEVICES = ('anagram', 'charade', 'container', 'deletion', 'double-definition',
           'hidden', 'homophone', 'reversal', 'cryptic-definition', 'other')
PLACEHOLDER = '[CRYPTIC CLUE REQUIRED]'

def review(puzzle):
    level=puzzle.get('difficulty')
    issues=[]
    if level not in DIFFICULTIES:
        issues.append('Missing or invalid difficulty')
    clues=puzzle.get('clues',{})
    all_clues=[(direction,c) for direction in ('across','down') for c in clues.get(direction,[])]
    if not all_clues:
        issues.append('No clues')
    devices=Counter()
    answer_set=set()
    signed=0
    for direction,clue in all_clues:
        ref=f"{clue.get('number','?')} {direction}"
        answer=clue.get('answer','')
        text=clue.get('text','')
        if not isinstance(text,str) or not text.strip() or PLACEHOLDER in text:
            issues.append(f'{ref}: missing cryptic clue')
        if answer in answer_set:
            issues.append(f'{ref}: duplicate answer {answer}')
        answer_set.add(answer)
        if not re.fullmatch('[A-Z]+',answer):
            issues.append(f'{ref}: invalid answer')
        editorial=clue.get('editorial')
        if not isinstance(editorial,dict):
            issues.append(f'{ref}: missing editorial record')
            continue
        device=editorial.get('device')
        if device not in DEVICES:
            issues.append(f'{ref}: unknown wordplay device')
        else:
            devices[device]+=1
        if not isinstance(editorial.get('definition'),str) or not editorial['definition'].strip():
            issues.append(f'{ref}: definition not documented')
        if not isinstance(editorial.get('wordplay'),str) or not editorial['wordplay'].strip():
            issues.append(f'{ref}: wordplay not documented')
        if editorial.get('fairness_reviewed') is not True:
            issues.append(f'{ref}: fairness not signed off')
        else:
            signed+=1
        if editorial.get('fairness_reviewed') is True and not editorial.get('reviewer'):
            issues.append(f'{ref}: signed-off clue lacks reviewer attribution')
    if len(devices)<3 and len(all_clues)>=10:
        issues.append('Insufficient variety of documented clue devices')
    return {'difficulty':level,'clue_count':len(all_clues),'signed_off_count':signed,'devices':dict(devices),
            'approved':not issues,'issues':issues}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('puzzle',help='Draft or publication candidate JSON')
    ap.add_argument('--report',help='Optional JSON report')
    args=ap.parse_args()
    report=review(json.loads(Path(args.puzzle).read_text()))
    if args.report:Path(args.report).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['approved'] else 1)

if __name__=='__main__':
    main()
