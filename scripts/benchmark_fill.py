#!/usr/bin/env python3
"""Find a complete 50–55-entry draft first, then attempt vocabulary improvement.

Requires cmudict and wordfreq. Produces an unreviewed draft, never a public puzzle.
"""
import argparse
import json
import tempfile
import time
from pathlib import Path

from fill_grid import fill
from generate_grid import generate, slots
from rank_grids import select, select_vocabulary, metrics

def run(seed=0, max_nodes=10000, grid_attempts=20000, min_frequency=3.0,
        grid_trials=4, max_exceptions=5, exception_floor=2.0,
        grid_candidates=8, grid_strategy='ranked'):
    if grid_candidates<1 or grid_strategy not in ('ranked','random','vocabulary'):
        raise ValueError('Invalid grid selection settings')
    if grid_trials<1 or max_nodes<grid_trials:
        raise ValueError('max_nodes must be >= grid_trials >= 1')
    if not 0<=max_exceptions<=55 or exception_floor>min_frequency:
        raise ValueError('Invalid exception settings')
    try:
        import cmudict
        from wordfreq import zipf_frequency
    except ImportError as exc:
        raise SystemExit('Install: python -m pip install cmudict wordfreq') from exc
    words=sorted({w.upper() for w in cmudict.words()
                  if w.isascii() and w.isalpha() and 3<=len(w)<=15})
    scores={w:zipf_frequency(w,'en') for w in words}
    from collections import Counter
    common_counts=Counter(len(w) for w in words if scores[w]>=min_frequency)
    eligible=sum(v>=min_frequency for v in scores.values())
    allowed=sum(v>=exception_floor for v in scores.values())
    start=time.monotonic()
    trials=[]
    # The budget is a total cap across all layouts, not per layout.
    base,extra=divmod(max_nodes,grid_trials)
    with tempfile.TemporaryDirectory() as tmp:
        dictionary=Path(tmp)/'words.txt'
        dictionary.write_text('\n'.join(words)+'\n',encoding='utf-8')
        for trial in range(grid_trials):
            trial_seed=seed+trial
            budget=base+(1 if trial<extra else 0)
            try:
                if grid_strategy=='vocabulary':
                    pattern,selected_seed,grid_metrics=select_vocabulary(
                        trial_seed,common_counts,grid_candidates,grid_attempts)
                elif grid_strategy=='ranked':
                    pattern,selected_seed,grid_metrics=select(
                        trial_seed,grid_candidates,grid_attempts)
                else:
                    pattern=generate(seed=trial_seed,attempts=grid_attempts)
                    selected_seed=trial_seed
                    grid_metrics=metrics(pattern)
            except RuntimeError as exc:
                trials.append({'seed':trial_seed,'status':'grid_failed','reason':str(exc)})
                continue
            # Paired comparison: both rankings evaluate the identical candidate pool.
            # No additional solver budget is spent on the alternate ranking.
            paired=None
            if grid_strategy in ('ranked','vocabulary'):
                geometric,geometric_seed,geometric_metrics=select(
                    trial_seed,grid_candidates,grid_attempts)
                lexical,lexical_seed,lexical_metrics=select_vocabulary(
                    trial_seed,common_counts,grid_candidates,grid_attempts)
                paired={'geometric_seed':geometric_seed,
                        'vocabulary_seed':lexical_seed,
                        'same_grid':geometric_seed==lexical_seed,
                        'geometric_metrics':geometric_metrics,
                        'vocabulary_metrics':lexical_metrics}
            entry_count=len(slots(pattern))
            if not 50<=entry_count<=55:
                raise AssertionError('Generated grid violates 50–55 entry contract')
            started=time.monotonic()
            # Attempt a high-quality fill first, with a strictly bounded budget.
            # If this fails, retain the unrestricted feasibility path.
            quality_started=time.monotonic()
            quality_status='unfilled'
            quality_nodes=None
            improved=None
            quality_budget=max(1,budget//4)
            try:
                improved,quality_nodes=fill(
                    pattern,dictionary,seed=trial_seed,max_nodes=quality_budget,
                    word_scores=scores,min_score=exception_floor,
                    preferred_score=min_frequency,max_exceptions=max_exceptions,
                    solver='backtracking')
                quality_status='filled_unreviewed'
            except (RuntimeError,ValueError):
                pass
            quality_seconds=round(time.monotonic()-quality_started,2)
            # Phase 1: prove a complete fill exists, without vocabulary constraints.
            try:
                baseline,feasibility_nodes=fill(
                    pattern,dictionary,seed=trial_seed,max_nodes=budget,
                    solver='backtracking')
            except RuntimeError as exc:
                if improved is not None:
                    baseline=improved
                    feasibility_nodes=None
                else:
                    trials.append({'seed':trial_seed,'status':'unfilled','entries':entry_count,
                               'node_budget':budget,'selected_grid_seed':selected_seed,
                               'grid_metrics':grid_metrics,'paired_selection':paired,'reason':str(exc),
                               'fill_seconds':round(time.monotonic()-started,2),
                               'quality_status':quality_status,
                               'quality_seconds':quality_seconds})
                    continue
            feasibility_seconds=round(time.monotonic()-started,2)
            def assess(draft):
                answers=[c['answer'] for group in draft['clues'].values() for c in group]
                exceptions=sorted(
                    ({'answer':w,'frequency':scores[w]} for w in answers
                     if scores[w]<min_frequency),
                    key=lambda x:(x['frequency'],x['answer']))
                return {'exceptions':exceptions,'exception_count':len(exceptions),
                        'mean_frequency':round(sum(scores[w] for w in answers)/len(answers),3),
                        'minimum_frequency':min(scores[w] for w in answers)}
            baseline_quality=assess(baseline)
            improved_quality=assess(improved) if improved else None
            # Fewer uncommon answers wins; then higher mean frequency.
            selected='baseline'
            draft=baseline
            if improved is not None and (
                improved_quality['exception_count'],-improved_quality['mean_frequency']
            ) < (baseline_quality['exception_count'],-baseline_quality['mean_frequency']):
                selected='improved'
                draft=improved
            selected_quality=assess(draft)
            trials.append({'seed':trial_seed,'status':'filled_unreviewed',
                           'entries':entry_count,'selected_grid_seed':selected_seed,
                           'grid_metrics':grid_metrics,'paired_selection':paired,'feasibility_nodes':feasibility_nodes,
                           'feasibility_seconds':feasibility_seconds,
                           'quality_status':quality_status,'quality_nodes':quality_nodes,
                           'quality_seconds':quality_seconds,
                           'baseline_quality':baseline_quality,
                           'improved_quality':improved_quality,
                           'selected':selected,
                           'quality_target_met':selected_quality['exception_count']<=max_exceptions,
                           **selected_quality})
            return {'status':'filled_unreviewed','seed':seed,'dictionary_words':len(words),
                    'eligible_words':eligible,'allowed_words':allowed,
                    'min_frequency':min_frequency,'exception_floor':exception_floor,
                    'max_exceptions':max_exceptions,'grid_trials':grid_trials,'grid_strategy':grid_strategy,
                    'grid_candidates':grid_candidates,
                    'max_nodes_total':max_nodes,'elapsed_seconds':round(time.monotonic()-start,2),
                    'trials':trials,'draft':draft}
    return {'status':'unfilled','seed':seed,'dictionary_words':len(words),
            'eligible_words':eligible,'allowed_words':allowed,
            'min_frequency':min_frequency,'exception_floor':exception_floor,
            'max_exceptions':max_exceptions,'grid_trials':grid_trials,'grid_strategy':grid_strategy,
            'grid_candidates':grid_candidates,
            'max_nodes_total':max_nodes,'elapsed_seconds':round(time.monotonic()-start,2),
            'trials':trials}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--max-nodes',type=int,default=10000)
    parser.add_argument('--grid-attempts',type=int,default=20000)
    parser.add_argument('--grid-trials',type=int,default=4)
    parser.add_argument('--grid-candidates',type=int,default=8)
    parser.add_argument('--grid-strategy',choices=('ranked','random','vocabulary'),default='ranked')
    parser.add_argument('--max-exceptions',type=int,default=5)
    parser.add_argument('--exception-floor',type=float,default=2.0)
    parser.add_argument('--min-frequency',type=float,default=3.0)
    parser.add_argument('--report',default='fill-benchmark.json')
    args=parser.parse_args()
    report=run(args.seed,args.max_nodes,args.grid_attempts,args.min_frequency,
               args.grid_trials,args.max_exceptions,args.exception_floor,
               args.grid_candidates,args.grid_strategy)
    target=Path(args.report).resolve()
    published=(Path(__file__).resolve().parents[1]/'site'/'puzzles').resolve()
    if target==published or published in target.parents:
        parser.error('Benchmark drafts cannot be written to published puzzles')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='draft'},indent=2))
    print('Report:',target)
    if report['status']!='filled_unreviewed':
        print('No complete fill found; inspect per-grid trial results.')

if __name__=='__main__':
    main()
