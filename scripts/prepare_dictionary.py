#!/usr/bin/env python3
"""Prepare a crossword word list from an existing newline-separated source.

Does not download or redistribute source dictionaries. Review licensing before use.
"""
import argparse
import collections
import re
from pathlib import Path

WORD = re.compile(r"[A-Za-z]{3,15}\Z")
def prepare(lines, excluded=(), minimum=3, maximum=15):
    blocked={w.strip().upper() for w in excluded if w.strip()}
    words=set()
    for line in lines:
        word=line.strip().upper()
        if minimum<=len(word)<=maximum and WORD.fullmatch(word) and word not in blocked:
            words.add(word)
    return sorted(words, key=lambda w:(len(w),w))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',help='Licensed word list, one word per line')
    parser.add_argument('--exclude',help='Optional list of disallowed words')
    parser.add_argument('--output',required=True)
    parser.add_argument('--min-length',type=int,default=3)
    parser.add_argument('--max-length',type=int,default=15)
    args=parser.parse_args()
    if not 3<=args.min_length<=args.max_length<=15:
        parser.error('lengths must satisfy 3 <= min <= max <= 15')
    source=Path(args.source)
    exclusions=Path(args.exclude).read_text(encoding='utf-8').splitlines() if args.exclude else []
    words=prepare(source.read_text(encoding='utf-8').splitlines(),exclusions,args.min_length,args.max_length)
    target=Path(args.output)
    if target.resolve()==source.resolve():parser.error('output cannot overwrite source')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('\n'.join(words)+'\n',encoding='utf-8')
    lengths=collections.Counter(map(len,words))
    print(f'Prepared {len(words)} distinct words at {target}')
    print('Counts by length:',dict(sorted(lengths.items())))
    if any(lengths.get(n,0)<100 for n in range(3,11)):
        print('WARNING: Few entries in one or more short lengths; full-grid filling may fail.')
    print('WARNING: Mechanical filtering does not establish word familiarity or clueability.')

if __name__=='__main__':main()
