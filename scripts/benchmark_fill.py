#!/usr/bin/env python3
"""Reproducible full-sized fill experiment, without publishing any puzzle.

Requires: pip install cmudict
Runs the existing grid generator and dictionary filler against real English
pronunciation-dictionary entries. A filled result is still NOT editorially approved.
"""
import argparse
import json
import tempfile
import time
from pathlib import Path

from fill_grid import fill
from generate_grid import generate, slots

def run(seed=0, max_nodes=10000, grid_attempts=20000, min_frequency=3.0):
    try:
        import cmudict
    except ImportError as exc:
        raise SystemExit('Install dependency with: python -m pip install cmudict') from exc
    raw=cmudict.words()
    words=sorted({w.upper() for w in raw if w.isascii() and w.isalpha() and 3<=len(w)<=15})
    try:
        from wordfreq import zipf_frequency
    except ImportError as exc:
        raise SystemExit('Install dependency with: python -m pip install wordfreq') from exc
    scores={w:zipf_frequency(w,'en') for w in words}
    eligible=sum(v>=min_frequency for v in scores.values())
    started=time.monotonic()
    pattern=generate(seed=seed, attempts=grid_attempts)
    grid_seconds=time.monotonic()-started
    with tempfile.TemporaryDirectory() as tmp:
        dictionary=Path(tmp)/'words.txt'
        dictionary.write_text('\n'.join(words)+'\n',encoding='utf-8')
        fill_started=time.monotonic()
        try:
            result,nodes=fill(pattern,dictionary,seed=seed,max_nodes=max_nodes,
                              word_scores=scores,min_score=min_frequency)
        except RuntimeError as exc:
            return {'status':'unfilled','seed':seed,'pattern':pattern,
                    'entries':len(slots(pattern)),'dictionary_words':len(words),'eligible_words':eligible,
            'min_frequency':min_frequency,'eligible_words':eligible,
                    'min_frequency':min_frequency,
                    'grid_seconds':round(grid_seconds,2),
                    'fill_seconds':round(time.monotonic()-fill_started,2),
                    'max_nodes':max_nodes,'reason':str(exc)}
    return {'status':'filled_unreviewed','seed':seed,'pattern':pattern,
            'entries':len(slots(pattern)),'dictionary_words':len(words),
            'grid_seconds':round(grid_seconds,2),
            'fill_seconds':round(time.monotonic()-fill_started,2),
            'nodes':nodes,'draft':result}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--max-nodes',type=int,default=10000)
    parser.add_argument('--grid-attempts',type=int,default=20000)
    parser.add_argument('--report',default='fill-benchmark.json')
    parser.add_argument('--min-frequency',type=float,default=3.0,
                        help='Minimum wordfreq English Zipf frequency (default 3.0)')
    args=parser.parse_args()
    report=run(args.seed,args.max_nodes,args.grid_attempts,args.min_frequency)
    target=Path(args.report)
    published=(Path(__file__).resolve().parents[1]/'site'/'puzzles').resolve()
    if target.resolve()==published or published in target.resolve().parents:
        parser.error('Benchmark drafts cannot be written to published puzzles')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('pattern','draft')},indent=2))
    print('Report:',target)
    if report['status']!='filled_unreviewed':
        print('No complete fill found. This is a measured result, not a valid puzzle.')

if __name__=='__main__':
    main()
