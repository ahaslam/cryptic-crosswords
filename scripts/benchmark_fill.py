#!/usr/bin/env python3
"""Find a complete 26–30-entry draft first, then attempt vocabulary improvement.

Requires cmudict and wordfreq. Produces an unreviewed draft, never a public puzzle.
"""
import argparse
import json
import tempfile
import time
from pathlib import Path

from fill_grid import fill
from generate_grid import generate, slots
from rank_grids import select, metrics, candidates
from vocabulary_grid_rank import select_vocabulary_aware
from answer_suitability import assess as assess_suitability
from editorial_signals import review_signal, review_draft
from grid_editorial_quality import score_draft

DIFFICULTY_PRESETS = {
    'accessible': {'cmu_min': 3.5, 'cmu_floor': 2.5, 'lufz_min': 85.0, 'lufz_floor': 60.0, 'max_exceptions': 2},
    'standard': {'cmu_min': 3.0, 'cmu_floor': 2.0, 'lufz_min': 80.0, 'lufz_floor': 50.0, 'max_exceptions': 5},
    'challenging': {'cmu_min': 2.7, 'cmu_floor': 1.8, 'lufz_min': 75.0, 'lufz_floor': 45.0, 'max_exceptions': 6},
}


def run(seed=0, max_nodes=10000, grid_attempts=20000, min_frequency=3.0,
        grid_trials=4, max_exceptions=5, exception_floor=2.0,
        grid_candidates=8, grid_strategy='ranked', scored_dictionary=None, solver='backtracking', difficulty='standard'):
    if difficulty not in DIFFICULTY_PRESETS:
        raise ValueError('Unknown difficulty')
    if solver not in ('backtracking','csp'):
        raise ValueError('Unknown solver')
    if grid_candidates<1 or grid_strategy not in ('ranked','random'):
        raise ValueError('Invalid grid selection settings')
    if grid_trials<1 or max_nodes<grid_trials:
        raise ValueError('max_nodes must be >= grid_trials >= 1')
    if not 0<=max_exceptions<=60 or exception_floor>min_frequency:
        raise ValueError('Invalid exception settings')
    if scored_dictionary is not None:
        from crossword_lexicon import load_scored_tsv
        scores=load_scored_tsv(scored_dictionary)
        words=sorted(scores)
    else:
        try:
            import cmudict
            from wordfreq import zipf_frequency
        except ImportError as exc:
            raise SystemExit('Install: python -m pip install cmudict wordfreq') from exc
        words=sorted({w.upper() for w in cmudict.words()
                      if w.isascii() and w.isalpha() and 3<=len(w)<=15})
        scores={w:zipf_frequency(w,'en') for w in words}
    # Preserve raw scores for reporting and exception budgets; use a separate
    # difficulty-sensitive preference for candidate ordering in the CSP solver.
    score_scale=100.0 if scored_dictionary else 7.0
    suitability_scores={w:assess_suitability(w,max(0,min(1,v/score_scale)),difficulty).score
                        for w,v in scores.items()}
    # Review flags affect ordering, never dictionary validity or cultural origin.
    # Keep the frequency-derived exception budget independent of these signals.
    for word in suitability_scores:
        if review_signal(word).review_required:
            suitability_scores[word]-=30
    eligible=sum(v>=min_frequency for v in scores.values())
    allowed=sum(v>=exception_floor for v in scores.values())
    start=time.monotonic()
    trials=[]
    best_fallback=None
    # The budget is a total cap across all layouts, not per layout.
    base,extra=divmod(max_nodes,grid_trials)
    with tempfile.TemporaryDirectory() as tmp:
        dictionary=Path(tmp)/'words.txt'
        dictionary.write_text('\n'.join(words)+'\n',encoding='utf-8')
        for trial in range(grid_trials):
            trial_seed=seed+trial
            budget=base+(1 if trial<extra else 0)
            try:
                if grid_strategy=='ranked':
                    if difficulty=='accessible':
                        pattern,selected_seed,grid_metrics=select_vocabulary_aware(
                            candidates(trial_seed,grid_candidates,grid_attempts),
                            scores,min_frequency,max_exceptions)
                    else:
                        pattern,selected_seed,grid_metrics=select(
                            trial_seed,grid_candidates,grid_attempts)
                else:
                    pattern=generate(seed=trial_seed,attempts=grid_attempts)
                    selected_seed=trial_seed
                    grid_metrics=metrics(pattern)
            except RuntimeError as exc:
                trials.append({'seed':trial_seed,'status':'grid_failed','reason':str(exc)})
                continue
            entry_count=len(slots(pattern))
            if not 26<=entry_count<=30:
                raise AssertionError('Generated grid violates 26–30 entry contract')
            started=time.monotonic()
            # Phase 1: prefer common entries for Lufz to limit branching.
            # Keep CMUdict baseline unchanged for a controlled comparison.
            try:
                baseline,feasibility_nodes=fill(
                    pattern,dictionary,seed=trial_seed,max_nodes=budget,
                    word_scores=scores if scored_dictionary else None,
                    min_score=exception_floor if scored_dictionary else None,
                    solver=solver,ranking_scores=suitability_scores)
            except RuntimeError as exc:
                trials.append({'seed':trial_seed,'status':'unfilled','entries':entry_count,
                               'node_budget':budget,'selected_grid_seed':selected_seed,
                               'grid_metrics':grid_metrics,'reason':str(exc),
                               'fill_seconds':round(time.monotonic()-started,2)})
                continue
            feasibility_seconds=round(time.monotonic()-started,2)
            # Phase 2: try a higher-quality fill, but never discard a valid baseline.
            quality_started=time.monotonic()
            quality_status='unfilled'
            quality_nodes=None
            try:
                improved,quality_nodes=fill(
                    pattern,dictionary,seed=trial_seed,max_nodes=budget,
                    word_scores=scores,min_score=exception_floor,
                    preferred_score=min_frequency,max_exceptions=max_exceptions,
                    solver=solver,ranking_scores=suitability_scores)
                quality_status='filled_unreviewed'
            except RuntimeError:
                improved=None
            quality_seconds=round(time.monotonic()-quality_started,2)

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
            # The quality phase enforces the exception cap inside the solver.
            # Keep the unconstrained baseline for diagnostics if no compliant fill exists.
            # First satisfy the rarity budget; among compliant fills prefer
            # better whole-grid editorial diversity, then fewer exceptions.
            selected='baseline'
            draft=baseline
            if improved is not None and (
                (baseline_quality['exception_count']>max_exceptions and
                 improved_quality['exception_count']<=max_exceptions) or
                (improved_quality['exception_count']<=max_exceptions and
                 baseline_quality['exception_count']<=max_exceptions and
                 (-score_draft(improved)['score'],
                  improved_quality['exception_count'],
                  -improved_quality['mean_frequency'])
                 < (-score_draft(baseline)['score'],
                    baseline_quality['exception_count'],
                    -baseline_quality['mean_frequency'])) or
                (improved_quality['exception_count']>max_exceptions and
                 baseline_quality['exception_count']>max_exceptions and
                 (improved_quality['exception_count'],-improved_quality['mean_frequency'])
                 < (baseline_quality['exception_count'],-baseline_quality['mean_frequency']))
            ):
                selected='improved'
                draft=improved
            draft['difficulty']=difficulty
            draft['ranking_policy']='graded_suitability_editorial_v2'
            draft['editorial_review']=review_draft(draft)
            draft['grid_editorial_quality']=score_draft(draft)
            selected_quality=assess(draft)
            trials.append({'seed':trial_seed,'status':'filled_unreviewed',
                           'entries':entry_count,'selected_grid_seed':selected_seed,
                           'grid_metrics':grid_metrics,'feasibility_nodes':feasibility_nodes,
                           'feasibility_seconds':feasibility_seconds,
                           'quality_status':quality_status,'quality_nodes':quality_nodes,
                           'quality_seconds':quality_seconds,
                           'baseline_quality':baseline_quality,
                           'improved_quality':improved_quality,
                           'selected':selected,
                           'baseline_editorial':score_draft(baseline),
                           'improved_editorial':score_draft(improved) if improved else None,
                           'quality_target_met':selected_quality['exception_count']<=max_exceptions,
                           **selected_quality})
            # Compare complete fills across layouts as well as within one layout.
            # A compliant but editorially weak first fill must not terminate
            # the search before alternative layouts have been considered.
            compliant=selected_quality['exception_count']<=max_exceptions
            editorial=score_draft(draft)['score']
            candidate=(0 if compliant else 1,
                       -editorial if compliant else selected_quality['exception_count'],
                       selected_quality['exception_count'] if compliant else -editorial,
                       -selected_quality['mean_frequency'])
            if best_fallback is None or candidate<best_fallback[0]:
                best_fallback=(candidate,draft,selected_quality)
    if best_fallback is not None:
        _,draft,quality=best_fallback
        return {'status':'filled_unreviewed','difficulty':difficulty,
                'dictionary_source':'lufz' if scored_dictionary else 'cmudict',
                'seed':seed,'dictionary_words':len(words),'eligible_words':eligible,
                'allowed_words':allowed,'min_frequency':min_frequency,
                'exception_floor':exception_floor,'max_exceptions':max_exceptions,
                'grid_trials':grid_trials,'grid_strategy':grid_strategy,
                'grid_candidates':grid_candidates,'solver':solver,
                'max_nodes_total':max_nodes,'elapsed_seconds':round(time.monotonic()-start,2),
                'trials':trials,'draft':draft,'selected_quality':quality,
                'quality_target_met':quality['exception_count']<=max_exceptions}
    return {'status':'unfilled','difficulty':difficulty,'seed':seed,'dictionary_words':len(words),
            'eligible_words':eligible,'allowed_words':allowed,
            'min_frequency':min_frequency,'exception_floor':exception_floor,
            'max_exceptions':max_exceptions,'grid_trials':grid_trials,'grid_strategy':grid_strategy,
            'grid_candidates':grid_candidates,
            'max_nodes_total':max_nodes,'elapsed_seconds':round(time.monotonic()-start,2),
            'trials':trials}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,default=0)
    parser.add_argument('--difficulty',choices=tuple(DIFFICULTY_PRESETS),default='standard',
                        help='Provisional answer-vocabulary profile; not a calibrated clue difficulty')
    parser.add_argument('--max-nodes',type=int,default=10000)
    parser.add_argument('--grid-attempts',type=int,default=20000)
    parser.add_argument('--grid-trials',type=int,default=4)
    parser.add_argument('--grid-candidates',type=int,default=8)
    parser.add_argument('--grid-strategy',choices=('ranked','random'),default='ranked')
    parser.add_argument('--max-exceptions',type=int,default=None)
    parser.add_argument('--exception-floor',type=float,default=None)
    parser.add_argument('--min-frequency',type=float,default=None)
    parser.add_argument('--solver',choices=('backtracking','csp'),default='backtracking')
    parser.add_argument('--scored-dictionary',help='Scored TSV export; uses 0..100 popularity scale')
    parser.add_argument('--report',default='fill-benchmark.json')
    args=parser.parse_args()
    preset=DIFFICULTY_PRESETS[args.difficulty]
    scale='lufz' if args.scored_dictionary else 'cmu'
    min_frequency=args.min_frequency if args.min_frequency is not None else preset[scale+'_min']
    exception_floor=args.exception_floor if args.exception_floor is not None else preset[scale+'_floor']
    max_exceptions=args.max_exceptions if args.max_exceptions is not None else preset['max_exceptions']
    report=run(args.seed,args.max_nodes,args.grid_attempts,min_frequency,
               args.grid_trials,max_exceptions,exception_floor,
               args.grid_candidates,args.grid_strategy,args.scored_dictionary,args.solver,args.difficulty)
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
