"""Vocabulary-aware grid pre-ranking.

This is a cheap *necessary-condition* heuristic, not a promise of a fill.
A slot with no preferred-length candidates must consume an exception; longer
slots with few preferred words are penalised before expensive CSP search.
"""
from collections import Counter
from generate_grid import slots
from rank_grids import metrics

def vocabulary_metrics(grid, scores, preferred_score, max_exceptions):
    lengths=Counter(len(s) for s in slots(grid))
    preferred=Counter(len(w) for w,v in scores.items() if v>=preferred_score)
    available=Counter(len(w) for w in scores)
    forced=sum(n for length,n in lengths.items() if preferred[length]==0)
    scarce=sum(n/max(1,preferred[length]) for length,n in lengths.items())
    impossible=sum(n for length,n in lengths.items() if available[length]<n)
    # A low structural score remains desirable, but vocabulary feasibility
    # dominates when evaluating candidate grids for Accessible difficulty.
    structural=metrics(grid)['score']
    return {'forced_exceptions_lower_bound':forced,
            'preferred_scarcity':round(scarce,5),
            'insufficient_length_supply':impossible,
            'structural_score':structural,
            'vocabulary_rank':round(10000*impossible+
                                    1000*max(0,forced-max_exceptions)+
                                    20*scarce+structural,5)}

def select_vocabulary_aware(candidates, scores, preferred_score, max_exceptions):
    """Accept (structural_score, seed, pattern) tuples; return best with metrics."""
    ranked=[]
    for _,seed,pattern in candidates:
        v=vocabulary_metrics(pattern,scores,preferred_score,max_exceptions)
        ranked.append((v['vocabulary_rank'],v['structural_score'],seed,pattern,v))
    if not ranked:
        raise ValueError('No candidate grids')
    _,_,seed,pattern,v=min(ranked,key=lambda x:(x[0],x[1],x[2]))
    return pattern,seed,{**metrics(pattern),'vocabulary':v}
